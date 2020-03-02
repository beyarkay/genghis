"""
1. Collect two robot scripts
2. paste the scripts into two separate directories
3. Run the scripts one after the other



"""
import os
import subprocess
import random
import requests
import sys
from shutil import copy

bot_paths = ["{}/bot.py".format(arg) for arg in sys.argv[1:]]
layout = []
count = 0

def main():
    global layout
    with open("layout.txt", "r") as mapfile:
        layout = [line.strip() for line in mapfile.readlines()]
    layout = [list(i) for i in zip(*layout)]
    for arg in sys.argv[1:]:
        print("Creating ./{}/".format(arg))
        if not os.path.exists(arg):
            os.mkdir(arg)
#        try:
        r = requests.get("https://people.cs.uct.ac.za/~{}/genghis/bot.py".format(arg)) 
        print(r)
        if r.ok:
            bot = r.text
        else:
            bot = requests.get("https://people.cs.uct.ac.za/~{}/ghengis/bot.py".format(arg)).text
 #       except Exception as e:
  #          print(e.args)
        with open("{}/bot.py".format(arg), "w+") as botfile:
            botfile.write(bot)
        copy("layout.txt", "{}/layout.txt".format(arg))
    run()


def run():
    global count
    is_over = False
    while not is_over:
        print("\n===============Round {}===============".format(count))
        for bot_path in bot_paths:
            copy("layout.txt", "{}/layout.txt".format(bot_path.split('/')[0]))
            print("\n".join(["".join(list(i)) for i in zip(*layout)]))
            step(bot_path)
            is_over = check_is_over()
            
            with open("layout.txt", "w+") as mapfile:
                mapfile.writelines(["".join(list(i)) + "\n" for i in zip(*layout)] )

def step(bot_path):
    result = subprocess.run(["python3", bot_path], stdout=subprocess.PIPE)
    cmd = str(result.stdout, encoding='utf8').strip()
    execute_cmd(bot_path, cmd)

def execute_cmd(bot_path, cmd):
    global layout
    print("{} is performing '{}'".format(bot_path, cmd))
    bot = (None, None)
    for x, col in enumerate(layout):
        for y, item in enumerate(col):
            if item == "a":
                bot = (x, y)
                break
        if bot[0] and bot[1]:
            break

    if (cmd == "l" and bot[0] - 1 >= 0) or \
        (cmd == "r" and bot[0] + 1 < len(layout)) or \
        (cmd == "u" and bot[1] - 1 >= 0) or \
        (cmd == "d" and bot[1] + 1 < len(layout[0])):
        if get_cell(layout, bot, cmd) == " ":
            move_bot(layout, bot, cmd)
        elif get_cell(layout, bot, cmd) == "@":
            move_bot(layout, bot, cmd)
            add_food(layout)

#    if cmd == "l" and bot[0] - 1 >= 0 and layout[bot[0] - 1][bot[1]] == " ":
#        layout[bot[0]][bot[1]] = " "
#        layout[bot[0] - 1][bot[1]] = "a"
#        
#    if cmd == "r" and bot[0] + 1 < len(layout) and layout[bot[0] + 1][bot[1]] == " ":
#        layout[bot[0]][bot[1]] = " "
#        layout[bot[0] + 1][bot[1]] = "a"
#
#    if cmd == "u" and bot[1] - 1 >= 0 and layout[bot[0]][bot[1] - 1] == " ":
#        layout[bot[0]][bot[1]] = " "
#        layout[bot[0]][bot[1] + 1] = "a"
#
#    if cmd == "d" and bot[1] + 1 < len(layout[0]) and layout[bot[0]][bot[1] + 1] == " ":
#        layout[bot[0]][bot[1]] = " "
#        layout[bot[0]][bot[1] + 1] = "a"

def get_cell(layout, bot, cmd):
    cmd_dict = {
        "l": (-1,  0),
        "r": ( 1,  0),
        "u": ( 0, -1),
        "d": ( 0,  1),
        "":  ( 0,  0)
    }
    return layout[bot[0] + cmd_dict[cmd][0]][bot[1] + cmd_dict[cmd][1]]

def add_food(layout):
    while True:
        location = (random.randint(0, len(layout) - 1), random.randint(0, len(layout[0]) - 1))
        if get_cell(layout, location, "") == " ":
            layout[location[0]][location[1]] = "@"
            break

def move_bot(layout, bot, cmd):
    cmd_dict = {
        "l": (-1,  0),
        "r": ( 1,  0),
        "u": ( 0, -1),
        "d": ( 0,  1),
        "":  ( 0,  0)
    }

    layout[bot[0]][bot[1]] = " "
    layout[bot[0] + cmd_dict[cmd][0]][bot[1] + cmd_dict[cmd][1]] = "a"


def check_is_over():
    global count
    count += 1
    return count > 20
    

if __name__ == '__main__':
    main()
