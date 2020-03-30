import requests 
import sys
import re
import os
import json
from shutil import copy
def main():
    """Given a student number as input, check if it's a valid student number.
    If it is valid, add that student number to the gamestate.json file such that the judge will add the
    bot to the battle

    """
    RE_SN = re.compile(r"([bcdfghjklmnpqrstvwxyz]{3}\w{3}\d{3})")
    if re.match(r"^[bcdfghjklmnpqrstvwxyz]{3}\w{3}\d{3}$", sys.argv[1].replace("'","").lower()):
        directory = "/" + os.path.join(*os.path.abspath(__file__).split(os.sep)[:-2])
        curr_node = re.search(RE_SN, os.path.abspath(__file__)).group(0).upper()
        sn = sys.argv[1].upper()
        gamestate_path = os.path.join(directory, "vars", "gamestate.json")

        with open(gamestate_path, "r+") as state_file:
            gamestate = json.load(state_file)
        if sn not in gamestate['bots'].keys():
            gamestate['bots'][sn] = {
                "default_icon": "",
                "student_number": sn
            }
            print("Added bot {} to {}".format(sn, gamestate_path))
            with open(gamestate_path, "w") as state_file:
                json.dump(gamestate, state_file, indent=2)
        else:
            print("Bot {} already in {}".format(sn, gamestate_path))

        print(gamestate)
    else:
        raise Exception("Error, '" +sys.argv[1]+ "' doesn't match regex")
        return

if __name__ == "__main__":
    main()
