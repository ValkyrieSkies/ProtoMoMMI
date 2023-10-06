import discord
import json
import wget
import os
import random
import re

from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv('TOKEN')

bot = discord.Bot(command_prefix="!",intents=discord.Intents.all())

statusurl = "https://ss13.moe/serverinfo/serverinfo.json"
giturl = "https://github.com/vgstation-coders/vgstation13/"
gitissuesurl = "https://api.github.com/repos/vgstation-coders/vgstation13/issues"
gitprurl = "https://api.github.com/repos/vgstation-coders/vgstation13/pulls"

dirname = os.path.dirname(__file__)
localstatusfile = os.path.join(dirname, 'localstatus.json')
localissuesfile = os.path.join(dirname, 'localissues.json')
localprfile = os.path.join(dirname, 'localpr.json')
respfile = os.path.join(dirname, 'resp.json')

respdict = {}

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    try:
        respdict = json.load(open('resp.json', 'r'))
        print(f'Loaded response file to dictionary successfully.')
    except:
        respdict = {}
        print(f'Failed to load response file to dictionary, starting with blank resp dictionary.')
    
@bot.command(name="status",description="Retrieves the status of the game server.")
async def slash_command(interaction:discord.Interaction):
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
    await interaction.response.send_message(outputmsg)
    
@bot.command(name="teststatus",description="Retrieves the status of the test server.")
async def slash_command(interaction:discord.Interaction):
    try:
        os.remove(localstatusfile)
    except OSError:
        pass
    wget.download(statusurl, 'localstatus.json')
    statusdict = json.load(open('localstatus.json', 'r'))
    outputmsg = '[Test Server] **' + statusdict[1]["players"] + '** players online, Current Map is **' + statusdict[1]["map_name"] + '** on **' + statusdict[1]["mode"] + '**, Station Time: **' + statusdict[1]["station_time"] + '**'
    outputmsg = outputmsg.replace("+", " ")
    outputmsg = outputmsg.replace("%3a", ":")
    await interaction.response.send_message(outputmsg)

@bot.command(name="who",description="Retrieves the list of active players from the game server.")
async def slash_command(interaction:discord.Interaction):
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
        await interaction.response.send_message(outputmsg)
    else:
        await interaction.response.send_message('No players are currently online.')
        
@bot.command(name="testwho",description="Retrieves the list of active players from the test server.")
async def slash_command(interaction:discord.Interaction):
    try:
        os.remove(localstatusfile)
    except OSError:
        pass
    wget.download(statusurl, 'localstatus.json')
    statusdict = json.load(open('localstatus.json', 'r'))
    playercount = int(statusdict[1]["players"])
    if playercount > 0:    
        playerticker = 0
        outputmsg = '[Test Server] Current active players: ';
        while playerticker < (playercount - 1):
            playerkey = 'player' + str(playerticker)
            outputmsg += statusdict[1][playerkey] + ', '
            playerticker += 1;
        playerkey = 'player' + str(playerticker)
        outputmsg += statusdict[1][playerkey]
        outputmsg = outputmsg.replace("+", " ")
        await interaction.response.send_message(outputmsg)
    else:
        await interaction.response.send_message('[Test Server] No players are currently online.')

@bot.command(name="coinflip",description="Flips a coin.")
async def slash_command(interaction:discord.Interaction):
    if(random.randint(1, 2) == 1):
        outputmsg = 'Heads'
    else:
        outputmsg = 'Tails'
    await interaction.response.send_message('🪙 Flipping a Coin: It\'s **' + outputmsg + '**!')

@bot.command(name="d6",description="Rolls a six-sided dice.")
async def slash_command(interaction:discord.Interaction):
    await interaction.response.send_message('🎲 Rolling a d6: **' + str(random.randint(1, 6)) + '**')

@bot.command(name="d20",description="Rolls a twenty-sided dice.")
async def slash_command(interaction:discord.Interaction):
    await interaction.response.send_message('🎲 Rolling a d20: **' + str(random.randint(1, 20)) + '**')
    
@bot.command(name="help",description="Lists available commands.")
async def slash_command(interaction:discord.Interaction):
    await interaction.response.send_message('Ping! I\'m the temporary replacement MoMMI seeing as the old one\'s gone. I don\'t have nearly as many features as the old one, but here\'s what I **can** do: */status, /who, /teststatus, /testwho, /help, /coinflip, /d6, /d20, [GitPRNumber], $bitch!!!, $bobo, $flarg, $grape, $manylo, $meta, $revealantags, $shotgun, $strangle*.')  
    
@bot.command(name="respadd",description="Adds a new response to the bot's records.")
# this explicitly tells pycord what types the options are instead of it figuring it out by itself
async def respadd(ctx, responsename: discord.Option(discord.SlashCommandOptionType.string), responsecontent: discord.Option(discord.SlashCommandOptionType.string)):
    if ' ' in responsename or '$' in responsename or '@' in responsename:
        await ctx.respond(f'Spaces, @, and $ are not allowed in response names.')
        return
    else:    
        respdict[responsename] = responsecontent
        try:
            os.remove(respfile)
        except OSError:
            pass
        with open('resp.json', 'w') as fp:
            json.dump(respdict, fp)
        await ctx.respond(f"Response $" + responsename + " has been added.")    
    
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('[') and message.content.endswith(']'):
        prnumber = message.content
        prnumber = prnumber.replace('[', '')
        prnumber = prnumber.replace(']', '')
        
        try:
            os.remove(localissuesfile)
        except OSError:
            pass
        wget.download(gitissuesurl, 'localissues.json')
        issuedict = json.load(open('localissues.json', 'r', encoding="utf-8"))
        
        try:
            os.remove(localprfile)
        except OSError:
            pass
        wget.download(gitprurl, 'localpr.json')
        prdict = json.load(open('localpr.json', 'r', encoding="utf-8"))
        
        if int(prdict[0]["number"]) >= int(issuedict[0]["number"]):
            gittotal = prdict[0]["number"]
        else:
            gittotal = issuedict[0]["number"]
            
        if len(prnumber) <= len(str(gittotal)):
            #try:
                if int(prnumber) <= gittotal and int(prnumber) > 0:
                    gitposturl = gitissuesurl + '/' + prnumber
                    try:
                        os.remove(localissuesfile)
                    except OSError:
                        pass
                    wget.download(gitposturl, 'localissues.json')
                    postdict = json.load(open('localissues.json', 'r', encoding="utf-8"))
                    embeddesc = re.sub('\n<!--.*?-->','', postdict["body"], flags=re.DOTALL)
                    embeddesc = embeddesc.replace("\r", "")
                    embeddesc = embeddesc.replace("\n", "")
                    embeddesc = embeddesc.replace("# Revision", "\nRevision: ")
                    embeddesc = embeddesc.replace("# Description", " - Description: ")
                    embeddesc = embeddesc.replace("# Steps to Reproduce", " - Steps to Reproduce: ")
                    embeddesc = embeddesc.replace("# What you Expected", " - What you Expected: ")
                    embeddesc = embeddesc.replace("# What Actually Happened", " - What Actually Happened: ")
                    embeddesc = embeddesc.replace("#", "")
                    embedcolor = 0x03bf16
                    embedtime = postdict["created_at"]
                    embedtime = embedtime.replace('T',' ')
                    embedtime = embedtime.replace('Z','')
                    
                    if postdict["state"] != "open":
                        embedcolor = 0xfc0202
                        
                    if len(postdict["body"]) >= 512:
                        embeddesc = embeddesc[:512] + '...'
                    embedVar = discord.Embed(title= "[" + prnumber + "] " + postdict["title"], description=embeddesc, color=embedcolor, url=postdict["html_url"])
                    embedVar.set_author(name=postdict["user"]["login"], url=postdict["user"]["html_url"], icon_url=postdict["user"]["avatar_url"])
                    embedVar.set_thumbnail(url="http://ss13.moe/img/vgstation-logo2.png")
                    embedVar.add_field(name="Created", value=embedtime, inline=False)
                    embedVar.add_field(name="Comments", value=postdict["comments"], inline=True)
                    embedVar.add_field(name="Upvotes", value=postdict["reactions"]["+1"], inline=True)
                    embedVar.add_field(name="Downvotes", value=postdict["reactions"]["-1"], inline=True)
                    await message.channel.send(embed=embedVar)
                else:
                    print("exit point 3")
                    return
            #except:
            #    print("exit point 2")
            #    return
        else:
            print("exit point 1")
            return

    #the dumb meme commands get to stay as dollar commands because tradition
    elif message.content.startswith('$'):
        if ' ' in message.content:
            return
        else:
            keyattempt = message.content[1:]
            try:
                await message.channel.send(respdict[keyattempt])
            except:
                pass
        
#create a file named ".env" in the same folder as this and just add a line that's "TOKEN=yourtokenhere"
bot.run(TOKEN)