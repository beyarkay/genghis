import os
import subprocess
import random
import requests
import sys
import shutil
import json
import time
import glob

bot_paths = ["{}/bot.py".format(arg) for arg in sys.argv[1:]]
layout = []
count = 0
CMD_LEFT = 'l'
CMD_RIGHT = 'r'
CMD_UP = 'u'
CMD_DOWN = 'd'

ICON_BOTS = list("abcdefghijklmnopqrstuvwxyz")
ICON_FOOD = '.'
ICON_FRUIT = '@'
ICON_SOLID = '#'
ICON_PORT = [str(i) for i in list(range(0, 20))]
ICON_AIR = ' '
ICON_SOFT = sum([ICON_BOTS, [ICON_FOOD], [ICON_FRUIT]], [])

ports = {
    "1": "KNXBOY001",
    "2": "MSHSTU001",
    "3": "KNXBOY001",
    "4": "MSHSTU001",
}
# TODO setup layout_template to be checked for random bot spawns wherever a _ is found
def main():
    # TODO currently gamestate.json doesn't have any checking to see if the file is already opened by bouncer.py
    global layout
    with open("layout_template.txt", "r") as mapfile:
        layout = [line.strip() for line in mapfile.readlines()]
    layout = [list(i) for i in zip(*layout)]
    for i, arg in enumerate(sys.argv[1:]):
        add_bot_dir(arg)
    run()

def add_bot_dir(sn):
    sn = sn.upper()
    print("Attempting new bot: " + sn)
    full_path = os.path.join("bots", sn)
    
    url = "https://people.cs.uct.ac.za/~{}/genghis/bot.py".format(sn)
    r = requests.get(url) 
    if r.ok:
        bot = r.text
    else:
        url = "https://people.cs.uct.ac.za/~{}/ghengis/bot.py".format(sn)
        r = requests.get(url)
        if r.ok:
            bot = r.text
        else:
            print("{}/bot.py collection failed: {}\nurl={}".format(sn, r.status_code, url))
    if r.ok:
        if not os.path.exists(full_path):
            print("Creating ./{}/".format(full_path))
            os.mkdir(full_path)
        
        with open("{}/bot.py".format(full_path), "w+") as botfile:
            botfile.write(bot)
        shutil.copy("layout_template.txt", "{}/layout.txt".format(full_path))

        with open("gamestate.json", "r+") as j:
            gamestate = json.load(j)

        bot_icon = gamestate['bots'][sn]['default_icon']
        if not bot_icon:
            available_icons = list("abcdefghijklmnopqrstuvwxyz")
            for bot in gamestate['bots'].values():
                ic = bot['default_icon']
                if ic: # new bots are initialised with an empty string as their icon
                    available_icons.remove(ic)
            if not available_icons:
                print("All icons are used up: " + gamestate['bots'])
            bot_icon = available_icons[0]

        # Write all the required files to the bot's directory
        
        bot_data = {
            "default_icon": bot_icon,
            "state": 0,
            "score": 0,
            "student_number": sn
        }
        gamestate['bots'][sn]["default_icon"] = bot_icon
        print("Bot data added: {}".format(gamestate['bots'][sn]))
        with open("{0}/{1}.json".format(full_path, sn), "w+") as statsfile:
            json.dump(bot_data, statsfile, indent=2)

        with open("gamestate.json", "w") as j:
            json.dump(gamestate, j, indent=2)



def run():
    print("Starting battle on: https://people.cs.uct.ac.za/~KNXBOY001/genghis/")
    count = 1
    while True:
        with open("gamestate.json", "r+") as j:
            gamestate = json.load(j)
            dirs = ["bots/" + sn for sn in gamestate['bots']]
        print("\n===============Round {}===============".format(count))
        for directory, sn in zip(dirs, gamestate['bots'].keys()):
            if not os.path.exists(directory):
                add_bot_dir(sn)

            shutil.copy("layout.txt", "{}/layout.txt".format(directory))
            time.sleep(0.5)
            step(directory)
            with open("layout.txt", "w+") as mapfile:
                mapfile.writelines(["".join(list(i)) + "\n" for i in zip(*layout)] )
            update_html()

#        print("\n".join(["".join(list(i)) for i in zip(*layout)]))
        count += 1
        if check_is_over():
            break

def step(directory):
    result = subprocess.run(["python3", os.path.join(directory, "bot.py")], stdout=subprocess.PIPE)
    cmd = str(result.stdout, encoding='utf8').strip()
    execute_cmd(directory, cmd)

# TODO refactor student_number --> directory
def execute_cmd(directory, cmd):
    print("Executing cmd: {} is doing {}".format(directory, cmd))
    global layout
    with open("{0}/{1}.json".format(directory, directory.split(os.sep)[-1]), "r") as statsfile:
        bot_data = json.load(statsfile)

    bot = (None, None)
    for x, col in enumerate(layout):
        for y, item in enumerate(col):
            if item == bot_data['default_icon']:
                bot = (x, y)
                break
        if bot[0] and bot[1]:
            break

    # Check if the move is legal
    if (cmd == "l" and bot[0] - 1 >= 0) or \
        (cmd == "r" and bot[0] + 1 < len(layout)) or \
        (cmd == "u" and bot[1] - 1 >= 0) or \
        (cmd == "d" and bot[1] + 1 < len(layout[0])):

        # Process the move, checking to see if the bot will collide with anything of interest
        if get_cell(layout, bot, cmd) == ICON_AIR:
            move_bot(layout, bot, cmd, bot_data['default_icon'])
        
        elif get_cell(layout, bot, cmd) == ICON_FRUIT:
            move_bot(layout, bot, cmd, bot_data['default_icon'])
            add_fruit(layout)

        elif get_cell(layout, bot, cmd) in ICON_PORT:
            port_bot(bot, bot_data, get_cell(layout, bot, cmd))


def get_cell(layout, bot, cmd):
    cmd_dict = {
        "l": (-1,  0),
        "r": ( 1,  0),
        "u": ( 0, -1),
        "d": ( 0,  1),
        "":  ( 0,  0)
    }
    return layout[bot[0] + cmd_dict[cmd][0]][bot[1] + cmd_dict[cmd][1]]


def move_bot(layout, bot, cmd, curr_bot_icon):
    cmd_dict = {
        "l": (-1,  0),
        "r": ( 1,  0),
        "u": ( 0, -1),
        "d": ( 0,  1),
        "":  ( 0,  0)
    }

    layout[bot[0]][bot[1]] = ICON_AIR 
    layout[bot[0] + cmd_dict[cmd][0]][bot[1] + cmd_dict[cmd][1]] = curr_bot_icon 

def add_fruit(layout):
    while True:
        location = (random.randint(0, len(layout) - 1), random.randint(0, len(layout[0]) - 1))
        if get_cell(layout, location, "") == ICON_AIR:
            layout[location[0]][location[1]] = ICON_FRUIT
            break

def port_bot(bot, bot_data, port):
    global ports
    new_node = ports[port]
    d = {
        "student_number": bot_data['student_number']
    }
    r = requests.post(
        "https://people.cs.uct.ac.za/~{}/genghis/requests.php".format(new_node), 
        data=d
    )
    print("Porting {} to {}".format(bot_data['student_number'], new_node))
    print(r.status_code)
    shutil.rmtree("bots/{}".format(bot_data['student_number'].upper()))


def check_is_over():
    return len(glob.glob(os.path.join("bots", "*"))) == 0

def update_html():
    with open("map_template.html", "r") as templatefile:
        html = "\n".join(templatefile.readlines())
    
    tbody = "<tbody>"
    for x, col in enumerate([list(i) for i in zip(*layout)]):
        tbody += "<tr>"
        for y, item in enumerate(col):
            tbody += "<td class=\"td_equal_relative\">" 
            tbody += item 
            tbody += "</td>" 

        tbody += "</tr>"
    tbody += "</tbody>"

    # TODO this may give troubles with file reading permissions
    host = os.path.abspath('../..').split(os.sep)[-1].upper() 
    host = "<a href=\"https://people.cs.uct.ac.za/~"+host+"/genghis/\">" + host + "</a>"

    bots = [arg + " as " + icon for arg, icon in zip(sys.argv[1:], ICON_BOTS)]
    bots = ["<a href=\"https://people.cs.uct.ac.za/~"+arg+"/genghis/\">" + arg + "</a> as " + icon for arg, icon in zip(sys.argv[1:], ICON_BOTS)]

    html = html.replace("{{tbody}}", tbody)
    html = html.replace("{{host}}", host)
    html = html.replace("{{bots}}", ", ".join(bots))
    with open("map.html", "w+") as mapfile:
        mapfile.write(html)




    

if __name__ == '__main__':
    main()
