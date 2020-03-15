import requests 
import sys
import re
import os
import json
from shutil import copy
# TODO add checks to see if the bot alread exists in the gamestate.json
def main():
    RE_SN = re.compile(r"([bcdfghjklmnpqrstvwxyz]{3}\w{3}\d{3})")
    if re.match(r"^[bcdfghjklmnpqrstvwxyz]{3}\w{3}\d{3}$", sys.argv[1].replace("'","").lower()):
        host = re.search(RE_SN, os.path.abspath('.')).group(0).upper()
        sn = sys.argv[1].upper()
        print("path = " + os.path.abspath('.'))
        with open(os.path.join(os.path.abspath('.'), "gamestate.json"), "r+") as gamestate:
            state = json.load(gamestate)
        state['bots'][sn] = {
            "default_icon": "",
            "student_number": sn
        }
        print("Added bot {} to {}/gamestate.json".format(sn, os.path.abspath('.')))
        with open(os.path.join(os.path.abspath('.'), "gamestate.json"), "w") as gamestate:
            json.dump(state, gamestate, indent=2)
    else:
        raise Exception("Error, '" +sys.argv[1]+ "' doesn't match regex")
        return

if __name__ == "__main__":
    main()
