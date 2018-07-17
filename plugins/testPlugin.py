import sys 
sys.path.append('..')
import discordBot as bot
import discord
    
botclient = None

__commands__ = ['!testplugin']

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
            
        if command == '!testplugin':
            await chat(ch, 'This is a command from the test plugin!')
        else:
            return False
            
    except:
        print('error in plugin')
        raise