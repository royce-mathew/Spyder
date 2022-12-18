# Variables
prefix = "!"

#     _____                                _        
#    |_   _|                              | |       
#      | |  _ __ ___   _ __    ___   _ __ | |_  ___ 
#      | | | '_ ` _ \ | '_ \  / _ \ | '__|| __|/ __|
#     _| |_| | | | | || |_) || (_) || |   | |_ \__ \
#     \___/|_| |_| |_|| .__/  \___/ |_|    \__||___/
#                     | |                           
#                     |_|                          
#
from modules import functions

import asyncio
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands # We import commands and tasks from discord ext

# Run __init__ method for Guild Data is ran in the json_handler class
from modules.data_handler import GuildData, roles_dict

intents = discord.Intents.all() # Declare Intents
load_dotenv() # Take enviornment variables from .env file

#     _____  _  _               _   
#    /  __ \| |(_)             | |  
#    | /  \/| | _   ___  _ __  | |_ 
#    | |    | || | / _ \| '_ \ | __|
#    | \__/\| || ||  __/| | | || |_ 
#     \____/|_||_| \___||_| |_| \__|
#                                  


# Create a client
client = commands.Bot(command_prefix=prefix, case_insensitive=True, intents=intents)
# Remove the help command so we can send a custom help command
client.remove_command('help')



#     _____                    _
#    |  ___|                  | |       
#    | |__ __   __ ___  _ __  | |_  ___ 
#    |  __|\ \ / // _ \| '_ \ | __|/ __|
#    | |___ \ V /|  __/| | | || |_ \__ \
#    \____/  \_/  \___||_| |_| \__||___/
#                                       


# On ready
@client.event
async def on_ready():
    print("Bot is online")
    for guild in client.guilds: # Loop through guilds
        GuildData.initialize_guild(guild) # Initialize Temp Guild Data


# On reaction Event
@client.event
async def on_raw_reaction_add(ctx: commands.Context):
    if ctx.message_id in roles_dict:
        guild = discord.utils.find(lambda g: g.id == ctx.guild_id, client.guilds)
        role = discord.utils.find(lambda r: r.name == ctx.emoji.name, guild.roles)
        if role is not None:
            member = discord.utils.find(lambda m: m.id == ctx.user_id, guild.members)  # ctx.member
            await member.add_roles(role, reason="Spyder Reaction Roles")
            print(f"Added role {role.name} to {member.name}")


# Remove reaction Event
@client.event
async def on_raw_reaction_remove(ctx: commands.Context):
    # Check if the message id is the same as the roles_msg_id
    if ctx.message_id in roles_dict:
        # Get guild, role and then remove the role
        local_guild_id = ctx.guild_id
        guild = discord.utils.find(lambda g: g.id == local_guild_id, client.guilds)
        role = discord.utils.find(lambda r: r.name == ctx.emoji.name, guild.roles)
        if role is not None:
            member = discord.utils.find(lambda m: m.id == ctx.user_id, guild.members)
            await member.remove_roles(role, reason="Spyder Reaction Roles")
            print(f"Removed role {role.name} from {member.name}")


# @param attach_array: The array with the file attachments
async def convert_to_file(attach_array: list):
    attachments: list = [] # array containingn attachments

    for x in attach_array: # Loop through attachments parameter
        file = await x.to_file() # Convert To File
        index = list.index(attach_array, x) 
        attachments.insert(index, file)

    return attachments # Return array with attachments


@client.event
async def on_message_delete(message: discord.Message):
    embed = functions.create_embed(
        "Message Deleted:",
        f"User `{message.author.display_name}`'s deleted their message"
    )

    content = f"```{message.content if message.content else ''}```"
    embed.add_field(name="Message Content", value=content, inline=True)
    embed.add_field(name="Channel", value="```{}```".format(message.channel.name))
    channel = discord.utils.get(message.guild.text_channels, name="chatlogs")

    # Convert attachments to file
    files = await convert_to_file(message.attachments)

    await channel.send(embed=embed, files=files)


@client.event
async def on_message_edit(before: discord.Message, after: discord.Message):
    embed = functions.create_embed(
        "Message Edited",
        f"User `{before.author.display_name}` edited their message"
    )

    # Needed or the embed messes up
    bf = f"```{before.content if before.content else 'None'}```"
    af = f"```{after.content if after.content else 'None'}```"

    embed.add_field(name="Before", value=bf, inline=True)
    embed.add_field(name="After", value=af, inline=True)
    embed.add_field(name="Channel", value=f"```{before.channel.name}`guilds``")
    channel = discord.utils.get(before.guild.text_channels, name="chatlogs")

    # Convert attachments to file
    files = await convert_to_file(before.attachments)

    await channel.send(embed=embed, files=files)


# Add it to the guilds event
@client.event
async def on_guild_join(ctx: commands.Context):
    GuildData.initialize_guild(ctx.guild) # Initialize New Guild Data


#
#     _____                                                 _      
#    /  __ \                                               | |     
#    | /  \/  ___   _ __ ___   _ __ ___    __ _  _ __    __| | ___ 
#    | |     / _ \ | '_ ` _ \ | '_ ` _ \  / _` || '_ \  / _` |/ __|
#    | \__/\| (_) || | | | | || | | | | || (_| || | | || (_| |\__ ]
#     \____/ \___/ |_| |_| |_||_| |_| |_| \__,_||_| |_| \__,_||___/
#                                                                 

# Load Command : Loads the Cog Specified
@client.command(name="Load", description="Loads a command")
@commands.check(functions.is_bot_owner) # Check bot owner
async def load(ctx: commands.Context, extension: str):
    extension = extension.lower().capitalize() # Reformat Extension
    print(f"Loaded {extension}") # Print and tell the console that the command was loaded
    await client.load_extension(f'cogs.{extension}') # Load the file
    embed = functions.create_embed("Loaded", f"Command `{extension}` has been loaded.") # Create and send embed
    await ctx.send(embed)


# Unload Command: Unloads the Cog specified
@client.command(name="Unload", description="Unloads a command")
@commands.check(functions.is_bot_owner)
async def unload(ctx: commands.Context, extension: str): # Unload Method
    extension = extension.lower().capitalize()
    print(f"Unloaded {extension}")  # Tell the console that the command was unloaded
    await client.unload_extension(f'cogs.{extension}') # Unload the file
    embed = functions.create_embed("Unloaded", f"Command `{extension}` has been unloaded.")
    await ctx.send(embed=embed)


# Reload Command: Reloads the Cog Specified
@client.command(name="Reload", description="Reloads a command")
@commands.check(functions.is_bot_owner)
async def reload(ctx: commands.Context, extension: str):
    extension = extension.lower().capitalize()
    print(f"Reloaded {extension}")    
    await client.reload_extension(f'cogs.{extension}') # Reload the file 
    embed = functions.create_embed("Reloaded", f"Command `{extension}` has been reloaded.")
    await ctx.send(embed=embed)


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
                name = len(filename) - 3; # Remove.py extension
                await client.load_extension(f'cogs.{filename[0:name]}'); # Load the file

        await client.start(os.getenv("DISCORD_TOKEN")) # Start the client 


asyncio.run(main());