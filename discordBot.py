## Modules
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
import config as cfg
#import musicPlayer as mP

TOKEN = cfg.token #gets token from config file, might change to a ConfigParser
client = discord.Client() # Creates client

## Variables
botIsOn = True #so bot can be turned on and off remotely, without having to stop the bot completley
sendMessages = True
errorChannel = discord.Object(id="420918104491687936") #error channel ID in my discord server so i can see the traceback of errors when i dont have access to the shell window

customCommandManagers = ["304316646946897920", "156128628726300673"] # ids of users who can add/edit/delete custom commands
quoteManagers = ["304316646946897920", "156128628726300673"] # people who can manage quotes, will change soon
dontReact = []
space = ' '

voice = None
player = None
# VVV list of global command names VVV
globalCommands = ['!off', '!on', '!exec', '!myid', '!tdmbstatus', '!playsong', '!addcom', '!comadd', '!quotes', '!quote', '!delcom', '!comdel', '!editcom', '!comedit', '!version', '!comhelp']


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

# I use ' (single quote) for any text that will be sent or printed, and " (double quote) for any internal things


quotesList = {}
def getQuotes():
    global quotesList
    try:
        with open('quotes.json') as f:
            quotesList = json.load(f)
    except:
        print('error getting quotes')
        raise

commandsList = {}
def getCustomCommands():
    global commandsList
    try:
        with open("commands.json") as f:
            commandsList = json.load(f)
    except:
        print('There was a problem getting the command list FeelsBadMan [' + str(sys.exc_info()) + ']')
        raise

class chat:

    async def chat(channel, message):
        if sendMessages:
            await client.send_message(channel, message)
        else:
            print('Sending Messages is disabled...')

    async def me(channel, message):
        await chat.chat(channel, '_' + message + '_')

    async def tableflip(channel, message):
        await chat.chat(channel, message + '(╯°□°）╯︵ ┻━┻')

    async def unflip(channel, message):
        await chat.chat(channel, message + '┬─┬ ノ( ゜-゜ノ)')

    async def shrug(channel, message):
        await chat.chat(channel, message + '¯\_(ツ)_/¯')

    async def tts(channel, message):
        await client.send_message(channel, message, tts=True)



async def checkStreamStatus():
    while not client.is_closed:
        await client.wait_until_ready()
        for server in client.servers:
            if server.owner.game.type == 1:
                await chat.chat(errorChannel, 'Owner of ' + str(server) + ' is now live on Twitch')
        time.sleep(100)

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

    try:
        if message.server == None:
            print(str(message.timestamp.time()).split('.')[0] + ': ' + str(message.channel) + ' >> ' + str(message.author) + ': ' + str(message.content))
        else:
            print(str(message.timestamp.time()).split('.')[0] + ': [' + str(message.server) + '] #' + str(message.channel) + ' >> ' + str(message.author) + ': ' + str(message.content))
        # Prints 'TIME: [server] #channel >> sender: message' to the log
        # If private message, 'TIME: Direct Message with <Username> >> Username#0000: <messabe>

        # we do not want the bot to reply to itself
        if message.author == client.user:
            return
        else:
            arguments = message.content.split(' ') # splits the command at each space, so we can eaisly get each argument
            command = arguments[0].lower() # takes first argument, makes it lowercase, and stores it in a variable so we can see if the command is something we should attempt to do something with



        if command == '!off': #allows me to turn the bot on and off
            if message.author.id == "304316646946897920":
                if botIsOn:
                    await chat.chat(message.channel, 'Turning off bot...')
                    botIsOn = False
                else:
                    await chat.chat(message.channel, 'Bot is already off!')
            else:
                await chat.chat(message.channel, 'This isn\'t the command you are looking for...')

        elif command == '!on': #allows me to turn the bot on and off
            if message.author.id == "304316646946897920":
                if not botIsOn:
                    await chat.chat(message.channel, 'Turning on bot...')
                    botIsOn = True
                else:
                    await chat.chat(message.channel, 'Bot is already on!')
            else:
                await chat.chat(message.channel, 'This isn\'t the command you are looking for...')

        elif command == '!error':
            if message.author.id == "304316646946897920":
                raise ZeroDivisionError('Error raised on request')

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

        elif command == '!tdmbstatus': #allows me to change the 'playing' status of the bot
            if message.author.id == "304316646946897920":
                await client.change_presence(game=discord.Game(name=message.content.split(' ', 1)[1]))
                await chat.chat(message.channel, 'Status is now: ' + message.content.split(' ', 1)[1])

        elif botIsOn: # if the bot is on:
            if command == '!myid': # puts the users ID in chat. This is not a private thing that nobody should know, you can see anyones ID if you are in devolper mode
                await chat.chat(message.channel, '{0.author.mention}, your unique ID is {0.author.id}.'.format(message))

            elif command == '!settings':
                if message.server == None:
                    await chat.chat(message.channel, 'This command cannot be used in Private Messages')
                    return
                if message.author == message.server.owner:
                    if arguments[1].lower() == 'autolike':
                        if arguments[2].lower() == 'false':
                            if message.server.id not in dontReact:
                                dontReact.append(message.server.id)
                                await chat.chat(message.channel, 'Setting \'autolike\' is now false')
                            else:
                                await chat.chat(message.channel, 'Setting \'autolike\' is already false')
                        elif arguments[2].lower() == 'true':
                            if message.server.id not in dontReact:
                                dontReact.pop(message.server.id)
                                await chat.chat(message.channel, 'Setting \'autolike\' is now true')
                            else:
                                await chat.chat(message.channel, 'Setting \'autolike\' is already true')

            elif command == '!song': # plays a song in the voice channel that the user is in.
                #client.delete_message(message)
                self = Music
                if message.server == None:
                    await chat.chat('This command cannot be used in Private Messages.')
                else:
                    try:
                        arguments[1]
                    except IndexError:
                        await chat.chat(message.channel, 'Did you provide any arguments?')
                        return
                    if arguments[1].lower() == 'join':
                        try:##### move functions to IF statements in !song in discordBot.py
                            await Music.create_voice_client(message.author.voiceChannel)
                        except discord.ClientException:
                            await chat.chat(message.server, 'Already in a voice channel...')
                        except discord.InvalidArgument:
                            await chat.chat(message.server, 'This is not a voice channel...')
                        else:
                            await chat.chat(message.server, 'Ready to play audio in ' + message.author.voiceChannel)
                    elif arguments[1].lower() == 'summon':
                        """Summons the bot to join your voice channel."""
                        summoned_channel = message.author.voice_channel
                        if summoned_channel is None:
                            await chat.chat(message.server, 'You are not in a voice channel.')
                            return

                        state = self.get_voice_state(Music, message.server)
                        if state.voice is None:
                            state.voice = await client.join_voice_channel(summoned_channel)
                        else:
                            await state.voice.move_to(summoned_channel)

                        return

                    elif arguments[1].lower() == 'play':
                        """Plays a song.
                        If there is a song currently in the queue, then it is
                        queued until the next song is done playing.
                        This command automatically searches as well from YouTube.
                        The list of supported sites can be found here:
                        https://rg3.github.io/youtube-dl/supportedsites.html
                        """
                        state = self.get_voice_state(Music, message.server)
                        opts = {
                            'default_search': 'auto',
                            'quiet': True,
                        }
                        try:
                            arguments[2]
                        except IndexError:
                            await chat.chat(message.server, 'Did you provide a song to listen to?')
                            return

                        summoned_channel = message.author.voice_channel
                        if summoned_channel is None:
                            await chat.chat(message.server, 'You are not in a voice channel.')
                            return

                        state = self.get_voice_state(Music, message.server)
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
                            await chat.chat(message.server, 'Enqueued ' + str(entry))
                            await state.songs.put(entry)

                    elif arguments[1].lower() == 'volume':
                        """Sets the volume of the currently playing song."""

                        state = self.get_voice_state(Music, message.server)
                        if state.is_playing():
                            player = state.player
                            player.volume = value / 100
                            await chat.chat(message.server, 'Set the volume to {:.0%}'.format(player.volume))

                    elif arguments[1].lower() == 'pause':
                        """Pauses the currently played song."""
                        state = self.get_voice_state(Music, message.server)
                        if state.is_playing():
                            player = state.player
                            player.pause()

                    elif arguments[1].lower() == 'resume':
                        """Resumes the currently played song."""
                        state = self.get_voice_state(Music, message.server)
                        if state.is_playing():
                            player = state.player
                            player.resume()

                    elif arguments[1].lower() == 'stop':
                        """Stops playing audio and leaves the voice channel.
                        This also clears the queue.
                        """
                        server = message.server
                        state = self.get_voice_state(Music, message.server)

                        if state.is_playing():
                            player = state.player
                            player.stop()

                        try:
                            state.audio_player.cancel()
                            del self.voice_states[message.server.id]
                            await state.voice.disconnect()
                        except:
                            pass


                    elif arguments[1].lower() == 'skip':
                        """Vote to skip a song. The song requester can automatically skip.
                        3 skip votes are needed for the song to be skipped.
                        """

                        state = self.get_voice_state(Music, message.server)
                        if not state.is_playing():
                            await chat.chat(message.server, 'Not playing any music right now...')
                            return

                        voter = message.author
                        if voter == state.current.requester:
                            await chat.chat(message.server, 'Requester requested skipping song...')
                            state.skip()
                        elif voter.id not in state.skip_votes:
                            state.skip_votes.add(voter.id)
                            total_votes = len(state.skip_votes)
                            if total_votes >= 3:
                                await chat.chat(message.server, 'Skip vote passed, skipping song...')
                                state.skip()
                            else:
                                await chat.chat(message.server, 'Skip vote added, currently at [{}/3]'.format(total_votes))
                        else:
                            await chat.chat(message.server, 'You have already voted to skip this song.')

                    elif arguments[1].lower() == 'playing':
                        """Shows info about the currently played song."""

                        state = self.get_voice_state(Music, message.server)
                        if state.current is None:
                            await chat.chat(message.server, 'Not playing anything.')
                        else:
                            skip_count = len(state.skip_votes)
                            await chat.chat(message.server, 'Now playing {} [skips: {}/3]'.format(state.current, skip_count))

            elif command == '!version': # says bot version in chat
                await chat.chat(message.channel, 'Bot Version: ' + cfg.version)

            elif command == '!age':
                try:
                    await chat.chat(message.channel, arguments[1] + ' is ' + str(random.randint(0, 100)) + ' years old :Kappa:')
                except IndexError:
                    await chat.chat(message.channel, str(message.author) + ' is ' + str(random.randint(0, 100)) + ' years old :Kappa:')

            elif command == '!hug':
                try:
                    await chat.me(message.channel, 'makes ' + str(message.author) + ' hug ' + arguments[1] + '! HUGS! TwitchUnity bleedPurple <3')
                except IndexError:
                    await chat.me(message.channel, 'hugs ' + str(message.author) + '! HUGS!!!')

            elif command == '!comhelp':
                await chat.chat(message.channel, 'You can use "{user}" and it will mention the user who sends the message, and "{time}" will put the time the users message was sent')

            elif command == '!addcom' or command == '!comadd':
                if message.server == None:
                    await chat.chat(message.channel, 'This command cannot be used in Private Messages')
                    return
                if message.author.id in customCommandManagers or message.author == message.server.owner:
                    if message.content.count(space) >= 2:
                        try:
                            newargs = arguments[2:]
                            output = ' '.join(newargs)

                            commandadd = arguments[1]
                            answer = output

                            if commandadd in globalCommands:
                                await chat.chat(message.channel, 'You cant add that command, as it is already a global TDMB command')
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
                    await chat.chat(message.channel, 'You dont have permission to use that command!')

            elif command == '!delcom' or command == '!comdel':
                if message.server == None:
                    await chat.chat(message.channel, 'This command cannot be used in Private Messages')
                    return
                if message.author.id in customCommandManagers or message.author == message.server.owner:
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
                    await chat.chat(message.channel, 'You dont have permission to use that command!')

            elif command == '!editcom' or command == '!comedit':
                if message.server == None:
                    await chat.chat(message.channel, 'This command cannot be used in Private Messages')
                    return
                if message.author.id in customCommandManagers or message.author == message.server.owner:
                    if message.content.count(space) >= 2:
                        try:
                            newargs = arguments[2:]
                            output = ' '.join(newargs)

                            commandedit = arguments[1]
                            answer = output

                            if commandedit in globalCommands:
                                await chat.chat(message.channel, 'You can\t edit global commands')
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
                    await chat.chat(message.channel, 'You dont have permission to use that command!')

                # END CUSTOM COMMANDS -----------------------------------------

                # QUOTES ----------------------------------------------------

            elif command == '!quotes' or command == '!quote':
                if message.server == None:
                    await chat.chat(message.channel, 'This command cannot be used in Private Messages')
                    return
                try:
                    quotesList[str(message.server.id)]
                except KeyError:
                    quotesList[str(message.server.id)] = {}

                try:
                    if arguments[1].lower() == 'add':
                        if message.author.id in quoteManagers or message.author == message.server.owner:
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
                            await chat.chat(message.channel, 'You dont have permission to add a quote!')
                    elif arguments[1].lower() == 'del':
                        if message.author.id in quoteManagers or message.author == message.server.owner:
                            try:
                                quotedel = arguments[2]

                                try:
                                    quotesList[message.server.id][quotedel]

                                    del quotesList[message.server.id][quotedel]
                                    await chat.chat(message.channel, 'Deleted Quote #' + quotedel)
                                    with open('quotes.json', 'w') as quoteDatabase:
                                        json.dump(quotesList, quoteDatabase)
                                except KeyError:
                                    await chat.chat(message.channel, 'You cant delete a quote that doesnt exist.')
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

            else:
                if message.server == None:
                    return
                if message.server.id not in dontReact and botIsOn:
                    await client.add_reaction(message, '👍')
                    await client.add_reaction(message, '👎')
                try:
                    for l in range(11):
                        try:
                            arguments[l]
                        except IndexError:
                            arguments.append('')
                    for key in commandsList[str(message.server.id)]:
                        if message.content.startswith(key):
                            await chat.chat(message.channel, str(commandsList[str(message.server.id)].get(key)).format(arguments[1], arguments[2], arguments[3], arguments[4], arguments[5], arguments[6], arguments[7], arguments[8], arguments[9], user = str(message.author.mention), time=str(message.timestamp.time()).split('.')[0]))
                except KeyError:
                    pass

    except Exception as err:
        try:
            tb = traceback.format_exc()
            await chat.chat(errorChannel, '\nError in server ' + str(message.server) + '\n' + tb)
        except:
            raise
@client.event
async def on_ready():
    os.system('title ' + cfg.version)
    print('\nLoading Custom Commands Database...')
    getCustomCommands()
    print('Loaded Custom Commands Database!\nLoading Quotes Database...')
    getQuotes()
    print('Loaded Quotes Database!')
    if not discord.opus.is_loaded():
        print('Loading Opus...')
        discord.opus.load_opus('opus')
        print('Loaded Opus!')
    print('Logged in...')
    print('Username: ' + client.user.name)
    print('Client ID: ' + client.user.id)
    print('----------------------------------')
    ##chat('main-chat', 'The Derpy Meme Bot version ' + cfg.version + ' is now running!')

    await client.change_presence(game=discord.Game(name=cfg.version, type=1))

    hard_coded_channel = discord.Object(id="332601647870115842")
    await chat.chat(hard_coded_channel, 'The Derpy Meme Bot version ' + cfg.version + ' is now running!')

def runBot():
    #client.loop.create_task(checkStreamStatus())
    #client.add_cog(Music(bot))
    client.run(TOKEN)

botT = threading.Thread(target=runBot)
if __name__ == '__main__':
    botT.start()
