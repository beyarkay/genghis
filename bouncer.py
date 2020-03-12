import requests 
import sys
import re
import os
import json
from shutil import copy

def main():
    if re.match(r"^[bcdfghjklmnpqrstvwxyz]{3}\w{3}\d{3}$", sys.argv[1].replace("'","").lower()):
        sn = sys.argv[1].upper()
        with open("gamestate.json", "r+") as gamestate:
            state = json.load(gamestate)
        state['bots'][sn] = {
            "default_icon": "",
            "student_number": sn
        }
        print(state)
        with open("gamestate.json", "w") as gamestate:
            json.dump(state, gamestate)
    else:
        print("Error, '" +sys.argv[1]+ "' doesn't match regex")
        return

if __name__ == "__main__":
    main()
