#!/usr/bin/python3
import re
import glob
import shutil
import time
import sys
import subprocess
import os
import json
from shlex import split


global genghis_dir
TESTING = False
DEBUG = False
def main():
    """Start a battle on the nodes belonging to the student numbers given as cmdline arguments

    During testing, copy over the KNXBOY001/public_html/genghis directory to the given nodes to make sure they're up to date

    This script will update the nodes given as cmdline args, reset them with some default parameters and start up their judge systems.
    This is intended to be used for testing only, and mimics what crontab should do on a daily basis
    
    """
    global TESTING
    global DEBUG
    node_str = []
    stop = len(sys.argv)

    TESTING = "t" in sys.argv[-1]
    DEBUG = "d" in sys.argv[-1]

    if sys.argv[-1].islower():
        stop -= 1

    for index, sn in enumerate(sys.argv[1:stop]):
        RE_SN = re.compile(r"([BCDFGHJKLMNPQRSTVWXYZ]{3}\w{3}\d{3})")
        if not re.match(RE_SN, sn):
            if TESTING:
                raise Exception("{} Doesn't match student number regex".format(sn))
            else:
                print("{} Doesn't match student number regex".format(sn))
                continue
        
        global genghis_dir
        genghis_dir = os.path.join("/home", sn[0].lower(), sn.lower(), "public_html", "genghis")
        node_str.append("https://people.cs.uct.ac.za/~{}/genghis/".format(sn.upper()))
        print("\nStarting battle on {}...".format(node_str[-1]))

        # If the node isn't KNXBOY001, copy over any updates that may have been made to the judge system and such
        if sn.lower() != "knxboy001" and DEBUG:
            cmd = ['rsync', '-r', '--delete', 
                    "--exclude", "bots/", 
                    "--exclude", "logs/", 
                    "--exclude", "node/ports.txt", 
                    "--exclude", "vars/", 
                    "--exclude", ".git", 
                    '/home/k/knxboy001/public_html/genghis/', '{}'.format(genghis_dir)]
            print(" ".join(cmd))
            subprocess.run(cmd).returncode
        
        # Get rid of any old/unrelevant game variables that may be left over
        reset_node(sn)
        
       # if TESTING:
       #     with open(os.path.join(genghis_dir, "node", "ports.txt") "w") as portsfile:
       #         
       #     # Run init.sh to update the permissions required
       #     node_index = (index + 1) % (len(sys.argv[1:stop]))
       #     node_for_ports = sys.argv[1:stop][node_index]
       #     cmd = [os.path.join(genghis_dir, "init.sh"), node_for_ports]
       #     print(" ".join(cmd))
       #     subprocess.run(cmd).returncode
      

        # start up the judge system in the background, writing output to logs/judge.log
        cmd = ["python3", os.path.join(genghis_dir, "node",  "judge.py")] 
        if TESTING:
            cmd.append("t")
        print(" ".join(cmd))
        with open(os.path.join(genghis_dir, "logs", "judge.log"), "w+") as judge_log:
            subprocess.Popen(cmd, stdout=judge_log)

    print("\n{} nodes started:\n\t{}".format(len(sys.argv[1:stop]), "\n\t".join(node_str)))

def reset_node(sn):
    """Clear any game variables that weren't left clean, and get the node ready for a new battle

    """
    global TESTING
    global genghis_dir
    #genghis_dir = os.path.join("/home", sn[0].lower(), sn.lower(), "public_html", "genghis")
    print("Resetting node...")
    # Check the registered edges, and add them as portals to the gamestate
    with open(os.path.join(genghis_dir, "node", "ports.txt"), "r") as ports_file:
        ports = ports_file.readlines()
    ports_dir = {str(k): v for k, v in zip(list(range(1, len(ports) + 1)), ports)}
    gamestate = {
        "bots": {},
        "ports": ports_dir,
        "self": sn,
        "coins": {
            sn.lower(): sn[0].lower()
        },
    }


    # First clear the gamestate file
    with open(os.path.join(genghis_dir, "vars", "gamestate.json"), "w+") as gamestate_file:
        json.dump(gamestate, gamestate_file, indent=2)
    
    # Clear any old bot data files
    to_delete = glob.glob(os.path.join(genghis_dir, "logs", "*"))
    print("\tDeleting: {}".format(str(to_delete)))
    for f in to_delete:
        try:
            os.remove(f)
        except:
            print("Error removing file: {}".format(f))
    # Now add the current bot to the logs/ directory
    millis = str(int(round(time.time())))
    bot_data = {
        "student_number": sn.upper(),
        "default_icon": "",
        "coins": {}
    }
    with open(os.path.join(genghis_dir, "logs", millis + ".json"), "w+") as bot_file:
        json.dump(bot_data, bot_file, indent=2)

    # Clear out the old bot data directories
    to_delete = glob.glob(os.path.join(genghis_dir, "bots", "*"))
    print("\tDeleting: {}".format(str(to_delete)))
    for f in to_delete:
        try:
            shutil.rmtree(f)
        except:
            print("Error removing directory: {}".format(f))

def log(string, g_dir=None):
    global genghis_dir
    if g_dir is None:
        g_dir = genghis_dir
    with open(os.path.join(g_dir, "logs", "judge.log"), "a") as logfile:
        logfile.write(string)

if __name__ == "__main__":
    main()

