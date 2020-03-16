#!/bin/bash
chmod 700 README.md gamestate.json init.sh judge.py layout.txt layout_template.txt map_template.html reset.py
chmod 710 start_battle.sh
chmod 744 bot.py index.html styles.css map.html
mkdir bots
chmod 755 -R bots bouncer.py requests.php 
pwd=`pwd`
crontab -l | { cat; echo "50 7-16 * * 1-5 $pwd/start_battle.sh"; } | crontab -
