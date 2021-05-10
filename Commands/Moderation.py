import functions
import discord
from discord.ext import commands


class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="Mute", description="Mute a user")
    @commands.check(functions.is_server_admin)
    async def mute(self, ctx, member: discord.Member):
        role = discord.utils.get(member.guild.roles, name="Muted")
        await member.add_roles(role)
        await ctx.send(
            embed=discord.Embed(
                title="Muted",
                description="User `{}` was muted by `{}`".format(member.display_name, ctx.message.author.display_name)
                )
            )

    @commands.command(name="Unmute", description="Unmute a user")
    @commands.check(functions.is_server_admin)
    async def unmute(self, ctx, member: discord.Member):
        role = discord.utils.get(member.guild.roles, name="Muted")
        await member.remove_roles(role)
        await ctx.send(
            embed=discord.Embed(
                title="Unmuted",
                description="User `{}` was unmuted by `{}`".format(member.display_name, ctx.message.author.display_name)
                )
            )


def setup(client):
    client.add_cog(Moderation(client))
