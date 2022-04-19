import random

from Data import functions
import discord
from discord.ext import commands

import asyncio
import re

string_regex = re.compile("[A-Za-z]+")  # Characters from range a-z


# age_regex = re.compile("[0-9]+")

def check(author):
    def inner_check(message):
        return message.author == author

    return inner_check


class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="Mute", description="Mute a user")
    @commands.check(functions.is_server_admin)
    # member: discord.Member = None basically checks if the member has type discord.Member, if not then let it be None
    async def mute(self, ctx, member: discord.Member = None):
        # If member has the default value
        if member is None:
            await ctx.send("User was not passed")
            return

        role = discord.utils.get(member.guild.roles, name="Muted")
        await member.add_roles(role)
        await ctx.send(
            embed=functions.create_embed(
                "Muted",
                "User `{}` was muted by `{}`".format(member.display_name, ctx.message.author.display_name)
            )
        )

    @commands.command(name="Unmute", description="Unmute a user")
    @commands.check(functions.is_server_admin)
    async def unmute(self, ctx, member: discord.Member = None):
        if member is None:
            await ctx.send("User was not passed")
            return

        role = discord.utils.get(member.guild.roles, name="Muted")
        await member.remove_roles(role)
        await ctx.send(
            embed=functions.create_embed(
                "Unmuted",
                "User `{}` was unmuted by `{}`".format(member.display_name, ctx.message.author.display_name)
            )
        )

    @commands.command(name="Nick", description="Give user nickname", aliases=["nickname", "rename"])
    @commands.check(functions.is_server_admin)
    async def nick(self, ctx, member: discord.Member = None,
                   # Default value for nickname
                   new_nickname=f"User_{random.randrange(1000, 100000)}"):

        # If not list checks if the list is empty
        # I used this type of if statement to learn more about one liners
        # The code was
        #    if [x for x in (member, new_nickname) if x is None]

        if member is None:
            await ctx.send("Member / Nickname was not passed")
            return

        await member.edit(nick=new_nickname)
        await ctx.send(
            embed=functions.create_embed(
                "Set Nickname",
                "User `{}` was renamed to `{}` by `{}`".format(member.name,
                                                               new_nickname,
                                                               ctx.message.author.display_name)
            )
        )

    @commands.command(name="register", description="Register for using commands that store data")
    async def register(self, ctx):
        author = ctx.message.author
        user_id = str(author.id)

        main_array = functions.get_main_array(user_id)

        if main_array:
            embed = functions.create_embed("Registered", "You are already registered")
            await ctx.send(embed=embed)

        else:
            bot_msg = await ctx.send(embed=functions.create_embed("Registration Process", "This process may take a while."))

            # Wait 2 seconds
            await asyncio.sleep(2)

            # Name Prompt
            await bot_msg.edit(embed=functions.create_embed("Name", "Enter your name, has to be an ascii character [A-Z,a-z]"))

            # Ask for name and stuff
            msg = await self.client.wait_for('message', check=check(author), timeout=30)
            name = msg.content
            # Check

            if not string_regex.match(name):
                embed = functions.create_embed("Invalid Characters in Name", "Characters must be [A-Z,a-z]. \nRun the "
                                                                             "!register command again.")
                await bot_msg.edit(embed=embed)

            # ToC prompt
            embed = functions.create_embed("Terms of Conditions", description="``` This server is not for children, "
                                                                              "we talk about sensitive topics here "
                                                                              "and if you are uncomfortable with nsfw "
                                                                              "or other sensitive topics, please do not"
                                                                              " consider verifying."
                                                                              "```\n\nDo you agree with "
                                                                              "these conditions? [Y | N] [Yes | No]")

            await bot_msg.edit(embed=embed)
            # Wait for response
            msg = await self.client.wait_for('message', check=check(author), timeout=30)
            str_said_yes = msg.content

            # Check valid string
            if not string_regex.match(str_said_yes):
                embed = functions.create_embed("Invalid Characters in Response",
                                               "Characters must be [A-Z,a-z]. \nRun the "
                                               "!register command again.")
                await ctx.send(embed=embed)

            # Check if yes
            if str_said_yes.lower() == "y" or str_said_yes.lower() == "yes":
                embed = functions.create_embed("Successfully Registered", f"You were registered as {name}. Welcome to "
                                                                          f"the Coalition.")
                role = discord.utils.find(lambda r: r.name == "Verified", ctx.guild.roles)
                await bot_msg.edit(embed=embed)

                if role is not None:
                    functions.create_main_array(user_id, {"name": name})
                    member = discord.utils.find(lambda m: m.id == ctx.user_id, ctx.guild)
                    await member.add_roles(role, reason=f"Spyder Verified, {name}")
                    print(f"Verified {name}")

            else:
                embed = functions.create_embed("Error", "You did not agree to the Terms of Conditions.")
                await bot_msg.edit(embed=embed)


def setup(client):
    client.add_cog(Moderation(client))
