import sys 
sys.path.append('..')
import discordBot as bot
import discord
import asyncio
   
botclient = None

__commands__ = ['!song']

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
        self.botclient = botclient
        self.play_next_song = asyncio.Event()
        self.songs = asyncio.Queue()
        self.skip_votes = set() # a set of user_ids that voted
        self.audio_player = self.botclient.loop.create_task(self.audio_player_task())

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
            self.skip_votes = set()

    def toggle_next(self):
        self.botclient.loop.call_soon_threadsafe(self.play_next_song.set)

    async def audio_player_task(self):
        while True:
            self.play_next_song.clear()
            self.current = await self.songs.get()
            await self.botclient.send_message(self.current.channel, 'Now playing ' + str(self.current))
            self.current.player.start()
            await self.play_next_song.wait()

class Music:
    """Voice related commands.
    Works in multiple servers at once.
    """
    voice_states = {}
    bot = botclient
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
        voice = await botclient.join_voice_channel(channel)
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

async def chat(channel, message=None, tts=False):
    if message == None:
        #dp('Bot tried sending an empty message!')
        return None
    else:
        try:
            msg = await botclient.send_message(channel, message, tts=tts)
            return msg
        except discord.errors.Forbidden:
            p('The bot is not allowed to send messages to this channel')
            return None
            
async def on_message(message):
    print('Got to on_message()')
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
            

            
          
        
        if command == '!song': # plays a song in the voice channel that the user is in. # move to song module
            #client.delete_message(message)
            print('Got to if command')
            if message.server == None:
                await chat(message.channel, cfg.noPMcmdRes)
                return 
            else:
                self = Music
                state = self.get_voice_state(Music, message.server)
                try:
                    arguments[1]
                except IndexError:
                    await chat(message.channel, 'Did you provide any arguments?')
                    return
                    
                if arguments[1].lower() == 'join':
                    try:
                        await Music.create_voice_client(message.author.voiceChannel)
                    except discord.ClientException:
                        await chat(message.channel, 'Already in a voice channel...')
                    except discord.InvalidArgument:
                        await chat(message.channel, 'This is not a voice channel...')
                    else:
                        await chat(message.channel, 'Ready to play audio in ' + message.author.voiceChannel)

                elif arguments[1].lower() == 'queue':
                    #dp(state.songs)
                    await chat(message.channel, 'Queue Entries: \n' + state.songs)


                elif arguments[1].lower() == 'summon':
                    """Summons the bot to join your voice channel."""
                    summoned_channel = message.author.voice_channel
                    if summoned_channel is None:
                        await chat(message.channel, 'You are not in a voice channel.')
                        return

                    if state.voice is None:
                        state.voice = await botclient.join_voice_channel(summoned_channel)
                        await chat(ch, 'Joined your voice channel')
                    else:
                        await state.voice.move_to(summoned_channel)
                        await chat(ch, 'Moved to your channel!')

                    return

                elif arguments[1].lower() == 'play':
                    """Plays a song. If there is a song currently in the queue, then it isqueued until the next song is done playing.This command automatically searches as well from YouTube.The list of supported sites can be found here:
                    https://rg3.github.io/youtube-dl/supportedsites.html"""
                    opts = {
                        'default_search': 'auto',
                        'quiet': True,
                        }
                    #try:
                       # points[message.server.id][message.author.id]
                    #except IndexError:
                        #try:
                        #    points[message.server.id]
                        #except IndexError:
                        #    points[message.server.id] = {}
                        
                        #points[message.server.id][message.author.id] = 0
                        
                        #await chat(message.channel, message.author.mention + ' You do not have enough points to request a song! You need 100 points, you have 0 points')
                        #return
                    #else:
                        #if points[message.server.id][message.author.id] >= 100:
                            #pass
                        #else:
                            #await chat(message.channel, message.author.mention + ' You do not have enough points to request a song! You need 100 points, you have ' + str(points[message.server.id][message.author.id]))
                            #return
                        #pass
                    try:
                        arguments[2]
                    except IndexError:
                        await chat(message.channel, 'Did you provide a song to listen to?')
                        return

                    summoned_channel = message.author.voice_channel
                    if summoned_channel is None:
                        await chat(message.channel, 'You are not in a voice channel.')
                        return

                    if state.voice is None:
                        state.voice = await botclient.join_voice_channel(summoned_channel)
                    else:
                        await state.voice.move_to(summoned_channel)

                    try:
                        player = await state.voice.create_ytdl_player(''.join(arguments[2:]), ytdl_options=opts, after=state.toggle_next)
                    except Exception as e:
                        fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
                        await botclient.send_message(message.channel, fmt.format(type(e).__name__, e))
                    else:
                        if player.duration > 900:
                            await chat(ch, 'That song is too long! The video must not be longer than 15 minutes, your request was ' + '**{0[0]}m {0[1]}s]**'.format(divmod(duration, 60)))
                        player.volume = 0.6
                        entry = VoiceEntry(message, player)
                        #await chat(message.channel, 'Enqueued ' + str(entry) + '. You now have ' + str(points[message.server.id][message.author.id] - 100) + ' points left.')
                        await chat(ch, 'Enqueued ' + str(entry) + '. You now have <coming soon> points left!')
                        await state.songs.put(entry)
                        #points[message.server.id][message.author.id] -= 100

                elif arguments[1].lower() == 'volume':
                    """Sets the volume of the currently playing song."""
                    
                    try:
                        arguments[2]
                    except IndexError:
                        await chat('You didnt provide a volume level')
                        return

                    if state.is_playing():
                        player = state.player
                        player.volume = arguments[2] / 100
                        await chat(message.channel, 'Set the volume to {:.0%}'.format(player.volume))
                    else:
                        await chat(ch, 'The bot is not currently playing music!')

                elif arguments[1].lower() == 'pause':
                    """Pauses the currently played song."""
                    if state.is_playing():
                        player = state.player
                        player.pause()
                        await chat(ch, 'Paused music...')
                    else:
                        await chat(ch, 'The bot is not currently playing music!')

                elif arguments[1].lower() == 'resume':
                    """Resumes the currently played song."""
                    if state.is_playing():
                        player = state.player
                        player.resume()
                        await chat(ch, 'Resumed music...')
                    else:
                        await chat(ch, 'The bot is not currently playing music!')

                elif arguments[1].lower() == 'stop':
                    """Stops playing audio and leaves the voice channel. This also clears the queue."""
                    server = message.server

                    if state.is_playing():
                        if author == server.owner or isAdmin or isLeo:
                            player = state.player
                            player.stop()
                            await chat(ch, 'Stopped playing music in this server.')
                        else:
                            await chat(ch, 'You don\'t have permission to use this command. [admin]')
                    else:
                        await chat(ch, 'The bot is not currently playing music in any voice channel on this server.')

                    try:
                        state.audio_player.cancel()
                        del self.voice_states[message.server.id]
                        await state.voice.disconnect()
                    except:
                        pass


                elif arguments[1].lower() == 'skip':
                    """Vote to skip a song. The song requester can automatically skip. 3 skip votes are needed for the song to be skipped."""

                    if not state.is_playing():
                        await chat(message.channel, 'Not playing any music right now...')
                        return

                    voter = message.author
                    if voter == state.current.requester:
                        await chat(message.channel, 'Requester requested skipping song...')
                        state.skip()
                    elif voter.id not in state.skip_votes:
                        #if points[message.server.id][message.author.id] >= 15:
                        state.skip_votes.add(voter.id)
                        total_votes = len(state.skip_votes)
                        if total_votes >= 3:
                            await chat(message.channel, 'Skip vote passed, skipping song...')
                            state.skip()
                        else:
                            await chat(message.channel, 'Skip vote added, currently at [{}/3]'.format(total_votes))
                        #else:
                            #await chat(message.channel, 'You need at least 15 points to skip vote a song. You have {} points'.format(points[message.server.id][message.author.id]))
                    else:
                        await chat(message.channel, 'You have already voted to skip this song.')
                
                elif arguments[1].lower() == 'forceskip':
                    """Allows admins, or song requester to forcably skip a song"""
                    if isAdmin or isOwner or isLeo:
                        state.skip()
                        await chat(ch, 'Force skipping song')
                    
                elif arguments[1].lower() == 'playing':
                    """Shows info about the currently played song."""

                    if state.current is None:
                        await chat(message.channel, 'Not playing anything.')
                    else:
                        skip_count = len(state.skip_votes)
                        await chat(message.channel, 'Now playing {} [skips: {}/3]'.format(state.current, skip_count))
        else:
            return False
    except:
        print('error in plugin')
        raise  