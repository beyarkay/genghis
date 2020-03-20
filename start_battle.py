#!/usr/bin/python3
import sys
import subprocess
import os

def main():
    node_str = []
    for sn in sys.argv[1:]:
        print("\nStarting node at {}".format(sn))
        node_dir = os.path.join("/home", sn[0].lower(), sn.lower(), "public_html", "genghis")
        node_str.append("https://people.cs.uct.ac.za/~{}/genghis/".format(sn.upper()))
        if sn.lower() != "knxboy001":
            cmd = ['rsync', '-r', '--delete', "--exclude", ".git", '/home/k/knxboy001/public_html/genghis/', '{}'.format(node_dir)]
            print(" ".join(cmd))
            subprocess.run(cmd)
            cmd = ['python3', os.path.join(node_dir, "init.py")]
            print(" ".join(cmd))
            subprocess.run(cmd)
        cmd = ["python3", os.path.join(node_dir, "reset.py")]
        print(" ".join(cmd))
        subprocess.run(cmd) 
        cmd = ["python3", os.path.join(node_dir, "judge.py")] 
        print(" ".join(cmd))
        with open(os.path.join(node_dir, "judge.log"), "w+") as judge_log:
            subprocess.Popen(cmd, stdout=judge_log)

    print("\n{} nodes started:\n\t{}".format(len(sys.argv[1:]), "\n\t".join(node_str)))


if __name__ == "__main__":
    main()












