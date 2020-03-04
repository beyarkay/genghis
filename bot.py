"""
layout.txt
#           - a wall
.           - food
@           - fruit
abcdefghij  - bots
ABCDEFGHIJ  - bots that have eaten fruit
"""
import json
import os

ENEMIES = list("abcdefghij")

def main():
    global bot_data
    with open("layout.txt", "r") as mapfile:
        layout = mapfile.readlines()
    
    student_number = os.path.abspath(__file__).split(os.sep)[-2].upper()
    with open("{0}/{0}.json".format(student_number), "r") as statsfile:
        bot_data = json.load(statsfile)

    print(get_move(layout))

def get_move(layout):
    global bot_data
    fruit = []
    enemies = []
    food = []
    walls = []
    bot = (None, None)
    # For the basic move, simply try to go towards the fruit
    for c, col in enumerate(layout):
        for r, item in enumerate(col):
            if item.lower() == bot_data['default_icon']:
                bot = (r, c)

            elif item == "#":
                walls.append((r, c))

            elif item == ".":
                food.append((r, c))

            elif item == "@":
                fruit.append((r, c))

            elif item in ENEMIES:
                enemies.append((r, c))  
    # Figure out the closest fruit:
    closest = fruit[0]
    closest_dist = abs(bot[0] - closest[0]) + abs(bot[1] - closest[1])
    for f in fruit:
        dist = abs(bot[0] - f[0]) + abs(bot[1] - f[1])
        if dist < closest_dist:
            closest = f
            closest_dist = dist


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
    


if __name__ == '__main__':
    main()
