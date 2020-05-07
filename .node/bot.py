"""
bot.py
author: Boyd Kane: https://github.com/beyarkay

This is the bare-bones, default bot for the genghis battle system. (https://github.com/beyarkay/genghis)
This bot expects to be run in its own directory with: 
    * gamestate.json
    * layout.txt

It will not work if not run under those conditions

This bot will try to get every coin on the map, and then it'll go to a port to move onto the next map
"""

import json
import os
bot_data = {}
gamestate = {}
# Get the student number of the current bot, based on the file path
sn = os.path.abspath(__file__).split(os.sep)[-2].upper()

# Get the absolute path of the bot file. Used to figure out where supporting files are
bot_dir = "/" + os.path.join(*os.path.abspath(__file__).split(os.sep)[:-1])

def main():
    """Setup the bot to calculate its move, given a gamestate and game layout

    """
    global bot_data
    global gamestate
    global sn
    # layout.txt describes the map of the game, where everything is.
    with open(os.path.join(bot_dir, "layout.txt"), "r") as mapfile:
        layout = mapfile.readlines()
    # data.json is the bot's gamestate file, containing meta information about the game
    with open(os.path.join(bot_dir, "data.json"), "r") as statsfile:
        gamestate = json.load(statsfile)
    bot_data = gamestate['bots'][sn]
    get_move(layout)

def get_move(layout):
    """Calculate the bot's move, and write it to ./move.json

    """
    move = {
        "action": '',
        "direction": '',
    }
    # Initialise variables. These are all populated with (x, y) coords, and can be used in developing a smarter bot
    global bot_data
    walls = []
    ports = []
    bot_loc = (None, None)
    enemies = []
    enemy_icons = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    coin_icons = [i.lower() for i in enemy_icons]
    coins = {}
    enemy_icons.remove(bot_data['default_icon'])

    # Iterate through every item in the layout. Note that the rows and columns are switched, such that the first
    # variable is the x-coordinate going left/right, and the second is the y-coordinate
    for c, col in enumerate(layout):
        for r, item in enumerate(col):
            if item == bot_data['default_icon']:
                bot_loc = (r, c)

            elif item == "#":
                walls.append((r, c))
            
            elif item in list("0123456789"):
                ports.append((r, c))
            
            elif item in coin_icons:
                if item in coins:
                    coins[item].append((r, c))
                else:
                    coins[item] = [(r, c)]

            elif item in enemy_icons:
                enemies.append((r, c))
    
    weapon_keys = [k for k, v in bot_data['coins'].items() if v > 0]
    move = {}
    if weapon_keys: #if we have a coin to fight with
        enemy_dists = [get_dist(e, bot_loc) for e in enemies]
        if any([dist == 1 for dist in enemy_dists]):
            move['action'] = 'attack'
            move['weapon'] = weapon_keys[0]
            enemy = get_closest(enemies, bot_loc)
            move['direction'] = get_dir(bot_loc, enemy)

        else:
            if enemies:
               closest = get_closest(enemies, bot_loc)
            else:
                closest = get_closest(ports, bot_loc)
            
            move['direction'] = get_dir(bot_loc, closest)
            move['action'] = 'walk'
    else:
        if coins.keys(): # If there are coins to be had, go get them 
            closest = get_closest(list(coins.values())[0], bot_loc)
        else: # Otherwise, go to a port and move on to the next node 
            closest = get_closest(ports, bot_loc)

        move['direction'] = get_dir(bot_loc, closest)
        move['action'] = 'walk'

    with open(os.path.join(bot_dir, "move.json"), "w+") as move_file:
        json.dump(move, move_file)


def get_dist(from_A, to_B):
    delta_x = abs(to_B[0] - from_A[0])
    delta_y = abs(to_B[1] - from_A[1])
    return max(delta_x, delta_y)
    

def get_dir(from_A, to_B):
    delta_x = min(1, max(-1, to_B[0] - from_A[0]))
    delta_y = min(1, max(-1, to_B[1] - from_A[1]))
    move_array = [
        ['lu', 'u', 'ru'], 
        ['l', '', 'r'], 
        ['ld', 'd', 'rd']
    ]
    return move_array[delta_y + 1][delta_x + 1]


def get_closest(locations, bot_location):
    """Given a list of (x, y) locations, and an initial bot_location, find the item of locations that's
    closest (allowing diagonal travel) to the given bot_location

    """

    if not bot_location or not bot_location[0] or not bot_location[1]:
        raise Exception("bot_locations is empty: {}".format(bot_location))
    if not locations:
        raise Exception("locations is empty: {}".format(locations))

    closest = locations[0]
    closest_dist = get_dist(closest, bot_location)
    for l in locations:
        dist = get_dist(l, bot_location)
        if dist < closest_dist:
            closest = l
            closest_dist = dist
    return closest


if __name__ == '__main__':
    main()
