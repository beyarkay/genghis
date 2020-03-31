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
cp node/basic_bot.py node/bot.py
```

4. Run `init.sh`:
```
cd genghis
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



## TODO
* Add in a 'commentary' card on the webpage, to explain what's going on
* Colour each of the bots/ports/coins so they're more distinguishable
* Get the webpage to update the cards more often
* Add in a handshake to happen before porting, to ensure that the foreign node is actually responsive
* Add in a difference checking between the bots
* Add an easy-setup system
* Add a walkthrough for how everything connects and making your first bot
