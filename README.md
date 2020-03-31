# Genghis Competitive Bot System
[Example of the battle system](https://people.cs.uct.ac.za/~KNXBOY001/genghis/)

Genghis is a collection of scripts that setup, run and coordinate a multi-bot battle system.

To start, a new user clones this repo into their public directory, edits the default bot as 
they like, and then can send that bot out into the network to find other bots to fight against.

As of 12 March 2020, Genghis can run stand-alone fights between bots, but many features are still
in development before a full release, including:

* Proper documentation to help new users to join the network
* An initiation script to take care of file permissions and setup
* A scheduling system, to only permit activity between 08h00 and 15h00 every weekday, for five minutes
from HH:50 to HH:55 every hour.

## Overview 

* Users build bots and host a judge system on their node. 
* The user then initialises the bot on their node. From the user's node, the bot can then travel to
each adjoining node
* At each new node, the bot can collect resources or fight other bots, in order to win the node an steal
their resources
* A leaderboard (not yet implemented) keeps track of which bot has won which node, and provides bragging rights

## Terminology

* A user is the person who has both a bot and a node
* A bot is simply the script that is run to determine the move of that bot each turn
* A node is everything else in the repository
* A network is a collection of nodes that are connected together, although not every node is connected
to every other node.
* Bots can travel between nodes.
* Each user's node is in charge of coordinating multiple bots to fight on that node
* The bot script is _not_ run on that bot's node. Rather it is copied into a subdirectory
of the node where it is currently fighting


## Quick Setup

1. Log into nightmare, and create a `public_html` directory
```
ssh <Student number>@nightmare.cs.uct.ac.za
<Enter your password>
mkdir ~/public_html
chmod 755 ~/public_html 
```
2. Clone this repo into `public_html/`
```
cd ~/public_html
git clone https://github.com/beyarkay/genghis.git
```

3. `init.sh` will give the files in `genghis/` the correct permissions, and add a job to your crontab. You need to pass in a the student number of another node, in order to connect yourself to the network. In this case use KNXBOY001:
```
cd genghis
./init.sh KNXBOY001
```
4. Now, you need to get someone else who's already setup to add you to their `node/ports.txt`. Have them run this command:
```
cd ~/public_html/genghis && echo "<YOUR STUDENT NUMBER HERE>" >> node/ports.txt
```
5. In order to get started, you need a `bot.py` script thats stored in the `node/` directory. For now copy the default bot:
```
cp node/basic_bot.py node/bot.py
```

And then start the battle in debug mode:

```
./start_battle.py <YOUR STUDENT NUMBER> t
```

## A more in depth setup
(work in progress)


## Customising your bot
(work in progress)


## TODO
* Add in a difference checking between the bots
* Add an easy-setup system
* Add a walkthrough for how everything connects and making your first bot
