## Modules
if True:
    import discord
    import threading
    import traceback
    import os
    import sys
    import json
    import time
    import datetime
    import asyncio
    import random

    from discord.ext import commands
    import schedule

## Everything Else
if True:
    import config as cfg
    #import musicPlayer as mP
    pass
    
if True:
    TOKEN = cfg.token #gets token from config file, might change to a ConfigParser
    client = discord.Client() # Creates client

    ## Variables
    botIsOn = True #so bot can be turned on and off remotely, without having to stop the bot completley
    sendMessages = True
    errorChannel = discord.Object(id="420918104491687936") #error channel ID in my discord server so i can see the traceback of errors when i dont have access to the shell window
    awaitingRestart = False
    dontReact = []
    drtf = {}
    space = ' '
    
    ignoredModules = ['__init__', 'PointsManager']
    
    awaitingRestart = False

    points = {}
    songQueue = {}
    rewards = {}
    quotesList = {}
    commandsList = {}
    
    awaitingDuel = {}
    currentRaffles = {}
    
    bannedUsers = []
    warnUsers = []
    noDMs = []
    
    cooldowns = {}
    
    voice = None
    player = None
    # VVV list of global command names VVV
    globalCommands = [
        '!addchannel', 
        '!removechannel', 
        '!exec', 
        '!error', 
        '!sudo', 
        '!tdmbnick', 
        '!tdmbstatus', 
        '!off', 
        '!on', 
        '!ban',
        '!age', 
        '!version', 
        '!hug', 
        '!id', 
        '!settings',
        '!plugins',
        '!hostbattery'
        ]

def p(txt):
    '''Prints some text'''
    if cfg.debug:
        import inspect
        parent = inspect.stack()[1][3]
        print(parent + '(): [INFO] ' + txt)
    else:
        print('[INFO] ' + txt)
    
def dp(txt):
    '''Prints some text, but only if the bot is in debug mode'''
    if cfg.debug:
        import inspect
        parent = inspect.stack()[1][3]
        print(parent + '(): [DEBUG] ' + txt)
        
def ep(txt):
    '''Prints an error'''
    print('[ERROR] ' + txt)
    
disabledPlugins = []

class pluginManager:
    def reloadData():
        loadDisabledPlugins()
        ## TODO: Have plugins reload their data as well
        ## Must first figure out how and where to save plugin info on RAM, possibly in a return variable in a dict
        ## {"pluginName": {"dataName": DATA}}
        pass
        
    def getPlugins():
        pluginFolder = os.listdir('plugins')
        validPlugins = []
        
        
        for file in pluginFolder:
            if file.endswith('.py') or file.endswith('.pyw'):
                pluginName = file.split('.')[0]
                if pluginName in ignoredModules:
                    pass
                else:
                    validPlugins.append(pluginName)
                
        return validPlugins
        
    def saveDisabledPlugins():
        global disabledPlugins
        with open('disabledPlugins.json','w') as f:
            json.dump(disabledPlugins, f)

    def loadDisabledPlugins():
        global disabledPlugins
        with open('disabledPlugins.json') as f:
            disabledPlugins = json.load(f)
            
    def getAllCommands():
        global globalCommands
        allCommands = []
        for command in globalCommands:
            allCommands.append(command)
            
        global disabledPlugins
        for plugin in pluginManager.getPlugins():
            if plugin in disabledPlugins:
                pass
            else:
                try:
                    exec('import plugins.' + plugin + ' as pluginuse', globals())
                    for command in pluginuse.__commands__:
                        allCommands.append(command)
                except AttributeError:
                    pass
                    
        return allCommands
            
    def disableAllPlugins():
        global disabledPlugins
        plugins = []
        for plugin in pluginManager.getPlugins():
            if plugin not in disabledPlugins:
                plugins.append(plugin)
                disabledPlugins.append(plugin)
        if plugins is not []:
            pluginManager.saveDisabledPlugins()
        return plugins
                
    def enableAllPlugins():
        global disabledPlugins
        plugins = []
        for plugin in pluginManager.getPlugins():
            if plugin in disabledPlugins:
                plugins.append(disabledPlugins.pop(0))
        if plugins is not []:
            pluginManager.saveDisabledPlugins()
        return plugins
                
    async def on_message(message):
        global disabledPlugins
        global client
        for plugin in pluginManager.getPlugins():
            if plugin in disabledPlugins:
                dp('Plugin ' + plugin + ' is disabled, skipping...')
            else:
                try:
                    exec('import plugins.' + plugin + ' as pluginuse', globals())
                    try:
                        getattr(pluginuse, 'on_message')
                    except AttributeError:
                        dp('Plugin ' + plugin + ' had no funtion on_message, skipping...')
                    else:
                        pluginuse.botclient = client
                        dp('Trying plugin: ' + plugin)
                        response = await pluginuse.on_message(message)
                        if response == None:
                            break
                except ImportError as err:
                    await chat.chat(errorChannel, 'Unable to import a plugin! ' + str(err))
                    dp('Unable to import ' + plugin + ', skipping...')
                    
def getDRTMFile():
    '''Returns the list of channels to not send messages to'''
    global drtf
    
    with open('dontRespondToMessages.json') as f:
        drtf = json.load(f)
    return drtf
                
def checkStatus():
    '''Starts the Status Checker and Debugger'''
    import checkDiscordBotStatus as StatusChecker
    global client
    StatusChecker.botClient = client
    StatusChecker.cmdFunc()
    
async def pointLoop():
    '''Loop that adds points to users'''
    getPointsFile()
    p('Loaded points file. Starting loop')
    global points
    global rewards
    global botIsOn
    doPointLoop = True
    while doPointLoop:
        #dp('doPointLoop')
        if botIsOn:
            #dp('botIsOn')
            for server in client.servers:
                #dp(str(server))
                if server.id not in points:
                    points[server.id] = {}
                    points[server.id]['pointsEarned'] = 10
                    points[server.id]['currencyName'] = 'points'
                if 'pointsEarned' not in points[server.id]:
                    points[server.id]['pointsEarned'] = 10
                if 'currencyName' not in points[server.id]:
                    points[server.id]['currencyName'] = 'points'
                for member in server.members:
                    #dp(str(member))
                    if member.id not in points[server.id]:
                        points[server.id][member.id] = points[server.id]['pointsEarned']
                        p('Added ' + str(member) + ' to points list in ' + str(server))
                    else:
                        #dp(str(member.status))
                        if member.status == discord.Status.offline or member.status == discord.Status.invisible:
                            pass
                        elif member.status == discord.Status.dnd or member.status == discord.Status.do_not_disturb or member.status == discord.Status.idle:
                            if points[server.id]['pointsEarned'] == 0:
                                pass
                            elif points[server.id]['pointsEarned'] == 1:
                                points[server.id][member.id] += 1
                            else:
                                points[server.id][member.id] += math.floor(points[server.id]['pointsEarned']/2)
                                
                        elif member.status == discord.Status.online:
                            points[server.id][member.id] += points[server.id]['pointsEarned']
                        
                        else:
                            await chat.chat(errorChannel, 'User ' + member.display_name + ' has an unknown status of ' + str(member.status))
                
                        
                        
            with open('points.json', 'w') as pointDatabase:
                json.dump(points, pointDatabase)
            with open('rewards.json', 'w') as rewDb:
                json.dump(rewards, rewDb)
        await asyncio.sleep(10)
        
def getBannedUsers():
    '''Returns a list of banned users'''
    global bannedUsers
    global warnUsers
    with open('bannedUsers.json') as f:
        bannedUsers = json.load(f)
    with open('warnUsers.json') as f:
        warnUsers = json.load(f)
        
    return [bannedUsers, warnUsers]
        
class chat:
    '''Methods of sending chat messages. Emulate some of discords chat commands'''
    
    async def chat(channel, message=None, tts=False):
        if message == None:
            dp('Bot tried sending an empty message!')
        else:
            try:    
                msg = await client.send_message(channel, message, tts=tts)
                return msg
            except discord.errors.Forbidden:
                p('The bot is not allowed to send messages to this channel')
                
    async def me(channel, message):
        return await chat.chat(channel, '_' + message + '_')

    async def tableflip(channel, message):
        return await chat.chat(channel, message + ' (╯°□°）╯︵ ┻━┻')

    async def unflip(channel, message):
        return await chat.chat(channel, message + ' ┬─┬ ノ( ゜-゜ノ)')

    async def shrug(channel, message):
        return await chat.chat(channel, message + ' ¯\_(ツ)_/¯')

    async def tts(channel, message):
        return await chat.chat(channel, message, tts=True)

@client.event
async def on_member_join(member):
    #server = member.server
    #await chat.chat(member, 'Welcome to ' + str(server) + '! The server now has ' + str(server.member_count) + ' members!\nThe server uses TheDerpyMemeBot, and has a points system. You earn ' + str(point[server.id]['pointsEarned']) + ' points every 10 seconds.\nYou can also gamble points by typing !gamble <points> and you can duel a user by typing !duel <userID> <points>')
    pass
    
async def checkStreamStatus():
    return
    dp('waiting for client ready')
    await client.wait_until_ready()
    dp('client is ready, finding TitanFam...')
    for server in client.servers:
        dp('checking server ' + str(server))
        if server.id == '432199586375794688':
            dp('found Titan Fam')
            titanLive = False
            while True:
                
                if server.owner.game.type == 1:
                    if titanLive is not True:
                        titanChannel = discord.Object(id='432199856623190030')
                        await chat.chat(titanChannel, '@here Titan is now live on Twitch! www.twitch.tv/titan_unlimited')
                        titanLive = True
                        
                else:
                    titanLive = False
                
                await asyncio.sleep(60)

def restart():
    p('Restart Engaged! SOUND THE ALARMS!!!')
    global botIsOn
    global awaitingRestart
    #cfg.no
    awaitingRestart = True
    botIsOn = False
    print('Restarting computer in 60 seconds...')
    time.sleep(60)
    #await client.logout()
    os.system('shutdown /r /c \'TDMB is restarting your computer...\'')
    
@client.event
async def on_message(message):
    #if message.author.bot == True:
    #    dp('Ignoring message from bot: ' + str(message.author))
    #    return
    #else:
    #    await afterMsg(message)
    await afterMsg(message)
    
async def sudoMsg(message, author, contents):
    message.content = contents
    message.author = author
    await afterMsg(message, sudo=True)#, author, contents, True)
    
async def afterMsg(message, author=None, contents=None, sudo=False):
    if True:
        global botIsOn
        global errorChannel
        #global customCommandManagers
        #global quoteManagers ##depreciated lists
        global space
        global globalCommands
        global commandsList
        global voice
        global player
        global quotesList
        global dontReact
        global points
        global rewards
        global songQueue
        global client
        global drtf
        global awaitingDuel
        global bannedUsers
        global warnUsers
        global cooldowns
        global currentRaffles
        global disabledPlugins
        global noDMs
        
        unicode = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
    
    try:
        try:
            if message.server == None:
                print(str(message.timestamp.time()).split('.')[0] + ': ' + str(message.channel) + ' >> ' + str(message.author) + ': ' + str(message.clean_content).translate(unicode))
            else:
                print(str(message.timestamp.time()).split('.')[0] + ': [' + str(message.server) + '] #' + str(message.channel) + ' >> ' + str(message.author) + ': ' + str(message.clean_content).translate(unicode))
        except UnicodeEncodeError:
            pass
        # Prints 'TIME: [server] #channel >> sender: message' to the log
        # If private message, 'TIME: Direct Message with <Username> >> Username#0000: <message>
        
        try:
            with open("ChatLog.txt", "a") as f:
                f.write("\n")
                if message.server == None:
                    f.write(str(message.timestamp.time()).split('.')[0] + ': ' + str(message.channel) + ' >> ' + str(message.author) + ': ' + str(message.clean_content).translate(unicode))
                else:
                    f.write((str(message.timestamp.time()).split('.')[0] + ': [' + str(message.server) + '] #' + str(message.channel) + ' >> ' + str(message.author) + ': ' + str(message.clean_content)).translate(unicode))
        except UnicodeEncodeError:
            pass
            # with open('ChatLog.txt', 'a') as f:
                # if message.server == None:
                    # f.write(str(message.timestamp.time()).split('.')[0] + ': ' + str(message.channel) + ' >> ' + str(message.author) + ': a message that contians unsupported unicode characters!')
                # else:
                    # f.write((str(message.timestamp.time()).split('.')[0] + ': [' + str(message.server) + '] #' + str(message.channel) + ' >> ' + str(message.author) + ': a message that contians unsupported unicode characters!'))

        # we do not want the bot to reply to itself
        if message.author == client.user or message.author.bot:
            return
        else:
            arguments = message.content.split(' ') # splits the command at each space, so we can eaisly get each argument
            command = arguments[0].lower() # takes first argument, makes it lowercase, and stores it in a variable so we can see if the command is something we should attempt to do something with
        
        
            
        server = message.server
        leo = '304316646946897920' #this should be the only hardcoded user ID. This is my (the original bot makers) ID, so I can let myself have more control over the bot.
        isLeo = message.author.id == leo
        
        ch = message.channel
        channel = message.channel
        author = message.author
        
        
        #if author == None:
            #author = message.author
        
        #if not contents == None:
            #message.content = contents
        
        if server == None:
            isAdmin = True
            serverCurrency = None
            serverCurr = None
            isOwner = True
        else:
            if not sudo:
                isAdmin = author.server_permissions.administrator
            else:
                isAdmin = True
            isOwner = author == server.owner
            #serverCurrency = points[server.id]['currencyName']
            #serverCurr = serverCurrency
                
        
        if command == '!addchannel':
            if server == None:
                await chat.chat(message.channel, cfg.noPMcmdRes)
                return
                
            if author == server.owner or author.id == leo or isAdmin:
                if server.id in drtf:
                    if channel.id in drtf[message.server.id]:
                        drtf[message.server.id].remove(message.channel.id)
                        with open('dontRespondToMessages.json', 'w') as f:
                            json.dump(drtf, f)
                    else:
                        await chat.chat(channel, 'This channel isn\'t in the list of ignored channels!')
                else:
                    drtf[server.id] = []
                    await chat.chat(ch, 'This channel isn\'t in the list of ignored channels!')
            else:
                await chat.chat(ch, 'You don\'t have permission to use this command!')
                
        elif command == '!notdmbdms':
            if author.id in noDMs:
                noDMs.remove(author.id)
                await chat.chat(ch, 'Ok, you will resume getting DMs from me!')
            else:
                await chat.chat(ch, 'Ok, you should no longer receive DMs from me anymore! If you run this command again, you will get DMs again')
                noDMs.append(author.id)
        
        elif command == '!off': #allows me to turn the bot on and off
            if author.id == leo:
                if botIsOn:
                    await chat.chat(channel, 'Turning off bot...')
                    botIsOn = False
                else:
                    await chat.chat(channel, 'Bot is already off!')
            else:
                await chat.chat(channel, 'This isn\'t the command you are looking for...')

        elif command == '!on': #allows me to turn the bot on and off
            if message.author.id == "304316646946897920":
                if not botIsOn:
                    await chat.chat(message.channel, 'Turning on bot...')
                    botIsOn = True
                else:
                    await chat.chat(message.channel, 'Bot is already on!')
            else:
                await chat.chat(message.channel, 'This isn\'t the command you are looking for...')

        elif command == '!error': # forces a DivisionByZero error
            if message.author.id == "304316646946897920":
                await chat.chat(message.channel, 'Raising a ZeroDivisionError on request!')
                raise ZeroDivisionError('Error raised on request')
            else:
                await chat.chat(message.channel, 'This isn\'t the command you are looking for...')
                
        elif command == '!exec': # allows me to run a command in the console from anywhere, and responds with the traceback
            if message.author.id == "304316646946897920":
                todo = message.content.split(' ', 1)[1]
                try:
                    exec(todo)
                except Exception as err:
                    tb = traceback.format_exc()
                    await chat.chat(message.channel, tb)
                else:
                    await chat.chat(message.channel, 'No exception occured in running this command!')
            else:
                await chat.chat(message.channel, 'This isn\'t the command you are looking for...')
                
        elif command == '!tdmbstatus': #allows me to change the 'playing' status of the bot
            if message.author.id == "304316646946897920":
                await client.change_presence(game=discord.Game(name=message.content.split(' ', 1)[1]))
                await chat.chat(message.channel, 'Status is now: ' + message.content.split(' ', 1)[1])
            else:
                await chat.chat(message.channel, 'This isn\'t the command you are looking for...')
                
        elif command == '!tdmbnick': # Changes the bots nickname in a server
            if message.author.id == "304316646946897920":
                try:
                    arguments[1]
                except IndexError:
                    await chat.chat(message.channel, 'Did you provide a name to change to?')
                else:
                    await client.change_nickname(message.server.me, str(arguments[1]))
                    await chat.chat(message.channel, 'Changed nickname in ' + message.server.name + ' to ' + arguments[1])
            else:
                await chat.chat(message.channel, 'This isn\'t the command you are looking for...')
                
        elif command == '!sudo':
            if message.server == None:
                return
            if message.author.id == '304316646946897920':
                try:
                    arguments[1]
                except IndexError:
                    await chat.chat(message.channel, 'Did you provide a user to run a command as?')
                else:
                    try:
                        arguments[2]
                    except IndexError:
                        await chat.chat(message.channel, 'Did you provide a command to run?')
                    else:
                        sudoUser = await client.get_user_info(arguments[1])
                        newContent = ' '.join(arguments[2:])
                        #await chat.chat(ch, newContent)
                        await sudoMsg(message, sudoUser, newContent)
                        
                        #await chat.chat(message.channel, 'FIGURE THIS OUT LEO DansGame')
            else:
                await chat.chat(message.channel, 'This isn\'t the command you are looking for...')
        
        elif command == '!ban': # lets me ban users
            if author.id == leo:
                try:
                    arguments[1]
                except IndexError:
                    await chat.chat(ch, 'Who do you want to ban?')
                else:
                    try:
                        arguments[2]
                    except IndexError:
                        arguments[2] = 'ban'
                    try:
                        arguments[3]
                    except IndexError:
                        arguments[3] = 'add'
                    try:
                        res = banUser(arguments[1], arguments[2], arguments[3])
                        await chat.chat(ch, res)
                    except:
                        pass
            else:
                pass
                        
        elif botIsOn: # if the bot is on:
            commandUsed = True
            
            if command.startswith('!'):
                if author == server.owner:
                    pass
                elif author.id in bannedUsers:
                    await chat.chat(ch, 'You have been banned from using TheDerpyMemeBot commands. If you think you should not be banned, please join this discord server to appeal your ban: https://discord.gg/ypVVrR5')
                    return
                elif author.id in warnUsers:
                    await chat.chat(ch, 'Please watch how many commands you are using!')
                    warnUsers.remove(author.id)
                    
            if message.server is not None:
                #if message.server.id not in points:
                    #await addServerToPointsList(server)
                
                #if message.author.id not in points[server.id]:
                    #points[message.server.id][message.author.id] = 10
                    #print('Added ' + str(message.author) + ' to points list in ' + str(message.server))
                    
                if message.server.id in drtf:
                    if message.channel.id in drtf[message.server.id]:
                        return
                else:
                    drtf[server.id] = []
                
            if author.id not in cooldowns:
                cooldowns[author.id] = []
                
            if command == '!plugins':
                if isLeo:
                    if len(arguments) >= 3:
                        if arguments[2].lower() == 'enable':
                            if arguments[1] == 'all':
                                plugins = pluginManager.enableAllPlugins()
                                await chat.chat(ch, 'Enabled the following plugins: ' + str(pluginManager.enableAllPlugins()))
                            if arguments[1] in disabledPlugins:
                                disabledPlugins.remove(arguments[2])
                                await chat.chat(ch, 'Enabled plugin ' + arguments[2])
                            else:
                                await chat.chat(ch, 'Plugin ' + arguments[2] + ' is already active!')
                        elif arguments[2].lower() == 'disable':
                            if arguments[1].lower() == 'pluginmanager':
                                await chat.chat(ch, 'Why would you want to do that!?!')
                            elif arguments[1] == 'all':
                                plugins = pluginManager.disableAllPlugins()
                                await chat.chat(ch, 'Disabled the following plugins: ' + str(pluginManager.disableAllPlugins()))
                            elif arguments[1] == 'mainbot':
                                await chat.chat(ch, 'Ok! Are you sure you want to murder me? Kappa')
                            elif arguments[1] in disabledPlugins:
                                await chat.chat(ch, 'Plugin ' + arguments[2] + ' is already disabled!')
                            else:
                                if arguments[1].lower() in [x.lower() for x in pluginManager.getPlugins()]:
                                    disabledPlugins.append(arguments[1])
                                    await chat.chat(ch, 'Disabled ' + arguments[1])
                                else:
                                    await chat.chat(ch, 'Unable to find plugin with that name!')
                else:
                    if isAdmin or isOwner:
                        await chat.chat(ch,'per-server plugin management coming soon!')
                    else:
                        await chat.chat(ch, 'You dont have persmission to use this command [admin]')
                                
            elif command == '!id': # puts the users ID in chat. This is not a private thing that nobody should know, you can see anyones ID if you are in devolper mode
                try:
                    arguments[1]
                except IndexError:
                    await chat.chat(message.channel, '{0.author.mention}, your unique ID is {0.author.id}.'.format(message))
                else:
                    user = server.get_member_named(arguments[1])
                    if user == None:
                        await chat.chat(ch, 'Unable to find user!')
                    else:
                        await chat.chat(ch, user.display_name + '\'s unique ID is ' + user.id)
            
            elif command == '!settings': # Manages bot settings for each server.
                if message.server == None:
                    await chat.chat(ch, 'User settings coming soon! Sorry!')
                elif message.author == message.server.owner or message.author.id == leo:
                    try:
                        arguments[1]
                    except IndexError:
                        await chat.chat(message.channel, 'Did you provide a setting to change?')
                    else:
                        try:
                            arguments[2]
                        except IndexError:
                            await chat.chat(message.channel, 'Did you provide a value to change the setting to?')
                        else:
                            if arguments[1].lower() == 'autolike':
                                if arguments[2].lower() == 'false':
                                    if message.server.id not in dontReact:
                                        dontReact.append(message.server.id)
                                        await chat.chat(message.channel, 'Setting \'autolike\' is now false.')
                                    else:
                                        await chat.chat(message.channel, 'Setting \'autolike\' is already false.')
                                elif arguments[2].lower() == 'true':
                                    if message.server.id not in dontReact:
                                        dontReact.pop(message.server.id)
                                        await chat.chat(message.channel, 'Setting \'autolike\' is now true.')
                                    else:
                                        await chat.chat(message.channel, 'Setting \'autolike\' is already true.')
                            elif arguments[1].lower() == 'pointsearned':
                                try:
                                    int(arguments[2])
                                except (TypeError, ValueError):
                                    await chat.chat('That isnt a valid number!')
                                else:
                                    points[message.server.id]['pointsEarned'] = int(arguments[2])
                            elif arguments[1].lower() == 'currencyname':
                                try:
                                    str(arguments[2])
                                except (TypeError, ValueError):
                                    raise
                                else:
                                    if 'currencyName' in points[server.id]:
                                        if points[server.id]['currencyName'] == arguments[2]:
                                            await chat.chat(ch, 'The name of the currency in this server is already named that!')
                                        else:
                                            points[server.id]['currencyName'] = arguments[2]
                                            await chat.chat(ch, 'The name of the currency in this server has been updated to \'' + arguments[2] + '\'!')
                                    else:
                                        points[server.id]['currencyName'] = arguments[2]
                                        await chat.chat(ch, 'The currency name in this server has been set to \'' + arguments[2] + '\'!')
                else:
                    await chat.chat(ch, 'If you would like to change your user settings, please run this command in a DM with TDMB')
            
            elif False == True:
            # elif command == '!claimreward': ## TODO: Move into Points Commands Module!
                # if 'rewards' in cooldowns[author.id]:
                    # print('Command was on cooldown')
                    # return
                # if server == None:
                    # await chat.chat(ch, cfg.noPMcmdRes)
                    # return
                
                
                # else:
                    # cooldowns[author.id].append('rewards')
                    # try:
                        # arguments[1]
                    # except IndexError:
                        # await chat.chat(ch, 'Did you provide a reward to claim?')
                    # else:
                        # if arguments[1] in rewards[server.id]:
                            # if points[server.id][author.id] >= rewards[server.id][arguments[1]]:
                                # points[server.id][author.id] = points[server.id][author.id] - rewards[server.id][arguments[1]]
                                # await chat.chat(ch, 'Succesfully redeemed reward: ' + arguments[1] + ' for ' + str(rewards[server.id][arguments[1]]) + ' ' + points[server.id]['currencyName'] + '!')
                                # await chat.chat(server.owner, str(author) + ' redeemed reward: ' + arguments[1])
                            # else:
                                # await chat.chat(ch, 'You don\'t have enough ' + points[server.id]['currencyName'] + ' for that reward. You need ' + str(rewards[server.id][arguments[1]] - points[server.id][author.id]) + ' more points.')
                # await asyncio.sleep(5)
                # cooldowns[author.id].remove('rewards')
                
            # elif command == '!managerewards': ## TODO: Move into Points Commands module!
                # if 'rewards' in cooldowns[author.id]:
                    # print('Command was on cooldown')
                    # return
                # # arg 1 = add/del
                # # arg 2 = reward name
                # # arg 3 = reward cost
                # cooldowns[author.id].append('rewards')
                # if message.server == None:
                    # await chat.chat(message.channel, cfg.noPMcmdRes)
                # else:
                    # if author is server.owner or author.id == leo or isAdmin:
                        # if server.id in rewards:
                            # pass
                        # else:
                            # rewards[server.id] = {}
                    # else:
                        # await chat.chat(ch, 'You don\'t have permission to use this command. [admin]')
                        # return
                    # try:
                        # arguments[1]
                    # except IndexError:
                        # await chat.chat(message.channel, 'You didn\'t provide a subcommand.')
                    # else:
                        # if arguments[1].lower() in ['del', 'delete', 'remove', 'add', 'create', 'make']:
                            # pass
                        # else:
                            # await chat.chat(ch, 'That isnt a valid subcommand.')
                            # return
                        # try:
                            # arguments[2]
                        # except IndexError:
                            # await chat.chat(ch, 'Did you provide a reward name to add or remove?')
                        # else:
                            # try:
                                # cost = int(arguments[3])
                            # except (IndexError, TypeError):
                                # if arguments[1] in ['del', 'delete', 'remove']:
                                    # if arguments[2] in rewards[server.id]:
                                        # rewards[server.id].pop(arguments[2])
                                        # await chat.chat(ch, 'Removed ' + arguments[2] + ' from the rewards list.')
                                    # else:
                                        # await chat.chat(ch, 'That reward doesnt exist!')
                                # else:
                                    # await chat.chat(ch, 'Did you provide a cost for the reward?')
                            # else:
                                # if arguments[1].lower() in ['add', 'create', 'make']:
                                    # if arguments[2] in rewards[server.id]:
                                        # await chat.chat(ch, 'That reward already exists!')
                                    # else:
                                        # rewards[server.id][arguments[2]] = cost
                                        # await chat.chat(ch, 'Added ' + arguments[2] + ' to the rewards list.')
                                # elif arguments[1].lower() in ['del', 'delete', 'remove']:
                                    # if arguments[2] in rewards[server.id]:
                                        # rewards[server.id].pop(arguments[2])
                                        # await chat.chat(ch, 'Removed ' + arguments[2] + ' from the rewards list.')
                                    # else:
                                        # await chat.chat(ch, 'That reward doesnt exist!')
                # await asyncio.sleep(5)
                # cooldowns[author.id].remove('rewards')
                
            # elif command == '!duel': # sends a request to duel with someone ## TODO: Move into Points Commands Module!
                # if server == None:
                    # await chat.chat(ch, 'You lost the duel! ' + cfg.noPMcmdRes)
                # else:
                    # if not server.id in awaitingDuel:
                        # awaitingDuel[server.id] = {}
                        
                    # if author.id in awaitingDuel[server.id]:
                        # await chat.chat(ch, 'You have already requested a duel to someone in this server!')
                    # else:
                        # if awaitingRestart:
                            # await chat.chat(ch, 'The bot is preparing to restart for a patch or update, try again in a few minutes!')
                            # return
                        # try:
                            # try:
                                # int(arguments[1])
                            # except (TypeError, ValueError):
                                # duelee = server.get_member_named(arguments[1])
                                # if duelee == None:
                                    # await chat.chat(ch, 'Unable to find user!')
                                    # return
                            # else:
                                # duelee = await client.get_user_info(arguments[1])
                            # if duelee == author:
                                # raise ZeroDivisionError
                            # if duelee == client.user:
                                # raise ImportError
                        # except IndexError:
                            # await chat.chat(ch, 'Did you provide the ID of a user to duel? If you don\'t know a users ID, use !id <username>')
                        # except (discord.errors.NotFound):
                            # await chat.chat(ch, 'Unable to find user with that ID')
                        # except ZeroDivisionError:
                            # await chat.chat(ch, 'You lost the duel! You cannot duel yourself.')
                        # except ImportError:
                            # await chat.chat(ch, 'You cannot duel me! I\'ll always win')
                        # else:
                            # try:
                                # int(arguments[2])
                            # except (IndexError, TypeError, ValueError):
                                # await chat.chat(ch, 'Did you provide a number of ' + serverCurr + ' to duel over?')
                            # else:
                                # if points[server.id][author.id] >= int(arguments[2]):
                                    # for duel in awaitingDuel[server.id]:
                                        # if awaitingDuel[server.id][duel][1] == arguments[1]:
                                            # await chat.chat(ch, 'Someone else has already send this user a duel request!')
                                            # return
                                    # if int(arguments[2]) > 0:
                                        # try:
                                            # points[server.id][arguments[1]]
                                        # except IndexError:
                                            # points[server.id][arguments[1]] = 0
                                            
                                        # if points[server.id][arguments[1]] >= int(arguments[2]):
                                            # awaitingDuel[server.id][author.id] = [arguments[1], int(arguments[2])]
                                            # await chat.chat(ch, 'Requesting ' + duelee.mention + ' to duel for ' + arguments[2] + ' ' + serverCurr + '. They have 10 minutes to accept the duel using !acceptduel.')
                                            # points[server.id][author.id] -= int(arguments[2])
                                            
                                            # await chat.chat(duelee, author.display_name + ' sent you a duel request in ' + server.name + '! Go to that server and type !acceptduel to accept the duel!')
                                            
                                            # def check(msg):
                                                # return msg.content.lower().startswith('!acceptduel')
                                                
                                            # duelAcceptedMsg = await wait_for_message(timeout=600, author=duelee, channel=channel, check=check)
                                            # if duelAcceptedMsg == None:
                                                # await chat.chat(ch, author.mention + ', ' + duelee.display_name + ' did not accept the duel in time. You have gotten your ' + serverCurr + ' back!')
                                            # else:
                                                # duelFound = False
                                                # for userID in awaitingDuel[server.id]:
                                                    # if awaitingDuel[server.id][userID][0] == author.id:
                                                        # duelFound = True
                                                        # winner = random.randint(1,2)
                                                        # dueler = await client.get_user_info(userID)
                                                        # points[server.id][author.id] -= int(awaitingDuel[server.id][userID][1])
                                                        
                                                        # if winner == 1:
                                                            # points[server.id][author.id] += awaitingDuel[server.id][userID][1]*2
                                                            # await chat.chat(ch, dueler.mention + ' lost the duel against ' + author.mention + '. The winner earned ' + str(awaitingDuel[server.id][userID][1]) + ' ' + serverCurr + '!')
                                                        # else:
                                                            # points[server.id][dueler.id] += awaitingDuel[server.id][userID][1]*2
                                                            # await chat.chat(ch, dueler.mention + ' won the duel against ' + author.mention + '. The winner earned ' + str(awaitingDuel[server.id][userID][1]) + ' ' + serverCurr + '!')
                                                        # awaitingDuel[server.id].pop(userID)
                                                        # break
                                                # if duelFound == False:
                                                    # await chat.chat(ch, 'Unable to find a duel in this server you are part of.')
                                                
                                                
                                            # # await asyncio.sleep(600)
                                            # # if author.id in awaitingDuel[server.id]:
                                                # # awaitingDuel[server.id].pop(author.id)
                                                # # await chat.chat(ch, duelee.mention + ' did not accept the request in time. You have gotten your points back!')
                                                # # points[server.id][author.id] += int(arguments[2])
                                        # else:
                                            # await chat.chat(ch, duelee.display_name + ' doesnt have that many ' + serverCurr + ', they only have ' + str(points[server.id][arguments[1]]) + ' ' + serverCurr + '.')
                                    # else:
                                        # await chat.chat(ch, 'You lost the duel! You can\'t duel over negitive or zero ' + serverCurr + '!')
                                # else:
                                    # await chat.chat(ch, 'You lost the duel! You don\'t have enough ' + serverCurr + ' to duel over that much')
                    
            # elif command == '!acceptduel': # accepts a duel request if you have one. ## Todo: move to points commands
                # return
                # if server == None:
                    # await chat.chat(ch, 'You lost the duel! ' + cfg.noPMcmdRes)
                # else:
                    # duelFound = False
                    # for userID in awaitingDuel[server.id]:
                        # if awaitingDuel[server.id][userID][0] == author.id:
                            # duelFound = True
                            # winner = random.randint(1,2)
                            # dueler = await client.get_user_info(userID)
                            # points[server.id][author.id] -= int(awaitingDuel[server.id][userID][1])
                            
                            # if winner == 1:
                                # points[server.id][author.id] += awaitingDuel[server.id][userID][1]*2
                                # await chat.chat(ch, dueler.mention + ' lost the duel against ' + author.mention + '. The winner earned ' + str(awaitingDuel[server.id][userID][1]) + ' points!')
                            # else:
                                # points[server.id][dueler.id] += awaitingDuel[server.id][userID][1]*2
                                # await chat.chat(ch, dueler.mention + ' won the duel against ' + author.mention + '. The winner earned ' + str(awaitingDuel[server.id][userID][1]) + ' points!')
                            # awaitingDuel[server.id].pop(userID)
                            # break
                    # if duelFound == False:
                        # await chat.chat(ch, 'Unable to find a duel in this server you are part of.')
            
            # elif command == '!slots': ## TODO: move to points commands
                # if 'slots' in cooldowns[author.id] and not isAdmin:
                    # return
                # cooldowns[author.id].append('slots')
                # if message.server == None:
                    # await chat.chat(message.channel, cfg.noPMcmdRes)
                    # await asyncio.sleep(5)
                    # cooldowns[author.id].remove('slots')
                    # return
                # else:
                    # if server.id not in points:
                        # await addServerToPointsList(server)
                        
                    # try:
                        # slotsRisked = int(arguments[1])
                    # except IndexError:
                        # await chat.chat(ch, 'Did you provide a number of ' + serverCurr + '?')
                    # except (TypeError, IndexError):
                        # await chat.chat(ch, 'That isnt a number!')
                    # else:
                        # if author.id not in points[server.id]:
                            # points[server.id][author.id] = 0
                            # await chat.chat(ch, 'You dont have enough ' + serverCurr + '!')
                        # else:
                            # dp('points check')
                            # if points[server.id][author.id] >= slotsRisked:
                                # points[server.id][author.id] -= slotsRisked
                                # slotsVariables = ['1', '2', '3', '4', '5', '6']
                                
                                # slots1 = random.choice(slotsVariables)
                                # slots2 = random.choice(slotsVariables)
                                # slots3 = random.choice(slotsVariables)
                                
                                # if slots1 == slots2 and slots2 == slots3:
                                    # points[server.id][author.id] += slotsRisked*5
                                    # await chat.chat(ch, author.mention + ' You got | ' + str(slots1) + ' | ' + str(slots2) + ' | ' + str(slots3) + ' | and earned ' + str(slotsRisked*5) + ' ' + serverCurr + '! You now have ' + str(points[server.id][author.id]))
                                    # #win
                                # elif slots1 == slots2 or slots2 == slots3 or slots1 == slots3:
                                    # points[server.id][author.id] += slotsRisked*2
                                    # await chat.chat(ch, author.mention + ' You got | ' + str(slots1) + ' | ' + str(slots2) + ' | ' + str(slots3) + ' | and earned ' + str(slotsRisked*2) + ' ' + serverCurr + '.  You now have ' + str(points[server.id][author.id]))
                                    # #half win
                                # else:
                                    # await chat.chat(ch, author.mention + ' You got | ' + str(slots1) + ' | ' + str(slots2) + ' | ' + str(slots3) + ' | and lost your ' + serverCurr + '.  You now have ' + str(points[server.id][author.id]))
                                    # #loss
                            # else:
                                # await chat.chat(ch, 'You dont have enough ' + serverCurr + '.')
                # await asyncio.sleep(5)
                # cooldowns[author.id].remove('slots')
            
            # elif command == '!raffle': ## todo: move to points commands
                # if 'raffle' in cooldowns[author.id]:
                    # return
                # else:
                    # cooldowns[author.id].append('raffle')
                    # if server == None:
                        # await chat.chat(ch, cfg.noPMcmdRes)
                    # else:
                        # try:
                            # arguments[1]
                        # except IndexError:
                            # await chat.chat(ch, 'Did you provide an argument for the command?')
                        # else:
                            # if arguments[1].lower() == 'start':
                                # if isAdmin or isOwner:
                                    # if server.id in currentRaffles:
                                        # await chat.chat(ch, 'There is already a raffle going on in this server!')
                                    # else:
                                        # currentRaffles[server.id] = []
                                        # await chat.chat(ch, 'Starting raffle! Type !join to join the raffle!')
                                        # await chat.chat(ch, 'The raffle will end in 60 seconds!')
                                        # await asyncio.sleep(30)
                                        # await chat.chat(ch, 'The raffle will end in 30 seconds!')
                                        # await asyncio.sleep(15)
                                        # await chat.chat(ch, 'The raffle will end in 15 seconds!')
                                        # await asyncio.sleep(10)
                                        # await chat.chat(ch, 'The raffle will end in 5 seconds!')
                                        # await asyncio.sleep(5)
                                        # await chat.chat(ch, 'The raffle has ended')
                                        
                                        # if currentRaffles[server.id] == [] or None:
                                            # await chat.chat(ch, 'Nobody entered the raffle! FeelsBadMan')
                                        # else:
                                            # winner = await client.get_user_info(random.choice(currentRaffles[server.id]))
                                            # await chat.chat(ch, 'The winner is ' + winner.mention + '!')
                                            
                                # else:
                                    # await chat.chat(ch, 'You dont have permission to use this command! [permissions.administrator]')
                                        
                            # if arguments[1].lower() == 'join':
                                # if server.id in currentRaffles:
                                    # await chat.chat(ch, author.mention + 'Joining the raffle!')
                                    # currentRaffles[server.id].append(author.id)
                                    
                                    
                    # await asycnio.sleep(5)
                    # cooldowns[author.id].remove('raffle')
                    
                pass
                
            elif command == '!version': # says bot version in chat
                await chat.chat(message.channel, 'Bot Version: ' + cfg.version)
                
            elif command == '!hostbattery': # says the hosts computers batter level. Useful if hosting on a laptop, or the like
                try:
                    from plyer import battery
                    try:
                        batt = battery.status
                    except OSError:
                        await chat.chat(ch, 'Unable to get host battery information.')
                    except NotImplementedError:
                        await chat.chat(ch, 'There is no support for battery information on the host\'s OS')
                    if batt['isCharging']:
                        await chat.chat(ch, 'The host is currently charging, and is at ' + str(batt['percentage']) + '%')
                    else:
                        await chat.chat(ch, 'The host is not currently charging, and is at ' + str(batt['percentage']) + '%')
                    #await chat.chat(message.channel, 'The bots current host\'s battery state is: ' + str(battery.status))
                except ModuleNotFoundError:
                    await chat.chat(ch, 'The host computer doesnt have the required library installed to check the battery percentage')
                
            elif command == '!removechannel': # stops the bot from sending messages to the channel this was used in
                if message.server == None:
                    await chat.chat(message.channel, cfg.noPMcmdRes)
                    return
                    
                if message.server.id not in drtf:
                    drtf[message.server.id] = []
                    
                if message.author == message.server.owner or message.author.id == '304316646946897920' or message.author.server_permissions.administrator:
                    msg = await chat.chat(message.channel, 'Removing this channel from channels to respond to. This message will be deleted in 5 seconds...')
                    drtf[message.server.id].append(message.channel.id)
                    await asyncio.sleep(5)
                    await client.delete_message(msg)
                    with open('dontRespondToMessages.json', 'w') as f:
                        json.dump(drtf, f)
                else:
                    await chat.chat(ch, 'You don\'t have permission to use this command. [admin]')
                    
            elif command == '!age': # says that a user is an age between 0 and 100 years old.
                try:
                    await chat.chat(message.channel, arguments[1] + ' is ' + str(random.randint(0, 100)) + ' years old :Kappa:')
                except IndexError:
                    await chat.chat(message.channel, str(message.author) + ' is ' + str(random.randint(0, 100)) + ' years old :Kappa:')

            elif command == '!hug': # hugs someone
                try:
                    await chat.me(message.channel, 'makes ' + str(message.author) + ' hug ' + arguments[1] + '! HUGS! TwitchUnity bleedPurple <3')
                except IndexError:
                    await chat.me(message.channel, 'hugs ' + str(message.author) + '! HUGS!!!')
                
            else:
                if not await pluginManager.on_message(message):
                    if 'customCommands' not in disabledPlugins and server is not None:
                        if author.id in bannedUsers:
                            return
                        else:
                            import plugins.customCommands as cmds
                            cmd = cmds.commandManager.getCommand(server.id, command)
                        
                            if cmd is not None:
                                await chat.chat(ch, cmd)

                                #if message.server.id in dontReact:
                                    #await client.add_reaction(message, '👍')
                                    #await client.add_reaction(message, '👎')
                                    
                    
    except discord.errors.Forbidden:
        p('The bot is not allowed to send messages to this channel')
        
    except Exception as err:
        try:
            tb = traceback.format_exc()
            await chat.chat(errorChannel, '\nError in server ' + str(message.server) + '\n' + tb + '\n\nMessage:\n' + str(message.author) + ': ' + str(message.clean_content))
            await chat.chat(message.channel, 'An error occured while running this command! ' + str(err) + ' This error has been logged and will hopefully get fixed!')
        except discord.errors.Forbidden:
            p('The bot is not allowed to send messages to this channel')
    
@client.event
async def on_ready():
    if not discord.opus.is_loaded():
        p('Loading Opus...')
        discord.opus.load_opus('opus')
        p('Loaded Opus!')
    p('Logged in...')
    p('Username: ' + client.user.name)
    p('Client ID: ' + client.user.id)
    print('----------------------------------------')
    ##await chat.chat('main-chat', 'The Derpy Meme Bot version ' + cfg.version + ' is now running!')

    await client.change_presence(game=discord.Game(name=cfg.version, url='https://github.com/LeotomasMC/TheDerpyMemeBotDiscord', type=1))

    hard_coded_channel = discord.Object(id="332601647870115842") # this is the ID of a channel in TheDerpyMemeSquad, the discord server of TheDerpyMemeBot, the home of TDMB devolopment
   # await chat.chat(hard_coded_channel, 'The Derpy Meme Bot version ' + cfg.version + ' is now running!')
    print('\n')
    
    # for server in client.servers:
        # if server.id in drtf:
            # pass
        # else:
            # drtf[server.id] = []
        # if server.id not in points:
            # points[server.id] = {}
            # points[server.id]['pointsEarned'] = 1
            # dp('Added ' + str(server) + ' to the points list')
            
        # if 'currencyName' not in points[server.id]:
            # points[server.id]['currencyName'] = 'points'
        # for member in server.members:
            # if member.id not in cooldowns:
                # cooldowns[member.id] = []   
            # if member == client.user:
                # pass
            # if member.id not in points[server.id]:
                # points[server.id][member.id] = 0
                # dp('Added ' + str(member) + ' to points list in ' + str(server))

def banUser(userID, tpe='ban', way='add'):
    '''Bans a user'''
    if tpe not in ['ban', 'warn']:
        tpe = 'ban'
    if way not in ['add', 'del']:
        way = 'add'
    
    if tpe == 'ban':
        if way == 'add':
            bannedUsers.append(str(userID))
            with open('bannedUsers.json') as f:
                json.dump(bannedUsers, f)
            return 'Added user to ban list'
        else:
            bannedUsers.remove(str(userID))
            with open('bannedUsers.json') as f:
                json.dump(bannedUsers, f)
            return 'Removed user from ban list'
    else:
            if way == 'add':
                warnUsers.append(str(userID))
                with open('warnUsers.json') as f:
                    json.dump(warnUsers, f)
                return 'Added user to warn list'
            else:
                warnUsers.remove(str(userID))
                with open('warnUsers.json') as f:
                    json.dump(warnUsers, f)
                return 'Removed user from warn list'
   
def runBot():
    '''Starts the bot'''
    
    if True:
        #p('Loading TheDerpyMemeBotDiscord files...')
        #dp('\nLoading Custom Commands Database...')
        #getCustomCommands()
        #dp('Loaded Custom Commands Database!\nLoading Quotes Database...')
        #getQuotes()
        #dp('Loaded Quotes Database!\nLoading Banned Users List...')
        #getBannedUsers()
        #dp('Loaded Banned Users List!')
        
        #print('Scheduling restart command...')
        #schedule.every().day.at('00:00').do(restart)
        
        p('Loaded TheDerpyMemeBotDiscord files!\nStarting Bot...')
        
        dp('client.loop')
        #client.loop.create_task(pointLoop())
        client.loop.create_task(checkStreamStatus())
        dp('client.run')
        client.run(TOKEN)
    
if __name__ == '__main__':
    botT = threading.Thread(target=runBot)
    os.system('title ' + cfg.version)
    with open("ChatLog.txt", "a") as f:
        f.write('\n'*3 + ('='*97 + '\n')*2 + '===---+(-)' + ' '*30 + 'New TDMB Session!' + ' '*30 + '(-)+---===\n' + ('='*97 + '\n')*2)
    botT.start()