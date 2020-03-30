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
# Get the student number of the current bot, based on the file path
sn = os.path.abspath(__file__).split(os.sep)[-2].upper()

# Get the absolute path of the bot file. Used to figure out where supporting files are
bot_dir = "/" + os.path.join(*os.path.abspath(__file__).split(os.sep)[:-1])

def main():
    """Setup the bot to calculate its move, given a gamestate and game layout

    """
    global bot_data
    global sn
    # layout.txt describes the map of the game, where everything is.
    with open(os.path.join(bot_dir, "layout.txt"), "r") as mapfile:
        layout = mapfile.readlines()
    # data.json is the bot's gamestate file, containing meta information about the game
    with open(os.path.join(bot_dir, "data.json"), "r") as statsfile:
        bot_data = json.load(statsfile)

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
    print(bot_data)
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
        enemy_dists = [(abs(e[0] - bot_loc[0]) + abs(e[1] - bot_loc[1])) for e in enemies]
        if any([dist==1 for dist in enemy_dists]): # and there's an enemy adjacent to us 
            move['action'] = 'attack'
            move['weapon'] = weapon_keys[0]

            enemy = get_closest(enemies, bot_loc)
            if enemy[0] < bot_loc[0]:
                move['direction'] = 'l'
            elif enemy[0] > bot_loc[0]:
                move['direction'] = 'r'
            elif enemy[1] < bot_loc[1]:
                move['direction'] = 'u'
            elif enemy[1] > bot_loc[1]:
                move['direction'] = 'd'
            else:
                raise Exception("Bot {} can't find the enemy {}".format(bot_loc, enemy))
        else:
            if enemies:
               closest = get_closest(enemies, bot_loc)
            else:
                closest = get_closest(ports, bot_loc)
            
            move = walk_to(closest, bot_loc)
    else:
        if coins.keys(): # If there are coins to be had, go get them 
            closest = get_closest(list(coins.values())[0], bot_loc)
        else: # Otherwise, go to a port and move on to the next node 
            closest = get_closest(ports, bot_loc)

        move = walk_to(closest, bot_loc)
    print("bot {} is moving: {}".format(bot_loc, str(move)))
    with open(os.path.join(bot_dir, "move.json"), "w+") as move_file:
        json.dump(move, move_file)

def walk_to(loc, bot_loc):
    move = {
        "action":"walk"
    }
    
    if loc[0] < bot_loc[0]:
        move['direction'] = 'l'
    elif loc[0] > bot_loc[0]:
        move['direction'] = 'r'
    elif loc[1] < bot_loc[1]:
        move['direction'] = 'u'
    elif loc[1] > bot_loc[1]:
        move['direction'] = 'd'
    return move




def get_closest(locations, bot_location):
    """Given a list of (x, y) locations, and an initial bot_location, find the item of locations that's
    closest (Manhatten-wise) to the given bot_location

    """


    if not bot_location or not bot_location[0] or not bot_location[1]:
        raise Exception("bot_locations is empty: {}".format(bot_location))
    if not locations:
        raise Exception("locations is empty: {}".format(locations))
    closest = locations[0]
    closest_dist = abs(bot_location[0] - closest[0]) + abs(bot_location[1] - closest[1])
    for l in locations:
        dist = abs(bot_location[0] - l[0]) + abs(bot_location[1] - l[1])
        if dist < closest_dist:
            closest = l
            closest_dist = dist
    return closest


if __name__ == '__main__':
    main()
