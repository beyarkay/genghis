import os
import json
data = {
    "bots": {},
    "ports": {
        "1":"KNXBOY001",
        "2":"MSHSTU001",
    },
    "self": "KNXBOY001",
}


with open("gamestate.json", "w+") as gamestate:
    json.dump(data, gamestate, 2)

os.system("rm -rf bots/*")
os.system("python3 bouncer.py KNXBOY001")
#os.system("python3 bouncer.py MSHSTU001")

