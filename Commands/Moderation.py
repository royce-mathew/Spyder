import random

from Data import functions
import discord
from discord.ext import commands


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
                   new_nickname="User_{}".format(random.randrange(1000, 100000))):

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


def setup(client):
    client.add_cog(Moderation(client))
