import os
import discord
import random
import yt_dlp
import functools

from discord.ext import commands, tasks
from modules.utils import create_embed

music_guilds: dict = {}
guild_music_default: dict =  {
    "playing": False,
    "queue": [],
    "looped": False,
    "voice_channel": None,
    "currently_playing": None,
    "voice_client": None,
}

# Dictionaries
ytdl_options = { # Youtube-DL+ Options
    'format': 'bestaudio/best',
    'default_search': 'ytsearch',
    'verbose': False, # Debug information
    'noplaylist': True,
    'max_filesize': 100000000
}
# FFMPEG Options
ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

def get_video_data(url, guild_data):
    with yt_dlp.YoutubeDL(ytdl_options) as ydl:
        info_dict = ydl.extract_info(url, download=False)  # Extract info from video
        return {
            "audio_id": info_dict.get("id", None),
            "audio_title": info_dict.get('title', None),
            "audio_url": info_dict.get('url', None),
            "audio_duration": info_dict.get('duration', None),
        }


class Music(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.client.guilds:
            music_guilds[guild.id] = guild_music_default

        self.audio_player_task.start()

    @commands.Cog.listener() # Set listener for guild join in Cog
    async def on_guild_join(ctx: commands.Context):
        music_guilds[ctx.guild.id] = guild_music_default


    async def connect_to_voice(self, guild, guild_data):
        try:
            await guild_data["voice_channel"].connect()
            guild_data["voice_client"] = discord.utils.get(self.client.voice_clients, guild=guild)
            print(guild)
        except (discord.errors.ClientException,KeyError) as Err:
            print(Err)


    @commands.command(name="Play", description="Register for using commands that store data", aliases=["p"])
    async def play(self, ctx, *args):
        # Find the voice state that the author is in
        voice_state = ctx.author.voice
        # If the member is not in a voice channel
        if voice_state is None:
            await ctx.send(embed=create_embed("Error", "You are not currently in a voice channel. Please join a voice channel to play music"))
            return

        # Get the channel the author is in
        channel = voice_state.channel # Get author voice channel
        guild_data = music_guilds[ctx.guild.id] # Get guild temp list

        url = " ".join(args)

        # Checks if url was passed
        if len(args) == 0:
            await ctx.send(embed=create_embed("No Url Passed.", "No url was passed to the command. Please try again."))
            return

        try: # Check bot's current voice channel
            if guild_data["voice_client"].is_playing() and guild_data["voice_channel"] != channel:  # If its already playing music not in the same channel
                # If the author's channel is not the bot's channel
                await ctx.send(embed=create_embed("Already Playing", f"The bot is already playing on channel `{guild_data['channel'].name}`"))
                return
        except (KeyError, AttributeError): # Currently not in a voice client
            pass

        message = await ctx.send(embed=create_embed("Setting Song!",  f"Song: `{url}` is now being extracted!. The music will automatically start playing as soon as the extraction finishes."))
        video_data = get_video_data(url, guild_data) # Get the video data
        
        if video_data["audio_duration"] > 3600: # Bigger than 1 hour
            await message.edit(embed=create_embed("Error", f"Song: `{video_data['audio_title']}` can not be played as its duration is too long. \n\nMax Duration is : `1 hour`."))
            return
            
        # Check if we are already playing music
        if len(guild_data["queue"]) > 0 or guild_data["currently_playing"] is not None:
            await message.edit(embed=create_embed("Added To Queue", f"Song: `{video_data['audio_title']}` was added to queue."))
        # Not already playing music, song will be added to queue
        else:
            await message.edit(embed=create_embed("Now Playing!", f"`{video_data['audio_title']}` is now playing!"))

        if guild_data["voice_client"] is None:
            guild_data["voice_channel"] = channel # Set the voice channel
            await self.connect_to_voice(ctx.guild, guild_data) # Join the voice channel
        guild_data["queue"].append(video_data) # Adding to queue should automatically make it join the voice channel
            


    @commands.command(name="Stop", description="Stops the current music. Disconnects the bot", aliases=["disconnect"])
    @commands.has_permissions(administrator=True)
    async def stop(self, ctx):
        try:
            guild_data = music_guilds[ctx.guild.id]
            guild_data["queue"].clear() # Empty the queue
            guild_data["currently_playing"] = None
            await guild_data["voice_client"].disconnect() # Disconnect Voice Client
            await ctx.send(embed=create_embed("Stopped playing song"))
        except (KeyError, AttributeError):
            await ctx.send(embed=create_embed("Error", "The client is not currently in a voice channel."))

    @commands.command(name="Pause", description="Pauses the current music.")
    async def pause(self, ctx):
        guild_data = music_guilds[ctx.guild.id]
        try:
            voice = guild_data["voice_client"]
            if voice.is_playing():
                await ctx.send(embed=create_embed("Paused song"))
                voice.pause()
            elif voice.is_paused():
                await ctx.send(embed=create_embed("Music is already paused. Run the `resume` command to start playing the music!"))
            else:
                await ctx.send(embed=create_embed("Currently no audio is playing."))
        except (KeyError, AttributeError) as Err:
            await ctx.send(embed=create_embed("Error", f"Bot is not currently in a voice channel. Run the `play` command to play music."))

    @commands.command(name="resume", description="Resumes the current music.", aliases=["unpause"])
    async def resume(self, ctx):
        guild_data = music_guilds[ctx.guild.id]
        try:
            voice_client = guild_data["voice_client"]
            if voice_client.is_paused():
                await ctx.send(embed=create_embed("Resumed Song"))
                voice_client.resume()
            else:
                await ctx.send(embed=create_embed("Music is not currently paused."))
        except (KeyError, AttributeError) as Err:
            await ctx.send(embed=create_embed("Error", "Bot is not currently in a voice channel. Run the `play` command to play music."))

    @commands.command(name="Skip", description="Skip the current music.")
    async def skip(self, ctx):
        guild_data = music_guilds[ctx.guild.id]
        try:
            guild_data["voice_client"].stop() # Stopping the song automatically goes to the next song
            await ctx.send(embed=create_embed("Skipped", "Current song was skipped"))

        except (KeyError, AttributeError) as Err:
            await ctx.send(embed=create_embed("Error", "Bot is not currently in a voice channel. Run the `play` command to play music."))

    @commands.command(name="Queue", description="Shows the current Queue", aliases=["q"])
    async def queue(self, ctx):
        local_guild = music_guilds[ctx.guild.id]
        try:
            main_string = ""
            index = 2
            
            main_string += f"**1.** `{local_guild['currently_playing']['audio_title']}`\n"

            for song in local_guild["queue"]:
                main_string += f"{index}. `{song['audio_title']}`\n"
                index += 1

            await ctx.send(embed=create_embed("Queue", main_string))

        except (KeyError, TypeError) :
            await ctx.send(embed=create_embed("Queue", "There is nothing in Queue"))


    @commands.command(name="Playing", description="Shows the music that's currently playing",  aliases=["currently_playing", "currentlyplaying"])
    async def playing(self, ctx):
        guild_data = music_guilds[ctx.guild.id]
        try:
            currently_playing = guild_data["currently_playing"]
            embed = create_embed("Currently Playing")
            for key, value in currently_playing.items():
                embed.add_field(
                    name=key,
                    value=value,
                    inline=True
                )
                    

            await ctx.send(embed=embed)

        except (KeyError, AttributeError):
            await ctx.send(embed=create_embed("Error",  "There is no music currently playing. Run the `play` command to play music."))

    @commands.command(name="Loop", description="Loops the current music")
    async def loop(self, ctx):
        try:
            music_guilds[ctx.guild.id]["looped"] = not music_guilds[ctx.guild.id]["looped"]
            await ctx.send(embed=create_embed("Set Loop", f'Loop is set to `{music_guilds[ctx.guild.id]["looped"]}`'))
        except KeyError:
            music_guilds[ctx.guild.id]["looped"] = True
            await ctx.send(embed=create_embed("Looping!",  f"Current song will be looped!"))

    
    @commands.command(name="Shuffle", description="Shuffle the current Queue")
    async def shuffle(self, ctx):
        random.shuffle(music_guilds[ctx.guild.id]["queue"]) # Deprecated in 3.9, Removed in 3.11
        await ctx.send(embed=create_embed("Shuffled", f'The Queue was shuffled.`'))

    # Keeps the queue updated
    @tasks.loop(seconds=2)
    async def audio_player_task(self):
        for guild_id, guild_list in music_guilds.items():
            try:
                voice_client = guild_list["voice_client"] # Try accessing the voice channel

                if not voice_client.is_playing() and not voice_client.is_paused(): # If we aren't already playing
                    if guild_list["currently_playing"] is not None and guild_list["looped"] == False:
                        guild_list["currently_playing"] = None;

                    if len(guild_list["queue"]) > 0 and guild_list["currently_playing"] is None:  # if there are music objects in queue
                        music_data = guild_list["queue"][0]
                        await self.connect_to_voice(await self.client.fetch_guild(guild_id), guild_list)
                        voice_client.play(discord.FFmpegPCMAudio(music_data["audio_url"], **ffmpeg_options)) 
                        guild_list["currently_playing"] = guild_list["queue"].pop(0) # Delete current song From Queue
                    else:
                        guild_list["queue"].clear() # Empty the queue
                        guild_list["currently_playing"] = None
                        await guild_list["voice_client"].disconnect() # Disconnect Voice Client

            except (KeyError, AttributeError) as Err:
                # print(Err)
                pass
    
    @audio_player_task.before_loop
    async def before_audio_loop(self):
        # Wait until the client is ready before starting the loop
        await self.client.wait_until_ready()
        for _, guild_list in music_guilds.items():
            guild_list["looped"] = False





async def setup(client):
    await client.add_cog(Music(client))
