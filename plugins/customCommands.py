import sys 
sys.path.append('..')
import discordBot as bot
import discord
import json

botclient = None

__commands__ = ['!addcom', '!comadd', '!delcom', '!comdel', '!editcom', '!comedit', '!comhelp']

class commandManager:
    def loadCommands(file='plugins\\commands.json'):
        '''Loads the custom commands list from a file'''
        with open(file) as f:
            commands = json.load(f)
            return commands
    
    def saveCommands(commands, file='plugins\\commands.json'):
        '''Saves the custom command list to a file'''
        with open(file, 'w') as f:
            json.dump(commands, f)
        
    def addServer(serverid):
        '''Adds a server to the custom command list'''
        cmds = commandManager.loadCommands()
        if serverid not in cmds:
            cmds[str(serverid)] = {}
            commandManager.saveCommands(cmds)
        return cmds
        
    def addCommand(serverid, command, response):
        '''Adds a custom command
        Returns False if the command already exists
        Returns None if the command is a Base TDMB command, or exists in another plugin
        Returns True if the command was added succesfully'''
        cmds = commandManager.addServer(serverid)
        if str(command) in bot.pluginManager.getAllCommands():
            return None
        elif str(command) not in cmds[str(serverid)]:
            cmds[str(serverid)][str(command)] = str(response)
            commandManager.saveCommands(cmds)
            return True
        else:
            return False
        
    def delCommand(serverid, command):
        '''Deletes a custom command
        Returns False if the command doesn't exist yet
        Returns True if the command was deleted succesfully'''
        cmds = commandManager.addServer(serverid)
        if str(command) in bot.pluginManager.getAllCommands():
            return None
        elif str(command) in cmds[str(serverid)]:
            cmds[str(serverid)].pop(str(command))
            commandManager.saveCommands(cmds)
            return True
        else:
            return False
        
    def editCommand(serverid, command, response):
        '''Edits a custom command
        Returns False if the command doesn't already exist
        Returns True if the command was edited succesfully
        '''
        delete = commandManager.delCommand(serverid, command)
        if delete == False:
            return False
        elif delete == None:
            return None
        else:
            add = commandManager.addCommand(serverid, command, response)
            if add == False:
                return False
            elif add == None:
                return None
            else:
                return True
        
    def getCommand(serverid, command):
        '''Gets a response from a custom command.
        Returns None if the command doesn't exist, otherwise, returns the commands response'''
        cmds = commandManager.addServer(serverid)
        if command in cmds[str(serverid)]:
            print(cmds[str(serverid)][command])
            return cmds[str(serverid)][command]
        else:
            return None

async def chat(channel, message=None, tts=False):
    if message == None:
        dp('Bot tried sending an empty message!')
        return None
    else:
        try:
            msg = await botclient.send_message(channel, message, tts=tts)
            return msg
        except discord.errors.Forbidden:
            p('The bot is not allowed to send messages to this channel')
            return None
            
async def on_message(message):
    try:
        server = message.server
        leo = '304316646946897920' #this should be the only hardcoded user ID. This is my (the original bot makers) ID, so I can let myself have more control over the bot.
        isLeo = message.author.id == leo
        
        ch = message.channel
        channel = message.channel
        author = message.author
        
        
        arguments = message.content.split(' ') # splits the command at each space, so we can eaisly get each argument
        command = arguments[0].lower()
        
        if server == None:
            isAdmin = True
            #serverCurrency = None
            #serverCurr = None
            isOwner = True
        else:
            isAdmin = author.server_permissions.administrator
            isOwner = author == message.server.owner
            #serverCurrency = points[server.id]['currencyName']
            #serverCurr = serverCurrency
            
        if command == '!comhelp':
            await chat(message.channel, 'You can use "{user}" and it will mention the user who sends the message, and "{time}" will put the time the users message was sent')
        
        elif command == '!addcom' or command == '!comadd': # adds a custom command ##todo: move to custom commands
            if message.server == None:
                await chat(message.channel, cfg.noPMcmdRes)
                
            elif message.author == message.server.owner or message.author.server_permissions.administrator:
                if len(arguments) >= 3:
                    response = ' '.join(arguments[2:])
                    addcmd = commandManager.addCommand(server.id, arguments[1], response)
                    
                    if addcmd == True:
                        await chat(ch, author.mention + ' Succesfully added the command {cmd}'.format(cmd=arguments[1]))
                    elif addcmd == False:
                        await chat(ch, author.mention + ' That command already exists!')
                    else:
                        await chat(ch, author.mention + ' You cannot overwrite a base TDMB command, or a command in another plugin.')
                else:
                    await chat(ch, author.mention + ' did you provide a command to add?')
            else:
                await chat(message.channel, 'You don\'t have permission to use that command! [admin]')
                    
        elif command == '!delcom' or command == '!comdel':
            if message.server == None:
                await chat(ch, cfg.noPMcmdRes)
                
            elif isOwner or isAdmin or isLeo:
                if len(arguments) == 2:
                    delete = commandManager.delCommand(server.id, arguments[1])
                    
                    if delete == True:
                        await chat(ch, author.mention + ' Deleted command')
                    elif delete == False:
                        await chat(ch, author.mention + ' Cant delete a command that doesnt exist!')
                    else:
                        await chat(ch, author.mention + ' Cant delete a base TDMB command, or a command in another plugin!')
                else:
                    await chat(ch, author.mention + ' did you provide a command to delete?')
            else:
                await chat(ch, 'You dont have permission to use this command! [admin]')
            
        elif command == '!editcom' or command == '!comedit':
            if message.server == None:
                await chat(ch, cfg.noPMcmdRes)
                
            elif isOwner or isAdmin or isLeo:
                if len(aguments) >= 3:
                    newresponse = ' '.join(arguments[2:])
                    edit = commandManager.editCommand(server.id, arguments[1], newresponse)
                    
                    if edit:
                        await chat(ch, author.mention + ' Edited command!')
                    else:
                        await chat(ch, author.mention + ' Couldnt edit the command because it doesnt exist')
                else:
                    await chat(ch, author.mention + ' did you provide a command to edit?')
            else:
                await chat(ch, 'You dont have permission to use this command! [admin]')
        
        else:
            return False
    except:
        print('error in plugin')
        raise