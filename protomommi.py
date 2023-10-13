import discord
import json
import wget
import os
import random
import re
import datetime
import urllib

from urllib.parse import unquote
from quart import *
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()

### ============== ###
### .env variables ###
### ============== ###

TOKEN = os.getenv('TOKEN')
LISTENPORT = os.getenv('LISTENPORT')
DISCPASS = os.getenv('DISCPASS')
DISCKILLPASS = os.getenv('DISCKILLPASS')
ROUNDENDPHRASE = os.getenv('ROUNDENDPHRASE')

# The chan variables are the identifiers as sent in the "meta" field of byond's requests, the chanid variables are the channel's numerical discord IDs
DISCAHELPCHAN = os.getenv('DISCAHELPCHAN')
DISCAHELPCHANID = int(os.getenv('DISCAHELPCHANID'))
DISCMAINCHAN = os.getenv('DISCMAINCHAN')
DISCMAINCHANID = int(os.getenv('DISCMAINCHANID'))
DISCSTATUSCHAN = os.getenv('DISCSTATUSCHAN')
DISCSTATUSCHANID = int(os.getenv('DISCSTATUSCHANID'))

DISCADMINROLEID = int(os.getenv('DISCADMINROLEID'))
DISCPLAYERROLEID = int(os.getenv('DISCPLAYERROLEID'))

#/vg/station's server stuff
SERVERICON = os.getenv('SERVERICON')
GAMESTATUSURL = os.getenv('GAMESTATUSURL')

#Github addresses for the PR fetch utility
GITURL = os.getenv('GITURL')
GITISSUESURL = os.getenv('GITISSUESURL')

### =============== ###
### Other Variables ###
### =============== ###

#Local file locations
dirname = os.path.dirname(__file__)
localgitfile = os.path.join(dirname, 'localgit.json')
respfile = os.path.join(dirname, 'resp.json')

#Characters disallowed in resp names
badCharacters = [' ', '/', '$', '>', '<', '@', '*', '%', ',', '"', "'", '\\', '|', '[', ']', '{', '}', '(', ')', '^', ':', ';']

#bot is the discord bot, app is the quart server
bot = discord.Bot(command_prefix="!",intents=discord.Intents.all())
app = Quart(__name__)

#Shortcut for printing the time at the start of console log messages
def logTime():
    return "[" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "]"
    
#Converts the url parameter from Byond's world.export GET requests into a list which it then converts into a Python dictionary, then removes the url encoding from "content" and returns the whole thing
def urlCleaner(incurl):
    incurl = incurl[(incurl.find('?')+1):]
    incurl = incurl.split("&")
    sortedurl = {}
    for x in incurl:
        newkey = x
        newkey = newkey[:newkey.find("=")]
        newvalue = x
        newvalue = newvalue[newvalue.find("=")+1:]
        sortedurl[newkey] = newvalue
    sortedurl["content"] = sortedurl["content"].replace("+", " ")
    sortedurl["content"] = unquote(sortedurl["content"])
    return sortedurl  

### ================= ###
### Bot startup event ###
### ================= ###

@bot.event
async def on_ready():
    print(logTime() + " - LOG: We have logged in as " + str(bot.user))
    try:
        global respdict
        with open('resp.json', 'r') as incoming:
            respdict = json.load(incoming)
        print(logTime() + " - LOG: Loaded response file to dictionary successfully.")
    except:
        #If you add a resp after a boot where the file failed to load, it will delete the old file if it exists. Oh well!
        respdict = {}
        print(logTime() + " - LOG: Failed to load response file to dictionary, starting with blank response dictionary.")

### ================ ###
### Byond listener   ###
### ================ ###

#This is the function Quart uses to listen for the incoming GET requests from Byond's world.export()
@app.route("/")
async def byondListen():
    urlpayload = str(request.url)
    #If an exception is thrown while running urlCleaner, then it wasn't a payload we wanted in the first place
    try:
        urldict = urlCleaner(urlpayload)
    except:
        return " "
    #"pass" is used to deny any data sent by anyone who doesn't have the configured discord_pass so they can't send arbitrary messages
    if urldict["pass"] == DISCPASS:
        #"meta" is the tag used to determine what channel to send to
        if urldict["meta"] == DISCAHELPCHAN:
            await ahelpMsg(urldict)
        elif urldict["meta"] == DISCSTATUSCHAN:
            await statusMsg(urldict)
        elif urldict["meta"] == DISCMAINCHAN:
            await ickMsg(urldict)
    return " "
        
#These methods post the "content" from each request to the relevant channel
async def statusMsg(passdict):
    channel = bot.get_channel(DISCSTATUSCHANID)
    if passdict["ping"] == "true":
        await channel.send(passdict["content"] + " <@&" + str(DISCPLAYERROLEID) + ">")
    else:
        await channel.send(passdict["content"])

async def ickMsg(passdict):
    channel = bot.get_channel(DISCMAINCHANID)
    if passdict["ping"] == "true":
        await channel.send(passdict["content"] + " <@&" + str(DISCPLAYERROLEID) + ">")
    else:
        await channel.send(passdict["content"])
    
async def ahelpMsg(passdict):
    channel = bot.get_channel(DISCAHELPCHANID)
    if passdict["ping"] == "true":
        await channel.send(passdict["content"] + " <@&" + str(DISCADMINROLEID) + ">")
    else:
        await channel.send(passdict["content"])
  

### ============== ###
### Slash commands ###
### ============== ###

@bot.command(name="help",description="Lists available commands.")
async def slash_command(interaction:discord.Interaction):
    await interaction.response.send_message('Ping! I\'m the temporary replacement MoMMI seeing as the old one\'s gone. I don\'t have quite as many features as the old one, but here\'s what I **can** do: */help, /status, /who, /teststatus, /testwho, /resplist, /coinflip, /roll, [GitPRNumber], and $ResponseName. Admins also have access to /respadd, /respdel, and /emergencykill.')
    
#Windows CMD didn't play nicely with killing the task via keyboard interrupt while Quart is running, so I added this command to allow killing the bot via Discord. Admin only AND requires the use of a password defined in the .env
@bot.command(name="emergencykill",description="Terminates the bot's process via Discord.")
@commands.has_permissions(administrator = True)
async def slash_command(ctx, killphrase: discord.Option(discord.SlashCommandOptionType.string)):
    if killphrase == DISCKILLPASS:
        print(logTime() + "- LOG: Bot killswitch successfully triggered by user " + str(ctx.author.id))
        await ctx.respond(f"Killphrase confirmed, terminating process.")
        exit()
    else:
        await ctx.respond(f"Incorrect killphrase.", ephemeral=True)

@bot.command(name="status",description="Retrieves the status of the game server.")
async def slash_command(interaction:discord.Interaction):
    #wget doesn't overwrite existing files, so you have to delete any pre-existing instances first
    try:
        os.remove(localstatusfile)
    except OSError:
        pass
    wget.download(GAMESTATUSURL, 'localstatus.json')
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
    wget.download(GAMESTATUSURL, 'localstatus.json')
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
    wget.download(GAMESTATUSURL, 'localstatus.json')
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
    wget.download(GAMESTATUSURL, 'localstatus.json')
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

# ---------------- #
# Gimmick commands #
# ---------------- #

@bot.command(name="coinflip",description="Flips a coin.")
async def slash_command(interaction:discord.Interaction):
    if(random.randint(1, 2) == 1):
        outputmsg = 'Heads'
    else:
        outputmsg = 'Tails'
    await interaction.response.send_message('🪙 Flipping a Coin: It\'s **' + outputmsg + '**!')

@bot.command(name="roll",description="Roll a number of specified dice.")
async def slash_command(ctx, diceamount: discord.Option(discord.SlashCommandOptionType.integer), dicesides: discord.Option(discord.SlashCommandOptionType.integer)):
    if diceamount > 100:
        await ctx.respond("No more than 100 dice at a time for sanity's sake.", ephemeral=True)

    elif dicesides > 1000:
        await ctx.respond("No, nothing larger than a d1000.", ephemeral=True)
      
    elif diceamount <= 0:
        await ctx.respond("You can't roll less than one dice bro.", ephemeral=True)
        
    elif dicesides <= 0:
        await ctx.respond("No, you can't have a dice with no sides.", ephemeral=True)
    
    else:  
        i = 0
        currentval = 0
        runtotal = 0
        outputmsg = ""
        while i < diceamount - 1:
            currentval = random.randint(1, dicesides)
            runtotal = runtotal + currentval
            if currentval == dicesides:
                outputmsg = outputmsg + "**" + str(currentval) + "**, "
            else: 
                outputmsg = outputmsg + str(currentval) + ", "
            i = i + 1
        currentval = random.randint(1, dicesides)
        runtotal = runtotal + currentval
        outputmsg = outputmsg + str(currentval)
        await ctx.respond("🎲 Rolling " + str(diceamount) + "d" + str(dicesides) + ", results: " + outputmsg + ", sum total = **" + str(runtotal) + "**")
            
@bot.command(name="rollexp",description="Roll a number of specified exploding dice.")
async def slash_command(ctx, diceamount: discord.Option(discord.SlashCommandOptionType.integer), dicesides: discord.Option(discord.SlashCommandOptionType.integer)):
    if diceamount > 20:
        await ctx.respond("No more than 20 explosive dice at a time for sanity's sake.", ephemeral=True)

    elif dicesides > 1000:
        await ctx.respond("No, nothing larger than a d1000.", ephemeral=True)
      
    elif diceamount <= 0:
        await ctx.respond("You can't roll less than one dice bro.", ephemeral=True)
        
    elif dicesides <= 0:
        await ctx.respond("No, you can't have a dice with no sides.", ephemeral=True)
    
    else:  
        i = 0
        currentval = 0
        runtotal = 0
        outputmsg = ""
        while i < diceamount - 1:
            currentval = random.randint(1, dicesides)
            runtotal = runtotal + currentval
            if currentval == dicesides:
                outputmsg = outputmsg + "**" + str(currentval) + "** ["
                while currentval == dicesides:
                    currentval = random.randint(1, dicesides)
                    runtotal = runtotal + currentval
                    if currentval == dicesides:
                        outputmsg = outputmsg + "**" + str(currentval) + "**, "
                    else: 
                        outputmsg = outputmsg + str(currentval) + "], "
            else: 
                outputmsg = outputmsg + str(currentval) + ", "
            i = i + 1
        currentval = random.randint(1, dicesides)
        runtotal = runtotal + currentval
        outputmsg = outputmsg + str(currentval)
        await ctx.respond("💥🎲 Rolling " + str(diceamount) + "d" + str(dicesides) + ", results: " + outputmsg + ", sum total = **" + str(runtotal) + "**")
    
# ------------- #
# Resp Commands #
# ------------- #

@bot.command(name="resplist",description="Lists available responses.")
async def slash_command(interaction:discord.Interaction):
    thelist = ""
    for x in respdict:
        thelist = thelist + "$" + x + ", "
    thelist = thelist[:(len(thelist)-2)]
    await interaction.response.send_message("Available responses: " + thelist)
    
@bot.command(name="respadd",description="Adds a new response to the bot's records.")
@commands.has_permissions(administrator = True)
async def slash_command(ctx, responsename: discord.Option(discord.SlashCommandOptionType.string), responsecontent: discord.Option(discord.SlashCommandOptionType.string)):
    try:
        if any([x in responsename for x in badCharacters]):
            await ctx.respond(f'Do not use non-text characters other than !, ?, -, and . in response names.', ephemeral=True)
            return
        else:    
            respdict[responsename] = responsecontent
            try:
                os.remove(respfile)
            except OSError:
                pass
            with open('resp.json', 'w') as outgoing:
                json.dump(respdict, outgoing)
            await ctx.respond(f"Response $" + responsename + " has been added.")
            print(logTime() + " - LOG: Reponse $" + responsename + " has been added via /respadd by " + str(ctx.author.id)  + " with content: \"" + responsecontent + "\"")
    except MissingPermissions:
        await ctx.respond(f"Administrator privileges are required to modify responses.", ephemeral=True)
        
@bot.command(name="respdel",description="Remove a response from the bot's records.")
@commands.has_permissions(administrator = True)
async def slash_command(ctx, responsename: discord.Option(discord.SlashCommandOptionType.string)):
    try:
        if any([x in responsename for x in badCharacters]):
            await ctx.respond(f'Special characters are disallowed here to prevent potentially dangerous code executions. If there\'s somehow an unwanted response with forbidden characters as its key, manually remove it from resp.json.', ephemeral=True)
            return
        else:
            try:
                del respdict[responsename]
            except:
                await ctx.respond(f"Response $" + responsename + " doesn't seem to exist.")
                return
            try:
                os.remove(respfile)
            except OSError:
                pass
            with open('resp.json', 'w') as outgoing:
                json.dump(respdict, outgoing)
            await ctx.respond(f"Response $" + responsename + " has been removed.")
            print(logTime() + " - LOG: Reponse $" + responsename + " has been deleted via /respdel by " + str(ctx.author.id) + "\"")
    except MissingPermissions:
        await ctx.respond(f"Administrator privileges are required to modify responses.", ephemeral=True)
        
### =================================== ###
### Non-Slash Commands below this point ###
### =================================== ###

@bot.event
async def on_message(message):
    #Ignore messages from self and other bots to prevent the resonance cascade
    if message.author == bot.user:
        return
    if message.author.bot:
        return

    #Github PR fetcher - If you ever end up on a repo with over 99,999 combined PRs and Issues, you'll have to change that < 6 to a < 7
    if message.content.split('[')[-1].split(']')[0].isnumeric() and len(message.content.split('[')[-1].split(']')[0]) < 6:
        prnumber = message.content.split('[')[-1].split(']')[0]
        gitposturl = GITISSUESURL + '/' + prnumber
        
        try:
            os.remove(localgitfile)
        except OSError:
            pass
        try:
            wget.download(gitposturl, 'localgit.json')
            postdict = json.load(open('localgit.json', 'r', encoding="utf-8"))
        except:
            return
        
        #Making sure there's an actual valid file that came through
        if not("number" in postdict):
            return
        else:
            #Strips styling effects and reformats some common blocks to look nicer on an embed
            embeddesc = re.sub('\n<!--.*?-->','', postdict["body"], flags=re.DOTALL)
            embeddesc = embeddesc.replace("\r", "")
            embeddesc = embeddesc.replace("\n", "")
            embeddesc = embeddesc.replace("# What this does", " - What this does: ")
            embeddesc = embeddesc.replace("# Why it's good", " - Why it's good: ")
            embeddesc = embeddesc.replace("# Changelog", "- Changelog: ")
            embeddesc = embeddesc.replace("# Revision", "\nRevision: ")
            embeddesc = embeddesc.replace("# Description", " - Description: ")
            embeddesc = embeddesc.replace("# Steps to Reproduce", " - Steps to Reproduce: ")
            embeddesc = embeddesc.replace("# What you Expected", " - What you Expected: ")
            embeddesc = embeddesc.replace("# What Actually Happened", " - What Actually Happened: ")
            embeddesc = embeddesc.replace("#", "")
            embedtime = postdict["created_at"]
            embedtime = embedtime.replace('T',' ')
            embedtime = embedtime.replace('Z','')
                
            #Changes the colour to green if open or purple if merged, otherwise it stays red
            embedcolour = 0xDA3633
            if postdict["state"] == "open":
                embedcolour = 0x238636
            elif "pull_request" in postdict:   
                if "merged_at" in postdict.get("pull_request", {}):
                    if postdict["pull_request"]["merged_at"] != None:
                        embedcolour = 0x8957E5
                
            #If the request is verbose, shrinks it down to 512 characters and adds an ellipses
            if len(postdict["body"]) >= 512:
                embeddesc = embeddesc[:512] + '...'
                    
            #Here's where the embed is actually constructed
            embedVar = discord.Embed(title= "[" + prnumber + "] " + postdict["title"], description=embeddesc, color=embedcolour, url=postdict["html_url"])
            embedVar.set_author(name=postdict["user"]["login"], url=postdict["user"]["html_url"], icon_url=postdict["user"]["avatar_url"])
            if SERVERICON != None:
                embedVar.set_thumbnail(url=SERVERICON)
            embedVar.add_field(name="Created", value=embedtime, inline=False)
            embedVar.add_field(name="Comments", value=postdict["comments"], inline=True)
            embedVar.add_field(name="Upvotes", value=postdict["reactions"]["+1"], inline=True)
            embedVar.add_field(name="Downvotes", value=postdict["reactions"]["-1"], inline=True)
            await message.channel.send(embed=embedVar)
            return
        

    #Response poster
    if message.content.startswith('$'):
        if any([x in message.content[1:] for x in badCharacters]):
            return
        else:
            try:
                await message.channel.send(respdict[message.content[1:]])
            except:
                return
     
#0.0.0.0 makes Quart listen for external requests, just make sure LISTENPORT is assigned to an accessible port
bot.loop.create_task(app.run_task("0.0.0.0", LISTENPORT))
     
#create a file named ".env" in the same folder as this and just add a line that's "TOKEN=yourtokenhere"
bot.run(TOKEN)
