import asyncio
from modules.utils import create_embed
import discord
from discord.ext import commands
from modules.data_handler import UserData, GuildData
import random
import re


string_regex = re.compile("[A-Za-z]+")  # Characters from range a-z


def check(author: discord.Message.author): # Check if the author is the author of the original message (For Verification)
    def inner_check(message: discord.Message):
        return message.author == author

    return inner_check


class Moderation(commands.Cog):
    def __init__(self, client: discord.Client):
        self.client = client

    @commands.command(name="Mute", description="Mute a user")
    @commands.has_permissions(administrator=True)
    # member: discord.Member = None basically checks if the member has type discord.Member, if not then let it be None
    async def mute(self, ctx: commands.Context, member: discord.Member = None):
        # If member has the default value
        if member is None:
            await ctx.send("User was not passed")
            return

        role = discord.utils.get(member.guild.roles, name="Muted")
        await member.add_roles(role)
        await ctx.send(
            embed=create_embed(
                "Muted",
                f"User `{member.display_name}` was muted by `{ctx.message.author.display_name}`"
            )
        )

    @commands.command(name="Unmute", description="Unmute a user")
    @commands.has_permissions(administrator=True)
    async def unmute(self, ctx: commands.Context, member: discord.Member = None):
        if member is None:
            await ctx.send("User was not passed")
            return

        role = discord.utils.get(member.guild.roles, name="Muted")
        await member.remove_roles(role)
        await ctx.send(
            embed=create_embed(
                "Unmuted",
                f"User `{member.display_name}` was unmuted by `{ctx.message.author.display_name}`"
            )
        )

    @commands.command(name="Nick", description="Give user nickname", aliases=["nickname", "rename"])
    @commands.has_permissions(administrator=True)
    async def nick(self, ctx: commands.Context, member: discord.Member = None,
                   # Default value for nickname
                   new_nickname=f"User_{random.randrange(1000, 100000)}"):

        if member is None:
            await ctx.send("Member / Nickname was not passed")
            return

        await member.edit(nick=new_nickname)
        await ctx.send(
            embed=create_embed(
                "Set Nickname",
                f"User `{member.name}` was renamed to `{new_nickname}` by `{ctx.message.author.display_name}`"
            )
        )


    @commands.command(name="Register", description="Register for using commands that store data")
    async def register(self, ctx: commands.Context):
        author: discord.Message.author = ctx.message.author # Message Author
        user_id: str = str(author.id) # Author ID converted to String
        role: discord.Role = discord.utils.find(lambda r: r.name == "Verified", ctx.guild.roles) # Find verified role in the Guild

        # CHECKS
        # Check if user already has role
        if (local_data := UserData.get_user_data(user_id)) is not None and local_data.get('name', None) is not None and role in author.roles:
            embed = create_embed("Registered", "You are already registered")
            return
        # Check if terms of conditions were set up in this guild
        if (terms_of_conditions := GuildData.get_value(ctx.guild, "terms_and_conditions")) == "":
            embed = create_embed("Terms and Conditions Not Setup", "Terms and Conditions were not set for this server. Please run the setup command to set variables for your server.")
            await ctx.send(embed=embed);
            return;


        # Send initial message
        bot_message: discord.Message = await ctx.send(embed=create_embed("Registration Process", "This process may take a while."))

        # Wait 2 seconds
        await asyncio.sleep(2)

        # Name Prompt
        await bot_message.edit(embed=create_embed("Name", "Enter username, has to be an ascii character [A-Z,a-z]"))

        # Wait for client input
        client_response = await self.client.wait_for('message', check=check(author), timeout=30)
        name: str = client_response.content

        # Check if name is valid
        if not string_regex.match(name):
            embed = create_embed("Invalid Characters in Name", "Characters must be [A-Z,a-z]. \nRun the !register command again.")
            await bot_message.edit(embed=embed)
            return


        # Terms of Conditions Prompt
        embed = create_embed("Terms of Conditions", 
        description=f"{terms_of_conditions}\n\nDo you agree with these conditions? [Y | N] [Yes | No]")

        await bot_message.edit(embed=embed) # Edit the message
        client_response = await self.client.wait_for('message', check=check(author), timeout=30) # Wait for response

        # Check valid string
        if not string_regex.match(client_response.content):
            embed = create_embed("Invalid Characters in Response",
                                        "Characters must be [A-Z,a-z]. \nRun the "
                                        "!register command again.")
            await ctx.send(embed=embed)
            return;

        # Check if yes
        if client_response.content.lower() == "y" or client_response.content.lower() == "yes":
            embed = create_embed("Successfully Registered", f"You were registered as {name}. Welcome to the Server.")
            await bot_message.edit(embed=embed)

            if role is not None:
                UserData.set_user_data(user_id, key="name", value=name);
                member = discord.utils.find(lambda m: m.id == author.id, ctx.guild.members)
                await member.add_roles(role, reason=f"Spyder Verified, {name}")
                print(f"Verified {name}")

        else:
            embed = create_embed("Error", "You did not agree to the Terms of Conditions.")
            await bot_message.edit(embed=embed)


async def setup(client: discord.Client):
    await client.add_cog(Moderation(client))
