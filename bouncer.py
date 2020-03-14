import requests 
import sys
import re
import os
import json
from shutil import copy
# TODO add checks to see if the bot alread exists in the gamestate.json
def main():
    if re.match(r"^[bcdfghjklmnpqrstvwxyz]{3}\w{3}\d{3}$", sys.argv[1].replace("'","").lower()):
        sn = sys.argv[1].upper()
        node_path = os.path.join("/home", sn[0].lower(), sn.lower(), "public_html/genghis/")
        print("node_path = " + node_path)
        with open(os.path.join(node_path, "gamestate.json"), "r+") as gamestate:
            state = json.load(gamestate)
        state['bots'][sn] = {
            "default_icon": "",
            "student_number": sn
        }
        print("Added bot {} to {}/gamestate.json".format(sn, node_path))
        with open(os.path.join(node_path, "gamestate.json"), "w") as gamestate:
            json.dump(state, gamestate, indent=2)
    else:
        raise Exception("Error, '" +sys.argv[1]+ "' doesn't match regex")
        return

if __name__ == "__main__":
    main()
