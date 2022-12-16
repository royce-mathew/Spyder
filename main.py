# Variables
prefix = "!"

# Dicts
guilds = {} # Stores Temp Data about Guilds
guild_data = {} # Stores Guild Configs
role_messages = {} # Roles for guilds

#     _____                                _        
#    |_   _|                              | |       
#      | |  _ __ ___   _ __    ___   _ __ | |_  ___ 
#      | | | '_ ` _ \ | '_ \  / _ \ | '__|| __|/ __|
#     _| |_| | | | | || |_) || (_) || |   | |_ \__ \
#     \___/|_| |_| |_|| .__/  \___/ |_|    \__||___/
#                     | |                           
#                     |_|                          
#
from Data import functions

import os
from dotenv import load_dotenv
import discord
from discord.ext import commands # We import commands and tasks from discord ext
import json

# Declare intents
intents = discord.Intents.all()
load_dotenv()

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


def initialize_guild_data(guild_obj):
    str_id: str = str(guild_obj.id) # Convert Guild ID to String

    if str_id not in guild_data: # Check if new guild joined
        guild_data[str_id] = {
            "stats_message_id": 0,
            "fact_channel_id": 0,
            "stats_channel_id": 0,
            "roles_message_id": 0
        }

    # Append All Roles Message Id 
    role_messages[guild_data[str_id]["roles_message_id"]] = str_id # Link Back to Guild

    # Temp Data
    guilds[guild_obj.id] = {
       "playing": False,
       "channel_id": None,
       "queue": [],
        "id": guild_obj.id,
        "obj": guild_obj
    }


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

    # Open the json file
    with open("Data/settings.json", "r") as settings_file:
        main_data: list = json.load(settings_file)
    
    for guild in client.guilds: # Loop through guilds

        initialize_guild_data(guild) # Initialize Temp Guild Data

    # Serialize the Json
    json_object = json.dumps(main_data, indent=4)

    # Open settings_file and write new guilds
    with open("Data/settings.json", "w") as settings_file:
        settings_file.write(json_object)


# On reaction Event
@client.event
async def on_raw_reaction_add(ctx):
    if ctx.message_id in role_messages:
        guild = discord.utils.find(lambda g: g.id == ctx.guild_id, client.guilds)
        role = discord.utils.find(lambda r: r.name == ctx.emoji.name, guild.roles)
        if role is not None:
            member = discord.utils.find(lambda m: m.id == ctx.user_id, guild.members)  # ctx.member
            await member.add_roles(role, reason="Spyder Reaction Roles")
            print(f"Added role {role.name} to {member.name}")


# Remove reaction Event
@client.event
async def on_raw_reaction_remove(ctx):
    # Check if the message id is the same as the roles_msg_id
    if ctx.message_id in role_messages:
        # Get guild, role and then remove the role
        local_guild_id = ctx.guild_id
        guild = discord.utils.find(lambda g: g.id == local_guild_id, client.guilds)
        role = discord.utils.find(lambda r: r.name == ctx.emoji.name, guild.roles)
        if role is not None:
            member = discord.utils.find(lambda m: m.id == ctx.user_id, guild.members)
            await member.remove_roles(role, reason="Spyder Reaction Roles")
            print(f"Removed role {role.name} from {member.name}")


async def convert_to_file(attach_array):
    attachments = []

    for x in attach_array:
        file = await x.to_file()
        index = list.index(attach_array, x)
        attachments.insert(index, file)

    return attachments


@client.event
async def on_message_delete(message):
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
async def on_message_edit(before, after):
    embed = functions.create_embed(
        "Message Edited",
        f"User `{before.author.display_name}` edited their message"
    )

    # Needed or the embed messes up
    bf = f"```{before.content if before.content else 'None'}```"
    af = f"```{after.content if after.content else 'None'}```"

    embed.add_field(name="Before", value=bf, inline=True)
    embed.add_field(name="After", value=af, inline=True)
    embed.add_field(name="Channel", value=f"```{before.channel.name}```")
    channel = discord.utils.get(before.guild.text_channels, name="chatlogs")

    # Convert attachments to file
    files = await convert_to_file(before.attachments)

    await channel.send(embed=embed, files=files)


# Add it to the guilds event
@client.event
async def on_guild_join(ctx):
    initialize_guild_data(ctx.guild)


#
#     _____                                                 _      
#    /  __ \                                               | |     
#    | /  \/  ___   _ __ ___   _ __ ___    __ _  _ __    __| | ___ 
#    | |     / _ \ | '_ ` _ \ | '_ ` _ \  / _` || '_ \  / _` |/ __|
#    | \__/\| (_) || | | | | || | | | | || (_| || | | || (_| |\__ ]
#     \____/ \___/ |_| |_| |_||_| |_| |_| \__,_||_| |_| \__,_||___/
#                                                                 

# Load Command
@client.command(name="Load", description="Loads a command")
# Check if the command runner is the bots owner
@commands.check(functions.is_bot_owner)
# Load function
async def load(ctx, extension):
    # Print and tell the console that the command was loaded
    print("Loaded" + extension)

    # Load the file
    client.load_extension(f'Commands.{extension}')

    # Create an embed and send it
    embed = functions.create_embed(
        "Loaded",
        f"Command `{extension}` has been loaded."
    )
    await ctx.send(embed)


# Unload Command
@client.command(name="Unload", description="Unloads a command")
# Check if the command can be ran and who is running the command
@commands.check(functions.is_bot_owner)
# Load function
async def unload(ctx, extension):
    # Tell the console that the command was unloaded
    print("Unloaded" + extension)

    # Unload the file
    client.unload_extension(f'Commands.{extension}')

    # Create a embed and send it
    embed = functions.create_embed(
        "Unloaded",
        f"Command `{extension}` has been unloaded."
    )
    await ctx.send(embed)


# Reload Command
@client.command(name="Reload", description="Reloads a command")
# Check if the command can be ran and who is running the command
@commands.check(functions.is_bot_owner)
# Reload function
async def reload(ctx, extension):
    # Tell the console that the command was reloaded
    print("Reloaded" + extension)

    # Reload the file 
    client.reload_extension(f'Commands.{extension}')

    # Make an embed and send it
    embed = functions.create_embed(
        "Reloaded",
        f"Command `{extension}` has been reloaded."
    )
    await ctx.send(embed)


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


# Gets all the files inside Commands folder using os.listdir,
# We can't use open("./Commands","r") because that only opens one file
for filename in os.listdir("./Commands"):
    if filename.endswith(".py"):
        # Take the length of the file name and remove 3 characters from that number
        name = len(filename) - 3
        # Remove the .py extension at the end when we send the filename to load
        client.load_extension(f'Commands.{filename[0:name]}')

# Run the token
client.run(os.getenv("DISCORD_TOKEN"))
