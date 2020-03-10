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

def main():
    global layout
    with open("layout_template.txt", "r") as mapfile:
        layout = [line.strip() for line in mapfile.readlines()]
    layout = [list(i) for i in zip(*layout)]
    for i, arg in enumerate(sys.argv[1:]):
        print("Creating ./{}/".format(arg))
        if not os.path.exists(arg):
            os.mkdir(arg)
#        try:
        r = requests.get("https://people.cs.uct.ac.za/~{}/genghis/bot.py".format(arg)) 
        print(r)
        if r.ok:
            bot = r.text
        else:
            bot = requests.get("https://people.cs.uct.ac.za/~{}/ghengis/bot.py".format(arg)).text


        # Write all the required files to the bot's directory
        with open("{}/bot.py".format(arg), "w+") as botfile:
            botfile.write(bot)
        shutil.copy("layout_template.txt", "{}/layout.txt".format(arg))
        
        bot_data = {
            "default_icon": ICON_BOTS[i],
            "state": 0,
            "score":0,
            "student_number": arg
        }
        with open("{0}/{0}.json".format(arg), "w+") as statsfile:
            json.dump(bot_data, statsfile)
    run()


def run():
    global count
    is_over = False
    while not is_over:
    # TODO instead, loop through each of the dirs in ./bots/
        dirs = glob.glob(os.path.join("bots", "*"))
        print("\n===============Round {}===============".format(count))
        for directory in dirs:
            """bots/KNXBOY001"""
            student_number = directory.split(os.sep)[-1]
            shutil.copy("layout.txt", "{}/layout.txt".format(directory))
            time.sleep(0.5)
            step(directory)
            is_over = check_is_over()
            with open("layout.txt", "w+") as mapfile:
                mapfile.writelines(["".join(list(i)) + "\n" for i in zip(*layout)] )
            update_html()

        for student_number, bot_path in zip(sys.argv[1:], bot_paths):
            shutil.copy("layout.txt", "{}/layout.txt".format(student_number))
            time.sleep(0.5)
            step(student_number)
            is_over = check_is_over()
            with open("layout.txt", "w+") as mapfile:
                mapfile.writelines(["".join(list(i)) + "\n" for i in zip(*layout)] )
            update_html()
        print("\n".join(["".join(list(i)) for i in zip(*layout)]))

def step(directory):
    result = subprocess.run(["python3", os.path.join(directory, "bot.py")], stdout=subprocess.PIPE)
    cmd = str(result.stdout, encoding='utf8').strip()
    execute_cmd(directory, cmd)
# TODO refactor student_number --> directory
def execute_cmd(directory, cmd):
    global layout
    with open("{0}/{1}.json".format(directory, directory.split(os.sep)[-1]), "r") as statsfile:
        bot_data = json.load(statsfile)

    print("{} is performing '{}'".format(student_number, cmd))
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
            port_bot(bot, bot_data)


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

def port_bot(bot, bot_data):
    r = requests.post(
        "https://people.cs.uct.ac.za/~{}/genghis/requests.php".format(bot_data['student_number']),
        data=bot_data
    ) 
    print(r.status_code)
    print(r.text)
    shutil.rmtree("bots/{}".format(bot_data['student_number']))

def check_is_over():
    global count
    count += 1
    return count > 100

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
