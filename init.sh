#!/bin/bash
chmod 700 README.md init.sh judge.py layout.txt layout_template.txt map_template.html reset.py
chmod 711 start_battle.py
chmod 744 bot.py index.html styles.css map.html
mkdir bots
chmod 755 -R bots bouncer.py requests.php 
chmod 777 gamestate.json
pwd=`pwd`
crontab -l | { cat; echo "50 7-16 * * 1-5 /usr/bin/python3 $pwd/start_battle.sh"; } | crontab -
