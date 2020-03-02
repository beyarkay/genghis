"""
layout.txt
#           - a wall
.           - food
@           - fruit
abcdefghij  - bots
ABCDEFGHIJ  - bots that have eaten fruit
"""

ENEMIES = list("abcdefghij")

def main():
    with open("layout.txt", "r") as mapfile:
        layout = mapfile.readlines()
    print(get_move(layout))


def get_move(layout):
    fruit = []
    enemies = []
    food = []
    walls = []
    bot = (None, None)
    # For the basic move, simply try to go towards the fruit
    for c, col in enumerate(layout):
        for r, item in enumerate(col):
            #print(item, end=" ")
            if item == "a":
                bot = (r, c)

            elif item == "#":
                walls.append((r, c))

            elif item == ".":
                food.append((r, c))

            elif item == "@":
                fruit.append((r, c))

            elif item in ENEMIES:
                enemies.append((r, c))  
     
    if fruit[0][0] < bot[0]:
        return "l"
    elif fruit[0][0] > bot[0]:
        return "r"
    elif fruit[0][1] < bot[1]:
        return "u"
    elif fruit[0][1] > bot[1]:
        return "d"
    else:
        return ""
    


if __name__ == '__main__':
    main()
