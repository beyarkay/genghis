import os
import json
sn = os.path.abspath('../..').split(os.sep)[-1].upper() 
data = {
    "bots": {},
    "ports": {
        "1":"KNXBOY001",
        "2":"MSHSTU001",
    },
    "self": sn,
    "coins": {
        sn: sn[3].lower()
    },
}


with open("gamestate.json", "w+") as gamestate:
    json.dump(data, gamestate, 2)

os.system("rm -rf bots/*")
os.system("python3 bouncer.py {}".format(sn))

