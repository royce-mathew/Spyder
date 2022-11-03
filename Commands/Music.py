import os
import discord
import yt_dlp

from discord.ext import commands, tasks
from Data import functions
from main import guilds


class DeleteFilesClass:
    def __init__(self):
        self._queue = []

    def queue_delete_file(self):
        if len(self._queue) > 1:
            os.remove(self._queue[0])
            print(f"Deleting {self._queue[0]}")
            self._queue.pop(0)

    def queue_file(self, file):
        self._queue.append(file)

    def delete_all(self):
        for x in self._queue:
            os.remove(x)
        self._queue.clear()


# Create a class of DeleteFilesClass
DeleteFiles = DeleteFilesClass()


def set_guild_video_data(url, guild):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'default_search': 'ytsearch',
        'verbose': True,
        'noplaylist': True,
        'max_filesize': 100000000
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)  # Extract info from video
        guild["queue"].append({
            "audio_id": info_dict.get("id", None),
            "audio_title": info_dict.get('title', None),
            "audio_url": url,
            "audio_file": f"Cache/{info_dict.get('id', None)}.mp3",
            "audio_duration": info_dict.get('duration', None),
        })


def download(guild, url):
    # Options to parse to youtube_dl
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': f"Cache/{guild['queue'][-1]['audio_id']}.mp3",
        'default_search': 'ytsearch',
        'noplaylist': True,
        'max_filesize': 100000000
    }

    if not os.path.isfile(f"Cache/{guild['queue'][-1]['audio_id']}.mp3"):
        print("Does not exist, downloading")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])


class Music(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.audio_player_task.start()
        self.file_deleter.start()

    async def connect_to_voice(self, guild):
        try:
            await guild["channel"].connect()
            guild["voice"] = discord.utils.get(self.client.voice_clients, guild=guild["obj"])
        except discord.errors.ClientException:
            pass
        except KeyError:
            pass

    async def _play(self, guild):
        music_data = guild["queue"][0]
        # channel = guild["channel"]
        # print("Connecting")

        # await channel.connect()  # Connect to channel
        # Voice, lets the bot use voice in discord
        # guild["voice"] = discord.utils.get(self.client.voice_clients, guild=guild["obj"])
        download(guild, music_data["audio_url"])
        await self.connect_to_voice(guild)
        guild["voice"].play(discord.FFmpegPCMAudio(music_data["audio_file"]))

    @commands.command(name="play", description="Register for using commands that store data",
                      aliases=["p"])
    async def play(self, ctx, *args):
        # Find the voice state that the author is in
        voice_state = ctx.author.voice
        # If the member is not in a voice channel
        if voice_state is None:
            await ctx.send(
                embed=functions.create_embed("Error", "You are not currently in a voice channel. Please join a "
                                                      "voice channel to play music"))
            return

        # Get the channel the author is in
        channel = ctx.author.voice.channel
        guild = guilds[ctx.guild.id]

        url = " ".join(args)

        # Checks if url was passed
        if len(args) == 0:
            await ctx.send(
                embed=functions.create_embed("No Url Passed.", "No url was passed to the command. Please try again."))
            return

        try:
            if guild["voice"].is_playing():  # If its already playing music
                # if its not in the same channel
                if guild["channel"] != channel:  # If the author's channel is not the bot's channel
                    await ctx.send(
                        embed=functions.create_embed("Already Playing",
                                                     f"The bot is already playing on channel `{guild['channel'].name}`"))
                    return
        except KeyError:
            pass

        message = await ctx.send(embed=functions.create_embed("Now Downloading!",
                                                              f"Song: `{url}` is now downloading!. The music will automatically start playing as soon as the download finishes."))

        set_guild_video_data(url, guild)
        guild["channel"] = channel
        await self.connect_to_voice(guild)

        # Check if there is a queue
        if len(guild["queue"]) > 0:
            try:
                if guild["queue"][-1]["audio_duration"] > 3600:
                    await message.edit(embed=functions.create_embed("Error",
                                                                    f"Song: `{guild['queue'][-1]['audio_title']}` can not be played as its duration is too long. \n\nMax Duration is : `1 hour`."))
                    return

                await message.edit(embed=functions.create_embed("Added To Queue",
                                                                f"Song: `{guild['queue'][-1]['audio_title']}` was added to queue."))
            except TypeError:
                await message.edit(embed=functions.create_embed("Error",
                                                                f"An error occured, guild['queue'][-1]['audio_duration'] could not be accessed"))
        else:  # There is nothing in the queue
            await message.edit(embed=functions.create_embed("Now Playing!",
                                                            f"`{guild['queue'][0]['audio_title']}` is now playing!"))

    @commands.command(name="stop", description="Stops the current music. Disconnects the bot")
    @commands.check(functions.is_server_admin)
    async def stop(self, ctx):
        guild = guilds[ctx.guild.id]
        guild["queue"].clear() # Empty the queue
        DeleteFiles.delete_all()

        try:
            voice = guild["voice"]
            await ctx.send(embed=functions.create_embed("Stopped playing song"))
            await voice.disconnect()
        except KeyError:
            await ctx.send(embed=functions.create_embed("Error", "The client is not currently in a voice channel."))

    @commands.command(name="pause", description="Pauses the current music.")
    @commands.check(functions.is_server_admin)
    async def pause(self, ctx):
        guild_id = ctx.guild.id
        try:
            voice = guilds[guild_id]["voice"]
            if voice.is_playing():
                await ctx.send(embed=functions.create_embed("Paused song"))
                voice.pause()
            else:
                await ctx.send(embed=functions.create_embed("Currently no audio is playing."))
        except KeyError:
            await ctx.send(embed=functions.create_embed("Error", "The client is not currently in a voice channel."))

    @commands.command(name="resume", description="Resumes the current music.")
    @commands.check(functions.is_server_admin)
    async def resume(self, ctx):
        guild_id = ctx.guild.id
        if guilds[guild_id]["voice"] is not None:
            voice = guilds[guild_id]["voice"]
            if voice.is_paused():
                await ctx.send(embed=functions.create_embed("Resumed Song"))
                voice.resume()
            else:
                await ctx.send(embed=functions.create_embed("Music is not currently paused."))

    @commands.command(name="skip", description="Skip the current music.")
    # @commands.check(functions.is_server_admin)
    async def skip(self, ctx):
        guild_id = ctx.guild.id
        guild = guilds[guild_id]
        try:
            voice = guild["voice"]
            if len(guild["queue"]) > 0:
                voice.stop()
                # Queue to Delete
                DeleteFiles.queue_file(guild["queue"].pop(0)["audio_file"])
                if len(guild["queue"]) > 0:
                    print(f"Before{guild['queue']}")
                    guild["currently_playing"] = guild["queue"][0]
                    print(f"After{guild['queue']}")
                await ctx.send(embed=functions.create_embed("Skipped",
                                                            "Current song was skipped"))
            else:
                await ctx.send(embed=functions.create_embed("Queue is empty",
                                                            "Call the `stop` command to stop the bot from playing music"))
        except KeyError:
            await ctx.send(embed=functions.create_embed("Error",
                                                        "Bot is not currently in a voice channel. Run the `play` command to play music."))

    @commands.command(name="queue", description="Shows the current Queue",
                      aliases=["q"])
    async def queue(self, ctx):
        guild_id = ctx.guild.id
        main_string = ""
        index = 1
        for _list in guilds[guild_id]["queue"]:
            main_string += f"{index}. `{_list['audio_title']}`\n"
            index += 1

        await ctx.send(embed=functions.create_embed("Queue", main_string))

    @commands.command(name="playing", description="Shows the music that's currently playing",
                      aliases=["currently_playing", "currentlyplaying"])
    async def playing(self, ctx):
        guild_id = ctx.guild.id
        guild = guilds[guild_id]
        try:
            currently_playing = guild["currently_playing"]
            embed = functions.create_embed("Currently Playing")
            for key, value in currently_playing.items():
                if key != "audio_file":
                    embed.add_field(
                        name=key,
                        value=value,
                        inline=True
                    )

            await ctx.send(embed=embed)

        except KeyError:
            await ctx.send(embed=functions.create_embed("Error",
                                                        "There is no music currently playing. Run the `play` command to play music."))

    @commands.command(name="loop", description="Loops the current music")
    async def loop(self, ctx):
        try:
            guilds[ctx.guild.id]["looped"] = not guilds[ctx.guild.id]["looped"]
            await ctx.send(embed=functions.create_embed("Set Loop",
                                            f'Loop is set to `{guilds[ctx.guild.id]["looped"]}`'))
        except KeyError:
            guilds[ctx.guild.id]["looped"] = True
            await ctx.send(embed=functions.create_embed("Looping!",
                                            f"Current song will be looped!"))

    # Keeps the queue updated
    @tasks.loop(seconds=1)
    async def audio_player_task(self):
        for guild_id, guild_list in guilds.items():
            try:
                # await self.connect_to_voice(guild_list)
                guild_voice = guild_list["voice"]
                if not guild_voice.is_playing():
                    if len(guild_list["queue"]) > 0:  # if there are music objects in queue
                        await self._play(guild_list)  # Play the sound

                        if not guild_list["looped"]:
                            # Queue to Delete
                            DeleteFiles.queue_file(guild_list["queue"].pop(0)["audio_file"])
                            guild_list["currently_playing"] = guild_list["queue"][0]

            except KeyError:
                pass

    @tasks.loop(minutes=10)
    async def file_deleter(self):
        DeleteFiles.queue_delete_file()

    @audio_player_task.before_loop
    async def before_stat(self):
        # Wait until the client is ready before starting the loop
        await self.client.wait_until_ready()
        for guild_id, guild_list in guilds.items():
            guild_list["looped"] = False



def setup(client):
    pass
    # client.add_cog(Music(client))
