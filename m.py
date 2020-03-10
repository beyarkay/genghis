
import json
data = {
    "bots": [],
    "nodes": [],
    "self": "KNXBOY001",
}

with open("gamestate.json", "w+") as gamestate:
    json.dump(data, gamestate, 2)
