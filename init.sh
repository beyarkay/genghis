#!/bin/bash
OLD_WD=`pwd`
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR
chmod 700 init.sh start_battle.py README.md
chmod 744 -fR index.html node
chmod 755 node node/bouncer.py

mkdir -p bots
chmod 755 -R www vars bots
chmod 777 -R logs
chmod 777 vars/gamestate.json
IFS='/' read -r -a array <<< $DIR
pwd=`pwd`
crontab -l | head -n -1 | { cat; echo "50 7-16 * * 1-5 /usr/bin/python3 $pwd/start_battle.py ${array[3]^^}"; } | crontab -
cd $OLD_WD

