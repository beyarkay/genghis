import json
import os
bot_data = {}
sn = ""
bot_dir = "/" + os.path.join(*os.path.abspath(__file__).split(os.sep)[:-1])

def main():
    global bot_data
    global sn
    sn = os.path.abspath(__file__).split(os.sep)[-2].upper()

    with open(os.path.join(bot_dir, "layout.txt"), "r") as mapfile:
        layout = mapfile.readlines()
    
    with open(os.path.join(bot_dir, sn + ".json"), "r") as statsfile:
        bot_data = json.load(statsfile)

    get_move(layout)

def get_move(layout):
    move = {
        "action": '',
        "direction": '',
    }
    global bot_data
    walls = []
    ports = []
    bot_loc = (None, None)
    enemies = []
    enemy_icons = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    coin_icons = [i.lower() for i in enemy_icons]
    coins = {}
    enemy_icons.remove(bot_data['default_icon'])
    # For the basic move, simply try to go towards the fruit
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
        closest = get_closest(list(coins.values())[0], bot_loc)
    else: # Otherwise, go to a port and move on to the next node 
        closest = get_closest(ports, bot_loc)
    
    move['action'] = "walk"
    
    if closest[0] < bot_loc[0]:
        move['direction'] = 'l'
    elif closest[0] > bot_loc[0]:
        move['direction'] = 'r'
    elif closest[1] < bot_loc[1]:
        move['direction'] = 'u'
    elif closest[1] > bot_loc[1]:
        move['direction'] = 'd'

    with open(os.path.join(bot_dir, "bot_move.json"), "w+") as move_file:
        json.dump(move, move_file)

def get_closest(locations, bot_location):
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
