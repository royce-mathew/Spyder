#     _____                                _
#    |_   _|                              | |
#      | |  _ __ ___   _ __    ___   _ __ | |_  ___
#      | | | '_ ` _ \ | '_ \  / _ \ | '__|| __|/ __|
#     _| |_| | | | | || |_) || (_) || |   | |_ \__ \
#     \___/|_| |_| |_|| .__/  \___/ |_|    \__||___/
#                     | |
#                     |_|
#
import asyncio
import os

import discord
from discord.ext import commands  # We import commands and tasks from discord ext
from dotenv import load_dotenv

# Run __init__ method for Guild Data is ran in the json_handler class
from modules.data_handler import GuildData
from modules.help import Help
from modules.utils import create_embed

load_dotenv()  # Take environment variables from .env file

#     _____  _  _               _
#    /  __ \| |(_)             | |
#    | /  \/| | _   ___  _ __  | |_
#    | |    | || | / _ \| '_ \ | __|
#    | \__/\| || ||  __/| | | || |_
#     \____/|_||_| \___||_| |_| \__|
#


def get_prefix(client: discord.Client, message: discord.Message):
    return commands.when_mentioned_or(GuildData.get_value(message.guild, "prefix"))(client, message)


# @param attach_array: The array with the file attachments
async def convert_to_file(attach_array: list):
    attachments: list = []  # array containing attachments
    for x in attach_array:  # Loop through attachments parameter
        file = await x.to_file()  # Convert To File
        index = list.index(attach_array, x)
        attachments.insert(index, file)
    return attachments  # Return array with attachments


class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix=get_prefix,
            help_command=Help(),
            case_insensitive=True,
            intents=intents,
        )

    async def on_command_error(self, ctx, error):
        await ctx.reply(embed=create_embed("Error", description=error), ephemeral=True)

    #     _____                    _
    #    |  ___|                  | |
    #    | |__ __   __ ___  _ __  | |_  ___
    #    |  __|\ \ / // _ \| '_ \ | __|/ __|
    #    | |___ \ V /|  __/| | | || |_ \__ \
    #    \____/  \_/  \___||_| |_| \__||___/
    #

    async def on_ready(self):
        print("Bot is online")
        # Set presence
        await client.change_presence(
            activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(client.guilds)} servers")
        )

        async for guild in client.fetch_guilds():  # Loop through guilds
            GuildData.initialize_guild(guild)  # Initialize Temp Guild Data

    async def on_guild_join(self, ctx: commands.Context):
        await client.change_presence(
            activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(client.guilds)} servers")
        )
        GuildData.initialize_guild(ctx.guild)  # Initialize New Guild Data

    async def on_guild_remove(ctx: commands.Context):
        await client.change_presence(
            activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(client.guilds)} servers")
        )
        GuildData.delete_guild(ctx.guild)

    # On reaction Event
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        role_messages = GuildData.get_value(payload.guild_id, "role_messages")  # Get the Guild's role messages
        if payload.message_id in role_messages:
            guild = discord.utils.find(lambda g: g.id == payload.guild_id, client.guilds)
            role = discord.utils.find(lambda r: r.name == payload.emoji.name, guild.roles)
            if role is not None:
                await payload.member.add_roles(role, reason="Spyder Reaction Roles")
                print(f"Added role {role.name} to {payload.member.name}")

    # Remove reaction Event
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        # Check if the message id is the same as the roles_msg_id
        role_messages = GuildData.get_value(payload.guild_id, "role_messages")
        if payload.message_id in role_messages:
            guild = discord.utils.find(lambda g: g.id == payload.guild_id, client.guilds)
            role = discord.utils.find(lambda r: r.name == payload.emoji.name, guild.roles)
            if role is not None:
                await payload.member.remove_roles(role, reason="Spyder Reaction Roles")
                print(f"Removed role {role.name} from {payload.member.name}")

    async def on_message_delete(self, message: discord.Message):
        """
        Called when a message is deleted, this only runs when the message that is deleted is already cached inside the Bot
        Sends an embed to a log channel with the message contents
        """
        if message.bot == True:
            return  # Return if the message author is a bot
        log_channel_id = GuildData.get_value_default(
            message.guild, "chatlogs_channel_id", None
        )  # Get chatlog ID in database
        if log_channel_id is None:
            return  # Could try to set it so if a chat-logs channel exist here then use that channel

        log_channel = message.guild.get_channel(int(log_channel_id))
        if log_channel is None:  # Channel got deleted?
            return

        embed = create_embed(
            "Message Deleted:",
            f"User `{message.author.display_name}`'s deleted their message",
        )

        content = f"```{message.content if message.content else 'None'}```"
        embed.add_field(name="Message Content", value=content, inline=True)
        embed.add_field(name="Channel", value="```{}```".format(message.channel.name))

        # Convert attachments to file
        files = await convert_to_file(message.attachments)
        await log_channel.send(embed=embed, files=files)

    async def on_message_edit(before: discord.Message, after: discord.Message):
        """
        Called when a message is edited, sends an embed to a log channel with the before and after message
        """
        # Fix empty message embeds
        if before.content is None and after.content is None:
            return
        if before.bot == True:
            return

        log_channel_id = GuildData.get_value_default(before.guild, "chatlogs_channel_id", None)
        if log_channel_id is None:
            return

        log_channel = before.guild.get_channel(int(log_channel_id))
        if log_channel is None:
            return

        embed = create_embed("Message Edited", f"User `{before.author.display_name}` edited their message")

        before_message = f"```{before.content if before.content else 'None'}```"
        after_message = f"```{after.content if after.content else 'None'}```"

        embed.add_field(name="Before", value=before_message, inline=True)
        embed.add_field(name="After", value=after_message, inline=True)
        embed.add_field(name="Channel", value=f"`{before.channel.name}`")

        files = await convert_to_file(before.attachments)
        await log_channel.send(embed=embed, files=files)


# Create a client
client = Bot()


#
#     _____                                                 _
#    /  __ \                                               | |
#    | /  \/  ___   _ __ ___   _ __ ___    __ _  _ __    __| | ___
#    | |     / _ \ | '_ ` _ \ | '_ ` _ \  / _` || '_ \  / _` |/ __|
#    | \__/\| (_) || | | | | || | | | | || (_| || | | || (_| |\__ ]
#     \____/ \___/ |_| |_| |_||_| |_| |_| \__,_||_| |_| \__,_||___/
#


# Load Command : Loads the Cog Specified
@client.hybrid_command(name="load", with_app_command=True, description="Loads a command")
@commands.is_owner()
async def load(ctx: commands.Context, extension: str):
    await client.load_extension(f"cogs.{extension}")  # Load the file
    embed = create_embed("Loaded", f"Command `{extension}` has been loaded.")  # Create and send embed
    await ctx.send(embed)
    print(f"Loaded {extension}")  # Print and tell the console that the command was loaded


# Unload Command: Unloads the Cog specified
@client.hybrid_command(name="unload", with_app_command=True, description="Unloads a command")
@commands.is_owner()
async def unload(ctx: commands.Context, extension: str):  # Unload Method
    await client.unload_extension(f"cogs.{extension}")  # Unload the file
    embed = create_embed("Unloaded", f"Command `{extension}` has been unloaded.")
    await ctx.send(embed=embed)
    print(f"Unloaded {extension}")  # Tell the console that the command was unloaded


# Reload Command: Reloads the Cog Specified
@client.hybrid_command(name="reload", with_app_command=True, description="Reloads a command")
@commands.is_owner()
async def reload(ctx: commands.Context, extension: str):
    await client.reload_extension(f"cogs.{extension}")  # Reload the file
    embed = create_embed("Reloaded", f"Command `{extension}` has been reloaded.")
    await ctx.send(embed=embed)
    print(f"Reloaded {extension}")


@client.hybrid_command(name="sync", with_app_command=True, description="Sync App Commands Globally")
@commands.is_owner()
async def sync(ctx: commands.Context):
    try:
        client.tree.copy_global_to()
        synced = await client.tree.sync()
        await ctx.reply(embed=create_embed("Synced", f"Synced {len(synced)} command(s)"))
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        await ctx.reply(embed=create_embed("Unable to Sync", f"```{e}```"))


#
#     _____                       _                        _
#    /  __ \                     | |                      | |
#    | /  \/  ___    __ _        | |      ___    __ _   __| |  ___  _ __
#    | |     / _ \  / _` |       | |     / _ \  / _` | / _` | / _ \| '__|
#    | \__/\| (_) || (_| |       | |____| (_) || (_| || (_| ||  __/| |
#     \____/ \___/  \__, |       \_____/ \___/  \__,_| \__,_| \___||_|
#                    __/ |
#                   |___/
#


async def main():
    async with client:
        # Gets all the files inside Commands folder using os.listdir,
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                name = len(filename) - 3
                # Remove.py extension
                try:
                    await client.load_extension(f"cogs.{filename[0:name]}")
                    # Load the file
                except Exception as e:
                    print(f"Unable to load Cog: [{filename}] - {e}")

        await client.start(os.getenv("DISCORD_TOKEN"))  # Start the client


try:
    asyncio.run(main())
except KeyboardInterrupt:
    asyncio.run(client.close())
    print("Closed Program")
