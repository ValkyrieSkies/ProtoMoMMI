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
            
    elif message.content.startswith('$manylo'):
        await message.channel.send('Fuckin\' shitman\'s like manylo are the reason this server struggles with pop. The players aren\'t bad, most of you are decent folk, the Admins aren\'t that bad, most are cool but that fucking SHITHEAD motherfucker is what makes people not enjoy the fucking game anymore.')
        
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
    

#create a file named ".env" in the same folder as this and just add a line that's "TOKEN=yourtokenhere"
client.run(TOKEN)