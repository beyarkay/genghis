#!/bin/bash
OLD_WD=`pwd`
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR
if [ $# -eq 0 ]
  then
    echo "Error: Missing Argument: Student number of the port you're connecting to"
    exit 1
fi
echo "$1" > node/ports.txt
chmod 700 init.sh start_battle.py README.md node/ports.txt
chmod 744 -fR index.html node
chmod 755 .. node node/bouncer.py

mkdir -p bots
chmod 755 -R www vars bots
chmod 777 -R logs
IFS='/' read -r -a array <<< $DIR
pwd=`pwd`
crontab -l | head -n -1 | { cat; echo "50 7-16 * * 1-5 /usr/bin/python3 $pwd/start_battle.py ${array[3]^^}"; } | crontab -
cd $OLD_WD

