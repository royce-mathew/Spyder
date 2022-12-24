import asyncio
from modules.utils import create_embed
import discord
from discord.ext import commands
from modules.data_handler import UserData, GuildData
import random

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


    @commands.command(name="Register", description="Register for using commands that store data", aliases=["verify"])
    async def register(self, ctx: commands.Context):
        author: discord.Message.author = ctx.message.author # Message Author
        user_id: str = str(author.id) # Author ID converted to String
        role: discord.Role = discord.utils.find(lambda r: r.name == "Verified", ctx.guild.roles) # Find verified role in the Guild

        # Check if user already has role
        if (local_data := UserData.get_user_data(user_id)) is not None:
            if (name := local_data.get('name', None)) is not None and name != "":
                if role in author.roles:
                    await ctx.send(create_embed("Registered", "You are already registered"))
                    return;
    
        # Send initial message
        bot_message: discord.Message = await ctx.send(embed=create_embed("Registration Process", "This process may take a while."))
        await asyncio.sleep(2) # Wait 2 seconds

        # Name Prompt
        await bot_message.edit(embed=create_embed("Name", "Enter username, has to be an ascii character [A-Z,a-z] and under 10 characters"))
        client_response: discord.Message = await self.client.wait_for('message', check=check(author), timeout=30) # Wait for client input
        name: str = client_response.content

        # Check if name is valid
        if not name.isalpha() or len(name) > 10:
            await bot_message.edit(embed=create_embed("Invalid Characters in Name", "Characters must be [A-Z,a-z] (Max 10 characters) \nRun the !register command again."))
            return;


        # Terms And Conditions
        if (terms := GuildData.get_value_default(ctx.guild, "terms_and_conditions", "")) != "":
            await bot_message.edit(embed=create_embed("Terms and Conditions", f"{terms}\n\nDo you agree with these conditions? [Y | N] [Yes | No]"))
            client_response = await self.client.wait_for('message', check=check(author), timeout=30)

            if client_response.content.lower()  not in  ["y", "yes"]: # Check if user agrees
                await bot_message.edit(embed=create_embed("Error", "You did not agree to the Terms of Conditions."))
                return;


        # Register User
        embed = create_embed("Successfully Registered", f"You were registered as {name}. Welcome to the Server.")
        await bot_message.edit(embed=embed)
        UserData.set_user_data(user_id, key="name", value=name); # Set user data regardless of role

        if role is not None:
            member = discord.utils.find(lambda m: m.id == author.id, ctx.guild.members)
            await member.add_roles(role, reason=f"Spyder Verified, {name}")
            print(f"Verified {name}")


async def setup(client: discord.Client):
    await client.add_cog(Moderation(client))
