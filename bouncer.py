import requests 
import sys
import re
import os
import json
from shutil import copy
def main():
    RE_SN = re.compile(r"([bcdfghjklmnpqrstvwxyz]{3}\w{3}\d{3})")
    if re.match(r"^[bcdfghjklmnpqrstvwxyz]{3}\w{3}\d{3}$", sys.argv[1].replace("'","").lower()):
        directory = "/" + os.path.join(*os.path.abspath(__file__).split(os.sep)[:-1])
        host = re.search(RE_SN, os.path.abspath(__file__)).group(0).upper()
        sn = sys.argv[1].upper()

        with open(os.path.join(directory, "gamestate.json"), "r+") as state_file:
            gamestate = json.load(state_file)
        if sn not in gamestate['bots'].keys():
            gamestate['bots'][sn] = {
                "default_icon": "",
                "student_number": sn
            }
            print("Added bot {} to {}/gamestate.json".format(sn, directory))
            with open(os.path.join(directory, "gamestate.json"), "w") as state_file:
                json.dump(gamestate, state_file, indent=2)
        else:
            print("Bot {} already in {}/gamestate.json".format(sn, directory))

        print(gamestate)
    else:
        raise Exception("Error, '" +sys.argv[1]+ "' doesn't match regex")
        return

if __name__ == "__main__":
    main()
