import requests 
import sys
import re
import os
import json
from shutil import copy

def main():
    if re.match(r"^[bcdfghjklmnpqrstvwxyz]{3}\w{3}\d{3}$", sys.argv[1].replace("'","").lower()):
        arg = sys.argv[1]
    else:
        print("Error, '" +sys.argv[1]+ "' doesn't match regex")
        return
    print("Creating ./bots/{}/".format(arg))
    if not os.path.exists("bots/" + arg):
        os.mkdir("bots/"+arg)
    r = requests.get("https://people.cs.uct.ac.za/~{}/genghis/bot.py".format(arg)) 
    print(r)
    if r.ok:
        bot = r.text
    else:
        bot = requests.get("https://people.cs.uct.ac.za/~{}/ghengis/bot.py".format(arg)).text


    # Write all the required files to the bot's directory
    with open("bots/{}/bot.py".format(arg), "w+") as botfile:
        botfile.write(bot)
    copy("layout_template.txt", "bots/{}/layout.txt".format(arg))
    
    bot_data = {
        "default_icon": "",
        "state": 0,
        "score":0,
        "student_number": arg
    }
    with open("bots/{0}/{0}.json".format(arg), "w+") as statsfile:

if __name__ == "__main__":
    main()
