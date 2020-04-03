# Genghis Competitive Bot System
[Example of the battle system](https://people.cs.uct.ac.za/~KNXBOY001/genghis/)

Genghis is a collection of scripts that setup, run and coordinate a multi-bot battle system.

![](battle.png)

To start, a new user clones this repo into their public directory, edits the default bot as 
they like, and then can send that bot out into the network to find other bots to fight against.

## Quick Setup

0. Don't abuse the system, or you'll find your way onto a blacklist.

1. Log into nightmare, and create a `public_html` directory
```
ssh <YOUR STUDENT NUMBER>@nightmare.cs.uct.ac.za
<ENTER YOUR PASSWORD>
mkdir ~/public_html
chmod 755 ~/public_html 
```
2. Clone this repo into `public_html/`
```
cd ~/public_html
git clone https://github.com/beyarkay/genghis.git
```

3. In order to get started, you need a `bot.py` script thats stored in the `node/` directory. For now copy the default bot:
```
cd genghis
cp node/basic_bot.py node/bot.py
```

4. Run `init.sh` to setup your node, and connect it to the network through the node 'KNXBOY001'
```
./init.sh KNXBOY001
```

`init.sh` will give the files in `genghis/` the correct permissions, and add a job to your crontab. You need to pass in a the student number of another node, in order to connect yourself to the network. 

5. And then start the battle in t[esting] mode

```
./start_battle.py <YOUR STUDENT NUMBER> t
```

6. You're done! go to `https://people.cs.uct.ac.za/~<STUDENT NUMBER>/genghis/` in a web browser to see your bot moving around.
* Battleground Legend:
    * Capital letters: Bots, moving about the network
    * lowercase letters: coins, one type of coin for each bot. You need coins in order to fight other bots
    * `#`: Walls, you can't pass through these
    * Numbers (1-9): These are ports, that can send your bot to other nodes. Click on the number in a web browser to view that node.
    
## Trouble Shooting

* This is a work in progress, and bugs are to be expected
* One of the most common errors is that the permissions aren't correct try running `./init.sh KNXBOY001` again.

## Some notes:

* Once you've run `init.sh`, your bot will automatically start up in between lectures (ie Monday to Friday, at 07h50, 08h50, 09h50, ..., 15h50, 16h50) for five minutes, along with every other node in the network. This is when the battle actually happens.


## Building your Bot
* DO NOT commit your bot to the git repo. All changes are reset back to origin/master before each battle, and you will lose your bot file if you commit it to the repo.
* To build your bot, you need to change the `node/bot.py` script.
* If you want to test your changes, you can run `./start_battle <YOUR STUDENT NUMBER> t` in order to start a test battle on your node
* In order to test your bot against someone elses, you'll need to wait for the daily battles

### Bot Basics
* When a bot is run on a node, the judge system creates a little environment for it in the form of `bots/<STUDENT NUMBER>/`
* The judge system will copy the up-to-date `layout.txt` and `data.json` file into this directory, which is how your bot knows where everything is, by reading these two files.
* Your bot script should read in these two files, decide on what it wants to do and then write its decision to `bots/<STUDENT NUMBER>/move.json` as a json string
* You should use the json library to convert a python dict into a json formatted file.
* Example `move.json`

```
{
    "action": "walk", 
    "direction": "u",
    "weapon": ""
}
```
* `move.json`:
    * "action" is either "walk" or "attack"
    * "direction" is one of "l", "r", "u", "d"
    * "weapon" is a lower-case student number representing one of the coins that the bot currently has
    * "weapon" is ignored unless "action" is "attack"

* Once the `bots/<STUDENT NUMBER>/bot.py` file has finished running, the judge system will try to read the contents of `bots/<STUDENT NUMBER>/move.json`, and if valid will execute the move.
* You pick up a coin by "walk"ing into it
* You travel through a port by "walk"ing into it
* You can see where everything is by analysing `bots/<STUDENT_NUMBER>/layout.txt`
* You can see meta-details about your bot and the battleground by analysing `bots/<STUDENT_NUMBER>/gamestate.json`

# Resources for if you've got no clue how to get started:
(Work in Progress...)



# Example File Structure and Permissions
Last updated 2020 April 01

```
knxboy001@nightmare:genghis$ ll *
drwxr-xr-x 8 knxboy001 knxboy001 4.0K Apr  1 19:02 .
drwxr-xr-x 3 knxboy001 knxboy001 4.0K Mar 31 23:10 ..
-rwx------ 1 knxboy001 knxboy001 4.4K Mar 31 18:48 README.md
-rw------- 1 knxboy001 knxboy001 491K Mar 31 18:46 battle.png
-rwxr--r-- 1 knxboy001 knxboy001 7.4K Mar 31 00:54 index.html
-rwx------ 1 knxboy001 knxboy001  947 Apr  1 19:00 init.sh
-rwx------ 1 knxboy001 knxboy001 5.1K Mar 31 16:35 start_battle.py

bots:
total 20K
drwxr-xr-x 4 knxboy001 knxboy001 4.0K Apr  1 16:55 .
drwxr-xr-x 8 knxboy001 knxboy001 4.0K Apr  1 19:00 ..
-rwxr-xr-x 1 knxboy001 knxboy001   71 Mar 31 14:27 .gitignore
drwx------ 2 knxboy001 knxboy001 4.0K Apr  1 16:54 KNXBOY001
drwx------ 2 knxboy001 knxboy001 4.0K Apr  1 16:54 MSHSTU001

logs:
total 300K
drwxrwxrwx 2 knxboy001 knxboy001 4.0K Apr  1 16:55 .
drwxr-xr-x 8 knxboy001 knxboy001 4.0K Apr  1 19:00 ..
-rwxrwxrwx 1 knxboy001 knxboy001   71 Mar 31 14:27 .gitignore
-rwxrwxrwx 1 www-data  www-data   328 Apr  1 16:55 2020-04-01T17:09:03+02:00.json
-rw------- 1 knxboy001 knxboy001 270K Apr  1 16:55 judge.log
-rw-r--r-- 1 www-data  www-data  4.1K Apr  1 16:55 requests.log

node:
total 60K
drwxr-xr-x 2 knxboy001 knxboy001 4.0K Apr  1 15:46 .
drwxr-xr-x 8 knxboy001 knxboy001 4.0K Apr  1 19:00 ..
-rwxr--r-- 1 knxboy001 knxboy001 4.7K Mar 31 17:09 basic_bot.py
-rwxr--r-- 1 knxboy001 knxboy001 5.3K Mar 31 13:02 bot.py
-rwxr-xr-x 1 knxboy001 knxboy001 1.5K Mar 22 12:24 bouncer.py
-rwxr--r-- 1 knxboy001 knxboy001  20K Mar 31 23:39 judge.py
-rwxr--r-- 1 knxboy001 knxboy001  506 Mar 23 22:53 layout_template.txt
-rwxr--r-- 1 knxboy001 knxboy001   10 Apr  1 15:50 ports.txt
-rwxr--r-- 1 knxboy001 knxboy001  870 Mar 23 16:39 requests.php

vars:
total 20K
drwxr-xr-x 2 knxboy001 knxboy001 4.0K Mar 31 14:27 .
drwxr-xr-x 8 knxboy001 knxboy001 4.0K Apr  1 19:00 ..
-rwxr-xr-x 1 knxboy001 knxboy001   71 Mar 31 14:27 .gitignore
-rwxr-xr-x 1 knxboy001 knxboy001 2.5K Apr  1 16:55 gamestate.json
-rwxr-xr-x 1 knxboy001 knxboy001  506 Apr  1 16:55 layout.txt

www:
total 40K
drwxr-xr-x 2 knxboy001 knxboy001 4.0K Apr  1 00:38 .
drwxr-xr-x 8 knxboy001 knxboy001 4.0K Apr  1 19:00 ..
-rwxr-xr-x 1 knxboy001 knxboy001  10K Mar 31 13:12 coin_generic.gif
-rwxr-xr-x 1 knxboy001 knxboy001 2.1K Mar 30 02:09 grid.css
-rwxr-xr-x 1 knxboy001 knxboy001 9.9K Apr  1 00:38 script.js
-rwxr-xr-x 1 knxboy001 knxboy001  928 Apr  1 00:38 styles.css

```

## TODO
* Add proper communication protocol between nodes:
    * A proper, bidirectional port system, that doesn't need to be setup by the user
    * A way to discover the entire graph network
    * A way to draw the entire graph network
* Add in a 'commentary' card on the webpage, to explain what's going on
* Colour each of the bots/ports/coins so they're more distinguishable
* Get the webpage to update the cards more often
* Add in a handshake to happen before porting, to ensure that the foreign node is actually responsive
* Add in a difference checking between the bots
* Add an easy-setup system
* Add a walkthrough for how everything connects and making your first bot
