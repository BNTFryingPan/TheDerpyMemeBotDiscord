# TDMB Builtin Plugin - Points Commands
# This plugin adds all the commands for the points system.
# This plugin REQUIRED the PointsManager plugin to be in the same folder as this plugin to function properly!
import sys 
sys.path.append('..')
import discordBot as bot
import discord
if __name__ == '__main__':
    import PointsManager as pm
else:
    import plugins.PointsManager as pm
import config as cfg
import random
    
botclient = None

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
    pm.addServer(str(message.server.id))
    pm.addUser(message.server.id, str(message.author.id))
    #rewards = pm.getRewards()[message.server.id]
    points = pm.getPoints()[message.server.id]

    try:
        server = message.server
        leo = '304316646946897920' #this should be the only hardcoded user ID. This is my (the original bot makers) ID, so I can let myself have more control over the bot.
        isLeo = message.author.id == leo
        
        ch = message.channel
        channel = message.channel
        author = message.author
        
        
        arguments = message.content.lower().split(' ') # splits the command at each space, so we can eaisly get each argument
        oargs = message.content.split(' ')
        command = arguments[0].lower()
        
        if server == None:
            isAdmin = True
            serverCurrency = 'points'
            serverCurr = 'points'
            isOwner = True
        else:
            isAdmin = author.server_permissions.administrator
            isOwner = author == message.server.owner
            serverCurrency = points['currency']
            serverCurr = serverCurrency
            
        if command == '!points' or command == ('!' + serverCurr).lower():
            if server == None:
                await chat(ch, cfg.noPMcmdRes)
            else:
                if len(arguments) == 1:
                    await chat(ch, author.mention + ' You have ' + str(points[author.id]) + ' ' + serverCurr + '!')
                else:
                    if arguments[1] in ['send', 'set', 'add', 'subtract']:
                        if not len(arguments) == 4:
                            await chat(ch, author.mention + ' You didnt provide enough arguments!')
                        if arguments[1] == 'send':
                            receiver = server.get_member(arguments[2])
                            if receiver == None:
                                await chat(ch, 'There is no user in this server with that ID')
                            else:
                                try:
                                    amount = int(arguments[3])
                                except ValueError:
                                    await chat(ch, 'That isnt a number!')
                                else:
                                    if pm.getUserPoints(server.id, user.id) >= amount:
                                        if amount <= 0:
                                            await chat(ch, 'You cant take {curr} from people! What kind of person are you!'.format(curr=serverCurr))
                                        pm.addUser(server.id, receiver.id)
                                        pm.setUserPoints(server.id, receiver.id, getUserPoints(server.id, receiver.id) + amount)
                                        pm.setUserPoints(server.id, user.id, getUserPoints(server.id, user.id) - amount)
                                        await chat(ch, receiver.mention + ' , ' + author.mention + ' gave you ' + str(amount) + ' ' + serverCurr + '!')
                                    else:
                                        await chat(ch, 'You dont have that many {curr} to give!'.format(curr=serverCurr))
                                        
                        else:
                            if not isAdmin:
                                await chat(ch, author.mention + ' You cant use this subcommand!')
                            else:
                                if arguments[1] == 'set':
                                    receiver = server.get_member(arguments[2])
                                    if receiver == None:
                                        await chat(ch, 'There is no user in this server with that ID')
                                    else:
                                        pm.addUser(server.id, receiver.id)
                                        pm.setUserPoints(server.id, receiver.id, int(arguments[3]))
                                        await chat(ch, 'Set the ' + serverCurr + ' of ' + receiver.display_name + ' to ' + str(int(arguments[3])))
                                elif arguments[1] == 'add':
                                    receiver = server.get_member(arguments[2])
                                    if receiver == None:
                                        await chat(ch, 'There is no user in this server with that ID')
                                    else:
                                        pm.addUser(server.id, receiver.id)
                                        pm.setUserPoints(server.id, receiver.id, getUserPoints(server.id, user.id) + int(arguments[3]))
                                        await chat(ch, 'Set the ' + serverCurr + ' of ' + receiver.display_name + ' to ' + str(int(arguments[3])))
                                elif arguments[1] == 'subtract':
                                    receiver = server.get_member(arguments[2])
                                    if receiver == None:
                                        await chat(ch, 'There is no user in this server with that ID')
                                    else:
                                        pm.addUser(server.id, receiver.id)
                                        pm.setUserPoints(server.id, receiver.id, getUserPoints(server.id, user.id) - int(arguments[3]))
                                        await chat(ch, 'Set the ' + serverCurr + ' of ' + receiver.display_name + ' to ' + str(int(arguments[3])))

        elif command == '!gamble' or command == '!gamblepoints':
            if len(arguments) == 1:
                await chat(ch, 'How many {curr} do you want to gamble?')
            elif len(arguments) == 2:
                try:
                    if arguments[1] == 'all':
                        gambling = int(pm.getUserPoints(server.id, author.id))
                    else:
                        gambling = int(arguments[1])
                except ValueError:
                    await chat(ch, 'That isnt a number!')
                else:
                    if gambling <= 0:
                        await chat(ch, 'You cant gamble 0 or negative {curr}! Thats just cheating!')
                    else:
                        userPoints = pm.getUserPoints(server.id, author.id)
                        if userPoints >= gambling:
                            await chat(ch, 'Gambling {amnt} {curr}...')
                            userPoints -= gambling
                            
                            result = random.randint(0, 10)
                            if result == 0:
                                userPoints += int(gambling*11)
                                await chat(ch, 'YOU HIT THE JACKPOT! You earned {amnt} {curr}! (x10) You now have {newAmnt} {curr}!'.format(amnt=str(gambling*10), curr=serverCurr, newAmnt=userPoints))
                                pm.setUserPoints(server.id, author.id, userPoints)
                            elif result in [1,2,3,4,5]:
                                await chat(ch, 'You didnt win monkaS you lost {amnt} {curr}. You now have {newAmnt} {curr}.'.format(amnt=gambling, curr=serverCurr, newAmnt=userPoints))
                                pm.setUserPoints(server.id, author.id, userPoints)
                            else:
                                userPoints += gambling*2
                                await chat(ch, 'You won! You earned {amnt} {curr}! You now have {newAmnt} {curr}!'.format(amnt=gambling, curr=serverCurr, newAmnt=userPoints))
                                pm.setUserPoints(server.id, author.id, userPoints)
                        else:
                            requiredPoints = gambling - userPoints
                            await chat(ch, 'You dont have enough {curr} to gamble {amnt}, you need {reqAmnt} more {curr} to gamble that much!'.format(curr=serverCurr, amnt=gambling, reqAmnt=requiredPoints))
            else:
                if isLeo:
                    await chat(ch, 'An error occured while running this command! NotImplementedError: Why didnt you add this yet? BabyRage')
                else:
                    await chat(ch, 'What, are you trying to cheat? Yeah no, thats not going to work! I could take all of your {curr}, but im not *THAT* mean')
        
        elif command == '!slots':
            await chat(ch, 'The bot is currently being almost 100% rewritten! This command hasnt been rewrote yet!')
            
        elif command == '!raffle':
            await chat(ch, 'The bot is currently being almost 100% rewritten! This command hasnt been rewrote yet!')
            
        elif command == '!duel':
            await chat(ch, 'The bot is currently being almost 100% rewritten! This command hasnt been rewrote yet!')
            
        elif command == '!acceptduel':
            await chat(ch, 'The bot is currently being almost 100% rewritten! This command hasnt been rewrote yet!')
            
        elif command == '!managerewards':
            await chat(ch, 'The bot is currently being almost 100% rewritten! This command hasnt been rewrote yet!')
            
        elif command == '!claimreward':
            if server == None:
                await chat.chat(ch, cfg.noPMcmdRes)
                return
            
            else:
                try:
                    arguments[1]
                except IndexError:
                    await chat(ch, 'Did you provide a reward to claim?')
                else:
                    reward = pm.getReward(server.id, arguments[1])
                    if reward == None:
                        await chat(ch, 'Unable to find that reward! Are you sure you spelt it right?')
                    else:
                        userPoints = pm.getUserPoints(server.id, author.id)
                        if userPoints >= reward:
                            userPoints -= reward
                            await chat(ch, 'Succesfully redeemed reward: {reward} for {cost} {curr}!'.format(reward=arguments[1], cost=reward, curr=serverCurr))
                            await chat(server.owner, str(author) + ' redeemed reward: {reward}'.format(reward=arguments[1]))
                        else:
                            await chat(ch, 'You don\'t have enough {curr} for that reward. You need ' + str(rewards[server.id][arguments[1]] - points[server.id][author.id]) + ' more points.')
            
        else:
            return False
    except:
        print('Error in plugin!')
        raise