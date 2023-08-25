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
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(self.guilds)} servers"))

        async for guild in self.fetch_guilds():  # Loop through guilds
            GuildData.initialize_guild(guild)  # Initialize Temp Guild Data

    async def on_guild_join(self, ctx: commands.Context):
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(self.guilds)} servers"))
        GuildData.initialize_guild(ctx.guild)  # Initialize New Guild Data

    async def on_guild_remove(ctx: commands.Context):
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(self.guilds)} servers"))
        GuildData.delete_guild(ctx.guild)

    # On reaction Event
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        role_messages = GuildData.get_value(payload.guild_id, "role_messages")  # Get the Guild's role messages
        if payload.message_id in role_messages:
            guild = discord.utils.find(lambda g: g.id == payload.guild_id, self.guilds)
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

        embed = create_embed(
            "Message Deleted:",
            f"User `{message.author.name}`'s deleted their message",
        )

        content = f"```{message.content if message.content else 'None'}```"
        embed.add_field(name="Message Content", value=content, inline=True)
        embed.add_field(name="Channel", value="```{}```".format(message.channel.name))

        # Convert attachments to file
        files = await convert_to_file(message.attachments)
        await GuildData.send_chat_log_message(message.guild, embed, files)

    async def on_message_edit(before: discord.Message, after: discord.Message):
        """
        Called when a message is edited, sends an embed to a log channel with the before and after message
        """
        # Fix empty message embeds
        if before.content is None and after.content is None:
            return
        if before.bot == True:
            return

        embed = create_embed("Message Edited", f"User `{before.author.name}` edited their message")

        before_message = f"```{before.content if before.content else 'None'}```"
        after_message = f"```{after.content if after.content else 'None'}```"

        embed.add_field(name="Before", value=before_message, inline=True)
        embed.add_field(name="After", value=after_message, inline=True)
        embed.add_field(name="Channel", value=f"`{before.channel.name}`")

        files = await convert_to_file(before.attachments)
        await GuildData.send_chat_log_message(before.guild, embed, files)


# Create a client
client = Bot()


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

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        asyncio.run(client.close())
        print("Closed Program")
