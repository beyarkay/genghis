import json
import os


def main():
    global bot_data
    with open("layout.txt", "r") as mapfile:
        layout = mapfile.readlines()
    
    student_number = os.path.abspath(__file__).split(os.sep)[-2].upper()
    with open("bots/{0}/{0}.json".format(student_number), "r") as statsfile:
        bot_data = json.load(statsfile)

    print(get_move(layout))

def get_move(layout):
    global bot_data
    fruit = []
    food = []
    walls = []
    ports = []
    bot = (None, None)
    # For the basic move, simply try to go towards the fruit
    for c, col in enumerate(layout):
        for r, item in enumerate(col):
            if item.lower() == bot_data['default_icon']:
                bot = (r, c)

            elif item == ".":
                food.append((r, c))

            elif item == "@":
                fruit.append((r, c))
           
            elif item == "#" or item != " ":
                walls.append((r, c))
            
            elif item in [str(n) for n in range(10)]:
                ports.append((r, c))
    
    # Figure out the closest fruit:
#    closest = get_closest(fruit, bot)
    
    closest = get_closest(ports, bot)

    if closest[0] < bot[0]:
        return "l"
    elif closest[0] > bot[0]:
        return "r"
    elif closest[1] < bot[1]:
        return "u"
    elif closest[1] > bot[1]:
        return "d"
    else:
        return ""

def get_closest(locations, bot_location):
    closest = locations[0]
    closest_dist = abs(bot_location[0] - closest[0]) + abs(bot_location[1] - closest[1])
    for l in locations:
        dist = abs(bot[0] - l[0]) + abs(bot[1] - l[1])
        if dist < closest_dist:
            closest = l
            closest_dist = dist
    return closest


if __name__ == '__main__':
    main()
