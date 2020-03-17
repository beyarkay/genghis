import os
import subprocess
import random
import datetime
import requests
import sys
import shutil
import json
import time
import glob

layout = []
count = 0

SPAWN_LOCATIONS = []

CMD_LEFT = 'l'
CMD_RIGHT = 'r'
CMD_UP = 'u'
CMD_DOWN = 'd'

START_TIME = datetime.datetime.now()

ICON_BOTS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
ICON_COINS = [l.lower() for l in ICON_BOTS]
ICON_SOLID = '#'
ICON_SPAWN = "_"
ICON_PORTS = [str(i) for i in list(range(0, 20))]
ICON_AIR = ' '

def main():
    # TODO currently gamestate.json doesn't have any checking to see if the file is already opened by bouncer.py
    global SPAWN_LOCATIONS
    global layout

    # Read in the layout template file to figure out spawn locations
    with open("layout_template.txt", "r") as mapfile:
        layout = [line.strip() for line in mapfile.readlines()]
    layout = [list(i) for i in zip(*layout)]

    # Create a list of spawn locations
    for c, col in enumerate(layout):
        for r, item in enumerate(col):
            if item == ICON_SPAWN:
                SPAWN_LOCATIONS.append((c, r))        
    spawn_locations = SPAWN_LOCATIONS[:]
    random.shuffle(spawn_locations)

    # Read gamestate.json to get a list of the bots
    with open("gamestate.json", "r+") as j:
        gamestate = json.load(j)
    # Loop through the bots, and add them to the map at one of the specified spawn locations
    for bot in gamestate['bots'].values():
        if spawn_locations:
            x_pos, y_pos = spawn_locations.pop()
            layout[x_pos][y_pos] = bot['default_icon']
        else:
            raise Exception("Not enough spawn locations for the number of bots, gamestate=" + gamestate)
    # Now replace the unused spawn locations with ICON_AIR
    for x_pos, y_pos in spawn_locations:        
        layout[x_pos][y_pos] = ICON_AIR
    
    add_coin(gamestate['coins'][gamestate['self']], n=5)

    # Save the game-ready 2D list to layout.txt, which will be copied into the bots' directories later
    with open("layout.txt", "w+") as mapfile:
        mapfile.writelines(["".join(list(i)) + "\n" for i in zip(*layout)] )
    # Start the game
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
            raise Exception("{}/bot.py collection failed: {}\nurl={}".format(sn, r.status_code, url))
    if r.ok:
        if not os.path.exists(full_path):
            os.mkdir(full_path)
        
        with open("{}/bot.py".format(full_path), "w+") as botfile:
            botfile.write(bot)
        shutil.copy("layout.txt", "{}/layout.txt".format(full_path))

        with open("gamestate.json", "r+") as j:
            gamestate = json.load(j)

        bot_icon = gamestate['bots'][sn]['default_icon']
        if not bot_icon:
            available_icons = ICON_BOTS[:]
            # Give the first letter of the bot's surname/name preference when picking a symbol
            available_icons.remove(sn[0])
            available_icons.insert(0, sn[0])
            available_icons.remove(sn[3])
            available_icons.insert(0, sn[3])
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
        print("Bot data added to botjson: {}".format(gamestate['bots'][sn]))
        with open("{0}/{1}.json".format(full_path, sn), "w+") as statsfile:
            json.dump(bot_data, statsfile, indent=2)

        with open("gamestate.json", "w") as j:
            json.dump(gamestate, j, indent=2)

def add_bot_to_layout(sn):
    with open("gamestate.json", "r+") as j:
        gamestate = json.load(j)

    inf_loop_count = 0
    while True:
        x_pos, y_pos = random.choice(SPAWN_LOCATIONS)
        if get_cell((x_pos, y_pos), "") == ICON_AIR:
            print("Adding {}({}) to map at {}".format(sn, gamestate['bots'][sn]['default_icon'], (x_pos, y_pos)))
            layout[x_pos][y_pos] = gamestate['bots'][sn]['default_icon']
            with open("layout.txt", "w+") as mapfile:
                mapfile.writelines(["".join(list(i)) + "\n" for i in zip(*layout)] )
            break
        inf_loop_count += 1
        if inf_loop_count > 200:
            raise Exception("Infinite loop: attempting to add {} to map".format(sn))
    

def run():
    global layout

    host = os.path.abspath('../..').split(os.sep)[-1].upper() 
    print("Starting battle on: \n\nhttps://people.cs.uct.ac.za/~{}/genghis/\n\n".format(host.lower()))
    count = 1
    while True:
        with open("gamestate.json", "r+") as j:
            gamestate = json.load(j)
        if gamestate['bots'].keys():
            print("\n===============Round {}===============".format(count))
        else:
            print("No bots in gamestate, sleeping")
            time.sleep(1)
            continue

        for sn in gamestate['bots'].keys():
            directory = "bots/" + sn
            if not os.path.exists(directory):
                add_bot_dir(sn)
                add_bot_to_layout(sn)

            with open("layout.txt", "w+") as mapfile:
                mapfile.writelines(["".join(list(i)) + "\n" for i in zip(*layout)] )
            shutil.copy("layout.txt", "{}/layout.txt".format(directory))
            time.sleep(0.5)
            step(directory)
            update_html()

        count += 1
        print("{} left".format(datetime.timedelta(minutes=5) - (datetime.datetime.now() - START_TIME)))
        if check_is_over():
            break

    # Finish the game nicely
    with open("layout_template.txt", "r") as mapfile:
        layout = [line.strip() for line in mapfile.readlines()]
    layout = [list(i) for i in zip(*layout)]
    update_html()

def step(directory):
    subprocess.run(["python3", os.path.join(directory, "bot.py")])
    with open(os.path.join(directory, "bot_move.json")) as move_file:
        bot_move = json.load(move_file)
    execute_cmd(directory, bot_move)

def execute_cmd(directory, bot_move):
    global layout
    print("Executing cmd: {} is doing {} {}".format(directory, bot_move['action'], bot_move['direction']))
    with open("{0}/{1}.json".format(directory, directory.split(os.sep)[-1]), "r") as statsfile:
        bot_data = json.load(statsfile)

    bot_loc = (None, None)
    for x, col in enumerate(layout):
        for y, item in enumerate(col):
            if item == bot_data['default_icon']:
                bot_loc = (x, y)
                break
        if bot_loc[0] and bot_loc[1]:
            break
    if bot_move['action'] == "walk":
        # Check if the move is legal
        if (bot_move['direction'] == "l" and bot_loc[0] - 1 >= 0) or \
            (bot_move['direction'] == "r" and bot_loc[0] + 1 < len(layout)) or \
            (bot_move['direction'] == "u" and bot_loc[1] - 1 >= 0) or \
            (bot_move['direction'] == "d" and bot_loc[1] + 1 < len(layout[0])):
    
            # Process the move, checking to see if the bot_loc will collide with anything of interest
            if get_cell(bot_loc, bot_move['direction']) == ICON_AIR:
                move_bot(bot_loc, bot_move['direction'], bot_data['default_icon'])
            
            if get_cell(bot_loc, bot_move['direction']) in ICON_COINS:
                grab_coin()
                move_bot(bot_loc, bot_move['direction'], bot_data['default_icon'])
             
            elif get_cell(bot_loc, bot_move['direction']) in ICON_PORTS:
                port_bot(bot_loc, bot_data, get_cell(bot_loc, bot_move['direction']))
    
    elif bot_move['action'] == "attack":
        # Check if there's a bot_loc in the cell that the bot_loc is attacking
        if get_cell(bot_loc, bot_move['direction']) in ICON_BOTS:
            attack(bot_loc, bot_move['direction'], bot_move['using'])
        
    elif bot_move['action'] == "dump":
        pass

    elif bot_move['action'] == "":
        pass

def attack(bot_loc, direction, using):
    pass

def grab_coin():
    print("grab_coin not implemented")

def get_cell(bot_loc, cmd):
    global layout
    cmd_dict = {
        "l": (-1,  0),
        "r": ( 1,  0),
        "u": ( 0, -1),
        "d": ( 0,  1),
        "":  ( 0,  0)
    }
    return layout[bot_loc[0] + cmd_dict[cmd][0]][bot_loc[1] + cmd_dict[cmd][1]]


def move_bot(bot_loc, cmd, curr_bot_icon):
    global layout
    cmd_dict = {
        "l": (-1,  0),
        "r": ( 1,  0),
        "u": ( 0, -1),
        "d": ( 0,  1),
        "":  ( 0,  0)
    }

    layout[bot_loc[0]][bot_loc[1]] = ICON_AIR 
    layout[bot_loc[0] + cmd_dict[cmd][0]][bot_loc[1] + cmd_dict[cmd][1]] = curr_bot_icon 

def add_coin(coin_icon, n=1):
    global layout
    for i in range(n):
        inf_loop_count = 0
        while True:
            location = (random.randint(0, len(layout) - 1), random.randint(0, len(layout[0]) - 1))
            if get_cell(location, "") == ICON_AIR:
                layout[location[0]][location[1]] = coin_icon
                break

            inf_loop_count += 1
            if inf_loop_count > 200:
                raise Exception("Infinite loop: attempting to add coin to map")

def port_bot(bot_loc, bot_data, port):
    """Attempt to transport the given bot to the given port (node)

    Usually called whne a bot touches a port in the game map.
    With a POST request, attempt to connect to the requested node and send through information
    about the bot to be ported.
    
    On success, remove the bot from the current node.
    On failure, raise an exception

    """
    
    global layout
    global ports
    with open("gamestate.json", "r+") as j:
        gamestate = json.load(j)
    new_node = gamestate['ports'][port]
    d = {
        "student_number": bot_data['student_number']
    }
    r = requests.post(
        "https://people.cs.uct.ac.za/~{}/genghis/requests.php".format(new_node), 
        data=d
    )
    if r.ok:
        print("Ported {} from {} to {}".format(bot_data['student_number'], bot_loc, new_node))
        shutil.rmtree("bots/{}".format(bot_data['student_number'].upper()))
        layout[bot_loc[0]][bot_loc[1]] = ICON_AIR
        del gamestate['bots'][bot_data['student_number']]
        with open("layout.txt", "w+") as mapfile:
            mapfile.writelines(["".join(list(i)) + "\n" for i in zip(*layout)])
        with open("gamestate.json", "w") as j:
            json.dump(gamestate, j, indent=2)
    else:
        raise Exception("Port failed: {} to {} gave error {}".format(bot_data['student_number'], new_node, r.status_code))
    

def check_is_over():
    """Check to see if the 5 minute time limit has been reached

    Returns True if over 5 minutes has passed since the script started
    """

    global START_TIME
    return datetime.datetime.now() - START_TIME > datetime.timedelta(minutes=5)



def update_html():
    """Update map.html to represent the current state of the game

    Using map_template.html as a template file, update map.html with some script 
    variables/gamestate.json variables.
    map.html is inserted into a div element in index.html by some JavaScript in the index.html file

    """
    with open("map_template.html", "r") as templatefile:
        html = "\n".join(templatefile.readlines())
    with open("gamestate.json", "r+") as j:
        gamestate = json.load(j)
    
    map_port_fstring = "<a href=\"https://people.cs.uct.ac.za/~{0}/genghis/\" target=\"_blank\">{1}</a>"
    tbody = "<tbody>"
    for x, col in enumerate([list(i) for i in zip(*layout)]):
        tbody += "<tr>"
        for y, item in enumerate(col):
            tbody += "<td class=\"td_equal_relative\">" 
            if item in gamestate['ports'].keys():
                tbody += map_port_fstring.format(gamestate['ports'][item], item)
            else:
                tbody += item 
            tbody += "</td>" 

        tbody += "</tr>"
    tbody += "</tbody>"

    host = os.path.abspath('../..').split(os.sep)[-1].upper() 
    host = "<a href=\"https://people.cs.uct.ac.za/~"+host+"/genghis/\">" + host + "</a>"
    
    sns = gamestate['bots'].keys()
    
    format_string = "<strong><a href=\"https://people.cs.uct.ac.za/~{}/genghis/\" target=\"_blank\">{}</a></strong> ({})"
    bot_icons = [bot['default_icon'] for bot in gamestate['bots'].values()]
    botstrings = [format_string.format(sn, sn, icon) for sn, icon in zip(sns, bot_icons)]
    botstring = ", ".join(botstrings)
    
    ports_fstring = "{0}=><a href=\"https://people.cs.uct.ac.za/~{1}/genghis/\" target=\"_blank\">{1}</a>"
    ports_strings = [ports_fstring.format(k, v) for (k, v) in gamestate['ports'].items()]
    ports_string = ", ".join(ports_strings)
    
    
    status = " (nobody's here...)" if check_is_over() else " (battle in progress!)"
    time_remaining = "{} remaining.".format(str(datetime.timedelta(minutes=5) - (datetime.datetime.now() - START_TIME)))
    
    html = html.replace("{{tbody}}", tbody)
    html = html.replace("{{host}}", host)
    html = html.replace("{{bots}}", botstring)
    html = html.replace("{{status}}", status)
    html = html.replace("{{ports}}", ports_string)
    html = html.replace("{{time_remaining}}", time_remaining)

    with open("map.html", "w+") as mapfile:
        mapfile.write(html)




    

if __name__ == '__main__':
    main()
