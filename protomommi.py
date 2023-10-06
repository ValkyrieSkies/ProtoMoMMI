import discord
import json
import wget
import os
import random

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

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    
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
                    embeddesc = postdict["body"]
                    if len(postdict["body"]) >= 4096:
                        embeddesc = embeddesc[:4092] + '...'
                    embedVar = discord.Embed(title= "[" + prnumber + "] " + postdict["title"], description=embeddesc, color=0x03bf16, url=postdict["url"])
                    embedVar.set_thumbnail(url="http://ss13.moe/img/vgstation-logo2.png")
                    embedVar.add_field(name="Comments", value=postdict["comments"], inline=False)
                    embedVar.add_field(name="Upvotes", value=postdict["reactions"]["+1"], inline=True)
                    embedVar.add_field(name="Downvotes", value=postdict["reactions"]["-1"], inline=True)
                    embedVar.set_footer(text=postdict["user"]["login"])
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

    elif message.content.startswith('$embedtest'):
        embedVar = discord.Embed(title="[696969] Removes Assistant", description="(WEB REPORT BY: doctorsergius REMOTE: 206.221.180.138:7777)\n# Revision\r\nf40bd5f75074f0e6b9d2631a138a9d7ba6fc1884\r\n\r\n# Description\r\nPlants with the no reactions trait still seem to allow reactions to happen, at least under certain circunstances\r\n# Steps to Reproduce\r\nGot blood tomato seeds, spliced them with no reactions and clonexadone production genes from fossil seeds, spliced together they grow tomatoes that contain clonex and blood in a stable manner past the amounts where they would make meat on harvest, but the no reactions trait seems to stop working past 110 potency or so\r\n# What you Expected\r\nTomatoes that make 10+ units of synthmeat when eaten/ thrown\r\n# What Actually Happ...", color=0x03bf16, url="http://valkyrieskies.ie")
        embedVar.set_thumbnail(url="http://ss13.moe/img/vgstation-logo2.png")
        embedVar.add_field(name="Comments", value="69", inline=False)
        embedVar.add_field(name="Upvotes", value="2", inline=True)
        embedVar.add_field(name="Downvotes", value="21", inline=True)
        embedVar.set_footer(text="ValkyrieSkies")
        await message.channel.send(embed=embedVar)

    #the dumb meme commands get to stay as dollar commands because tradition
    elif message.content.startswith('$manylo'):
        await message.channel.send('Fuckin\' shitman\'s like manylo are the reason this server struggles with pop. The players aren\'t bad, most of you are decent folk, the Admins aren\'t that bad, most are cool but that fucking SHITHEAD motherfucker is what makes people not enjoy the fucking game anymore.')
        
    elif message.content.startswith('$grape'):
        await message.channel.send('Shut the fuck up you dumb irrelevant grape holy shit I hate you, you are a waste of space')
        
    elif message.content.startswith('$shotgun'):
        await message.channel.send('I used the shotgun. You know why? Cause the shot gun doesn\'t miss, and unlike the shitty hybrid taser it stops a criminal in their tracks in two hits. Bang, bang, and they\'re fucking done. I use four shots just to make damn sure. Because, once again, I\'m not there to coddle a buncha criminal scum sucking ***, I\'m there to 1) Survive the fucking round. 2) Guard the armory. So you can absolutely get fucked. If I get unbanned, which I won\'t, you can guarantee I will continue to use the shotgun to apprehend criminals. Because it\'s quick, clean and effective as fuck. Why in the seven hells would I fuck around with the disabler shots, which take half a clip just to bring someone down, or with the tazer bolts which are slow as balls, impossible to aim and do about next to jack shit, fuck all. The shotgun is the superior law enforcement weapon. Because it stops crime. And it stops crime by reducing the number of criminals roaming the fucking halls.')
        
    elif message.content.startswith('$flarg'):
        await message.channel.send('I have been: abused, analized, africanized, battered, bummed, buggered, buckbroken, brainscorched, beaten, berated, bludgeoned by big black blocks, cummed, creamed, circumcised, constipated, clapped, dicked, dommmed, edified, fucked, fingered, face-sat, fugged, frazzled, farted on, fumpled, femenized, guzzled, gashed, gaslight, girl bossed, gushed, hemmed, hurt, inseminated, intercoursed, illicted, jacked off, jacked into, jacked onto, killed, kumed, key-stoned, licked, loved, lied to, mushed, ordained, obscured, pooed, pied, pissed, pumped, pillared, quzangled, rectum-fied, raped, ransaked, ravaged, skinned, slaved, slapped, sexoooed, slutified, stuffed, tummied, touched, un-feminized, unloved, vertically-insulted, vroomed, wanked, walled, wrapped, xxxxGAYBOYxxx\'d, yinkled, and zombie-raped.')
        
    elif message.content.startswith('$bitch!!!'):
        await message.channel.send('https://media.tenor.com/QPgNJ7ZEFHsAAAAC/swag-cat.gif')
        
    elif message.content.startswith('$meta'):
        await message.channel.send('https://media.discordapp.net/attachments/1021562311074390066/1026672867645071420/unknown.png?width=682&height=637')
        
    elif message.content.startswith('$strangle'):
        await message.channel.send('https://media.discordapp.net/attachments/1021561310728699905/1045606728378630174/unknown.png?width=846&height=211')

    elif message.content.startswith('$bobo'):
        await message.channel.send('https://media.tenor.com/gsD143k10RcAAAAC/bobo-reddit.gif')
       
    elif message.content.startswith('$revealantags'):
        match random.randint(1, 40):
            case 1:
                await message.channel.send("IT\S **REVS**!")
            case 2:
                await message.channel.send("IT\'S **CULT**!")
            case 3:
                await message.channel.send("IT\'S **MALF**!")
            case 4:
                await message.channel.send("IT\'S **EXTENDED**!")
            case 5:
                await message.channel.send("IT\'S **NUKE OPS**!")
            case 6:
                await message.channel.send("IT\'S **RAGIN\' MAGES**!")
            case 7:
                await message.channel.send("IT\'S **TRAITOR-LINGS**!")
            case 8:
                await message.channel.send("IT\'S **VAMPSTENDED**!")
            case 9:
                await message.channel.send("IT\'S **WIZARD**!")
            case 10:
                await message.channel.send("IT\'S **MONKEY MADNESS**!")
            case 11:
                await message.channel.send("IT\'S **REVSQUAD**!")
            case 12:
                await message.channel.send("IT\'S **HIGHLANDER**!")
            case 13:
                await message.channel.send("IT\'S **BLOB**!")
            case 14:
                await message.channel.send("IT\'S **DORF**!")
            case 15:
                await message.channel.send("IT\'S **AN SS14 PLAYTEST**!")
            case 16:
                await message.channel.send("IT\'S **CHALLENGERS**!")
            case 17:
                await message.channel.send("IT\'S **TRAITORS**!")
            case 18:
                await message.channel.send("IT\'S **ANTAG MADNESS**!")
            case 19:
                await message.channel.send("IT\'S **GORILLIONAIRES & BOOTYBORGS**!")
            case 20:
                await message.channel.send("IT\'S **TAG MODE**!")
            case 21:
                await message.channel.send("IT\'S **ADMINBUS**!")
            case 22:
                await message.channel.send("IT\'S **HIGH RP**!")
            case 23:
                await message.channel.send("IT\'S **COLONIAL MARINES**!")
            case 24:
                await message.channel.send("IT\'S **SPACE NINJA**!")
            case 25:
                await message.channel.send("IT\'S **TIME AGENTS**!")
            case 26:
                await message.channel.send("IT\'S **READIED UP FOR FUN**!")
            case 27:
                await message.channel.send("IT\'S **METEORS**!")
            case 28:
                await message.channel.send("IT\'S **LOOSE CATBEAST**!")
            case 29:
                await message.channel.send("IT\'S **CHANGELINGS**!")
            case 30:
                await message.channel.send("IT\'S **CLOCKWORK CULT**!")
            case 31:
                await message.channel.send("IT\'S **DEATH SQUAD**!")
            case 32:
                await message.channel.send("IT\'S **AN AWAY MISSION**!")
            case 33:
                await message.channel.send("IT\'S **GRUE INFESTATION**!")
            case 34:
                await message.channel.send("IT\'S **PULSE DEMONS**!")
            case 35:
                await message.channel.send("IT\'S **AUTOTRAITOR**!")
            case 36:
                await message.channel.send("IT\'S **SOKOBAN**!")
            case 37:
                await message.channel.send("IT\'S **BOMBERMAN**!")
            case 38:
                await message.channel.send("IT\'S **SURVIVORS**!")
            case 39:
                await message.channel.send("IT\'S **HARDCORE MODE**!")
            case 40:
                await message.channel.send("IT\'S **CRASHED!**!")
            case _:
                await message.channel.send('It\'s *Malcolm in the Middle*.')

#create a file named ".env" in the same folder as this and just add a line that's "TOKEN=yourtokenhere"
bot.run(TOKEN)