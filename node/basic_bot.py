"""
basic_bot.py
author: Boyd Kane: https://github.com/beyarkay

This is the bare-bones, default bot for the genghis battle system. (https://github.com/beyarkay/genghis)

This bot will try to get every coin on the battleground, and then it'll go to a port in order to get to a different node
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
    
    # Now that the setup is complete, calculate the bot's move:
    get_move(layout)

def get_move(layout):
    """Calculate the bot's move, and write it to ./move.json
    The bot's move is a dictionary, with the following keys permitted:
        * 'action': one of ('walk', 'attack')
            * 'walk': simply walk 1 block in the direction specified by 'direction'
            * 'attack': perform an attack, in the direction specified by 'direction', using the coin specified by 'weapon' as the thing you're attacking with
        * 'direction': one of ('l', 'r', 'u', 'd')
            * Simply the direction (left, right, up, or down) in which to perform the action
        * 'weapon': must be a valid, lowercase student number
            * Only used when 'action' is 'attack'
    
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

    # Iterate through every item in the layout and populate the variables initialised above
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
    

    if coins.keys(): # If there are coins to be had, go get them 
        coin_to_get = random.choice(list(coins.keys()))
        closest = get_closest(coins[coin_to_get], bot_loc)
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
