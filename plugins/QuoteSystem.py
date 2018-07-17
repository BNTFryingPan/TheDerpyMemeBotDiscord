import sys 
sys.path.append('..')
import discordBot as bot
import discord
import json
#from random import choice
import random
    
botclient = None

class quoteManager:
    def getQuotes():
        with open('plugins\\quotes.json') as f:
            quotes = json.load(f)
        return quotes
            
    def addServer(serverid):
        quotes = quoteManager.getQuotes()
        if serverid not in quotes:
            quotes[serverid] = []
            quoteManager.saveQuotes(quotes)
        return quotes
            
    def addQuote(serverid, quote):
        quotes = quoteManager.addServer(serverid)
        if quote in quotes[serverid]:
            return False
        else:
            quotes[serverid].append(quote)
            return True
        
    def delQuote(serverid, quotenumber):
        quotes = quoteManager.addServer(serverid)
        if quote not in quotes[serverid]:
            return False
        else:
            quotes[serverid].remove(quote)
            return True
        
    def retreiveQuote(serverid, quoteid=-1):
        quoteid = int(quoteid)
        quotes = quoteManager.addServer(serverid)[serverid]
        if quoteid == -1:
            try:
                randomQuoteNum = random.randint(0, len(quotes) - 1 )
                return [quotes[randomQuoteNum], randomQuoteNum]
            except IndexError:
                return None
        else:
            try:
                return [quotes[serverid][quoteid], quoteid]
            except IndexError:
                return None
                
    def saveQuotes(quotes):
        with open('plugins\\quotes.json','w') as f:
            json.dump(quotes, f)
        

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
            if isLeo:
                isAdmin = True
                isOwner = True
            if isOwner:
                isAdmin = True
            
        if command == '!quote' or command == '!quotes':
            if len(arguments) == 1:
                randomQuote = quoteManager.retreiveQuote(server.id)
                if randomQuote == None:
                    await chat(ch, 'This server has no quotes yet! Admins can add quotes using !quote add <quote>')
                else:
                    await chat(ch, 'Quote {num}: {quote}'.format(num=randomQuote[1], quote=randomQuote[0]))
            elif len(arguments) == 2:
                if arguments[1] == 'del':
                    if isAdmin:
                        await chat(ch, 'Did you provide a quote to delete?')
                    else:
                        await chat(ch, 'You cannot use this subcommand! [admin]')
                elif arguments[1] == 'add':
                    if isAdmin:
                        await chat(ch, 'Did you provide a quote to add?')
                    else:
                        await chat(ch, 'You cannot use this subcommand! [admin]')
                else:
                    try:
                        int(arguments[1])
                    except ValueError:
                        await chat(ch, 'That isnt a valid quote number')
                    else:
                        quotel = quoteManager.retreiveQuote(server.id, int(arguments[1]))
                        if quotel == None:
                            await chat(ch, 'Unable to find quote!')
                        else:
                            await chat(ch, 'Quote {num}: {quote}'.format(num=quotel[1], quote=quotel[0]))
            else:
                if arguments[1] == 'add':
                    if isAdmin:
                        newQuote = ' '.join(arguments[2:])
                        add = quoteManager.addQuote(server.id, newQuote)
                        if add == False:
                            await chat(ch, 'That quote already exists!')
                        else:
                            await chat(ch, 'Added quote: "' + newQuote + '"')
                    else:
                        await chat(ch, 'You cannot use this subcommand! [admin]')
                        
                elif arguments[1] == 'del':
                    if isAdmin:
                        try:
                            quoteNumber = int(arguments[2])
                        except ValueError:
                            await chat(ch, 'That isnt a valid quote number!')
                        else:
                            delete = quoteManager.delQuote(server.id, quoteNumber)
                            
                            if delete == False:
                                await chat(ch, 'No quote with that ID!')
                            else:
                                await chat(ch, 'Succesfully Deleted quote with ID of {num}'.format(num=quoteNumber))
                    else:
                        await chat(ch, 'You cannot use this subcommand! [admin]')
                        
        else:
            return False
    except:
        print('error in plugin')
        raise