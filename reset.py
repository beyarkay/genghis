import subprocess
import os
import json
sn = os.path.abspath(__file__).split(os.sep)[-4].upper() 
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

directory ="/" + os.path.join(*os.path.abspath(__file__).split(os.sep)[:-1]) 

cmd = ["rm", "-rf", os.path.join(directory, "bots/*")]
print(" ".join(cmd))
subprocess.run(cmd) 

cmd = ["python3", os.path.join(directory, "bouncer.py"), sn]
print(" ".join(cmd))
subprocess.run(cmd) 

