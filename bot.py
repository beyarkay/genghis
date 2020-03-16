import json
import os


def main():
    global bot_data
    with open("layout.txt", "r") as mapfile:
        layout = mapfile.readlines()
    

    student_number = os.path.abspath(__file__).split(os.sep)[-2].upper()
#    print("I am {} in {}".format(student_number, __file__))
    with open("bots/{0}/{0}.json".format(student_number), "r") as statsfile:
        bot_data = json.load(statsfile)

    print(get_move(layout))

def get_move(layout):
    move = {
        "action": '',
        "direction": '',
    }
    global bot_data
    fruit = []
    food = []
    walls = []
    ports = []
    bot = (None, None)
    enemies = []
    enemy_icons = list("abcdefghijklmnopqrstuvwxyz")
    enemy_icons.remove(bot_data['default_icon'])
    # For the basic move, simply try to go towards the fruit
    for c, col in enumerate(layout):
        for r, item in enumerate(col):
            if item.lower() == bot_data['default_icon']:
                bot = (r, c)

            elif item == ".":
                food.append((r, c))

            elif item == "@":
                fruit.append((r, c))
           
            elif item == "#":
                walls.append((r, c))
            
            elif item in list("0123456789"):
                ports.append((r, c))
            
            elif item in enemy_icons:
                enemies.append((r, c))
    # Figure out the closest fruit:
    closest = get_closest(fruit, bot)
    
#    closest = get_closest(ports, bot)
#    closest = get_closest(enemies, bot)
    
    move['action'] = "walk"
    
    if closest[0] < bot[0]:
        move['direction'] = 'l'
    elif closest[0] > bot[0]:
        move['direction'] = 'r'
    elif closest[1] < bot[1]:
        move['direction'] = 'u'
    elif closest[1] > bot[1]:
        move['direction'] = 'd'

    with open('bot_move.json', "w+") as move_file:
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
