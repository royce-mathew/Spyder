# Variables
maincolor = 0x000



#     _____                                _        
#    |_   _|                              | |       
#      | |  _ __ ___   _ __    ___   _ __ | |_  ___ 
#      | | | '_ ` _ \ | '_ \  / _ \ | '__|| __|/ __|
#     _| |_| | | | | || |_) || (_) || |   | |_ \__ \
#     \___/|_| |_| |_|| .__/  \___/ |_|    \__||___/
#                     | |                           
#                     |_|                          
#
import discord, os
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
client = commands.Bot(command_prefix="/", case_insensitive=True, intents=intents)
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


# On reaction Event
@client.event
async def on_raw_reaction_add(payload):
    msgid = payload.message_id
    if msgid == 789644217634127883:
        guild_id = payload.guild_id
        guild = discord.utils.find(lambda g : g.id == guild_id, client.guilds)
        role = discord.utils.find(lambda r : r.name == payload.emoji.name, guild.roles)
        if role is not None:
            member = discord.utils.find(lambda m : m.id == payload.user_id, guild.members) # payload.member
            await member.add_roles(role, reason="Spyder Reaction Roles")
            print(f"Added role {role.name} to {member.name}")
            return

# Remove reaction Event
@client.event
async def on_raw_reaction_remove(payload):
    msgid = payload.message_id
    if msgid == 789644217634127883:
        guild_id = payload.guild_id
        guild = discord.utils.find(lambda g : g.id == guild_id, client.guilds)
        role = discord.utils.find(lambda r: r.name == payload.emoji.name, guild.roles)
        if role is not None:
            member = discord.utils.find(lambda m : m.id == payload.user_id, guild.members)
            await member.remove_roles(role, reason="Spyder Reaction Roles")
            print(f"Removed role {role.name} from {member.name}")
            return


#    
#     _____                    _    _                    
#    |  ___|                  | |  (_)                   
#    | |_  _   _  _ __    ___ | |_  _   ___   _ __   ___ 
#    |  _|| | | || '_ \  / __|| __|| | / _ \ | '_ \ / __|
#    | |  | |_| || | | || (__ | |_ | || (_) || | | |\__ ]
#    \_|   \__,_||_| |_| \___| \__||_| \___/ |_| |_||___/
#                                                       



# Checks
def IsBotOwner(ctx):
    return ctx.message.author.id == 461509995444437003
        
def IsServerOwner(ctx):
    return ctx.message.author == ctx.message.guild.owner

#    
#     _____                                                 _      
#    /  __ \                                               | |     
#    | /  \/  ___   _ __ ___   _ __ ___    __ _  _ __    __| | ___ 
#    | |     / _ \ | '_ ` _ \ | '_ ` _ \  / _` || '_ \  / _` |/ __|
#    | \__/\| (_) || | | | | || | | | | || (_| || | | || (_| |\__ ]
#     \____/ \___/ |_| |_| |_||_| |_| |_| \__,_||_| |_| \__,_||___/
#                                                                 

# Load Command
@client.command(name="Load",description="Loads a command")
# Check if the command runner is the bot's owner
@commands.check(IsBotOwner)
# Load function
async def load(ctx, extension):
    # Print and tell the console that the command was loaded
    print("Loaded"+extension)

    # Load the file
    client.load_extension(f'Commands.{extension}')

    # Create an embed and send it
    embed = discord.Embed(
            colour = maincolor
            )
    embed.title = "**Loaded**"
    embed.description = f"Command `{extension}` has been loaded."
    embed.timestamp = ctx.message.created_at
    embed.set_footer(text="Spyder", icon_url=client.user.avatar_url)
    await ctx.message.channel.send(embed)



# Unload Command
@client.command(name="Unload", description="Unloads a command")
# Check if the command can be ran and who is running the command
@commands.check(IsBotOwner)
# Load function
async def unload(ctx, extension):

    # Tell the console that the command was unloaded
    print("Unloaded"+extension)

    # Unload the file
    client.unload_extension(f'Commands.{extension}')

    # Create a embed and send it
    embed = discord.Embed(
            colour = maincolor
            )
    embed.title = "**Unloaded**"
    embed.description = f"Command `{extension}` has been unloaded."
    embed.timestamp = ctx.message.created_at
    embed.set_footer(text="Spyder", icon_url=client.user.avatar_url)
    await ctx.message.channel.send(embed)




# Reload Command
@client.command(name="Reload",description="Reloads a command")
# Check if the command can be ran and who is running the command
@commands.check(IsBotOwner)
# Reload function
async def reload(ctx, extension):

    #Tell the console that the command was reloaded
    print("Reloaded"+extension)

    # Reload the file 
    client.reload_extension(f'Commands.{extension}')

    # Make an embed and send it
    embed = discord.Embed(
            colour = maincolor
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
        name = len(filename)-3
        # Remove the .py extension at the end when we send the filename to laod
        client.load_extension(f'Commands.{filename[0:name]}')


#    
#     _____       _                
#    |_   _|     | |               
#      | |  ___  | | __ ___  _ __  
#      | | / _ \ | |/ // _ \| '_ \ 
#      | || (_) ||   <|  __/| | | |
#      \_/ \___/ |_|\_\\___||_| |_|
#                                  



# Run the token
client.run("NzMwMTcxMTkxNjMyOTg2MjM0.XwuZzg.fVsgMOaq2VUaSdZXmGVDIBuqxpk")