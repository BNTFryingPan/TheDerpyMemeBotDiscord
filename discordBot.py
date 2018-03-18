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
## Everything Else
import config as cfg

# I use ' (single quote) for any text that will be sent or printed, and " (double quote) for any internal things

TOKEN = cfg.token #gets token from config file, might change to a ConfigParser
client = discord.Client() # Creates client

## Variables
botIsOn = True #so bot can be turned on and off remotley, without having to stop the bot completley
sendMessages = True
errorChannel = discord.Object(id="420918104491687936") #error channel ID in my discord server so i can see the traceback of errors when i dont have access to the shell window

customCommandManagers = ["304316646946897920", "156128628726300673"] # ids of users who can add/edit/delete custom commands
quoteManagers = ["304316646946897920"] # people who can manage quotes, will change soon
space = ' '

voice = None
player = None
# VVV list of global command names VVV
globalCommands = ['!off', '!on', '!exec', '!myid', '!tdmbstatus', '!playsong', '!addcom', '!comadd', '!quotes', '!quote', '!delcom', '!comdel', '!editcom', '!comedit', '!version', '!comhelp']

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
    
    try:
        print(str(message.timestamp.time()).split('.')[0] + ': [' + str(message.server) + '] #' + str(message.channel) + ' >> ' + str(message.author) + ': ' + str(message.content))
        # Prints 'TIME: [server] #channel >> sender: message' to the log
        
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
                
            elif command == '!song': # plays a song in the voice channel that the user is in. COMING SOON
                #client.delete_message(message)
                try:
                    arguments[1]
                except IndexError:
                    await chat.chat(message.channel, 'Did you supply the id of the video to listen to?')
                    return
                if arguments[1].lower() in ['current', 'title']:
                    await chat.chat(message.channel, '[' + player.duration + '] ' + player.title)
                elif arguments[1].lower() in ['desc', 'description']:
                    await chat.chat(message.channel, player.description)
                else:
                    try:
                        voice = await client.join_voice_channel(message.author.voice_channel)
                        player = await voice.create_ytdl_player('https://www.youtube.com/watch?v=' + arguments[1])
                        if player.likes > player.dislikes and player.duration <= 600:
                            await chat.chat(message.channel, 'Playing ' + player.title + ' in ' + str(message.author.voice_channel) + '...')
                            player.start()
                            await asyncio.sleep(int(player.duration + 2))
                            await voice.disconnect()
                        else:
                            await chat.chat(message.channel, 'The video needs to have more likes than dislikes and be less that 10 minutes long.')

                    except discord.errors.InvalidArgument:
                        await chat.chat(message.channel, 'You must me in a voice channel to use this command')
                    except discord.errors.ClientException:
                        await chat.chat(message.channel, 'The bot is already in a voice channel...')
                    except Exception as err:
                        await chat.chat(errorChannel, 'Error Playing music... Server: ' + str(message.server) + ', Error: ' + str(err) + ', Check the python console for more information.')
                        await voice.disconnect()
                        raise
                    
            elif command == '!version': # says bot version in chat
                await chat.chat(message.channel, 'Bot Version: ' + cfg.version)
                
            elif command == '!age':
                try:
                    await chat.chat(message.channel, arguments[1] + ' is ' + str(random.randint(0, 100)) + ' years old :Kappa:')
                except IndexError:
                    await chat.chat(message.channel, str(message.author) + ' is ' + str(random.randint(0, 100)) + ' years old :Kappa:')
                    
            elif command == '!hug':
                try:
                    await chat.chat(message.channel, '/me makes ' + str(message.author) + ' hug ' + arguments[1] + '! HUGS! TwitchUnity bleedPurple <3')
                except IndexError:
                    await chat.chat(message.channel, '/me hugs ' + str(message.author) + '! HUGS!!!')
                
            elif command == '!comhelp':
                await chat.chat(message.channel, 'You can use "{user}" and it will mention the user who sends the message, and "{time}" will put the time the users message was sent')
            
            elif command == '!addcom' or command == '!comadd':
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
                try:
                    for l in range(11):
                        try:
                            arguments[l]
                        except IndexError:
                            arguments.append('')
                    for key in commandsList[str(message.server.id)]:
                        if message.content.startswith(key): # NORMAL custom commands
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
        discord.opus.load_opus(opus)
        print('Loaded Opus!')
    print('Logged in...')
    print('Username: ' + client.user.name)
    print('Client ID: ' + client.user.id)
    print('----------------------------------')
    ##chat('main-chat', 'The Derpy Meme Bot version ' + cfg.version + ' is now running!')
    
    await client.change_presence(game=discord.Game(name=cfg.version))
    
    hard_coded_channel = discord.Object(id="332601647870115842")
    await chat.chat(hard_coded_channel, 'The Derpy Meme Bot version ' + cfg.version + ' is now running!')

def runBot():
    #client.loop.create_task(checkStreamStatus())
    client.run(TOKEN)
    
botT = threading.Thread(target=runBot)
if __name__ == '__main__':
    botT.start()