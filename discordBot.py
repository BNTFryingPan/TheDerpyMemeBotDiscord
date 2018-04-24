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
    
    customCommandManagers = ["304316646946897920", "156128628726300673"] # ids of users who can add/edit/delete custom commands
    quoteManagers = ["304316646946897920", "156128628726300673"] # people who can manage quotes, will change soon
    dontReact = []
    drtf = {}
    space = ' '

    points = {}
    songQueue = {}
    rewards = {}
    quotesList = {}
    commandsList = {}
    
    awaitingDuel = {}
    
    bannedUsers = []
    warnUsers = []
    
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
        '!quotes', 
        '!quote', 
        '!comadd', 
        '!addcom', 
        '!delcom', 
        '!comdel', 
        '!editcom', 
        '!comedit', 
        '!comhelp', 
        '!points', 
        '!gamble', 
        '!gamblepoints', 
        '!usepoints', 
        '!managerewards',
        '!claimreward',
        '!age', 
        '!version', 
        '!hug', 
        '!id', 
        '!settings', 
        '!song',
        '!duel',
        '!acceptduel',
        ]

def getDRTMFile():
    global drtf
    
    with open('dontRespondToMessages.json') as f:
        drtf = json.load(f)
        
def pointLoop():
    global points
    global rewards
    global botIsOn
    
    try:
        with open('points.json') as f:
            points = json.load(f)
        with open('rewards.json') as f:
            rewards = json.load(f)
            
    except:
        print('Error gettings Points')
        raise
        return
        
        
    else:    
        print('Loaded points file. Starting loop')
        while pointLoop:
            if botIsOn:
                for server in points:
                    for member in points[server]:
                        if member == 'pointsEarned':
                            pass
                        else:
                            points[server][member] += points[server]['pointsEarned']
                with open('points.json', 'w') as pointDatabase:
                    json.dump(points, pointDatabase)
                with open('rewards.json', 'w') as rewDb:
                    json.dump(rewards, rewDb)
            time.sleep(10)
        
class VoiceEntry:
    def __init__(self, message, player):
        self.requester = message.author
        self.channel = message.channel
        self.player = player

    def __str__(self):
        fmt = '*{0.title}*, uploaded by **{0.uploader}**, requested by **{1.display_name}**'
        duration = self.player.duration
        if duration:
            fmt = fmt + ' [length: **{0[0]}m {0[1]}s]**'.format(divmod(duration, 60))
        return fmt.format(self.player, self.requester)

class VoiceState:
    def __init__(self, bot):
        self.current = None
        self.voice = None
        self.client = client
        self.play_next_song = asyncio.Event()
        self.songs = asyncio.Queue()
        self.skip_votes = set() # a set of user_ids that voted
        self.audio_player = self.client.loop.create_task(self.audio_player_task())

    def is_playing(self):
        if self.voice is None or self.current is None:
            return False

        player = self.current.player
        return not player.is_done()

    @property
    def player(self):
        return self.current.player

    def skip(self):
        self.skip_votes.clear()
        if self.is_playing():
            self.player.stop()

    def toggle_next(self):
        self.client.loop.call_soon_threadsafe(self.play_next_song.set)

    async def audio_player_task(self):
        while True:
            self.play_next_song.clear()
            self.current = await self.songs.get()
            await self.client.send_message(self.current.channel, 'Now playing ' + str(self.current))
            self.current.player.start()
            await self.play_next_song.wait()

class Music:
    """Voice related commands.
    Works in multiple servers at once.
    """
    voice_states = {}
    bot = client
    #def __init__(self, bot):
        #self.bot = bot
        #self.voice_states = {}

    def get_voice_state(self, server):
        state = self.voice_states.get(server.id)
        if state is None:
            state = VoiceState(self.bot)
            self.voice_states[server.id] = state

        return state

    async def create_voice_client(self, channel):
        voice = await client.join_voice_channel(channel)
        state = self.get_voice_state(channel.server)
        state.voice = voice

    def __unload(self):
        for state in self.voice_states.values():
            try:
                state.audio_player.cancel()
                if state.voice:
                    self.bot.loop.create_task(state.voice.disconnect())
            except:
                pass

def getQuotes():
    global quotesList
    try:
        with open('quotes.json') as f:
            quotesList = json.load(f)
    except:
        print('error getting quotes')
        raise

def getCustomCommands():
    global commandsList
    try:
        with open("commands.json") as f:
            commandsList = json.load(f)
    except:
        print('There was a problem getting the command list FeelsBadMan [' + str(sys.exc_info()) + ']')
        raise
        
def getSongQueue():
    return
    global songQueue
    try:
        with open('songsQueue.json') as f:
            songQueue = json.load(f)
    except:
        print('There was a problem getting the songs queue FeelsBadMan [' + str(sys.exc_info()) + ']')
        raise
    else:
        return
        
def getBannedUsers():
    global bannedUsers
    global warnUsers
    with open('bannedUsers.json') as f:
        bannedUsers = json.load(f)
    with open('warnUsers.json') as f:
        warnUsers = json.load(f)
        
class chat:
    async def chat(channel, message, tts=False):
        msg = await client.send_message(channel, message, tts=tts)
        return msg

    async def me(channel, message):
        return await chat.chat(channel, '_' + message + '_')

    async def tableflip(channel, message):
        return await chat.chat(channel, message + '(╯°□°）╯︵ ┻━┻')

    async def unflip(channel, message):
        return await chat.chat(channel, message + '┬─┬ ノ( ゜-゜ノ)')

    async def shrug(channel, message):
        return await chat.chat(channel, message + '¯\_(ツ)_/¯')

    async def tts(channel, message):
        return await chat.chat(channel, message, tts=True)

@client.event
async def on_member_join(member):
    #server = member.server
    #await chat.chat(member, 'Welcome to ' + str(server) + '! The server now has ' + str(server.member_count) + ' members!\nThe server uses TheDerpyMemeBot, and has a points system. You earn ' + str(point[server.id]['pointsEarned']) + ' points every 10 seconds.\nYou can also gamble points by typing !gamble <points> and you can duel a user by typing !duel <userID> <points>')
    pass
    
async def checkStreamStatus():
    await client.wait_until_ready()
    for server in client.servers:
        while True:
            if server.id == '432199586375794688':
                if server.owner.game.type == 1:
                    if titanLive is not True:
                        titanChannel = discord.Object(id='432199586375794688')
                        await chat.chat(titanChannel, 'Titan is now live on Twitch!')
                        titanLive = True
                        
                else:
                    titanLive = False
                
                time.sleep(60)

@client.event
async def on_message(message):
    global botIsOn
    global errorChannel
    global customCommandManagers
    global quoteManagers
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
            with open('ChatLog.txt', 'a') as f:
                if message.server == None:
                    f.write(str(message.timestamp.time()).split('.')[0] + ': ' + str(message.channel) + ' >> ' + str(message.author) + ': a message that contians unsupported unicode characters!')
                else:
                    f.write((str(message.timestamp.time()).split('.')[0] + ': [' + str(message.server) + '] #' + str(message.channel) + ' >> ' + str(message.author) + ': a message that contians unsupported unicode characters!'))

        # we do not want the bot to reply to itself
        if message.author == client.user:
            return
        else:
            arguments = message.content.split(' ') # splits the command at each space, so we can eaisly get each argument
            command = arguments[0].lower() # takes first argument, makes it lowercase, and stores it in a variable so we can see if the command is something we should attempt to do something with
        
        
        server = message.server
        leo = '304316646946897920'
        author = message.author
        ch = message.channel
        channel = message.channel
        
        if server == None:
            isAdmin = True
        else:
            isAdmin = author.server_permissions.administrator
        
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
                        await chat.chat(message.channel, 'FIGURE THIS OUT LEO DansGame')
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
                    
            if message.server == None:
                pass
            else:
                if message.server.id not in points:
                    points[message.server.id] = {'pointsEarned': 1}
                    print('Added ' + str(message.server) + ' to points list')
                
                if message.author.id not in points[server.id]:
                    points[message.server.id][message.author.id] = 0
                    print('Added ' + str(message.author) + ' to points list in ' + str(message.server))
                    
                if message.server.id in drtf:
                    if message.channel.id in drtf[message.server.id]:
                        return
                else:
                    drtf[server.id] = []
                
            if author.id in cooldowns:
                pass
            else:
                cooldowns[author.id] = []
                                
            if command == '!id': # puts the users ID in chat. This is not a private thing that nobody should know, you can see anyones ID if you are in devolper mode
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
                    await chat.chat(message.channel, cfg.noPMcmdRes)
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
                            if arguments[1].lower() == 'pointsEarned':
                                try:
                                    int(arguments[2])
                                except TypeError:
                                    await chat.chat('That isnt a valid number!')
                                else:
                                    points[message.server.id]['pointsEarned'] = int(arguments[2])
                else:
                    await chat.chat(message.channel, 'You don\'t have permission to use this command! [owner]')
            
            elif command == '!claimreward':
                if 'rewards' in cooldowns[author.id]:
                    print('Command was on cooldown')
                    return
                if server == None:
                    await chat.chat(ch, cfg.noPMcmdRes)
                    return
                
                
                else:
                    cooldowns[author.id].append('rewards')
                    try:
                        arguments[1]
                    except IndexError:
                        await chat.chat(ch, 'Did you provide a reward to claim?')
                    else:
                        if arguments[1] in rewards[server.id]:
                            if points[server.id][author.id] >= rewards[server.id][arguments[1]]:
                                points[server.id][author.id] = points[server.id][author.id] - rewards[server.id][arguments[1]]
                                await chat.chat(ch, 'Succesfully redeemed reward: ' + arguments[1] + ' for ' + str(rewards[server.id][arguments[1]]) + ' points!')
                                await chat.chat(server.owner, str(author) + ' redeemed reward: ' + arguments[1])
                            else:
                                await chat.chat(ch, 'You don\'t have enough points for that reward. You need ' + str(rewards[server.id][arguments[1]] - points[server.id][author.id]) + ' more points.')
                await asyncio.sleep(5)
                cooldowns[author.id].remove('rewards')
                
            elif command == '!managerewards':
                if 'rewards' in cooldowns[author.id]:
                    print('Command was on cooldown')
                    return
                # arg 1 = add/del
                # arg 2 = reward name
                # arg 3 = reward cost
                cooldowns[author.id].append('rewards')
                if message.server == None:
                    await chat.chat(message.channel, cfg.noPMcmdRes)
                else:
                    if author is server.owner or author.id == leo or isAdmin:
                        if server.id in rewards:
                            pass
                        else:
                            rewards[server.id] = {}
                    else:
                        await chat.chat(ch, 'You don\'t have permission to use this command. [admin]')
                        return
                    try:
                        arguments[1]
                    except IndexError:
                        await chat.chat(message.channel, 'You didn\'t provide a subcommand.')
                    else:
                        if arguments[1].lower() in ['del', 'delete', 'remove', 'add', 'create', 'make']:
                            pass
                        else:
                            await chat.chat(ch, 'That isnt a valid subcommand.')
                            return
                        try:
                            arguments[2]
                        except IndexError:
                            await chat.chat(ch, 'Did you provide a reward name to add or remove?')
                        else:
                            try:
                                cost = int(arguments[3])
                            except (IndexError, TypeError):
                                if arguments[1] in ['del', 'delete', 'remove']:
                                    if arguments[2] in rewards[server.id]:
                                        rewards[server.id].pop(arguments[2])
                                        await chat.chat(ch, 'Removed ' + arguments[2] + ' from the rewards list.')
                                    else:
                                        await chat.chat(ch, 'That reward doesnt exist!')
                                else:
                                    await chat.chat(ch, 'Did you provide a cost for the reward?')
                            else:
                                if arguments[1].lower() in ['add', 'create', 'make']:
                                    if arguments[2] in rewards[server.id]:
                                        await chat.chat(ch, 'That reward already exists!')
                                    else:
                                        rewards[server.id][arguments[2]] = cost
                                        await chat.chat(ch, 'Added ' + arguments[2] + ' to the rewards list.')
                                elif arguments[1].lower() in ['del', 'delete', 'remove']:
                                    if arguments[2] in rewards[server.id]:
                                        rewards[server.id].pop(arguments[2])
                                        await chat.chat(ch, 'Removed ' + arguments[2] + ' from the rewards list.')
                                    else:
                                        await chat.chat(ch, 'That reward doesnt exist!')
                await asyncio.sleep(5)
                cooldowns[author.id].remove('rewards')
                
            elif command == '!gamblepoints' or command == '!gamble': # Gambles points
                if 'gamble' in cooldowns[author.id]:
                    return
                    
                if message.server == None:
                    await chat.chat(message.channel, cfg.noPMcmdRes)
                    return
                    
                try:
                    gambling = int(arguments[1])
                except IndexError:
                    await chat.chat(message.channel, 'You didn\'t give a number of points to gamble.')
                except TypeError:
                    await chat.chat(ch, 'That isn\'t a number!')
                except ValueError:
                    await chat.chat(ch, 'That isn\'t a number!')
                else:
                    if gambling <= points[message.server.id][message.author.id]:
                        if gambling >= 1:
                            cooldowns[author.id].append('gamble')
                            await chat.chat(message.channel, 'Gambling ' + str(gambling) + ' points...')
                            points[message.server.id][message.author.id] -= gambling
                            
                            result = random.randint(0,11)
                            if result in [1,2,3,4,5]:
                                await asyncio.sleep(5)
                                await chat.chat(message.channel, message.author.mention + ' You lost ' + str(gambling) + ' points from gambling. You now have ' + str(points[message.server.id][message.author.id]) + ' points! Don\'t get too greedy!')
                            elif result in [11]:
                                await asyncio.sleep(5)
                                points[message.server.id][message.author.id] += gambling * 10
                                await chat.chat(message.channel, message.author.mention + ' You earned ' + str(gambling * 10) + ' points from gambling. You now have ' + str(points[message.server.id][message.author.id]) + ' points! Don\'t get too greedy!')
                            else:
                                await asyncio.sleep(5)
                                points[message.server.id][message.author.id] += gambling * 2
                                await chat.chat(message.channel, message.author.mention + ' You earned ' + str(gambling) + ' points from gambling. You now have ' + str(points[message.server.id][message.author.id]) + ' points! Don\'t get too greedy!')
                            
                            
                            await asyncio.sleep(1)
                            if 'gamble' in cooldowns[author.id]:
                                cooldowns[author.id].remove('gamble')
                        else:
                            await chat.chat(message.channel, 'You can\'t bet zero or negitive points')
                    else:
                        await chat.chat(message.channel, 'You don\'t have that many points! You need ' + str(gambling-points[message.server.id][message.author.id]) + ' more points to gamble that amount.')
            
            elif command == '!duel': # sends a request to duel with someone
                if server == None:
                    await chat.chat(ch, 'You lost the duel! ' + cfg.noPMcmdRes)
                else:
                    if not server.id in awaitingDuel:
                        awaitingDuel[server.id] = {}
                        
                    if author.id in awaitingDuel[server.id]:
                        await chat.chat(ch, 'You have already requested a duel to someone in this server!')
                    else:
                        if awaitingRestart:
                            await chat.chat(ch, 'The bot is preparing to restart for a patch or update, try again in a few minutes!')
                            return
                        try:
                            int(arguments[1])
                            duelee = await client.get_user_info(arguments[1])
                            if duelee == author:
                                raise ZeroDivisionError
                            if duelee == client.user:
                                raise ImportError
                        except (IndexError, TypeError, ValueError):
                            await chat.chat(ch, 'Did you provide the ID of a user to duel? If you don\'t know a users ID, use !id <username>')
                        except (discord.errors.NotFound):
                            await chat.chat(ch, 'Unable to find user with that ID')
                        except ZeroDivisionError:
                            await chat.chat(ch, 'You lost the duel! You cannot duel yourself.')
                        except ImportError:
                            await chat.chat(ch, 'You cannot duel me! I\'ll always win')
                        else:
                            try:
                                int(arguments[2])
                            except (IndexError, TypeError, ValueError):
                                await chat.chat(ch, 'Did you provide a number of points to duel over?')
                            else:
                                if points[server.id][author.id] >= int(arguments[2]):
                                    for duel in awaitingDuel[server.id]:
                                        if awaitingDuel[server.id][duel][1] == arguments[1]:
                                            await chat.chat(ch, 'Someone else has already send this user a duel request!')
                                            return
                                    if int(arguments[2]) > 0:
                                        try:
                                            points[server.id][arguments[1]]
                                        except IndexError:
                                            points[server.id][arguments[1]] = 0
                                            
                                        if points[server.id][arguments[1]] >= int(arguments[2]):
                                            awaitingDuel[server.id][author.id] = [arguments[1], int(arguments[2])]
                                            await chat.chat(ch, 'Requesting ' + duelee.mention + ' to duel for ' + arguments[2] + ' points. They have 10 minutes to accept the duel using !acceptduel.')
                                            points[server.id][author.id] -= int(arguments[2])
                                            
                                            await chat.chat(duelee, author.display_name + ' sent you a duel request in ' + server.name + '! Go to that server and type !acceptduel to accept the duel!')
                                            
                                            await asyncio.sleep(600)
                                            if author.id in awaitingDuel[server.id]:
                                                awaitingDuel[server.id].pop(author.id)
                                                await chat.chat(ch, duelee.mention + ' did not accept the request in time. You have gotten your points back!')
                                                points[server.id][author.id] += int(arguments[2])
                                        else:
                                            await chat.chat(ch, duelee.display_name + ' doesnt have that many points, they only have ' + str(points[server.id][arguments[1]]) + ' points.')
                                    else:
                                        await chat.chat(ch, 'You lost the duel! You can\'t duel over negitive or zero points')
                                else:
                                    await chat.chat(ch, 'You lost the duel! You don\'t have enough points to duel over that much')
                    
            elif command == '!acceptduel': # accepts a duel request if you have one.
                if server == None:
                    await chat.chat(ch, 'You lost the duel! ' + cfg.noPMcmdRes)
                else:
                    duelFound = False
                    for userID in awaitingDuel[server.id]:
                        if awaitingDuel[server.id][userID][0] == author.id:
                            duelFound = True
                            winner = random.randint(1,2)
                            dueler = await client.get_user_info(userID)
                            points[server.id][author.id] -= int(awaitingDuel[server.id][userID][1])
                            
                            if winner == 1:
                                points[server.id][author.id] += awaitingDuel[server.id][userID][1]*2
                                await chat.chat(ch, dueler.mention + ' lost the duel against ' + author.mention + '. The winner earned ' + str(awaitingDuel[server.id][userID][1]) + ' points!')
                            else:
                                points[server.id][dueler.id] += awaitingDuel[server.id][userID][1]*2
                                await chat.chat(ch, dueler.mention + ' won the duel against ' + author.mention + '. The winner earned ' + str(awaitingDuel[server.id][userID][1]) + ' points!')
                            awaitingDuel[server.id].pop(userID)
                            break
                    if duelFound == False:
                        await chat.chat(ch, 'Unable to find a duel in this server you are part of.')
                        
            elif command == '!points': # get the points of a user, or sets the points of another user.
                if 'points' in cooldowns[author.id]:
                    return
                    
                if message.server == None:
                    await chat.chat(message.channel, cfg.noPMcmdRes)
                    return
                    
                cooldowns[author.id].append('points')
                try:
                    arguments[1]
                except IndexError:
                    try:
                        if points[server.id][author.id] > 1000000000:
                            await chat.chat(message.channel, message.author.mention + ' has ' + str(points[message.server.id][message.author.id]) + ' points! They are currently level ' + str(int(points[server.id][author.id]/1000)) + '! https://www.youtube.com/watch?v=9Deg7VrpHbM')
                        else:
                            await chat.chat(message.channel, message.author.mention + ' has ' + str(points[message.server.id][message.author.id]) + ' points! They are currently level ' + str(int(points[server.id][author.id]/1000)) + '!')
                    except:
                        try:
                            points[message.server.id]
                        except:
                            points[message.server.id] = {}
                            points[message.server.id][message.author.id] = 0
                            await chat.chat(message.channel, message.author.mention + ' has 0 points! They are currently level 0!')
                        else: 
                            points[message.server.id][message.author.id] = 0
                            await chat.chat(message.channel, message.author.mention + ' has 0 points! They are currently level 0!')
                else:
                    if arguments[1] == 'set':
                        if message.author == message.server.owner or message.author.id == "304316646946897920" or isAdmin:
                            try:
                                arguments[2]
                            except IndexError:
                                await chat.chat(message.channel, 'Did you provide a user id to set the points of?')
                                return
                            else:
                                try:
                                    int(arguments[2])
                                except (TypeError, ValueError):
                                    await chat.chat(message.channel, 'Invalid user ID!')
                                    return
                                else:
                                    try:
                                        newPoints = int(arguments[3])
                                    except IndexError:
                                        await chat.chat(message.channel, 'Did you provide a number of points?')
                                    except ValueError:
                                        await chat.chat(ch, 'That isnt a number!')
                                    else:
                                        try:
                                            points[message.server.id]
                                        except IndexError:
                                            points[message.server.id] = {}
                                        points[message.server.id][arguments[2]] = newPoints
                                        user = await client.get_user_info(arguments[2])
                                        await chat.chat(message.channel, 'User ' + user.mention + ' now has ' + str(points[message.server.id][arguments[2]]) + ' points!')
                        else:
                            await chat.chat(ch, 'You don\'t have permission to use this command. [admin]')
                    elif arguments[1] == 'send':
                        try:
                            int(arguments[2])
                        except IndexError:
                            await chat.chat(ch, 'Did you provide a user to send points to?')
                        except ValueError:
                            await chat.chat(ch, 'That isnt a valid user ID')
                        else:
                            try:
                                int(arguments[3])
                            except IndexError:
                                await chat.chat(ch, 'Did you provide an amount of points to give?')
                            except ValueError:
                                await chat.chat(ch, 'That isnt a valid number!')
                            else:
                                receiver = server.get_member(arguments[2])
                                if receiver == None:
                                    await chat.chat(ch, 'There is no user in this server with that ID')
                                else:
                                    if receiver.id in points[server.id]:
                                        pass
                                    else:
                                        points[server.id][receiver.id] = 0
                                        
                                    if points[server.id][author.id] >= int(arguments[3]):
                                        points[server.id][author.id] -= int(arguments[3])
                                        points[server.id][arguments[2]] += int(arguments[3])
                                        await chat.chat(ch, author.mention + ' gave ' + arguments[3] + ' points to ' +  receiver.mention)
                                    else:
                                        await chat.chat(ch, 'You don\'t have that many points to give!')
                    else:
                        try:
                            int(arguments[1])
                        except IndexError:
                            await chat.chat(message.channel, 'Did you provide a user id to get the points of?')
                            return
                        except ValueError:
                            await chat.chat(message.channel, 'That isnt a valid user ID!')
                        else:
                            user = server.get_member(arguments[1])
                            if user == None:
                                await chat.chat(ch, 'Couldn\'t find the user with that ID.')
                            else:
                                if user.id in points[server.id]:
                                    await chat.chat(message.channel, 'User ' + user.mention + ' has ' + str(points[message.server.id][user.id]) + ' points!' + 'They are currently level ' + str(int(points[server.id][user.id]/1000)) + '!')
                                else:
                                    points[server.id][user.id] = 0
                                    await chat.chat(ch, 'User ' + user.mention + ' has 0 points! They are currently level ' + str(int(points[server.id][user.id]/1000)) + '!')
                await asyncio.sleep(5)
                cooldowns[author.id].remove('points')
                
            elif command == '!song': # plays a song in the voice channel that the user is in.
                #client.delete_message(message)
                if message.server == None:
                    await chat.chat(message.channel, cfg.noPMcmdRes)
                    return
                else:
                    self = Music
                    state = self.get_voice_state(Music, message.server)
                    try:
                        arguments[1]
                    except IndexError:
                        await chat.chat(message.channel, 'Did you provide any arguments?')
                        return
                    if arguments[1].lower() == 'join':
                        try:
                            await Music.create_voice_client(message.author.voiceChannel)
                        except discord.ClientException:
                            await chat.chat(message.channel, 'Already in a voice channel...')
                        except discord.InvalidArgument:
                            await chat.chat(message.channel, 'This is not a voice channel...')
                        else:
                            await chat.chat(message.channel, 'Ready to play audio in ' + message.author.voiceChannel)

                    elif arguments[1].lower() == 'queue':
                        #print(state.songs)
                        await chat.chat(message.channel, 'Queue Entries: \n' + state.songs)


                    elif arguments[1].lower() == 'summon':
                        """Summons the bot to join your voice channel."""
                        summoned_channel = message.author.voice_channel
                        if summoned_channel is None:
                            await chat.chat(message.channel, 'You are not in a voice channel.')
                            return

                        if state.voice is None:
                            state.voice = await client.join_voice_channel(summoned_channel)
                        else:
                            await state.voice.move_to(summoned_channel)

                        return

                    elif arguments[1].lower() == 'play':
                        """Plays a song. If there is a song currently in the queue, then it isqueued until the next song is done playing.This command automatically searches as well from YouTube.The list of supported sites can be found here:
                        https://rg3.github.io/youtube-dl/supportedsites.html"""
                        opts = {
                            'default_search': 'auto',
                            'quiet': True,
                            }
                        try:
                            points[message.server.id][message.author.id]
                        except IndexError:
                            try:
                                points[message.server.id]
                            except IndexError:
                                points[message.server.id] = {}
                            
                            points[message.server.id][message.author.id] = 0
                            
                            await chat.chat(message.channel, message.author.mention + ' You do not have enough points to request a song! You need 100 points, you have 0 points')
                            return
                        else:
                            if points[message.server.id][message.author.id] >= 100:
                                pass
                            else:
                                await chat.chat(message.channel, message.author.mention + ' You do not have enough points to request a song! You need 100 points, you have ' + str(points[message.server.id][message.author.id]))
                                return
                        try:
                            arguments[2]
                        except IndexError:
                            await chat.chat(message.channel, 'Did you provide a song to listen to?')
                            return

                        summoned_channel = message.author.voice_channel
                        if summoned_channel is None:
                            await chat.chat(message.channel, 'You are not in a voice channel.')
                            return

                        if state.voice is None:
                            state.voice = await client.join_voice_channel(summoned_channel)
                        else:
                            await state.voice.move_to(summoned_channel)

                        try:
                            player = await state.voice.create_ytdl_player(arguments[2], ytdl_options=opts, after=state.toggle_next)
                        except Exception as e:
                            fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
                            await client.send_message(message.channel, fmt.format(type(e).__name__, e))
                        else:
                            player.volume = 0.6
                            entry = VoiceEntry(message, player)
                            await chat.chat(message.channel, 'Enqueued ' + str(entry) + '. You now have ' + str(points[message.server.id][message.author.id] - 100) + ' points left.')
                            await state.songs.put(entry)
                            points[message.server.id][message.author.id] -= 100

                    elif arguments[1].lower() == 'volume':
                        """Sets the volume of the currently playing song."""
                        
                        try:
                            arguments[2]
                        except IndexError:
                            await chat.chat('You didnt provide a volume level')
                            return

                        if state.is_playing():
                            player = state.player
                            player.volume = arguments[2] / 100
                            await chat.chat(message.channel, 'Set the volume to {:.0%}'.format(player.volume))

                    elif arguments[1].lower() == 'pause':
                        """Pauses the currently played song."""
                        if state.is_playing():
                            player = state.player
                            player.pause()

                    elif arguments[1].lower() == 'resume':
                        """Resumes the currently played song."""
                        if state.is_playing():
                            player = state.player
                            player.resume()

                    elif arguments[1].lower() == 'stop':
                        """Stops playing audio and leaves the voice channel. This also clears the queue."""
                        server = message.server

                        if state.is_playing():
                            if author == server.owner or isAdmin:
                                player = state.player
                                player.stop()
                                await chat.chat(ch, 'Stopped playing music in this server.')
                            else:
                                await chat.chat(ch, 'You don\'t have permission to use this command. [admin]')
                        else:
                            await chat.chat(ch, 'The bot is not currently playing music in any voice channel on this server.')
                            return

                        try:
                            state.audio_player.cancel()
                            del self.voice_states[message.server.id]
                            await state.voice.disconnect()
                        except:
                            pass


                    elif arguments[1].lower() == 'skip':
                        """Vote to skip a song. The song requester can automatically skip. 3 skip votes are needed for the song to be skipped."""

                        if not state.is_playing():
                            await chat.chat(message.channel, 'Not playing any music right now...')
                            return

                        voter = message.author
                        if voter == state.current.requester:
                            await chat.chat(message.channel, 'Requester requested skipping song...')
                            state.skip()
                        elif voter.id not in state.skip_votes:
                            if points[message.server.id][message.author.id] >= 15:
                                state.skip_votes.add(voter.id)
                                total_votes = len(state.skip_votes)
                                if total_votes >= 3:
                                    await chat.chat(message.channel, 'Skip vote passed, skipping song...')
                                    state.skip()
                                else:
                                    await chat.chat(message.channel, 'Skip vote added, currently at [{}/3]'.format(total_votes))
                            else:
                                await chat.chat(message.channel, 'You need at least 15 points to skip vote a song. You have {} points'.format(points[message.server.id][message.author.id]))
                        else:
                            await chat.chat(message.channel, 'You have already voted to skip this song.')

                    elif arguments[1].lower() == 'playing':
                        """Shows info about the currently played song."""

                        if state.current is None:
                            await chat.chat(message.channel, 'Not playing anything.')
                        else:
                            skip_count = len(state.skip_votes)
                            await chat.chat(message.channel, 'Now playing {} [skips: {}/3]'.format(state.current, skip_count))
                            
            elif command == '!version': # says bot version in chat
                await chat.chat(message.channel, 'Bot Version: ' + cfg.version)
                
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

            elif command == '!comhelp': # help for custom commands
                await chat.chat(message.channel, 'You can use "{user}" and it will mention the user who sends the message, and "{time}" will put the time the users message was sent')

            elif command == '!addcom' or command == '!comadd': # adds a custom command
                if message.server == None:
                    await chat.chat(message.channel, cfg.noPMcmdRes)
                    return
                if message.author.id in customCommandManagers or message.author == message.server.owner or message.author.server_permissions.administrator:
                    if message.content.count(space) >= 2:
                        try:
                            newargs = arguments[2:]
                            output = ' '.join(newargs)

                            commandadd = arguments[1]
                            answer = output

                            if commandadd in globalCommands:
                                await chat.chat(message.channel, 'You can\'t add that command, as it is already a global TDMB command')
                            else:
                                try:
                                    commandsList[str(message.server.id)][commandadd]
                                except KeyError:
                                    try:
                                        commandsList[str(message.server.id)]
                                    except KeyError:
                                        commandsList[str(message.server.id)] = {}
                                    commandsList[str(message.server.id)][commandadd] = answer
                                    await chat.chat(message.channel, 'The command, ' + commandadd + ' has been added')
                                    with open("commands.json", "w") as commandsDatabase:
                                        json.dump(commandsList, commandsDatabase)
                        except IndexError:
                            await chat.chat(message.channel, '[ERROR] Did you use the command the right way? !addcom <commandTrigger> <output>')
                            if debug == true:
                                await chat.chat(str(sys.exc_info()[0]))

                else:
                    await chat.chat(message.channel, 'You don\'t have permission to use that command! [admin]')

            elif command == '!delcom' or command == '!comdel': # removes a custom command
                if message.server == None:
                    await chat.chat(message.channel, cfg.noPMcmdRes)
                    return
                if author.id in customCommandManagers or author == server.owner or isAdmin:
                    if message.content.count(space) == 1:
                        try:
                            commanddel = arguments[1]
                            blab = 0

                        except IndexError:
                            await chat.chat(message.channel, 'Did you use the command the right way?')
                            blab = 1
                            if debug == true:
                                await chat.chat(message.channel, str(sys.exc_info()[0]))

                        if blab == 0:
                            if commanddel in globalCommands:
                                await chat.chat(message.channel, 'You can\'t delete a global command')
                            else:
                                try:
                                    print(str(commandsList[str(message.server.id)][commanddel]))
                                except KeyError:
                                    await chat.chat(message.channel, 'You cannot delete a command that doesn\'t exist')
                                    blab = 1

                                if blab == 0:
                                    del commandsList[str(message.server.id)][commanddel]
                                    await chat.chat(message.channel, 'Command Deleted.')
                                    with open("commands.json","w") as commandsDatabase:
                                        json.dump(commandsList, commandsDatabase)
                else:
                    await chat.chat(message.channel, 'You don\'t have permission to use that command! [admin]')

            elif command == '!editcom' or command == '!comedit': # edits a custom command
                if message.server == None:
                    await chat.chat(message.channel, cfg.noPMcmdRes)
                    return
                if message.author.id in customCommandManagers or message.author == message.server.owner or message.author.server_permissions.administrator:
                    if message.content.count(space) >= 2:
                        try:
                            newargs = arguments[2:]
                            output = ' '.join(newargs)

                            commandedit = arguments[1]
                            answer = output

                            if commandedit in globalCommands:
                                await chat.chat(message.channel, 'You can\'t edit global commands')
                            else:
                                try:
                                    commandsList[str(message.server.id)][commandedit] = answer
                                    await chat.chat(message.channel, 'The command, ' + commandedit + ' has been edited')
                                    with open("commands.json", "w") as commandsDatabase:
                                        json.dump(commandsList, commandsDatabase)
                                except KeyError:
                                    await chat.chat(message.channel, 'That command doesnt exist.')

                        except IndexError:
                            blab = 1
                            await chat.chat(message.channel, 'Did you use the command the right way? !editcom <commandTrigger> <output>')
                            if debug == true:
                                await chat.chat(message.channel, str(sys.exc_info()[0]))

                else:
                    await chat.chat(message.channel, 'You don\'t have permission to use that command!')

            elif command == '!quotes' or command == '!quote': # manages quotes
                if 'quotes' in cooldowns[author.id]:
                    return
                if message.server == None:
                    await chat.chat(message.channel, 'This command cannot be used in Private Messages')
                    return
                
                cooldowns[author.id].append('quotes')
                try:
                    quotesList[str(message.server.id)]
                except KeyError:
                    quotesList[str(message.server.id)] = {}

                try:
                    if arguments[1].lower() == 'add':
                        if message.author.id in quoteManagers or message.author == message.server.owner or message.author.server_permissions.administrator:
                            try:
                                newargs = arguments[2:]
                                newQuote = ' '.join(newargs)

                                loop = True
                                while loop == True:
                                    quoteNumber = 1
                                    try:
                                        quotesList[message.server.id][str(quoteNumber)]

                                        quoteNumber += 1
                                    except KeyError:
                                        quoteNumber = str(quoteNumber)
                                        loop = False

                                try:
                                    quotesList[str(message.server.id)][quoteNumber]
                                except KeyError:
                                    quotesList[str(message.server.id)][quoteNumber] = newQuote
                                    await chat.chat(message.channel, 'Quote Added as #' + quoteNumber + '!')
                                    with open('quotes.json', 'w') as quoteDatabase:
                                        json.dump(quotesList, quoteDatabase)

                            except IndexError:
                                await chat.chat(message.channel, 'Did you provide a quote to add?')

                        else:
                            await chat.chat(message.channel, 'You don\'t have permission to add a quote!')
                    elif arguments[1].lower() == 'del':
                        if message.author.id in quoteManagers or message.author == message.server.owner or message.author.server_permissions.administrator:
                            try:
                                quotedel = arguments[2]

                                try:
                                    quotesList[message.server.id][quotedel]

                                    del quotesList[message.server.id][quotedel]
                                    await chat.chat(message.channel, 'Deleted Quote #' + quotedel)
                                    with open('quotes.json', 'w') as quoteDatabase:
                                        json.dump(quotesList, quoteDatabase)
                                except KeyError:
                                    await chat.chat(message.channel, 'You can\'t delete a quote that doesnt exist.')
                            except IndexError:
                                await chat.chat(message.channel, 'Did you provide a quote number to delete?')
                        else:
                            await chat.chat(message.channel, 'You do not have permission to delete a quote!')
                    else:
                        try:
                            quoteNumber = str(int(arguments[1]))

                            try:
                                await chat.chat(message.channel, 'Quote #' + quoteNumber + ': ' + quotesList[message.server.id][quoteNumber])
                            except (IndexError, KeyError):
                                await chat.chat(message.channel, 'That quote doesnt exist!')
                        except ValueError:
                            await chat.chat(message.channel, 'Did you enter a quote number?')

                except IndexError:
                    try:
                        randomQuote = random.choice(list(quotesList[message.server.id].keys()))

                        await chat.chat(message.channel, 'Quote #' + str(randomQuote) + ': ' + quotesList[message.server.id][str(randomQuote)])
                    except (IndexError, KeyError):
                        await chat.chat(message.channel, 'There are no quotes yet!')
                await asyncio.sleep(10)
                cooldowns[author.id].remove('quotes')
                
            else:
                if server == None:
                    pass
                else:
                    try:
                        for l in range(11):
                            try:
                                arguments[l]
                            except IndexError:
                                arguments.append('')
                        for key in commandsList[str(message.server.id)]:
                            if message.content.startswith(key):
                                await chat.chat(message.channel, str(commandsList[str(message.server.id)].get(key)).format(arguments[1], arguments[2], arguments[3], arguments[4], arguments[5], arguments[6], arguments[7], arguments[8], arguments[9], user = str(message.author.mention), time=str(message.timestamp.time()).split('.')[0]))
                                commandUsed = True
                                break
                    except KeyError:
                        if message.server == None:
                            commandUsed = False
                        else:
                            if message.server.id in dontReact:
                                await client.add_reaction(message, '👍')
                                await client.add_reaction(message, '👎')
                            commandUsed = False
                        
            if commandUsed == True:            
                pass
                    
    except discord.errors.Forbidden:
        print('The bot is not allowed to send messages to this channel')
    except Exception as err:
        try:
            tb = traceback.format_exc()
            await chat.chat(errorChannel, '\nError in server ' + str(message.server) + '\n' + tb)
            await chat.chat(message.channel, 'An error occured while running this command! This error has been logged and will hopefully get fixed!')
        except discord.errors.Forbidden:
            print('The bot is not allowed to send messages to this channel')
    
@client.event
async def on_ready():
    if not discord.opus.is_loaded():
        print('Loading Opus...')
        discord.opus.load_opus('opus')
        print('Loaded Opus!')
    print('Logged in...')
    print('Username: ' + client.user.name)
    print('Client ID: ' + client.user.id)
    print('----------------------------------')
    ##chat('main-chat', 'The Derpy Meme Bot version ' + cfg.version + ' is now running!')

    await client.change_presence(game=discord.Game(name=cfg.version, url='https://github.com/LeotomasMC/TheDerpyMemeBotDiscord', type=1))

    hard_coded_channel = discord.Object(id="332601647870115842")
   # await chat.chat(hard_coded_channel, 'The Derpy Meme Bot version ' + cfg.version + ' is now running!')
    print('\n')
    
    for server in client.servers:
        if server.id in drtf:
            pass
        else:
            drtf[server.id] = []
        if server.id in points:
            pass
        else:
            points[server.id] = {}
            points[server.id]['pointsEarned'] = 1
            print('Added ' + str(server) + ' to the points list')
        for member in server.members:
            if member.id in cooldowns:
                pass
            else:
                cooldowns[member.id] = []
                
            if member == client.user:
                #points[server.id].remove(client.user.id)
                pass
            if member.id in points[server.id]:
                pass
            else:
                points[server.id][member.id] = 0
                print('Added ' + str(member) + ' to points list in ' + str(server))

    def banUser(userID, tpe='ban', way='add'):
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
    #client.loop.create_task(checkStreamStatus())
    #client.add_cog(Music(bot))
    print('Loading TheDerpyMemeBotDiscord files...')
    print('Creating Points Loop...')
    pointLoopT = threading.Thread(target=pointLoop)
    print('Starting points loop...')
    pointLoopT.start()
    print('\nLoading Custom Commands Database...')
    getCustomCommands()
    print('Loaded Custom Commands Database!\nLoading Quotes Database...')
    getQuotes()
    print('Loaded Quotes Database!\nLoading Banned Users List...')
    getBannedUsers()
    print('Loaded Banned Users List!')
    
    print('Starting Bot...')
    client.run(TOKEN)
    
    loop = asyncio.get_event_loop()
    # Blocking call which returns when the hello_world() coroutine is done
    loop.run_until_complete(consoleChat(serverID, message))
    loop.close()
    
if __name__ == '__main__':
    botT = threading.Thread(target=runBot)
    os.system('title ' + cfg.version)
    with open("ChatLog.txt", "a") as f:
            f.write('\n'*3 + ('='*97 + '\n')*2 + '===---+(-)' + ' '*30 + 'New TDMB Session!' + ' '*30 + '(-)+---===\n' + ('='*97 + '\n')*2)
    botT.start()
