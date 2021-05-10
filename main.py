# Variables
maincolor = 0x000
prefix = "!"
guild_id = 572487931327938593
stats_message_id = 836999076167548998
stats_channel_id = 836647371588239363

#     _____                                _        
#    |_   _|                              | |       
#      | |  _ __ ___   _ __    ___   _ __ | |_  ___ 
#      | | | '_ ` _ \ | '_ \  / _ \ | '__|| __|/ __|
#     _| |_| | | | | || |_) || (_) || |   | |_ \__ \
#     \___/|_| |_| |_|| .__/  \___/ |_|    \__||___/
#                     | |                           
#                     |_|                          
#

import os
# Import functions file so we can access functions globally
import functions

import discord
# We import commands and tasks from discord ext
from discord.ext import commands

# Declare intents
intents = discord.Intents.all()

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


roles_msg_id = 789644217634127883


# On reaction Event
@client.event
async def on_raw_reaction_add(ctx):
    if ctx.message_id == roles_msg_id:
        guild_id = ctx.guild_id
        guild = discord.utils.find(lambda g: g.id == guild_id, client.guilds)
        role = discord.utils.find(lambda r: r.name == ctx.emoji.name, guild.roles)
        if role is not None:
            member = discord.utils.find(lambda m: m.id == ctx.user_id, guild.members)  # ctx.member
            await member.add_roles(role, reason="Spyder Reaction Roles")
            print(f"Added role {role.name} to {member.name}")


# Remove reaction Event
@client.event
async def on_raw_reaction_remove(ctx):
    # Check if the message id is the same as the roles_msg_id
    if ctx.message_id == roles_msg_id:
        # Get guild, role and then remove the role
        guild_id = ctx.guild_id
        guild = discord.utils.find(lambda g: g.id == guild_id, client.guilds)
        role = discord.utils.find(lambda r: r.name == ctx.emoji.name, guild.roles)
        if role is not None:
            member = discord.utils.find(lambda m: m.id == ctx.user_id, guild.members)
            await member.remove_roles(role, reason="Spyder Reaction Roles")
            print(f"Removed role {role.name} from {member.name}")


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
    embed = discord.Embed(
        colour=maincolor
    )
    embed.title = "**Loaded**"
    embed.description = f"Command `{extension}` has been loaded."
    embed.timestamp = ctx.message.created_at
    embed.set_footer(text="Spyder", icon_url=client.user.avatar_url)
    await ctx.message.channel.send(embed)


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
    embed = discord.Embed(
        colour=maincolor
    )
    embed.title = "**Unloaded**"
    embed.description = f"Command `{extension}` has been unloaded."
    embed.timestamp = ctx.message.created_at
    embed.set_footer(text="Spyder", icon_url=client.user.avatar_url)
    await ctx.message.channel.send(embed)


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
    embed = discord.Embed(
        colour=maincolor
    )
    embed.title = "**Reloaded**"
    embed.description = f"Command `{extension}` has been reloaded."
    embed.timestamp = ctx.message.created_at
    embed.set_footer(text="Spyder", icon_url=client.user.avatar_url)
    await ctx.message.channel.send(embed)


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
client.run("NzMwMTcxMTkxNjMyOTg2MjM0.XwuZzg.fVsgMOaq2VUaSdZXmGVDIBuqxpk")
