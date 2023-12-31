###### **This branch is specifically for /vg/station13's server**. If you want to run this bot for your own fork, there will be a specific branch for that *soon*.

# ![protomommi image](https://github.com/ValkyrieSkies/vg-protomommi/blob/vg-hardcoded/avatar.png?raw=true) vg-protomommi
A discord bot for the /vg/station13 Discord Server. Provides functions such as fetching the current server info, fetching the list of players online, listening for status updates from the game server and posting them to set discord channels, generating infoboxes for requested PRs/Issues on the /vg/station13 github, and a few other bonus fun features such as dice rolling and a programmable persistent response dictionary.

# Required Python packages
This bot requires Python 3.10 to run.

The following packages are also required, and can be installed via "pip install packagename" (on Windows via CMD at least, if you're on Linux you probably know how to do it anyway)

- discord.py
- requests
- python-dotenv
- py-cord
- quart
- wget

# Setup for /vg/station13

1) Download the "vg-hardcoded" branch (default)
2) Open the .env file in your text editor of choice
3) Set TOKEN to your Discord bot session token, LISTENPORT to the port you want it to listen for, DISCPASS to the value of DISCORD_PASSWORD as declared in the codebase's config.txt, and DISCKILLPASS to a password you want to share with anyone you entrust with the rights to terminate the bot
4) Run the bot via "py -3 protomommi.py" (Again, this is the Windows CMD command, might be different on Linux)
5) And there you go, everything should be running smoothly!
