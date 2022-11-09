#version 1.0.3-4
import asyncio
import os
import shutil
import json
import random
import copy
import sys
import traceback
import codecs
import discord
from discord.utils import get
from datetime import datetime
from discord import app_commands
from typing import Union

#custom modules
import config
import chessBridge
import musicBridge
import getevn
from config import Colors as col
from mPrint import mPrint as mp
def mPrint(tag, value):mp(tag, 'bot', value)

try: #This is specific to my own server, if you want to delete this also delete the other myServer lines in on_message()
    import NotLatif
    MM = True
except ModuleNotFoundError:
    MM = False

#oh boy for whoever is looking at this, good luck
#I'm  not reorganizing the code for now (maybe willdo)
#update 17/09/2022 actually kind of readable? I mean it was worse before

TOKEN = getevn.getenv('DISCORD_TOKEN', True)
GENIOUS = getevn.getenv('GENIOUS_SECRET')
OWNER_ID = int(getevn.getenv('OWNER_ID')) #(optional) needed for the bot to send you feedback when users use /feedback command
                                          # you will still see user-submitted feedback in the feedback.log file (will be createt automatically if not present)

intents = discord.Intents.all()
intents.members = True
intents.messages = True

settingsFile = "botFiles/guildsData.json"

global settings
settings = {}
with open(settingsFile, 'a'): pass #make guild setting file if it does not exist

with codecs.open('botFiles/lang.json', 'r', 'utf-8') as f:
    strings : dict[str,str] = json.load(f)['IT']

SETTINGS_TEMPLATE = {"id":{"responseSettings":{"enabled_channels":[],"join_message":"%name% likes butt!","leave_message":"Bye %name%, never come back","send_join_msg":False,"send_leave_msg":False,"response_perc":35,"other_response":9,"response_to_bots_perc":35,"will_respond_to_bots":False,"use_global_words":False,"custom_words":["butt"]},"chessGame":{"enabled_channels":[],"default_board":"default","boards":{},"default_design":"default","designs":{}},"musicbot":{"enabled_channels":[],"saved_playlists":{},"youtube_search_overwrite":{},"player_shuffle": True,"timeline_precision": 14}}}

#Useful funtions
def splitString(str, separator = ' ', delimiter = '\"') -> list:
    #https://icodelog.wordpress.com/2018/08/01/splitting-on-comma-outside-quotes-python/
    #splits string based on separator only if outside double quotes
    i = -1
    isQ = False
    lstStr = []
    for s in str:
        if s != separator and s != delimiter:
            if i == -1 or i < len(lstStr):
                lstStr.append(s)
                i = len(lstStr)
            else:
                lstStr[i-1] = lstStr[i-1] + s
         
        elif s == separator and isQ == False:
            lstStr.append('')
            i = len(lstStr)
             
        elif s == delimiter and isQ == False:
            isQ = True
            continue
         
        elif s == delimiter and isQ == True:
            isQ = False
            continue
         
        elif s == separator and isQ == True:
            lstStr[i-1] = lstStr[i-1] + s
         
    return lstStr

def culobotData(mode, data = None):
    with open('botFiles/culobotdata.json', mode) as f:
        if mode == 'r':
            return json.load(f)
        elif mode == 'w':
            json.dump(data, f, indent=2)

def updateCulobotData(key, value):
    data = culobotData('r')
    data[key] = value
    culobotData('w', data)

def dumpSettings(): #only use this function to save data to guildData.json (This should avoid conflicts with coroutines idk)
    """Saves the settings to file"""
    dump = {str(k): settings[k] for k in settings}
    with open(settingsFile, 'w') as f:
        json.dump(dump, f, indent=2)

def loadSettings():
    template = {}
    global settings
    try:
        with open(settingsFile, 'r') as f:
            settings = json.load(f)
    except json.JSONDecodeError: #file is empty FIXME testing, what if file is not empty and it's a decode error?
        with open(settingsFile, 'w') as fp:
            json.dump(template, fp , indent=2)
        return 0

    settings = {int(k): settings[k] for k in settings}

def createSettings(id : int): #creates settings for new guilds
    id = int(id)
    with open(settingsFile, 'r') as f:
        temp = json.load(f)
    temp[id] = SETTINGS_TEMPLATE["id"]

    with open(settingsFile, 'w') as f:
        json.dump(temp, f, indent=2)

    loadSettings()
  
def checkSettingsIntegrity(id : int):
    id = int(id)
    mPrint('DEBUG', f'Checking guildData integrity')

    try:
        settingsToCheck = copy.deepcopy(settings[id])
    except KeyError:
        mPrint('FATAL', f'Settings for guild were not initialized correctly\n{traceback.format_exc()}')
        sys.exit(-1)

    #check if there is more data than there should
    for key in settingsToCheck:
        if(key not in SETTINGS_TEMPLATE["id"]): #check if there is a key that should not be there (avoid useless data)
            del settings[id][key]
            mPrint('DEBUG', f'Deleting: {key}')

        if(type(settingsToCheck[key]) == dict):
            #if(key in ["saved_playlists", "youtube_search_overwrite"]): continue #whitelist
            for subkey in settingsToCheck[key]:
                if(subkey not in SETTINGS_TEMPLATE["id"][key]): #check if there is a subkey that should not be there (avoid useless data)
                    del settings[id][key][subkey]
                    mPrint('DEBUG', f'Deleting: {subkey}')

    #check if data is missing
    for key in SETTINGS_TEMPLATE["id"]:
        if(key not in settings[id]): #check if there is a key that should not be there (avoid useless data)
            settings[id][key] = SETTINGS_TEMPLATE["id"][key]
            mPrint('DEBUG', f'Creating key: {key}')

        #it it's a dict also check it's keys
        if(type(SETTINGS_TEMPLATE["id"][key]) == dict):
            for subkey in SETTINGS_TEMPLATE["id"][key]:
                if(subkey not in settings[id][key]): #check if there is a key that should not be there (avoid useless data)
                    settings[id][key][subkey] = SETTINGS_TEMPLATE["id"][key][subkey]
                    mPrint('DEBUG', f'Creating subkey: {subkey}')

    dumpSettings()

    mPrint('INFO', f'GuildSettings for {id} seem good.')

def formatLangStr(string : str, replace : Union[list, str]) -> str: #this has no reason of being so well documented lmao
    """
    Replaces the occurences of `$varx` in `string` with the contents of `replace`
    - ##### E.g.1
    - `format('this is $var0 test $var1.', ['a'])`
    - `format('this is $var0 test $var1.', 'a')`
    - will result in -> `this is a test $var1.`
    - ##### E.g. 2
    - `format('this is $var0 test $var1.', ['a', 'bye', 'whatever'])`
    - will result in -> `this is a test bye.`
    """

    if type(replace) != list: replace = str(replace)

    if type(replace) == str:
        return string.replace('$var0', str(replace))
    #else
    for x, r in enumerate(replace):
        keyword = '$varx'.replace('x', str(x))
        string = string.replace(keyword, str(r))

        print(f'x: {x}; r: {r}; keyword: {keyword}')

    return string

def getWord(all=False) -> Union[str,list]:
    """
    :return: A random line from the words.txt file.
    e.g. culo, i culi
    """
    with open('botFiles/words.txt', 'r') as words:
        lines = words.read().splitlines()
        if(all):
            return lines
        return random.choice(lines)

def parseWord(message:str, i:int, words:str, articoli:list[str]) -> tuple[str, str]:
    #message = 'No voglio il rosso'
    #words = 'il culo, i culi'
    
    article_word = words.split(', ') #['il culo', 'i culi']
    #sorry for spaghetti code maybe will reparse later

    if len(article_word) == 1: #word has only one form (eg: ['il culo'])
        if len(article_word[0].split()) == 1:
            return (message[i-1], article_word[0]) #eg. words = ['culo']
        if message[i-1] not in articoli: #don't change the word before if not an article
            return (message[i-1], article_word[0].split()[1]) #eg. words = ['il culo']
        return (article_word[0].split()[0], article_word[0].split()[1]) #eg. words = ['il culo']

    if message[i-1] not in articoli: #the word before is not an article
        if message[i-1].isnumeric(): #e.g. '3 cavolfiori'
            if message[i-1] == '1':
                return (message[i-1], article_word[0].split()[1]) #'1 culo'
            else:
                return (message[i-1], article_word[1].split()[1]) #'3 culi'
        return (message[i-1], article_word[0].split()[1]) #eg. returns ('ciao', 'culo')

    if message[i-1] in ['il', 'lo', 'la']: #eg. returns ('il', 'culo')
        return (article_word[0].split()[0], article_word[0].split()[1])

    if message[i-1] in ['i', 'gli', 'le']: #eg. returns ('i', 'culi')
        return (article_word[1].split()[0], article_word[1].split()[1])
    
    return ('parsing error', 'parseWord(str, int, str, list[str]) -> tuple[str, str]')


#           -----           DISCORD BOT            -----       #
class MyBot(discord.Client):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    async def on_error(self, *args, **kwargs):
        mPrint('ERROR', f"DISCORDPY on_error:\n{traceback.format_exc()}")
        mPrint('WARN', "ARGS:")
        for x in args:
            mPrint('ERROR', {x})

    async def on_guild_join(self, guild:discord.Guild):
        mPrint("INFO", f"Joined guild {guild.name} (id: {guild.id})")
        updateCulobotData('total_guilds', len(bot.guilds))

        members = '\n - '.join([member.name for member in guild.members])
        mPrint('DEBUG', f'Guild Members:\n - {members}')
        if (int(guild.id) not in settings):
            mPrint('DEBUG', f'^ Generating settings for guild {int(guild.id)}')
            createSettings(int(guild.id))
        else:
            mPrint('DEBUG', f'settings for {int(guild.id)} are present in {settings}')

        checkSettingsIntegrity(int(guild.id))

    async def on_guild_remove(self, guild:discord.Guild):
        updateCulobotData('total_guilds', len(bot.guilds))
    
    async def on_ready(self):
        try:
            self.dev = await bot.fetch_user(OWNER_ID)
        except discord.errors.NotFound:
            self.dev = None
        await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name="/help"))
        await tree.sync()

        updateCulobotData('total_guilds', len(bot.guilds))

        mPrint("DEBUG", "Called on_ready")
        if len(sys.argv) == 5 and sys.argv[1] == "RESTART":
            mPrint("INFO", "BOT WAS RESTARTED")
            guild = await bot.fetch_guild(sys.argv[2])
            channel = await guild.fetch_channel(sys.argv[3])
            message = await channel.fetch_message(sys.argv[4])
            await message.reply("Bot restarted")
            
        mPrint("INFO", f'Connected to {len(bot.guilds)} guild(s):')
        for guild in bot.guilds:
            mPrint('DEBUG', f'Checking {guild.id}')
            if (int(guild.id) not in settings):
                mPrint('DEBUG', f'^ Generating settings')
                createSettings(int(guild.id))
            else:
                mPrint('DEBUG', f'settings for are present.')

            checkSettingsIntegrity(int(guild.id))

    async def on_member_join(self, member : discord.Member):
        if settings[int(member.guild.id)]['responseSettings']['send_join_msg']:
            joinString:str = settings[int(member.guild.id)]['responseSettings']['join_message']
            joinString = joinString.replace('%name%', member.name)
            await member.guild.system_channel.send(joinString)
#--------------------------------- This is specific to my server---# 

        if MM and member.guild.id == 1019985578772664441:                   #  There is another block like this 
            await NotLatif.joinImageSend(member, member.guild)      #    a little below this one
#--------------------------------- you can safely delete this------# 

    async def on_member_remove(self, member : discord.Member):
        if settings[int(member.guild.id)]['responseSettings']['send_leave_msg']:
            leaveString:str = settings[int(member.guild.id)]['responseSettings']['leave_message']
            leaveString= leaveString.replace('%name%', member.name)
            await member.guild.system_channel.send(leaveString)
    
    async def on_message(self, message : discord.Message):
        if len(message.content.split())==0: return
        global settings

        try:
            respSettings = settings[int(message.guild.id)]["responseSettings"]
        except AttributeError:
            return #this gets triggered with ephemeral messages

#--------------------------------- This is specific to my server---#
        if MM and message.content[0] == '!' and  message.author.id == 348199387543109654:
            await NotLatif.parseCmd(message, settings)
            return
#--------------------------------- you can safely delete this------# 

        if message.channel.id not in settings[message.guild.id]['responseSettings']['enabled_channels']:
            return #module is not in whitelist

        #don't respond to self, commands, messages with less than 2 words
        if message.author.id == bot.user.id or message.content[0] in ["!", "/", "?", "|", '$', "&", ">", "<"] or len(message.content.split()) < 2:
            return

        #if guild does not want bot responses and sender is a bot, ignore the message
        if message.author.bot and not respSettings["will_respond_to_bots"]: return 0

        #culificazione
        articoli = ['il', 'lo', 'la', 'i', 'gli', 'le'] #Italian specific

        if random.randrange(1, 100) > respSettings["response_perc"]: #implement % of answering
            return

        msg = message.content.split() #trasforma messaggio in lista
        
        for i in range(len(msg) // 2): #culifico al massimo metà delle parole
            scelta = random.randrange(1, len(msg)) #scegli una parola

            # se la parola scelta è un articolo (e non è l'ultima parola), cambio la prossima parola
            # e.g "ciao sono il meccanico" (se prendo la parola DOPO "il") -> "ciao sono il culo"   
            if msg[scelta] in articoli and scelta < len(msg)-1:
                scelta += 1
            parola = getWord() #scegli con cosa cambiarla
            articolo, parola = parseWord(msg, scelta, parola, articoli)

            msg[scelta-1] = articolo
            if(msg[scelta].isupper()): #controlla se la parola è maiuscola, o se la prima lettera è maiuscola
                parola = parola.upper()
            elif(msg[scelta][0].isupper()):
                parola = parola[0].upper() + parola[1:]
            msg[scelta] = parola #sostituisci parola

            if(random.randrange(1, 100) > respSettings['other_response']):
                i+=1
            i+=1

        msg = " ".join(msg) #trasforma messaggio in stringa

        await message.reply(msg, mention_author=False)
        mPrint('DEBUG', f'Ho risposto ad un messaggio.')


bot = MyBot(intents = intents)
tree = app_commands.CommandTree(bot)


#           -----           DISCORD BOT SLASH COMMANDS           -----       #

@tree.command(name="join-msg", description="Cambia il messaggio di benvenuto, /help join-msg per più info")
async def joinmsg(interaction : discord.Interaction, message : str = None, enabled : bool = None):
    mPrint('CMDS', f'called /join-msg {message}')
    guildID = int(interaction.guild.id)

    if enabled != None:
        settings[guildID]['responseSettings']['send_join_msg'] = enabled
        dumpSettings()

    if message != None: #edit join-message or show help
        settings[guildID]['responseSettings']['join_message'] = message
        dumpSettings()

    embed = discord.Embed(
        title="Join Message",
        description=f"Enabled: {settings[guildID]['responseSettings']['send_join_msg']}\nMessage: {settings[guildID]['responseSettings']['join_message']}",
        color=col.orange
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="leave-msg", description="Cambia il messaggio di addio, /help leave-msg per più info")
async def leavemsg(interaction : discord.Interaction, message : str = None, enabled : bool = None):
    mPrint('CMDS', f'called /leave-msg {message}')
    guildID = int(interaction.guild.id)

    if enabled != None:
        settings[guildID]['responseSettings']['send_leave_msg'] = enabled
        dumpSettings()

    if message != None: #edit join-message or show help
        settings[guildID]['responseSettings']['leave_message'] = message
        dumpSettings()
    
    embed = discord.Embed(
        title="Leave Message",
        description=f"Enabled: {settings[guildID]['responseSettings']['send_leave_msg']}\nMessage: {settings[guildID]['responseSettings']['leave_message']}",
        color=col.orange
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="respond-perc", description="Imposta la percentuale di risposta del bot (0-100)")
async def responsePerc(interaction : discord.Interaction, value : int = -1):
    mPrint('CMDS', f'called /respond-perc {value}')
    guildID = int(interaction.guild.id)

    respSettings = settings[guildID]["responseSettings"] #readonly 

    if(value == -1):
        await interaction.response.send_message(formatLangStr(strings["bot.resp.info"], str(respSettings["response_perc"])))
        return
    
    elif (respSettings['response_perc'] == value):
        await interaction.response.send_message(strings['nothing_changed'])
        return
    #else
    #keep value between 0 and 100
    value = 100 if value > 100 else 0 if value < 0 else value

    await interaction.response.send_message(formatLangStr(strings['bot.resp.newperc'], value))

    mPrint('INFO', f'{interaction.user.name} set response to {value}%')
    settings[guildID]['responseSettings']['response_perc'] = value
    dumpSettings()

@tree.command(name="respond-to-bots", description="Decidi se culobot può rispondere ad altri bot")
async def botRespToggle(interaction : discord.Interaction, value : bool):
    mPrint('CMDS', f'called /respond-to-bots {value}')
    guildID = int(interaction.guild.id)
        
    if value == True:
        response = strings['bot.resp.resp_to_bots.affirmative']
    else:
        response = strings['bot.resp.resp_to_bots.negative']
    await interaction.response.send_message(response)

    settings[guildID]['responseSettings']['will_respond_to_bots'] = value
    dumpSettings()
    return

@tree.command(name="respond-to-bots-perc", description="Imposta la percentuale di probabilità di rispondere ad un bot (0-100)")
async def botRespPerc(interaction : discord.Interaction, value : int = -1):
    mPrint('CMDS', f'called /respond-to-bots-perc {value}')
    guildID = int(interaction.guild.id)

    if value == -1:
        await interaction.response.send_message(formatLangStr( #this just formats the string in lang.json with the data
            strings["bot.resp.resp_to_bots.info"],[#list of 2 variables to replace
                settings[guildID]["responseSettings"]["will_respond_to_bots"],#0
                settings[guildID]["responseSettings"]["response_to_bots_perc"]#1
            ]
            )
        )
        return

    #else
    #keep value between 0 and 100
    value = 100 if value > 100 else 0 if value < 0 else value

    await interaction.response.send_message(formatLangStr(strings["bot.resp.resp_to_bots.edit"], value))
    settings[guildID]['responseSettings']['response_to_bots_perc'] = value
    dumpSettings()
    return

@tree.command(name="dictionary", description="Mostra le parole conosciute dal bot")
async def dictionary(interaction : discord.Interaction):
    mPrint('CMDS', f'called /dictionary')
    guildID = int(interaction.guild.id)

    #1. Send a description
    custom_words = settings[guildID]['responseSettings']['custom_words']
    description = formatLangStr(strings['bot.words.info'], interaction.guild.name)

    if not settings[guildID]['responseSettings']['use_global_words']:
        description += formatLangStr(strings['bot.words.use_global_words'], interaction.guild.name)
        
    embed = discord.Embed(
        title = strings['bot.words.known_words'],
        description = description,
        colour = col.orange
    )

    value = ''
    #2a. get the global words
    botWords = getWord(True)

    #2b. if the guild uses the global words, append them to value
    if settings[guildID]['responseSettings']['use_global_words']:
        #is server uses default words
        value = '\n'.join(botWords)
        embed.add_field(name = strings['bot.words.bot_words'], value=value)
        value = '' 

    #2c. append the guild(local) words to value
    for i, cw in enumerate(custom_words):
        value += f'[`{i}`]: {cw}\n'
    if value == '': value=strings['bot.words.no_guild_words']
    embed.add_field(name = formatLangStr(strings['bot.words.guild_words'], interaction.guild.name), value=value)
    
    #3. send the words
    await interaction.response.send_message(embed=embed)

@tree.command(name="dictionary-add", description="Aggiunge una parola al dizionario")
async def dictionary_add(interaction : discord.Interaction, new_word : str):
    """
    Aggiunge una parola al dizionario.
    
    :param new_word: La parola che si vuole aggiungere
    """
    mPrint('CMDS', f'called /dictionary add {new_word}')
    guildID = int(interaction.guild.id)

    settings[guildID]['responseSettings']['custom_words'].append(new_word)
    await interaction.response.send_message(strings['bot.words.learned'], ephemeral=True)
    dumpSettings()
    return

@tree.command(name="dictionary-edit", description="Modifica una parola del dizionario")
async def dictionary_edit(interaction : discord.Interaction, id : int, new_word : str):
    """
    Modifica una parola del dizionario.
    
    :param id: L'id della parola che vuoi modificare
    :param new_word: La parola che vuoi rimpiazzare
    """
    mPrint('CMDS', f'called /dictionary edit {id}, {new_word}')
    guildID = int(interaction.guild.id)

    editWord = id
    if len(settings[guildID]['responseSettings']['custom_words']) > editWord:
        settings[guildID]['responseSettings']['custom_words'][editWord] = new_word
        dumpSettings()
        await interaction.response.send_message(strings['done'], ephemeral=True)
    else:
        await interaction.response.send_message(strings['bot.words.id_not_found'], ephemeral=True)
    return

@tree.command(name="dictionary-del", description="Elimina una parola dal dizionario", )
async def dictionary_del(interaction : discord.Interaction, id : int):
    """
    It deletes a word from the dictionary.

    :param id: L'id della parola che vuoi eliminare
    """
    mPrint('CMDS', f'called /dictionary del {id}')
    guildID = int(interaction.guild.id)

    delWord = id
    if len(settings[guildID]['responseSettings']['custom_words']) > delWord:
        del settings[guildID]['responseSettings']['custom_words'][delWord]
        dumpSettings()
        await interaction.response.send_message(strings['done'], ephemeral=True)
    else:
        await interaction.response.send_message(strings['bot.words.id_not_found'], ephemeral=True)
    return

@tree.command(name="dictionary-useglobal", description="Attiva/Disattiva il dizionario globale")
async def dictionary_default(interaction : discord.Interaction, value : bool ):
    mPrint('CMDS', f'called /dictionary useglobal {value}')
    guildID = int(interaction.guild.id)

    settings[guildID]["responseSettings"]["use_global_words"] = value
    await interaction.response.send_message(f'useDefault: {value}', ephemeral=True)
    dumpSettings()
    return

@tree.command(name="chess", description="Fai una partita di scacchi!")
async def chess(interaction : discord.Interaction, challenge : Union[discord.Role, discord.User] = None):
    """
    :param challenge: Il ruolo o l'utente da sfidare
    :param fen: Il layout delle pedine nella scacchiera (Se numerico indica uno dei FEN salvati)
    :param design: Il nome del design della scacchiera
    """
    mPrint('CMDS', f'called /chess: ch: {challenge}')
    guildID = int(interaction.guild.id)

    if interaction.channel.id not in settings[guildID]['chessGame']['enabled_channels']:
        await interaction.response.send_message("This module is not enabled in this channel.", ephemeral=True)
        return

    await interaction.channel.typing()
#1. Prepare the variables
    #info about the player challenging another player or a role to a match
    class Challenge:
        type = 0             #can be: 0-> Everyone / 1-> Role / 2-> Player
        whitelist = []       #list of user ids (int) (or 1 role id) 
        authorJoined = False #Needed when type = 1

    challengeData = Challenge()

    #2A. parse challenges
    if challenge == None:
        mPrint('DEBUG', 'Challenged everyone')
        challengeData.type = 0

    elif '<@&' in challenge.mention: #user challenged role
        mPrint('DEBUG', f'challenged role: {challenge.id} ({challenge.name})')
        challengeData.type = 1
        challengeData.whitelist.append(challenge.id)
        
    else: #user challenged user
        mPrint('DEBUG', f'challenged user: {challenge.id} ({challenge.name})')
        challengeData.type = 2
        challengeData.whitelist.append(interaction.user.id)
        challengeData.whitelist.append(challenge.id)

    #useful for FENs: eg   (!chess) game fen="bla bla bla" < str.strip will return ["game", "fen=bla", "bla", "bla"]
    # args = splitString(args)                    #wheras splitString will return ["game", "fen=", "bla", "bla", "bla"]

    #Ask user if he wants FEN and/or design
    class GameData():
        selectedLayout = None
        selectedDesign = None
    gameData = GameData()

    #FEN options
    globalBoards = chessBridge.getBoards()
    guildBoards = settings[guildID]['chessGame']['boards']
    layoutChoices = discord.ui.Select(options=[], placeholder=strings['bot.chess.layout.render.select'])

    for layout in globalBoards: #global layouts
        isDefault = False
        if layout == settings[guildID]["chessGame"]["default_board"]:
            isDefault = True
            gameData.selectedLayout = globalBoards[layout]
        layoutChoices.add_option(label=f"FEN: {layout}", description=globalBoards[layout], value=globalBoards[layout], default=isDefault)

    for layout in guildBoards: #guild layouts
        isDefault = False
        if layout == settings[guildID]["chessGame"]["default_board"]:
            isDefault = True
            gameData.selectedLayout = guildBoards[layout]
        layoutChoices.add_option(label=f"FEN: {layout}", description=guildBoards[layout], value=guildBoards[layout], default=isDefault)

    #Design options
    globalDesigns = chessBridge.chessMain.getDesignNames()
    guildDesigns = settings[guildID]['chessGame']['designs']
    designChoices = discord.ui.Select(options=[], placeholder=strings['bot.chess.design.render.select'])

    for design in globalDesigns: #guild layouts
        isDefault = False
        if design == settings[guildID]["chessGame"]["default_design"]:
            isDefault = True
            gameData.selectedDesign = design
        designChoices.add_option(label=f"Design: {design}", value=design, default=isDefault)
    for design in guildDesigns: #guild layouts
        isDefault = False
        if design == settings[guildID]["chessGame"]["default_design"]:
            isDefault = True
            gameData.selectedDesign = design
        designChoices.add_option(label=f"Design: {design}", description=str(guildDesigns[design]), value=design, default=isDefault)

    #handlers for select choices
    async def layoutChoice(interaction : discord.Interaction):
        gameData.selectedLayout = str(layoutChoices.values[0])
        mPrint('DEBUG', f'Selected layout {gameData.selectedLayout}')
        await interaction.response.defer()

    async def designChoice(interaction : discord.Interaction):
        gameData.selectedDesign = str(designChoices.values[0])
        mPrint('DEBUG', f'Selected design {gameData.selectedDesign}')
        
        await interaction.response.defer()

    layoutChoices.callback = layoutChoice
    designChoices.callback = designChoice

    async def btn_cancel(interaction : discord.Interaction): #User cancels matchmaking
        confirm.disabled = True
        cancel.disabled = True
        layoutChoices.disabled = True
        designChoices.disabled = True
        await interaction.response.edit_message(view=view)
        return

    async def btn_confirm(interaction : discord.Interaction): # When user confirms the data this function starts the game
        if (gameData.selectedDesign != None) and (gameData.selectedLayout != None):
            confirm.disabled = True
            cancel.disabled = True
            layoutChoices.disabled = True
            designChoices.disabled = True
            await interaction.response.edit_message(view=view)
            await interaction.channel.typing()
            await startGame(interaction, gameData.selectedLayout, gameData.selectedDesign)
        else:
            await interaction.response.send_message("You have to choose a design and layout", ephemeral=True)
        return

    confirm = discord.ui.Button(label="Conferma", style = discord.ButtonStyle.primary)
    confirm.callback = btn_confirm

    cancel = discord.ui.Button(label="Annulla", style=discord.ButtonStyle.danger)
    cancel.callback = btn_cancel

    view = discord.ui.View()
    view.add_item(layoutChoices)
    view.add_item(designChoices)
    view.add_item(confirm)
    view.add_item(cancel)

    await interaction.response.send_message(view=view, ephemeral=True)
    
    async def startGame(interaction:discord.Interaction, gameFEN, gameDesign):
        designName = gameDesign
    #2C. double-check the data retreived
        board = ()
        if gameFEN != '': #if fen is provided, check if valid
            if('k' not in gameFEN or 'K' not in gameFEN):
                print(gameFEN)
                embed = discord.Embed(
                    title = 'Problema con il FEN: manca il Re!',
                    description= f'Re mancante: {"black" if "k" not in gameFEN else ""} {"white" if "K" not in gameFEN else ""}',
                    color = col.red)
                await interaction.response.send_message(embed=embed)
                return -1
            #else, fen is valid
            board = ('FEN', gameFEN)

        mPrint('TEST', f'Design {gameDesign} ')
        if gameDesign != 'default': #if user asked for a design, check if it exists
            #give priority to guild designs
            if gameDesign in settings[guildID]['chessGame']['designs']:
                mPrint('TEST', f'Found Local design {gameDesign} ')
                colors = settings[guildID]['chessGame']['designs'][gameDesign]
                gameDesign = chessBridge.chessMain.gameRenderer.renderBoard(colors, interaction.id)
            elif chessBridge.chessMain.gameRenderer.doesDesignExist(gameDesign):
                mPrint('TEST', f'Found Global design {gameDesign}')
                gameDesign = chessBridge.chessMain.gameRenderer.getGlobalDesign(gameDesign) 
            else:
                mPrint('TEST', f'Design not found')
                gameDesign = 'default'
        
    # 3. All seems good, now let's send the embed to find some players
        #3A. Challenge one user
        class Challenge:
            type = 0             #can be: 0-> Everyone / 1-> Role / 2-> Player
            whitelist = []       #list of user ids (int) (or 1 role id) 
            authorJoined = False #Needed when type = 1

        if challengeData.type == 2: 
            embed = discord.Embed(title = f'{challenge.name}, sei stato sfidato da {interaction.user.name}!\nUsate una reazione per unirti ad un team (max 1 per squadra)',
                description=f'Scacchiera: {gameFEN}, design: {designName}',
                color = col.blu
            )
            
        #3B. Challenge one guild
        elif challengeData.type == 1:
            embed = discord.Embed(title = f'{challenge.name}, siete stati sfidati da {interaction.user.name}!\nUno di voi può unirsi alla partita!',
                description=f'Scacchiera: {gameFEN}, design: {designName}',
                color = col.blu
            )

        #3C. Challenge everyone
        else:
            embed = discord.Embed(title = f'Cerco giocatori per una partita di scacchi! ♟,\nUsa una reazione per unirti ad un team (max 1 per squadra)',
                description=f'Scacchiera: {gameFEN}, design: {designName}',
                color = col.blu).set_footer(text=f'Partita richiesta da {interaction.user.name}')
                        
        #3D. SEND THE EMBED FINALLY
        if challengeData.type != 0:
            await interaction.channel.send(f'{interaction.user} Ha sfidato {challenge.mention} a scacchi!')
        playerFetchMsg = await interaction.channel.send(embed=embed)

    #4. Await player joins
        #4A. setting up
        reactions = ('⚪', '🌑') #('🤍', '🖤')
        r1, r2 = reactions

        availableTeams = [reactions[0], reactions[1]] # Needed to avoid players from joining the same team
        players = [0, 0] #this will store discord.Members

        mPrint('DEBUG','chessGame: challenge whitelist')
        mPrint('DEBUG', challengeData.whitelist)

        #add reactions to the embed that people can use as buttons to join the teams
        await playerFetchMsg.add_reaction(r1)
        await playerFetchMsg.add_reaction(r2)
        await playerFetchMsg.add_reaction("❌") #if the author changes their mind


        def fetchChecker(reaction : discord.Reaction, user : Union[discord.Member, discord.User]) -> bool: #this is one fat checker damn
            """Checks if user team join request is valid"""

            # async def remove(reaction, user): #remove invalid reactions
            #     await reaction.remove(user)   #will figure out some way

            mPrint('DEBUG', f'chessGame: Check: {reaction}, {user}\nchallenge whitelist: {challengeData.whitelist}\navailable: {availableTeams}\n--------')
            
            #1- prevent bot from joining teams
            if (user == bot.user): 
                return False
            
            if (reaction.message.id != playerFetchMsg.id): #the reaction was given to another message
                return False

            if(str(reaction.emoji) == "❌" and user == interaction.user):
                return True #only the author can cancel the search

            #2- check if color is still available (prevent two players from joining the same team)
            if(str(reaction.emoji) not in availableTeams):
                return False #remember to remove the reaction before every return True

            userID = int(user.id)
            
            #3a- If player challenged a user:
            if(challengeData.type == 2): #0 everyone, 1 role, 2 user
                #check if joining player is in whitelist
                if userID not in challengeData.whitelist: return False
                
                challengeData.whitelist.remove(userID) #prevent user from rejoining another team
                availableTeams.remove(str(reaction.emoji)) #prevent player/s from joining the same team
                return True

            #3b- If player challenged a role:
            elif(challengeData.type == 1):
                challengedRole = challenge.id #challenge has only one entry containing the role id
                
                #if the user joining is the author:
                if user == interaction.user and challengeData.authorJoined == False: #the message author can join even if he does not have the role
                    mPrint('DEBUG', 'chessGame: User is author') #check the user BEFORE the role, so if the user has the role it does not get deleted
                    challengeData.authorJoined = True #prevent author from joining 2 teams
                    availableTeams.remove(str(reaction.emoji)) #prevent player/s from joining the same team
                    return True 
                
                #if the user joining isn't the author but has the role requested
                elif user.get_role(challengedRole) != None: #user has the role  
                    mPrint('DEBUG', 'chessGame: User has required role')
                    challengeData.whitelist = [] #delete the role to prevent two players with the role from joining (keeping out the author)
                    availableTeams.remove(str(reaction.emoji)) #prevent player/s from joining the same team
                    return True

                mPrint('WARN',f'chessGame: User {user.name} is not allowerd to join (Role challenge)')
                return False

            #3c- If player challenged everyone:
            else: #no need to check who joins (can also play with yourself)
                availableTeams.remove(str(reaction.emoji)) #prevent player/s from joining the same team
                return True

            # fetchChecker end #

        #4B. await user joins (with reactions)
        async def stopsearch():
            embed.title = "Ricerca annullata"
            embed.description = ""
            embed.color = col.red

            designFolder = f'{chessBridge.chessMain.gameRenderer.spritesFolder}{design}'
            if design.find('\\') != -1 or design.find('/') != -1:
                shutil.rmtree(designFolder)
            await playerFetchMsg.clear_reactions()
            await playerFetchMsg.edit(embed=embed)

        try:
            #i. await first player
            r1, players[0] = await bot.wait_for('reaction_add', timeout=60.0, check=fetchChecker)
            if str(r1.emoji) == "❌": 
                await stopsearch()
                return -2
            embed.description += f'\n{players[0]} si è unito a {r1}!'
            await playerFetchMsg.edit(embed=embed)
            

            #ii. await second player
            r2, players[1] = await bot.wait_for('reaction_add', timeout=60.0, check=fetchChecker)
            if str(r2.emoji) == "❌": 
                await stopsearch()
                return -2
            embed.description += f'\n{players[1]} si è unito a {r2}!\nGenerating game please wait...'
            embed.set_footer(text = 'tutti i caricamenti sono ovviamente falsissimi.')
            
            embed.color = col.green
            await playerFetchMsg.edit(embed=embed)
            #iii. fake sleep for professionality
            await asyncio.sleep(random.randrange(0,2))

        except asyncio.TimeoutError: #players did not join in time
            embed = discord.Embed(
                title = 'Non ci sono abbastanza giocatori.',
                colour = col.red
            )
            await interaction.channel.send(embed=embed)
            await playerFetchMsg.delete()
            return -1

        else: #players did join in time

            if str(r1.emoji) == reactions[0]: #first player choose white
                player1 = players[1] #white
                player2 = players[0] #black
            else: #first player choose black
                player1 = players[0] #white
                player2 = players[1] #black
            mPrint('INFO', f'p1: {player1}\np2: {player2}')

            #iv. Send an embed with the details of the game
            embed = discord.Embed(
                title = f'Giocatori trovati\n{r1} {player1} :vs: {player2} {r2}',
                description=f"Impostazioni:\n- Scacchiera: {gameFEN}, Design: {gameDesign}",
                colour = col.green
            )
            
            #v. start a thread where the game will be disputed, join the players in there
            thread = await interaction.channel.send(embed=embed)
            gameThread = await thread.create_thread(name=(f'{str(player1)[:-5]} -VS- {str(player2)[:-5]}'), auto_archive_duration=60, reason='Scacchi')
            await gameThread.add_user(player1)
            await gameThread.add_user(player2)
            await playerFetchMsg.delete()
            mainThreadEmbed = (thread, embed)

    #5. FINALLY, start the game
            mPrint('TEST', f'design: {gameDesign}')
            await chessBridge.loadGame(gameThread, bot, [player1, player2], mainThreadEmbed, board, gameDesign)
            #                                        #send them backwards (info on chessBrige.py) [black, white]
            await gameThread.edit(archived=True, locked=True)
            designFolder = f'{chessBridge.chessMain.gameRenderer.spritesFolder}{gameDesign}'
            if gameDesign.find('\\') != -1 or design.find('/') != -1:
                shutil.rmtree(designFolder)

@tree.command(name="chess-layout", description="Informazioni sui layout (FEN) delle scachiere")
@app_commands.choices(sub_command=[
        app_commands.Choice(name="Info", value="0"),
        app_commands.Choice(name="Render", value="1"),
        app_commands.Choice(name="Add", value="2"),
        app_commands.Choice(name="Edit", value="3"),
        app_commands.Choice(name="Remove", value="4"),
])
@app_commands.describe(sub_command="choose a subcommand")
async def chess_layout(interaction : discord.Interaction, sub_command: app_commands.Choice[str]): #, name:str=None, fen:str = None
    mPrint('CMDS', f'called /chess-layout: {sub_command.name}')
    guildID = int(interaction.guild.id)
    response = int(sub_command.value)
    botBoards = chessBridge.getBoards()
    guildBoards = settings[guildID]['chessGame']['boards']
    

    #send saved layouts
    if response == 0: 
        embed = discord.Embed(
            title = strings['bot.chess.layout.description'],
            colour = col.orange
        )
        #ii. append the global data boards to the embed
        
        value = ''
        for b in botBoards:
            value += f"**{b}**: {botBoards[b]}\n"
        embed.add_field(name = strings['bot.chess.layout.global_layouts'], value=value, inline=False)

        #iii. if guild data has boards, append them to the embed
        if settings[guildID]['chessGame']['boards'] != {}:
            guildBoards = ''
            for b in settings[guildID]['chessGame']['boards']:
                guildBoards += f"**{b}**: {settings[guildID]['chessGame']['boards'][b]}\n"
            embed.add_field(name = formatLangStr(strings['bot.chess.layout.guild_layouts'], interaction.guild.name), value=guildBoards, inline=False)
        
        #iv. send the embed
        await interaction.response.send_message(embed=embed)
        return 0

    elif response == 1: # renders a FEN and send it in chat
        choices = discord.ui.Select(options= #global layouts
            [discord.SelectOption(label=name, description=botBoards[name], value=botBoards[name]) for name in botBoards],
            placeholder=strings['bot.chess.layout.render.select']
        )
        for layout in guildBoards: #guild layouts
            choices.add_option(label=layout, description=guildBoards[layout], value=guildBoards[layout])

        view = discord.ui.View()
        view.add_item(choices)

        async def render_and_send_image(interaction : discord.Interaction):
            mPrint("TEST", choices.values)
            layoutFEN = choices.values[0]
            
            #ii. let the Engine make the image
            try:
                image = chessBridge.getBoardImgPath(layoutFEN, interaction.id)
                mPrint('DEBUG', f'got image path: {image}')
            except Exception:
                await interaction.response.send_message(strings['bot.chess.layout.render.error'])
                return -2

            if image == 'Invalid':
                await interaction.response.send_message(f"{strings['bot.chess.layout.render.invalid']} {layoutFEN}")
                return -1
            mPrint('DEBUG', f'rendered image: {image}')

            #iii. Send the image to discord
            imgpath = (f'{image[0]}')
            with open(imgpath, "rb") as fh:
                f = discord.File(fh, filename=imgpath)
            #iv. data hoarding is bad
            await interaction.response.send_message(f"{interaction.user.name} rendered board {layoutFEN}", file=f)
            try:
                os.remove(imgpath)
            except PermissionError:
                mPrint('ERROR', f'Could not delete file {imgpath}\n{traceback.format_exc()}')

            try:
                os.remove(imgpath.replace('png', 'log'))
            except PermissionError:
                mPrint('ERROR', f'Could not delete file {imgpath.replace("png", "log")}\n{traceback.format_exc()}')
            
        choices.callback = render_and_send_image
        await interaction.response.send_message(view=view, ephemeral=True)
        return 0

    elif response == 2: # adds a board in the Data
        class NewLayoutData(discord.ui.Modal, title='Inserisci un nuovo layout'):
            name = discord.ui.TextInput(label='Nome', placeholder="Name", style=discord.TextStyle.short, required=True)
            fen = discord.ui.TextInput(label='FEN', placeholder="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w - - 0 0", default="https://lichess.org/editor", style=discord.TextStyle.long, required=True)

            async def on_submit(self, interaction: discord.Interaction):
                mPrint('TEST', f"{self.name}: {self.fen}")
                if str(self.name) not in settings[guildID]['chessGame']['boards']:
                    #iii. append the board and dump the json data
                    settings[guildID]['chessGame']['boards'][str(self.name)] = str(self.fen)
                    dumpSettings()
                    await interaction.response.send_message(formatLangStr(strings['bot.chess.layout.add.done'], [str(self.name), str(self.fen)]))
                else:
                    await interaction.response.send_message(strings['bot.chess.layout.add.exists'])

        await interaction.response.send_modal(NewLayoutData())

        return

    elif response == 3: #rename a board
        # setup guild layout in choices
        choices = discord.ui.Select(options=
            [discord.SelectOption(label=name, description=guildBoards[name]) for name in guildBoards],
            placeholder=strings['bot.chess.layout.edit.select']
        )
        view = discord.ui.View()
        view.add_item(choices)

        async def edit_board(interaction : discord.Interaction): # This triggers when user selects the board to edit
            layoutname = str(choices.values[0])
            class EditLayoutData(discord.ui.Modal, title=formatLangStr(strings['bot.chess.layout.edit.title'], layoutname)):
                newfen = discord.ui.TextInput(label=f'Edit the FEN for "{layoutname}"', default=guildBoards[layoutname], style=discord.TextStyle.long, required=True)

                async def on_submit(self, interaction: discord.Interaction): #this triggers when user submits the modal with the new data
                    settings[guildID]['chessGame']['boards'][layoutname] = str(self.newfen)
                    dumpSettings()
                    await interaction.response.send_message(formatLangStr(strings['bot.chess.layout.edit.ok'], [layoutname, str(self.newfen)]))
            await interaction.response.send_modal(EditLayoutData())

        choices.callback = edit_board

        if guildBoards != {}:
            await interaction.response.send_message(view=view, ephemeral=True)
        else:
            await interaction.response.send_message(strings['bot.chess.layout.no_layouts'], ephemeral=True)
        return 0
    
    elif response == 4: #delete a board
        # setup guild layout in choices
        choices = discord.ui.Select(options=
            [discord.SelectOption(label=name, description=guildBoards[name]) for name in guildBoards],
            placeholder=strings['bot.chess.layout.delete.select']
        )
        view = discord.ui.View()
        view.add_item(choices)

        async def delete_board(interaction : discord.Interaction): # This triggers when user selects the board to edit
            layoutname = choices.values[0]
            if layoutname in settings[guildID]['chessGame']['boards']:
                fen = settings[guildID]['chessGame']['boards'].pop(layoutname)
                dumpSettings()
                await interaction.response.send_message(formatLangStr(strings['bot.chess.layout.delete.ok'], [layoutname, fen]))

        choices.callback = delete_board
        if guildBoards != {}:
            await interaction.response.send_message(view=view, ephemeral=True)
        else:
            await interaction.response.send_message(strings['bot.chess.layout.no_layouts'], ephemeral=True)
        return 0
    
@tree.command(name="chess-designs", description="Informazioni sui design delle scachiere")
@app_commands.choices(sub_command=[
        app_commands.Choice(name="Info", value="0"),
        app_commands.Choice(name="Render", value="1"),
        app_commands.Choice(name="Add", value="2"),
        app_commands.Choice(name="Edit", value="3"),
        app_commands.Choice(name="Remove", value="4"),
])
@app_commands.describe(sub_command="choose a subcommand")
async def chess_design(interaction : discord.Interaction, sub_command: app_commands.Choice[str]): #, name:str=None, fen:str = None
    mPrint('CMDS', f'called /chess-designs: {sub_command.name}')
    guildID = int(interaction.guild.id)
    response = int(sub_command.value)

    globalDesigns = chessBridge.chessMain.getDesignNames()
    guildDesigns = settings[guildID]['chessGame']['designs']

    mPrint('TEST', globalDesigns)
    mPrint('TEST', guildDesigns)

    def parseHEX(hex1, hex2) -> list: #helper function
        colors = [hex1, hex2]
        possible = ['#', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']
        for i, hex in enumerate(colors): #foreach color
            mPrint('DEBUG', f'parsing hex {hex}')
            # if it has not an # add it
            if hex[0] != '#': 
                hex = '#' + hex
            for char in hex: #check if color digits are valid
                if char.lower() not in possible:
                    return '0'
            if len(hex) == 4: #if the hex type is #fff expand it to #ffffff
                hex = f'#{hex[1]}{hex[1]}{hex[2]}{hex[2]}{hex[3]}{hex[3]}'
            if len(hex) != 7:
                return '0'
            colors[i] = hex
        return colors

    if response == 0: #show board designs
        embed = discord.Embed(
            title = 'Design disponibili: ',
            colour = col.orange
        )

        #ii. append the global data designs to the embed
        value = ''
        for b in range(len(globalDesigns)):
            value += f"{globalDesigns[b]}\n"

        embed.add_field(name = 'Design disponibili:', value=value, inline=False)

        #iii. if guild data has designs, append them to the embed
        if settings[guildID]['chessGame']['designs'] != {}:
            guildDesigns = ''
            for b in settings[guildID]['chessGame']['designs']:
                guildDesigns += f"**{b}**: {settings[guildID]['chessGame']['designs'][b]}\n"
            embed.add_field(name = f'Design di {interaction.guild.name}:', value=guildDesigns, inline=False)
        
        #iv. send the embed
        await interaction.response.send_message(embed=embed)
        return 0
        
    if response == 1: # Render and send designs
        choices = discord.ui.Select(options= #global layouts
            [discord.SelectOption(label=x, value=x) for x in globalDesigns],
            placeholder=strings['bot.chess.design.render.select']
        )
        for design in guildDesigns: #guild layouts
            choices.add_option(label=design, description=str(guildDesigns[design]), value=design)

        view = discord.ui.View()
        view.add_item(choices)

        async def render_and_send_image(interaction : discord.Interaction):
            mPrint("TEST", choices.values)
            designChoice = str(choices.values[0])
            if designChoice in settings[guildID]['chessGame']['designs']: #design exists in guildData
                colors = settings[guildID]['chessGame']['designs'][designChoice]
                designPath = chessBridge.chessMain.gameRenderer.renderBoard(colors, interaction.message.id)
                with open(designPath+'chessboard.png', "rb") as fh:
                    f = discord.File(fh, filename=(designPath + 'chessboard.png'))
                    await interaction.response.send_message(formatLangStr(strings['bot.chess.design.generated'], [interaction.user.name, str(designChoice)]), file=f)
                shutil.rmtree(designPath, ignore_errors=False, onerror=None)
                return 0

            #design does not exist in guildData, search if exists in sprites folder
            elif chessBridge.chessMain.gameRenderer.doesDesignExist(designChoice):
                design = f'{chessBridge.chessMain.gameRenderer.spritesFolder}{designChoice}/chessboard.png'
                with open(design, "rb") as fh:
                    f = discord.File(fh, filename=design)
                    await interaction.response.send_message(formatLangStr(strings['bot.chess.design.generated'], [interaction.user.name, str(designChoice)]), file=f)
            else:
                await interaction.response.send_message(strings['bot.chess.design.404'])
    
        choices.callback = render_and_send_image
        await interaction.response.send_message(view=view, ephemeral=True)
        return 0

    elif response == 2: # adds a design in guildsData
        class NewDesignData(discord.ui.Modal, title='Inserisci un nuovo Design'):
            name = discord.ui.TextInput(label='Nome', placeholder="", style=discord.TextStyle.short, required=True)
            hex1 = discord.ui.TextInput(label='Principale', placeholder="#aabbcc | #abc", style=discord.TextStyle.short, required=True, max_length=7)
            hex2 = discord.ui.TextInput(label='Secondario', placeholder="#11dd33 | #1d3", style=discord.TextStyle.short, required=True, max_length=7)

            async def on_submit(self, interaction: discord.Interaction):
                name = str(self.name)
                col1 = str(self.hex1)
                col2 = str(self.hex2)

                mPrint('TEST', f"{self.name}: {col1} {col2}")
                if name not in settings[guildID]['chessGame']['designs']:#check if already exists
                    #if not, make new design
                    #parse colors
                    colors = parseHEX(col1, col2)
                    if colors == '0':
                        await interaction.response.send_message(f"Invalid hex {col1} {col2}", ephemeral=True)
                        return -2
                    settings[guildID]['chessGame']['designs'][name] = colors
                    await interaction.response.send_message(formatLangStr(strings['bot.chess.design.add.done'], [name, colors]))
                    dumpSettings()
                    
                else:
                    await interaction.response.send_message(strings['bot.chess.design.add.exists'])

        await interaction.response.send_modal(NewDesignData())

        return

    elif response == 3: # edits a design in guildsData
        # setup guild designs in choices
        choices = discord.ui.Select(options=
            [discord.SelectOption(label=design, description=str(guildDesigns[design]), value=design) for design in guildDesigns],
            placeholder=strings['bot.chess.design.edit.select']
        )

        view = discord.ui.View()
        view.add_item(choices)

        async def edit_design(interaction : discord.Interaction): # This triggers when user selects the board to edit
            designName = choices.values[0]
            class EditDesignData(discord.ui.Modal, title=formatLangStr(strings['bot.chess.design.edit.title'], designName)):
                c1 = discord.ui.TextInput(label=f'Primary  ', default=guildDesigns[designName][0], placeholder="#aabbcc | #abc", style=discord.TextStyle.short, required=True, max_length=7)
                c2 = discord.ui.TextInput(label=f'Secondary', default=guildDesigns[designName][1], placeholder="#11dd33 | #1d3", style=discord.TextStyle.short, required=True, max_length=7)

                async def on_submit(self, interaction: discord.Interaction): #this triggers when user submits the modal with the new data
                    col1,col2 = str(self.c1), str(self.c2)
                    colors = parseHEX(col1, col2)
                    if colors == '0':
                        await interaction.response.send_message(f"Invalid hex {col1} {col2}", ephemeral=True)
                        return -2
                    #else
                    settings[guildID]['chessGame']['designs'][designName] = [col1, col2]
                    await interaction.response.send_message(formatLangStr(strings['bot.chess.design.edit.ok'], [designName, str([col1, col2])]))
            await interaction.response.send_modal(EditDesignData())

        choices.callback = edit_design

        if guildDesigns != {}:
            await interaction.response.send_message(view=view, ephemeral=True)
        else:
            await interaction.response.send_message(strings['bot.chess.design.no_designs'], ephemeral=True)
        return 0

    elif response == 4: # deletes a design in guildsData
        # setup guild designs in choices
        choices = discord.ui.Select(options=
            [discord.SelectOption(label=design, description=str(guildDesigns[design]), value=design) for design in guildDesigns],
            placeholder=strings['bot.chess.design.delete.select']
        )
        view = discord.ui.View()
        view.add_item(choices)

        async def delete_board(interaction : discord.Interaction): # This triggers when user selects the board to edit
            designname = choices.values[0]
            if designname in settings[guildID]['chessGame']['designs']:
                colors = settings[guildID]['chessGame']['designs'].pop(designname)
                dumpSettings()
                await interaction.response.send_message(formatLangStr(strings['bot.chess.design.delete.ok'], [designname, str(colors)]))

        choices.callback = delete_board
        if guildDesigns != {}:
            await interaction.response.send_message(view=view, ephemeral=True)
        else:
            await interaction.response.send_message(strings['bot.chess.design.no_layouts'], ephemeral=True)
        return 0

@tree.command(name="playlist", description="Gestisci le playlist salvate")
@app_commands.choices(sub_command=[
        app_commands.Choice(name="Info", value="0"),
        app_commands.Choice(name="Add", value="1"),
        app_commands.Choice(name="Edit", value="2"),
        app_commands.Choice(name="Remove", value="3"),
])
async def playlists(interaction : discord.Interaction, sub_command: app_commands.Choice[str]):
    mPrint('CMDS', f'called /playlist: ')
    guildID = int(interaction.guild.id)
    response = int(sub_command.value)

    savedPlaylists = settings[guildID]["musicbot"]["saved_playlists"]

    if response == 0: #send the playlist list list to user
        
        embed = discord.Embed(
            title=f"Saved playlists for {interaction.guild.name}",
            description="Puoi salvare più link in una playlist in modo da non dover rifare gli stessi comandi più volte!",
            color=col.green
        )
        for plist in settings[guildID]["musicbot"]["saved_playlists"]:
            urls=''
            for i, t in enumerate(settings[guildID]["musicbot"]["saved_playlists"][plist]):
                urls += f'**{i}**: {t}\n' 
            embed.add_field(name=plist, value=urls, inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return    

    elif response == 1:  #add a new playlist
        class NewPlaylist(discord.ui.Modal, title='Crea una nuova playlist'):
            name = discord.ui.TextInput(label='Nome', placeholder="", style=discord.TextStyle.short, required=True)
            links = discord.ui.TextInput(label='Tracce', placeholder="Inserisci i link o i nomi delle canzoni uno per riga (spotify/youtube, anche playlist)", style=discord.TextStyle.paragraph, required=True)

            async def on_submit(self, interaction: discord.Interaction):
                name = str(self.name)
                links = str(self.links).split('\n')

                mPrint('TEST', f"{name}: {links}")

                errors = ''
                tracks = []
                for x in links:
                    isUrlValid = musicBridge.evalUrl(x)

                    if isUrlValid == False:
                        errors += f"Error: Could not find song/playlist {x}\n"

                    else:
                        if "open.spotify.com" not in x and "youtube.com" not in x:
                            mPrint('MUSIC', f'Searching for user requested song: ({x})')
                            x = musicBridge.youtubeParser.searchYTurl(x)
                        tracks.append(x)

                if errors != '':
                    embed = discord.Embed(
                        title="ERRORS:",
                        description=errors,
                        color=col.error
                    )

                    if tracks == []:
                        embed.add_field(name='ERROR', value=': every song/playlist failed')
                        interaction.response.send_message(embed=embed, ephemeral=True)

                trackList = ''
                for i, t in enumerate(tracks):
                    trackList += f"\n**{i}**. {t}"

                #Save the song/playlist URL in a list of one element and inform the user
                settings[guildID]["musicbot"]["saved_playlists"][name] = tracks
                dumpSettings()

                embed = discord.Embed(
                    title = f"Playlist {name}: ",
                    description=f"{trackList}\n{errors}",
                    color = col.orange if errors == "" else col.red
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                
                return

        await interaction.response.send_modal(NewPlaylist())
        return

    elif response == 2: #edit a playlist
        # get playlists and put them in choices
        choices = discord.ui.Select(options=
            [discord.SelectOption(label=playlist, value=playlist) for playlist in savedPlaylists],
            placeholder=strings['bot.music.playlist.edit.select']
        )

        view = discord.ui.View()
        view.add_item(choices)

        async def edit_playlist(interaction : discord.Interaction): # This triggers when user selects which playlist to edit
            playlistName = str(choices.values[0])
            mPrint('TEST', f'playlist name: {playlistName}')
            class EditPlaylistData(discord.ui.Modal, title=formatLangStr(strings['bot.music.playlist.edit.title'], playlistName)):
                plists = '\n'.join(savedPlaylists[playlistName])
                links = discord.ui.TextInput(label='Tracce', placeholder="Inserisci i link o i nomi delle canzoni uno per riga (spotify/youtube, anche playlist)", default=plists, style=discord.TextStyle.paragraph, required=True)

                async def on_submit(self, interaction: discord.Interaction): #this triggers when user submits the modal with the new data
                    links = str(self.links).split('\n')
                    # this is the same as creating a new playlist

                    mPrint('TEST', f"{playlistName}: {links}")

                    errors = ''
                    tracks = []
                    for x in links:
                        isUrlValid = musicBridge.evalUrl(x)

                        if isUrlValid == False:
                            errors += f"Error: Could not find song/playlist {x}\n"

                        else:
                            if "open.spotify.com" not in x and "youtube.com" not in x:
                                mPrint('MUSIC', f'Searching for user requested song: ({x})')
                                x = musicBridge.youtubeParser.searchYTurl(x)
                            tracks.append(x)

                    if errors != '':
                        embed = discord.Embed(
                            title="ERRORS:",
                            description=errors,
                            color=col.error
                        )

                        if tracks == []:
                            await interaction.response.send_message('Error: every song/playlist failed', ephemeral=True)
                            return

                    trackList = ''
                    for i, t in enumerate(tracks):
                        trackList += f"\n**{i}**. {t}"

                    #Save the song/playlist URL in a list of one element and inform the user
                    settings[guildID]["musicbot"]["saved_playlists"][playlistName] = tracks
                    dumpSettings()

                    embed = discord.Embed(
                        title = f"Playlist {playlistName}: ",
                        description=f"{trackList}\n{errors}",
                        color = col.orange if errors == "" else col.red
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    
                    return

            await interaction.response.send_modal(EditPlaylistData())

        choices.callback = edit_playlist

        if savedPlaylists != {}:
            await interaction.response.send_message(view=view, ephemeral=True)
        else:
            await interaction.response.send_message(strings['bot.music.playlists.404'], ephemeral=True)
        return 0

    elif response == 3: #remove a playlist
        # setup guild designs in choices
        choices = discord.ui.Select(options=
            [discord.SelectOption(label=playlist, value=playlist) for playlist in savedPlaylists],
            placeholder=strings['bot.music.playlist.delete.select']
        )
        view = discord.ui.View()
        view.add_item(choices)

        async def delete_playlist(interaction : discord.Interaction): # This triggers when user selects the playlist to delete
            playlistName = str(choices.values[0])
            if playlistName in settings[guildID]["musicbot"]['saved_playlists']:
                links = settings[guildID]["musicbot"]['saved_playlists'].pop(playlistName)
                dumpSettings()
                links = "\n".join(links)
                await interaction.response.send_message(formatLangStr(strings['bot.music.playlist.delete.ok'], [playlistName, f'```{links}```']), ephemeral=True)

        choices.callback = delete_playlist
        if savedPlaylists != {}:
            await interaction.response.send_message(view=view, ephemeral=True)
        else:
            await interaction.response.send_message(strings['bot.music.playlist.404'], ephemeral=True)
        return 0

    return


@tree.command(name="player-settings", description="Regola le impostazioni del player")
@app_commands.choices(setting=[
        app_commands.Choice(name="Info", value="0"),
        app_commands.Choice(name="Shuffle", value="1"),
        app_commands.Choice(name="Precision", value="2"),
])
async def playerSettings(interaction : discord.Interaction, setting : app_commands.Choice[str], value : int = None):
    """
    :param setting: DO NOT INSERT value FOR SHUFFLE 
    """
    mPrint('CMDS', f'called /player-settings: ')
    guildID = int(interaction.guild.id)
    response = int(setting.value)

    if response == 0: #print settings
        embed = discord.Embed(
            title="MusicBot Settings",
            description="/player-settings",
            color=col.green
        )
        embed.add_field(name="Shuffle: ", value=f"{settings[guildID]['musicbot']['player_shuffle']}", inline=False)
        embed.add_field(name="Precision: ", value=f"{settings[guildID]['musicbot']['timeline_precision']} / {config.timeline_max}", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    elif response == 1: # shuffle setting
        current = bool(settings[guildID]['musicbot']["player_shuffle"])
        choices = discord.ui.Select(options=[
            discord.SelectOption(label="True", description="Il player fa il primo shuffle in automatico", value=True, default=current),
            discord.SelectOption(label="False", description="Il player riproduce le canzoni in ordine", value=False, default=(not current))
            ]
        )
        view = discord.ui.View()
        view.add_item(choices)

        async def shuffle_response(interaction : discord.Interaction):
            mPrint('TEST', f"{choices.values[0]}")
            settings[guildID]['musicbot']["player_shuffle"] = choices.values[0]
            dumpSettings()
            await interaction.response.defer()

        choices.callback = shuffle_response
        await interaction.response.send_message(view=view, ephemeral=True)

    elif response == 2: #precision
        if value == None:
            await interaction.response.send_message("Per questa impostazione devi specificare un valore nel comando", ephemeral=True)
            return
        warnmsg = ''
        newPrec = value
        if newPrec > config.timeline_max:
            newPrec = config.timeline_max
            warnmsg = f"\nTimeline max precision is {config.timeline_max}"

        if newPrec < 0:
            newPrec = 0
            warnmsg = "\nTimeline min precision is 0"
        
        settings[guildID]['musicbot']["timeline_precision"] = newPrec
        dumpSettings()
        await interaction.response.send_message(f"La nuova precisione è {newPrec}{warnmsg}", ephemeral=True)

    return
    
@tree.command(name="play", description="Riproduci qualcosa! (Youtube & Spotify)")
@app_commands.describe(tracks="URL / Title / saved playlist (/playlist)")
async def playSong(interaction : discord.Interaction, tracks : str):
    guildID = int(interaction.guild.id)

    if interaction.channel.id not in settings[guildID]['musicbot']['enabled_channels']:
        await interaction.response.send_message("This module is not enabled in this channel.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    voice_client : discord.VoiceClient = get(bot.voice_clients, guild=interaction.guild)

    #TODO improve
    if voice_client != None:
        if voice_client.is_connected():
            await interaction.followup.send('Sono già connesso in un canale vocale', ephemeral=True)
        return

    #user searched a link
    playContent = ''
    if "open.spotify.com" in tracks or "youtube.com" in tracks or "youtu.be" in tracks:
        mPrint('INFO', f'FOUND SUPPORTED URL: {tracks}')
        playContent = tracks

    #user wants a saved playlist
    elif tracks in settings[guildID]["musicbot"]["saved_playlists"]:
        trackURL_list : list = settings[guildID]["musicbot"]["saved_playlists"][tracks]
        mPrint('INFO', f'FOUND SAVED PLAYLIST: {trackURL_list}')
        playContent = trackURL_list
    
    #user wants to search for a song title
    else:
        mPrint('MUSIC', f'Searching for user requested song: ({tracks})')
        trackURL = musicBridge.youtubeParser.searchYTurl(tracks)
        mPrint('INFO', f'SEARCHED SONG URL: {trackURL}')
        playContent = trackURL
    
    overwrite,shuffle,precision = settings[guildID]['musicbot']['youtube_search_overwrite'],settings[guildID]['musicbot']["player_shuffle"],settings[guildID]['musicbot']["timeline_precision"]
    
    # interaction.response.defer()
    try:
        mPrint('TEST', f'--- playing song --- \n{playContent}')
        await musicBridge.play(playContent, interaction, bot, shuffle, precision, overwrite)
    except Exception:
        await interaction.followup.send("C'è stato un errore.", ephemeral=True)
        mPrint('ERROR', traceback.format_exc())

@tree.command(name='suggest', description="Sovrascrivi una canzone sbagliata") #Player
async def suggest(interaction : discord.Interaction):
    await interaction.response.send_message('Function is currently disabled', ephemeral=True)
    return

    await interaction.channel.typing()
    await asyncio.sleep(2) #ensure that file exists
    if os.path.isfile(f'botFiles/suggestions/{str(interaction.guild.id)}.json'):
        with open(f'botFiles/{str(interaction.guild.id)}.json') as f:
            newOverwrites = json.load(f)
            if settings[interaction.guild.id]['musicbot']['youtube_search_overwrite'] == newOverwrites:
                await interaction.channel.send('Non è cambiato niente...')
            else:
                settings[interaction.guild.id]['musicbot']['youtube_search_overwrite'] = newOverwrites
                dumpSettings()
                await interaction.channel.send('Done')
    else:
        await interaction.channel.send('C\'è stato un errore...')

@tree.command(name="ping", description="ping del bot")
async def ping(interaction : discord.Interaction):
    mPrint('CMDS', f'called /ping')

    pingms = round(bot.latency*1000)
    await interaction.response.send_message(f'Pong! {pingms}ms')
    mPrint('INFO', f'ping detected: {pingms} ms')


@tree.command(name="module-info", description="Mostra lo stato dei moduli")
@app_commands.default_permissions()
async def module_info(interaction : discord.Interaction):
    guildID = int(interaction.guild.id)
    await interaction.response.defer(ephemeral=True)

    embed=discord.Embed(
        title=f"CuloBot modules for {interaction.guild.name}",
        description="You can change this data using the command /module <module> [#channel] [enable]",
        color=col.orange
    )

    #get all guild channels
    allChannels = await interaction.guild.fetch_channels()
    #extract only the TextChannels
    allChannels:list[discord.TextChannel] = [x for x in allChannels if x.type == discord.ChannelType.text]
    allChannelsID:list[int] = [x.id for x in allChannels if x.type == discord.ChannelType.text]

    #well this is not confusing at all -.-

    responseChannels = ""
    #foreach ch in [guild enabled channels]
    for ch in settings[guildID]['responseSettings']['enabled_channels']:
        #if ch is present in the guild channel
        for guildCh in allChannels:
            if ch == guildCh.id:
                responseChannels = responseChannels + f"{guildCh.mention}\n"
                break
        #clean guildsData from no-longer existing channels:
        if ch not in allChannelsID:
            mPrint('DEBUG', f'found removed channel {ch}')
            settings[guildID]['responseSettings']['enabled_channels'].remove(ch)
    #Add N/A if string
    responseChannels = "No whitelisted channels" if responseChannels == "" else responseChannels

    chessChannels = ""
    #foreach ch in [guild enabled channels]
    for ch in settings[guildID]['chessGame']['enabled_channels']:
        #if ch is present in the guild channel
        for guildCh in allChannels:
            if ch == guildCh.id:
                chessChannels = chessChannels + f"{guildCh.mention}\n"
                break
        #clean guildsData from no-longer existing channels:
        if ch not in allChannelsID:
            mPrint('DEBUG', f'found removed channel {ch}')
            settings[guildID]['chessGame']['enabled_channels'].remove(ch)
    #Add N/A if string
    chessChannels = "No whitelisted channels" if chessChannels == "" else chessChannels

    musicChannels = ""
    #foreach ch in [guild enabled channels]
    for ch in settings[guildID]['musicbot']['enabled_channels']:
        #if ch is present in the guild channel
        for guildCh in allChannels:
            if ch == guildCh.id:
                musicChannels = musicChannels + f"{guildCh.mention}\n"
                break
        #clean guildsData from no-longer existing channels:
        if ch not in allChannelsID:
            mPrint('DEBUG', f'found removed channel {ch}')
            settings[guildID]['musicbot']['enabled_channels'].remove(ch)
    #Add N/A if string
    musicChannels = "No whitelisted channels" if musicChannels == "" else musicChannels


    embed.add_field(name="**Chat replies:**", value=responseChannels, inline=False)
    embed.add_field(name="**Chess:**", value=chessChannels, inline=False)
    embed.add_field(name="**Music Bot:**", value=musicChannels, inline=False)
    
    await interaction.followup.send(embed=embed, ephemeral=True)

@tree.command(name="module", description="Attiva/Disattiva funzioni del bot")
@app_commands.choices(modules=[
        app_commands.Choice(name="All Modules", value="0"),
        app_commands.Choice(name="Message Reply", value="1"),
        app_commands.Choice(name="Chess", value="2"),
        app_commands.Choice(name="Music", value="3"),
])
@app_commands.default_permissions()
async def module_settings(interaction : discord.Interaction, modules:app_commands.Choice[str], channel:discord.TextChannel=None, enable:bool=None):
    """
    :param channel: on which text channel (default=every channel)
    :param enable: whether to enable or disable the module
    """
    mPrint('CMDS', f'called /module: {modules.name})')
    guildID = int(interaction.guild.id)
    response = int(modules.value)
    await interaction.response.defer(ephemeral=True)

    wantedModules = ""
    if response == 0:
        wantedModules = ['responseSettings', 'chessGame', 'musicbot']
    elif response == 1:
        wantedModules = ['responseSettings']
    elif response == 2:
        wantedModules = ['chessGame']
    elif response == 3:
        wantedModules = ['musicbot']
    else:
        mPrint('ERROR', f'Invalid response "{response}" for module_settings()')
        return

    if len(wantedModules) == 1:
        module = wantedModules[0]
        if enable == None: #send info about the module
            resp = f"Module {modules.name} is enabled for:\n"
            for ch in settings[guildID][module]['enabled_channels']:
                channel = await bot.fetch_channel(ch)
                resp = resp + f"{channel.mention}\n"
            await interaction.followup.send(resp, ephemeral=True)
            return
        elif channel == None: #change setting for every channel
            if enable == True: #user wants to enable setting in every channel
                allChannels = await interaction.guild.fetch_channels()
                settings[guildID][module]['enabled_channels'] = []
                for c in allChannels:
                    if c.type == discord.ChannelType.text:
                        settings[guildID][module]['enabled_channels'].append(c.id)
                dumpSettings()
                await interaction.followup.send(f"Module {modules.name} was enabled for every channel", ephemeral=True)
            else: #user wants to disable setting in every channel
                settings[guildID][module]['enabled_channels'] = []
                dumpSettings()
                await interaction.followup.send(f"Module {modules.name} was disabled for every channel", ephemeral=True)
        else: #change setting for specific channel
            if channel.id in settings[guildID][module]['enabled_channels']: #channel was enabled
                if enable == True:
                    await interaction.followup.send(f"Module {modules.name} was already enabled for {channel.mention}", ephemeral=True)
                    pass #channel was already enabled
                else:
                    settings[guildID][module]['enabled_channels'].remove(channel.id)
                    dumpSettings()
                    await interaction.followup.send(f"Module {modules.name} is now disabled for {channel.mention}", ephemeral=True)
            else: #channel was disabled
                if enable == True:
                    settings[guildID][module]['enabled_channels'].append(channel.id)
                    dumpSettings()
                    await interaction.followup.send(f"Module {modules.name} is now enabled for {channel.mention}", ephemeral=True)
                else:
                    await interaction.followup.send(f"Module {modules.name} was already disabled for {channel.mention}", ephemeral=True)
                    pass #channel was already disabled
    else:
        if enable == None:
            await interaction.followup.send('You have to select a value for the "enable" variable when enabling/disabling every module at once.\nIf you want infos about the modules use /module-info', ephemeral=True)
            return
        try:
            allChannels = await interaction.guild.fetch_channels()
            for module in wantedModules:
                if channel == None: #change every module for every channel
                    if enable == True: #user wants to enable setting in every channel
                        settings[guildID][module]['enabled_channels'] = []
                        for ch in allChannels:
                            if ch.type == discord.ChannelType.text:
                                settings[guildID][module]['enabled_channels'].append(ch.id)
                        
                    else: #user wants to disable setting in every channel
                        settings[guildID][module]['enabled_channels'] = []
                        
                else: #change setting for specific channel
                    if channel.id in settings[guildID][module]['enabled_channels']: #channel was enabled
                        if enable == True:
                            pass #channel was already enabled
                        else:
                            settings[guildID][module]['enabled_channels'].remove(channel.id)
                            
                    else: #channel was disabled
                        if enable == True:
                            settings[guildID][module]['enabled_channels'].append(channel.id)
                            
                        else:
                            pass #channel was already disabled
            dumpSettings()
            await interaction.followup.send("Done, use /module-info if you want to see the changes\n")
        except Exception:
            mPrint('ERROR', f'0x1000\n{traceback.format_exc()}')
            await interaction.followup.send("There was an unknown error, please report this issue 0x1000", ephemeral=True)

@tree.command(name="help", description="Help")
@app_commands.choices(command=[
        app_commands.Choice(name="WIP", value="-1"),
        app_commands.Choice(name="Music", value="0"),
])
async def help(interaction : discord.Interaction, command:app_commands.Choice[str]=None):
    if command == "0":
        await interaction.response.send_message("You can see music commands here https://culobot.notlatif.com", ephemeral=True)
        return

    await interaction.response.send_message("Sorry, this section is under construction, a quick startup is using the command `/module` to enable the bot in specific chats.", ephemeral=True)


@tree.command(name="feedback", description="Send a message to the developer!")
@app_commands.choices(category=[
        app_commands.Choice(name="Bug report", value="0"),
        app_commands.Choice(name="Feature request", value="1"),
        app_commands.Choice(name="Other", value="2"),
])
async def feedback(interaction : discord.Interaction, category:app_commands.Choice[str]):
    """
    :param category: PRESS ENTER AFTER SELECTING CATEGORY
    """
    class Feedback(discord.ui.Modal, title='Invia il feedback'):
        input = discord.ui.TextInput(label="This form is anonymous", style=discord.TextStyle.long, required=True, placeholder="If you want a reply, add your name#0000 in this form")
 
        async def on_submit(self, interaction: discord.Interaction):
            now = datetime.now().strftime("[%d/%m/%y %H:%M:%S]")
            message = f"{now}-({interaction.id})\nUser submitted feedback **{category.name}**\n`{str(self.input.value)}`\n"
            try:
                if bot.dev != None:
                    await bot.dev.send(message)
            except Exception:
                await bot.dev.send(f"Someone sent a feedback: ID -> {interaction.id}")


            mPrint('INFO', message)
            with open('feedback.log', 'a') as f:
                f.writelines(message)

            await interaction.response.send_message(f'Thank you for your feedback ❤', ephemeral=True)
 
    await interaction.response.send_modal(Feedback())

    return


loadSettings()
try:
    bot.run(TOKEN)
except:
    mPrint('FATAL', f'Discord key absent or wrong. Unauthorized\n{traceback.format_exc()}')


#Birthday: 07/May/2022
