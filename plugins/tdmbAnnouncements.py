## TDMB Builtin Plugin
## Announcements
## This module is used so people can signup for announcements about TDMB, and it will whisper them about new features, changes, etc...

import sys 
sys.path.append('..')
import discordBot as bot
import discord
    
botclient = None

__commands__ = ['!getannouncements', '!announcementsinfo']

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
            
        if command == '!gettdmbannouncements':
            await chat(ch, 'You will now get occasional DMs from TheDerpyMemeBot about updates, changes, downtimes, and other various things!\nYou should now get a test DM to make sure you can receive DMs from TheDerpyMemeBot.')
            await chat(author, 'This is the test DM! Type ```!announcementsinfo``` for info about these announcements')
            
        elif command == '!announcementsinfo':
            if server == None:
                await chat(ch, 'These announcements that you may receive if you signed up are to tell you about the status of TDMB. You will get DMs about new TDMB features, command changes, announcements if the bot will go offline, and sometimes a few other things. TDMB will not spam you with DMs. If you dont want to receive DMs from TDMB for any reason, type !notdmbdms')
        else:
            return False
            
    except:
        print('error in plugin')
        raise