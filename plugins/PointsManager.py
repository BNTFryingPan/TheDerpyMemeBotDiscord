#TDMB Builtin Plugin - Points Manager
#
#Note, this plugin is the plugin thats creates the functions neccisary for the points command system work
#on its own, this plugin does nothing.
import json

async def on_message(message):
    return False

def getPointsFile():
    '''Returns the list of servers and points'''
    try:
        with open('plugins\\points.json') as f:
            points = json.load(f)
        with open('plugins\\rewards.json') as f:
            rewards = json.load(f)
    except:
        raise
    else:
        return [points, rewards]
        
def getPoints():
    '''Returns just the points list'''
    return getPointsFile()[0]
    
def getRewards():
    '''Returns just the rewards list'''
    return getPointsFile()[1]
    
def addServer(serverid):
    points = getPoints()
    if str(serverid) not in points:
        points[str(serverid)] = {'rate': 10, 'currency': 'points'}
        savePointsFile(points)
    rewards = getRewards()
    if str(serverid) not in rewards:
        rewards[str(serverid)] = {}
    return True
    
def addUser(serverid, userid):
    addServer(str(serverid))
    points = getPoints()
    if str(userid) not in points:
        points[str(serverid)][userid] = 0
        savePointsFile(points)
    return
    
def getUserPoints(serverid, userid):
    addUser(serverid, userid)
    return getPoints()[serverid][userid]

def setUserPoints(serverid, userid, amount):
    addUser(serverid, userid)
    points = getPoints()
    points[serverid][userid] = int(amount)
    savePointsFile(points)
    return True
    
def changeRate(serverid, newRate):
    addServer(str(serverid))
    points = getPoints()
    points[str(serverid)]['rate'] = str(newRate)
    savePointsFile(points)
    return True
    
def changeCurrency(serverid, newCurrency):
    '''Changes a servers currency name'''
    addServer(str(serverid))
    points = getPoints()
    points[str(serverid)]['currency'] = str(newCurrency)
    savePointsFile(points)
    return True
    
def addReward(serverid, reward, cost):
    '''Adds a reward to a servers reward list.
    Returns:
    
    0 - Added succesfully
    1 - Already exists
    2 - Invalid cost
    '''
    addServer(str(serverid))
    rewards = getRewards()
    if reward in rewards[str(serverid)]:
        return 1
    elif cost <= 0:
        return 2
    else:
        rewards[str(serverid)][reward] = cost
        saveRewardsFile(rewards)
        return
        
def getReward(serverid, reward):
    '''Returns the price of reward, if reward doesnt exist, returns none'''
    addServer(str(serverid))
    rewards = getRewards()
    if reward in rewards[server.id]:
        return rewards[server.id][arguments[1]]
    else:
        return None
    
def removeReward(serverid, reward):
    '''Removes a reward from a servers reward list.
    Returns:
    
    0 - Removed succesfully
    1 - Doesn't exist
    '''
    addServer(str(serverid))
    rewards = getRewards()
    if reward not in rewards[str(serverid)]:
        return 1
    else:
        rewards[str(serverid)].pop(reward)
        saveRewardsFile(rewards)
        return 0
        
def savePointsFile(points):
    '''THIS IS A VERY DANGEROUS FUNCTION! USE IT CAREFULLY!!!'''
    with open('plugins\\points.json', 'w') as f:
        json.dump(points, f)
    return True
        
def saveRewardsFile(rewards):
    with open('plugins\\rewards.json', 'w') as f:
        json.dump(rewards, f)
    return True