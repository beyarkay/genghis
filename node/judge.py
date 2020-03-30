import re
import glob
import datetime
import json
import os
import random
import shutil
import subprocess
import time

import requests

SPAWN_LOCATIONS = []
PORT_LOCATIONS = []
COINS_PER_BATTLE = 10
TICK_DURATION = 2

START_TIME = datetime.datetime.now()

ICON_BOTS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
ICON_COINS = [l.lower() for l in ICON_BOTS]
ICON_SPAWN = "_"
ICON_PORT = "0"
ICON_PORTS = [str(i) for i in list(range(1, 10))]
ICON_AIR = ' '
cmd_dict = {
    "l": (-1, 0),
    "r": (1, 0),
    "u": (0, -1),
    "d": (0, 1),
    "": (0, 0)
}
RE_SN = re.compile(r"([BCDFGHJKLMNPQRSTVWXYZ]{3}\w{3}\d{3})")
node_dir = "/" + os.path.join(*os.path.abspath(__file__).split(os.sep)[:-1])
genghis_dir = "/" + os.path.join(*os.path.abspath(__file__).split(os.sep)[:-2])

def main():
    global SPAWN_LOCATIONS
    global PORT_LOCATIONS
    with open(os.path.join(node_dir, "layout_template.txt"), "r") as mapfile:
        layout = [line.strip() for line in mapfile.readlines()]
    layout = [list(i) for i in zip(*layout)]
    # Create a list of spawn locations
    for c, col in enumerate(layout):
        for r, item in enumerate(col):
            if item == ICON_SPAWN:
                SPAWN_LOCATIONS.append((c, r))
            elif item == ICON_PORT:
                PORT_LOCATIONS.append((c, r))

    # Load up the registered ports into a list
    gamestate = get_gamestate()
    with open(os.path.join(genghis_dir, "node", "ports.txt"), "r") as ports_file:
        ports = [port.strip() for port in ports_file.readlines() if RE_SN.match(port)]
    random.shuffle(ports)
    random.shuffle(PORT_LOCATIONS) 
    # Add in all the registered ports to the layout and gamestate.
    for port_number, (x_pos, y_pos) in enumerate(PORT_LOCATIONS, 1):
        if ports:
            layout[x_pos][y_pos] = str(port_number)
            gamestate['ports'][str(port_number)] = ports.pop()
        else:
            layout[x_pos][y_pos] = ICON_AIR
    if ports:
        raise Exception("{} is not enough PORT icons in layout template; {} ports left undisplayed".format(len(PORT_LOCATIONS), len(ports)))
    dump_gamestate(gamestate)

    for x_pos, y_pos in SPAWN_LOCATIONS:
        layout[x_pos][y_pos] = ICON_AIR
    dump_layout(layout)

    # Loop through the bots, and add them to the map at one of the specified spawn locations
    add_any_new_bots()
    gamestate = get_gamestate()
    add_coin(gamestate['self'], n=COINS_PER_BATTLE)
    run()

def add_any_new_bots():
    gamestate = get_gamestate()
    bot_paths = glob.glob(os.path.join(genghis_dir, "logs", "*.json"))
    RE_SN = re.compile(r"([BCDFGHJKLMNPQRSTVWXYZ]{3}\w{3}\d{3})")
    for bot_path in bot_paths:
        gamestate = get_gamestate()
        print("Processing botpath: " + bot_path)
        with open(os.path.join(genghis_dir, "logs", bot_path), "r") as bot_file:
            data = json.load(bot_file)
        if data['student_number'] not in gamestate['bots'].keys() and re.match(RE_SN, data['student_number']):
            gamestate['bots'][data['student_number']] = data
            os.remove(os.path.join(genghis_dir, "logs", bot_path))
        else:
            print("Invalid/pre-existing bot found in " + bot_path)
            print("\tBot data={}".format(data))
        # Add as directory
        dump_gamestate(gamestate)
        add_bot_dir(data['student_number'])
        add_bot_to_layout(data['student_number'])


def add_bot_dir(sn):
    sn = sn.upper()
    print("Attempting new bot: " + sn)
    bot_dir = os.path.join(genghis_dir, "bots", sn)

    url = "https://people.cs.uct.ac.za/~{}/genghis/node/bot.py".format(sn)
    r = requests.get(url)
    if not r.ok:
        raise Exception("{}/bot.py collection failed: {}\nurl={}".format(sn, r.status_code, url))
    else:
        bot = r.text
        if not os.path.exists(bot_dir):
            os.mkdir(bot_dir)

        with open("{}/bot.py".format(bot_dir), "w+") as botfile:
            botfile.write(bot)
        shutil.copy(os.path.join(genghis_dir, "vars", "layout.txt"), "{}/layout.txt".format(bot_dir))

        gamestate = get_gamestate()
        print("Gamestate: " + str(gamestate))
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
                if ic:  # new bots are initialised with an empty string as their icon
                    available_icons.remove(ic)
            if not available_icons:
                print("All icons are used up: " + gamestate['bots'])
            bot_icon = available_icons[0]
            gamestate['bots'][sn]["default_icon"] = bot_icon

        print("Bot data added to botjson: {}".format(gamestate['bots'][sn]))
        with open(os.path.join(bot_dir, "data.json"), "w+") as statsfile:
            json.dump(gamestate['bots'][sn], statsfile, indent=2)
        dump_gamestate(gamestate)


def add_bot_to_layout(sn):
    gamestate = get_gamestate()
    layout = get_layout()

    inf_loop_count = 0
    while True:
        assert SPAWN_LOCATIONS
        x_pos, y_pos = random.choice(SPAWN_LOCATIONS)
        if get_cell((x_pos, y_pos), "") == ICON_AIR:
            print("Adding {}({}) to map at {}".format(sn, gamestate['bots'][sn]['default_icon'], (x_pos, y_pos)))
            layout[x_pos][y_pos] = gamestate['bots'][sn]['default_icon']
            dump_layout(layout)
            break
        inf_loop_count += 1
        if inf_loop_count > 200:
            layout_string = "\n".join(["".join(list(i)) for i in zip(*layout)])
            raise Exception("Infinite loop: attempting to add {} to map \n{}".format(sn, layout_string))


def run():
    host_sn = os.path.abspath(__file__).split(os.sep)[3].upper()
    print("Starting battle on: \nhttps://people.cs.uct.ac.za/~{}/genghis/\n".format(host_sn.lower()))
    count = 1

    while True:
        add_any_new_bots()
        gamestate = get_gamestate()
        print(gamestate)
        if gamestate['bots'].keys():
            print("\n===============Round {}===============".format(count))
        else:
            print("No bots in gamestate, sleeping")
            update_html()
            time.sleep(TICK_DURATION)
            continue

        for sn in gamestate['bots'].keys():
            directory = os.path.join(genghis_dir, "bots", sn)
            if not os.path.exists(directory):
                add_bot_dir(sn)
                add_bot_to_layout(sn)

            shutil.copy(os.path.join(genghis_dir, "vars", "layout.txt"), "{}/layout.txt".format(directory))
            time.sleep(TICK_DURATION/len(gamestate['bots'].keys()))
            step_bot(directory)
            update_html()

        count += 1
        time_left = datetime.timedelta(minutes=5) - (datetime.datetime.now() - START_TIME)
        print("{} left".format(str(time_left - datetime.timedelta(microseconds=time_left.microseconds))))
        
        if game_is_over():
            break

    # Finish the game nicely
    with open(os.path.join(node_dir, "layout_template.txt"), "r") as mapfile:
        layout = [line.strip() for line in mapfile.readlines()]
    layout = [list(i) for i in zip(*layout)]
    update_html()


def step_bot(bot_dir):
    subprocess.run(["python3", os.path.join(bot_dir, "bot.py")])
    with open(os.path.join(bot_dir, "move.json"), "r") as move_file:
        bot_move = json.load(move_file)
    execute_cmd(bot_dir, bot_move)


def execute_cmd(bot_dir, bot_move):
    print("Executing cmd: {} is doing {} {}".format(bot_dir, bot_move['action'], bot_move['direction']))
    sn = bot_dir.split(os.sep)[-1]
    with open(os.path.join(bot_dir, "data.json"), "r") as statsfile:
        bot_data = json.load(statsfile)
    layout = get_layout()

    bot_loc = (None, None)
    for x, col in enumerate(layout):
        for y, item in enumerate(col):
            if item == bot_data['default_icon']:
                bot_loc = (x, y)
                break
        if bot_loc[0] and bot_loc[1]:
            break
    assert bot_loc[0] is not None and bot_loc[1] is not None, "bot_data={} and layout=\n{}".format(str(bot_data), "\n".join(["".join(list(i)) for i in zip(*layout)]))
    if bot_move['action'] == "walk":
        # Check if the move is legal
        if (bot_move['direction'] == "l" and bot_loc[0] - 1 >= 0) or \
                (bot_move['direction'] == "r" and bot_loc[0] + 1 < len(layout)) or \
                (bot_move['direction'] == "u" and bot_loc[1] - 1 >= 0) or \
                (bot_move['direction'] == "d" and bot_loc[1] + 1 < len(layout[0])):

            # Process the move, checking to see if the bot_loc will collide with anything of interest
            cell = get_cell(bot_loc, bot_move['direction'])
            if cell == ICON_AIR:
                move_bot(bot_loc, bot_move['direction'], bot_data['default_icon'])

            if cell in ICON_COINS:
                grab_coin(bot_data['student_number'], cell)
                move_bot(bot_loc, bot_move['direction'], bot_data['default_icon'])

            elif cell in ICON_PORTS:
                port_bot(bot_loc, bot_data, get_cell(bot_loc, bot_move['direction']))

    elif bot_move['action'] == "attack":
        # Check if there's a bot_loc in the cell that the bot_loc is attacking
        if get_cell(bot_loc, bot_move['direction']) in ICON_BOTS:
            attack(bot_loc, bot_move['direction'], bot_move['weapon'])

    elif bot_move['action'] == "dump":
        pass

    elif bot_move['action'] == "":
        pass


def attack(bot_loc, direction, weapon):
    """Calculate the damage done, which is based off of the value of `using`

    For one bot(the attacker) to attack another(the defender), the attacker must spend a coin.
    The letters that make up the coin's student number will determine how effective the attack is against a given defender.

    let A_1 be the first char of the attacker's coin, and D_1 be the first char of the defender's student numnber
    The formula for damage done is:
    round(1 - (ord(A_1) - ord(D_1) - ord('A')) / 26)

    (Note that Python3 will round to the nearest even number in the case of `round(XX.5)`)
    
    For example, if bot BBBBBB001 is attacked with the coin AAAAAA001, then a damage of 1 will be delt to BBBBBB001
    if bot CCCCCC001 is attacked with coin AAAAAA001, the damage to CCCCCC001 will still be 1
    This is the same for DDDDDD0001, ..., NNNNNN001 (all get delt a damage of 1)
    The flip side of the alphabet is immune, and get delt damage of 0. ie student numbers MMMMMM001 through to ZZZZZZ001 will receive no damage when attacked with a coin who's student number is AAAAAA001

    """
    # TODO convert all coins to be lowercase 
    gamestate = get_gamestate()
    print("Gamestate before {} attacks with {}:\n{}".format(bot_loc, weapon, gamestate))
    defender_icon = get_cell(bot_loc, direction)
    attacker_icon = get_cell(bot_loc, "")
    defender = {}
    attacker = {}
    for sn, bot in gamestate['bots'].items():
        if bot['default_icon'] == attacker_icon:
            attacker = bot
        elif bot['default_icon'] == defender_icon:
            defender = bot
        if attacker and defender:
            break
    if not attacker:
        raise Exception("Attacker {} not found in bots: {}".format(attacker_icon, gamestate['bots']))
    if not defender:
        raise Exception("Defender {} not found in bots: {}".format(defender_icon, gamestate['bots']))
    
    # Check the attacking bot has the coins
    if weapon in attacker['coins'].keys() and attacker['coins'][weapon] > 0:
        # Calculate the attack amount
        wpn_ord = ord(weapon[0]) - ord('a')
        dfn_ord = ord(defender['student_number'][0]) - ord('A')
        damage = round(1 - (wpn_ord - dfn_ord)/26)

        # Make the defending bot drop the appropriate coinage
        if defender['coins']: # random.choices raises IndexError if the population is empty
            dropped_coin = random.choices(
                list(defender['coins'].keys()),
                [int(v) for v in defender['coins'].values()],
                k=1
            )[0]
            defender['coins'][dropped_coin] -= 1
            if damage == 1: # don't just remove the coin from the defender, also add it to the attacker
                if dropped_coin in attacker['coins'].keys():
                    attacker['coins'][dropped_coin] += 1
                else:
                    attacker['coins'][dropped_coin] = 1
        
        # Remove the weapon from the attacking bot
        attacker['coins'][weapon] -= 1;
    else:
        print("Bot {} does not have the weapon {} that it's trying to attack with".format(attacker, weapon))
    
    print("Gamestate after {} attacked with {}:\n{}".format(bot_loc, weapon, gamestate))
    
    dump_gamestate(gamestate)

def grab_coin(sn, icon):
    # First update the gamestate, then update the bot's files
    gamestate = get_gamestate()

    # Figure out what the coin associated with the given coin_icon is
    for coin_sn, coin_icon in gamestate['coins'].items():
        if icon == coin_icon:
            coin = coin_sn
            break
    if 'coins' not in gamestate['bots'][sn].keys():
        gamestate['bots'][sn]['coins'] = {}
        
    if gamestate['bots'][sn]['coins'][coin]:
        gamestate['bots'][sn]['coins'][coin] += 1
    else:
        gamestate['bots'][sn]['coins'][coin] = 1

    dump_gamestate(gamestate)

    # TODO refactor out a method to copy over the bot's information from gamestate to bots/.../data.json
    # Now write the same data to the bot's data.json
    with open(os.path.join(genghis_dir, "bots", sn, "data.json"), "r") as data_file:
        data = json.load(data_file)
    if 'coins' not in data.keys():
        data['coins'] = {
            sn: 1
        }
    elif coin in data['coins'].keys():
        data['coins'][coin] += 1
    else:
        data['coins'][coin] = 1

    with open(os.path.join(genghis_dir, "bots", sn, "data.json"), "w") as data_file:
        json.dump(data, data_file, indent=2)

def get_cell(bot_loc, cmd):
    layout = get_layout()
    global cmd_dict
    return layout[bot_loc[0] + cmd_dict[cmd][0]][bot_loc[1] + cmd_dict[cmd][1]]


def move_bot(bot_loc, cmd, curr_bot_icon):
    global cmd_dict
    layout = get_layout()
    assert layout
    assert 0 <= bot_loc[0] < len(layout)
    assert 0 <= bot_loc[1] < len(layout[0])
    layout[bot_loc[0]][bot_loc[1]] = ICON_AIR
    layout[bot_loc[0] + cmd_dict[cmd][0]][bot_loc[1] + cmd_dict[cmd][1]] = curr_bot_icon
    dump_layout(layout)


def add_coin(sn, n=1):
    """Create a potentially new coin, and if required, add it to the layout file, the gamestate's log of coins, and every bot's coin counter
    --sn str: the student number of the coin to be added to the node
    --n=1 int: the number of coins to add (in random positions) to the layout file
    """

    gamestate = get_gamestate()
    print("Making {} x {}".format(n, sn))
    # If the coin doesn't have an icon, give it one based on the student number
    if sn.lower() not in gamestate['coins'].keys():
        available_coins = list("abcdefghijklmnopqrstuvwxyz")
        for coin_icon in gamestate['coins'].values():
            available_coins.remove(coin_icon)
        if sn[3].lower() in available_coins:
            gamestate['coins'][sn.lower()] = sn[3].lower()

        elif sn[0].lower() in available_coins:
            gamestate['coins'][sn.lower()] = sn[0].lower()

        else:
            gamestate['coins'][sn.lower()] = available_coins[0]

    coin_icon = gamestate['coins'][sn.lower()]
    # Now check that each bot in the node has a counter for the potentially new coin
    for bot_sn, bot in gamestate['bots'].items():
        if 'coins' not in bot.keys():
            bot['coins'] = {}
        bot['coins'][sn.lower()] = 0

    # Finally, add the potentially new coin to the layout
    layout = get_layout()
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
    dump_gamestate(gamestate)
    dump_layout(layout)


def port_bot(bot_loc, bot_data, port):
    """Attempt to transport the given bot to the given port (node)

    Usually called whne a bot touches a port in the game map.
    With a POST request, attempt to connect to the requested node and send through information
    about the bot to be ported.
    
    On success, remove the bot from the current node.
    On failure, raise an exception

    """
    layout = get_layout()
    gamestate = get_gamestate()
    # We cannot guarantee the bot will be ported, so temporarily remove the bot from the current layout, gamestate and bots/
    shutil.move(
        os.path.join(genghis_dir, "bots", bot_data['student_number'].upper()),
        os.path.join(genghis_dir, "bots", "." + bot_data['student_number'].upper())
    )
    layout[bot_loc[0]][bot_loc[1]] = ICON_AIR
    tmp_bot = gamestate['bots'][bot_data['student_number']]
    del gamestate['bots'][bot_data['student_number']]
    dump_gamestate(gamestate)
    dump_layout(layout)

    # Attempt to port the bot
    new_node = gamestate['ports'][port]
    r = requests.post(
        "https://people.cs.uct.ac.za/~{}/genghis/node/requests.php".format(new_node),
        json=bot_data
    )

    # If the port was successful, permenantly delete all the temporary files
    if r.ok:
        print("Ported {} from {} to {} (bot_data={})".format(bot_data['student_number'], bot_loc, new_node, bot_data))
        shutil.rmtree(os.path.join(genghis_dir, "bots", "." + bot_data['student_number'].upper()))
    else:
        # else, move all the temporary files back to where they were and raise an error
        shutil.move(
            os.path.join(genghis_dir, "bots", "." + bot_data['student_number'].upper()),
            os.path.join(genghis_dir, "bots", bot_data['student_number'].upper())
        )
        layout[bot_loc[0]][bot_loc[1]] = bot_data['default_icon']
        gamestate['bots'][bot_data['student_number']] = tmp_bot
        dump_gamestate(gamestate)
        dump_layout(layout)


def game_is_over():
    """Check to see if the 5 minute time limit has been reached

    :return: True if over 5 minutes has passed since the script started
    """
    global START_TIME
    return datetime.datetime.now() - START_TIME > datetime.timedelta(minutes=5)


def update_html():
    """Update map.html to represent the current state of the game

    Using map_template.html as a template file, update map.html with some script 
    variables/gamestate.json variables.
    map.html is inserted into a div element in index.html by some JavaScript in the index.html file

    """
    pass
#    with open(os.path.join(genghis_dir, "node", "map_template.html"), "r") as templatefile:
#        html = "\n".join(templatefile.readlines())
#    layout = get_layout()
#    gamestate = get_gamestate()
#
#    map_port_fstring = "<a href=\"https://people.cs.uct.ac.za/~{0}/genghis/\" >{1}</a>"
#    tbody = "\n<tbody>\n"
#    for x, col in enumerate([list(i) for i in zip(*layout)]):
#        tbody += "\t<tr>\n"
#        for y, item in enumerate(col):
#            tbody += "\t\t<td class=\"td_equal_relative\">\n\t\t\t"
#            if item in gamestate['ports'].keys():
#                tbody += map_port_fstring.format(gamestate['ports'][item], item)
#            else:
#                tbody += item
#            tbody += "\n\t\t</td>\n"
#
#        tbody += "\t</tr>\n"
#    tbody += "</tbody>"
#
#    host = str(os.path.abspath(__file__).split(os.sep)[3].upper())
#    host_string = "<a href=\"https://people.cs.uct.ac.za/~" + host + "/genghis/\">" + host + "</a>"
#
#    sns = gamestate['bots'].keys()
#
#    format_string = "<strong><a href=\"https://people.cs.uct.ac.za/~{}/genghis/\" >{}</a></strong> ({})"
#    bot_icons = [bot['default_icon'] for bot in gamestate['bots'].values()]
#    botstrings = [format_string.format(sn, sn, icon) for sn, icon in zip(sns, bot_icons)]
#    botstring = ", ".join(botstrings)
#
#    ports_fstring = "{0} -> <a href=\"https://people.cs.uct.ac.za/~{1}/genghis/\">{1}</a>"
#    ports_strings = [ports_fstring.format(k, v) for (k, v) in gamestate['ports'].items()]
#    ports_string = ",    ".join(ports_strings)
#    
#    if game_is_over():
#        status = " (Time's up)"
#        time_remaining = "No time remaining"
#    else:
#        status = " (battle in progress!)"
#        time_left = datetime.timedelta(minutes=5) - (datetime.datetime.now() - START_TIME)
#        time_remaining = "{} left".format(str(time_left - datetime.timedelta(microseconds=time_left.microseconds)))
#
#    coins_strings = []
#    count = 0
#    print("Gamestate while writing to html: {}".format(str(gamestate)))
#    for sn, bot in gamestate['bots'].items():
#        if 'coins' in bot.keys():
#            coin_arr = []
#            for coin, count in bot['coins'].items():
#                coin_arr.append("{0} x {1}".format(count, coin.lower()))
#            coins_strings.append("{} has: {}".format(sn,  ", ".join(coin_arr)))
#    coins_str = "<br>".join(coins_strings)
#
#    html = html.replace("{{tbody}}", tbody)
#    html = html.replace("{{host}}", host_string)
#    html = html.replace("{{bots}}", botstring)
#    html = html.replace("{{status}}", status)
#    html = html.replace("{{ports}}", ports_string)
#    html = html.replace("{{time_remaining}}", time_remaining)
#    html = html.replace("{{coins}}", coins_str)
#
#    with open(os.path.join(genghis_dir, "www", "map.html"), "w+") as mapfile:
#        mapfile.write(html)


def get_gamestate():
    with open(os.path.join(genghis_dir, "vars", "gamestate.json"), "r+") as j:
        gamestate = json.load(j)
    return gamestate


def dump_gamestate(state):
    with open(os.path.join(genghis_dir, "vars", "gamestate.json"), "w") as j:
        json.dump(state, j, indent=2)


def dump_layout(layout_arr):
   # print("".join(["".join(list(i)) + "\n" for i in zip(*layout_arr)]))
    with open(os.path.join(genghis_dir, "vars", "layout.txt"), "w+") as mapfile:
        mapfile.writelines(["".join(list(i)) + "\n" for i in zip(*layout_arr)])


def get_layout():
    # Read in the layout template file to figure out spawn locations
    with open(os.path.join(genghis_dir, "vars", "layout.txt"), "r") as mapfile:
        layout = [line.strip() for line in mapfile.readlines()]
    return [list(i) for i in zip(*layout)]


if __name__ == '__main__':
    main()