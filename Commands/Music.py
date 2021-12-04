from Data import functions

import time
import os
import threading

from discord.ext import commands, tasks
import discord
import yt_dlp

from main import guilds


class DeleteFilesClass:
    def __init__(self):
        self._queue = []

    def queue_delete_file(self):
        if len(self._queue) > 5:
            os.remove(self._queue[0]["audio_file"])
            self._queue.pop(0)

    def queue_file(self, file):
        self._queue.append(file)


# Create a class of DeleteFilesClass
DeleteFiles = DeleteFilesClass()


def wait_for_sound(guild):
    guild_voice = guild["voice"]
    # While the song is playing
    while guild_voice.is_playing() or guild_voice.is_paused():
        time.sleep(1)

    val_popped = guild["queue"].pop(0)
    DeleteFiles.queue_file(val_popped["audio_file"])
    guild["playing"] = False
    # guild_voice.stop()


def set_guild_video_data(url, guild):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'default_search': 'ytsearch',
        'noplaylist': True,
        'max_filesize': 100000000
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)  # Extract info from video
        guild["queue"].append({
            "audio_id": info_dict.get("id", None),
            "audio_title": info_dict.get('title', None),
            "audio_url": url,
            "audio_file": f"Cache/{info_dict.get('id', None)}.mp3"
        })
       #  print(guild["queue"])


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

    async def _play(self, guild):
        music_data = guild["queue"][0]
        channel = guild["channel"]
        print("Connecting")

        # await channel.connect()  # Connect to channel
        # Voice, lets the bot use voice in discord
        # guild["voice"] = discord.utils.get(self.client.voice_clients, guild=guild["obj"])
        download(guild, music_data["audio_url"])

        try:
            # Connect to voice again
            await channel.connect()
            guild["voice"] = discord.utils.get(self.client.voice_clients, guild=guild["obj"])

        except discord.errors.ClientException:
            pass  # Already connected to a voice channel
        guild["voice"].play(discord.FFmpegPCMAudio(music_data["audio_file"]))
        guild["playing"] = True

    @commands.command(name="play", description="Register for using commands that store data")
    async def play(self, ctx, url=None):
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

        # Checks if url was passed
        if url is None:
            await ctx.send(
                embed=functions.create_embed("No Url Passed.", "No url was passed to the command. Please try again."))
            return

        if guild["playing"]:
            # if its not in the same channel
            if guild["channel"] != channel:
                await ctx.send(
                    embed=functions.create_embed("Already Playing",
                                                 f"The bot is already playing on channel `{guild['channel_id']}`"))
                return

        message = await ctx.send(embed=functions.create_embed("Now Downloading!",
                                                        f"Song: `{url}` is now downloading!. The music will automatically start playing as soon as the download finishes."))

        set_guild_video_data(url, guild)
        guild["channel"] = channel

        # Check if there is a queue
        if len(guild["queue"]) > 1:
            await message.edit(embed=functions.create_embed("Added To Queue",
                                                        f"Song: `{guild['queue'][-1]['audio_title']}` was added to queue."))

        else:  # There is nothing in the queue
            await message.edit(embed=functions.create_embed("Now Playing!",
                                                        f"`{guild['queue'][0]['audio_title']}` is now playing!"))

    @commands.command(name="stop", description="Stops the current music. Disconnects the bot")
    @commands.check(functions.is_server_admin)
    async def stop(self, ctx):
        guild_id = ctx.guild.id
        if guilds[guild_id]["voice"] is not None:
            voice = guilds[guild_id]["voice"]
            await ctx.send(embed=functions.create_embed("Stopped playing song"))
            voice.stop()

    @commands.command(name="pause", description="Pauses the current music.")
    @commands.check(functions.is_server_admin)
    async def pause(self, ctx):
        guild_id = ctx.guild.id
        if guilds[guild_id]["voice"] is not None:
            voice = guilds[guild_id]["voice"]
            if voice.is_playing():
                await ctx.send(embed=functions.create_embed("Paused song"))
                voice.pause()
            else:
                await ctx.send(embed=functions.create_embed("Currently no audio is playing."))

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
    @commands.check(functions.is_server_admin)
    async def skip(self, ctx):
        guild_id = ctx.guild.id
        guild = guilds[guild_id]
        if guild["playing"] and guilds[guild_id]["voice"] is not None:
            voice = guilds[guild_id]["voice"]
            if len(guild["queue"]) > 1:
                print(len(guild["queue"]))
                await ctx.send(embed=functions.create_embed("Skipped song"))
                voice.stop()
                val_popped = guild["queue"].pop(0)
                DeleteFiles.queue_file(val_popped["audio_file"])
                await self._play(guild)
                # guild["playing"] = False
            else:
                await ctx.send(embed=functions.create_embed("Queue is empty", "Call the `stop` command to stop the bot from playing music"))
        else:
            await ctx.send(embed=functions.create_embed("No music currently playing."))


    @commands.command(name="queue", description="Shows the current Queue")
    async def queue(self, ctx):
        guild_id = ctx.guild.id
        main_string = ""
        index = 1
        for _list in guilds[guild_id]["queue"]:
            main_string += f"{index}. `{_list['audio_title']}`\n"
            index += 1

        await ctx.send(embed=functions.create_embed("Queue", main_string))

    # Keeps the queue updated
    @tasks.loop(seconds=1)
    async def audio_player_task(self):
        for guild_id, guild_list in guilds.items():
            # print(guild_id, guild_list)
            if not guild_list["playing"]:  # If the music object exists
                if len(guild_list["queue"]) != 0:  # if there are music objects in queue
                    # threading.Thread(target=self.music_obj.play, args=(self.music.queue[0]))
                    await self._play(guild_list)

                    try:
                        # Start the wait thread, wait for the music to finish
                        if not guild_list["wait_thread"].is_alive():
                            # Set a thread
                            guild_list["wait_thread"].start()
                    except KeyError:
                        guild_list["wait_thread"] = threading.Thread(target=wait_for_sound, args=(guild_list,),
                                                                     daemon=True)
                        guild_list["wait_thread"].start()
                    except RuntimeError:
                        pass

    @tasks.loop(minutes=15)
    async def file_deleter(self):
        DeleteFiles.queue_delete_file()

    @audio_player_task.before_loop
    async def before_stat(self):
        # Wait until the client is ready before starting the loop
        await self.client.wait_until_ready()


def setup(client):
    client.add_cog(Music(client))
