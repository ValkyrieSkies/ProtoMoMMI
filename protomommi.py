import discord
import json
import wget
import os

from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv('TOKEN')


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

#url for the json file with current round info
statusurl = "https://ss13.moe/serverinfo/serverinfo.json"

dirname = os.path.dirname(__file__)
localstatusfile = os.path.join(dirname, 'localstatus.json')

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    #returns general information on the current round status
    if message.content.startswith('!status'):
        #wget doesn't overwrite existing files, so you have to delete any pre-existing instances first
        try:
            os.remove(localstatusfile)
        except OSError:
            pass
        wget.download(statusurl, 'localstatus.json')
        statusdict = json.load(open('localstatus.json', 'r'))
        outputmsg = '**' + statusdict[0]["players"] + '** players online, Current Map is **' + statusdict[0]["map_name"] + '** on **' + statusdict[0]["mode"] + '**, Station Time: **' + statusdict[0]["station_time"] + '**'
        outputmsg = outputmsg.replace("+", " ")
        outputmsg = outputmsg.replace("%3a", ":")
        await message.channel.send(outputmsg)
        
    #returns a list of the current active players
    elif message.content.startswith('!who'):
        try:
            os.remove(localstatusfile)
        except OSError:
            pass
        wget.download(statusurl, 'localstatus.json')
        statusdict = json.load(open('localstatus.json', 'r'))
        playercount = int(statusdict[0]["players"])
        if playercount > 0:
        
            playerticker = 0
            outputmsg = 'Current active players: ';
            while playerticker < (playercount - 1):
                playerkey = 'player' + str(playerticker)
                outputmsg += statusdict[0][playerkey] + ', '
                playerticker += 1;
            playerkey = 'player' + str(playerticker)
            outputmsg += statusdict[0][playerkey]
            outputmsg = outputmsg.replace("+", " ")
            await message.channel.send(outputmsg)
        else:
            await message.channel.send('No players are currently online.')

#create a file named ".env" in the same folder as this and just add a line that's "TOKEN=yourtokenhere"
client.run(TOKEN)