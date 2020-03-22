#!/usr/bin/python3
import sys
import subprocess
import os
import json
from shlex import split
def main():
    """Start a battle on the nodes belonging to the student numbers given as cmdline arguments

    During testing, copy over the KNXBOY001/public_html/genghis directory to the given nodes to make sure they're up to date

    This script will update the nodes given as cmdline args, reset them with some default parameters and start up their judge systems.
    This is intended to be used for testing only, and mimics what crontab should do on a daily basis
    
    """
    node_str = []
    for sn in sys.argv[1:]:
        print("\nStarting node at {}".format(sn))
        genghis_dir = os.path.join("/home", sn[0].lower(), sn.lower(), "public_html", "genghis")
        node_str.append("https://people.cs.uct.ac.za/~{}/genghis/".format(sn.upper()))

        # If the node isn't KNXBOY001, copy over any updates that may have been made to the judge system and such
        if sn.lower() != "knxboy001":
            cmd = ['rsync', '-r', '--delete', "--exclude", ".git", '/home/k/knxboy001/public_html/genghis/', '{}'.format(genghis_dir)]
            print(" ".join(cmd))
            subprocess.run(cmd)
        
        # Get rid of any old/unrelevant game variables that may be left over
        reset_node(sn)
        
        # Run init.sh to update the permissions required
        cmd = [os.path.join(genghis_dir, "init.sh")]
        print(" ".join(cmd))
        subprocess.run(cmd)
       

        # start up the judge system in the background, writing output to logs/judge.log
        cmd = ["python3", os.path.join(genghis_dir, "node",  "judge.py")] 
        print(" ".join(cmd))
        with open(os.path.join(genghis_dir, "judge.log"), "w+") as judge_log:
            subprocess.Popen(cmd, stdout=judge_log)

    print("\n{} nodes started:\n\t{}".format(len(sys.argv[1:]), "\n\t".join(node_str)))

def reset_node(sn):
    #TODO Update this to write to logs/ instead of the gamestate.json
    """Clear any game variables that weren't left clean, and get the node ready for a new battle

    """
    genghis_dir = os.path.join("/home", sn[0].lower(), sn.lower(), "public_html", "genghis")
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
    
    with open(os.path.join(genghis_dir, "vars", "gamestate.json"), "w+") as gamestate:
        json.dump(data, gamestate, indent=2)

    cmd = ["rm", "-rf", os.path.join(genghis_dir, "bots", "*")]
    print(" ".join(cmd))
    subprocess.run(cmd) 


    cmd = ["python3", os.path.join(genghis_dir, "node", "bouncer.py"), sn]
    print(" ".join(cmd))
    subprocess.run(cmd) 


if __name__ == "__main__":
    main()

