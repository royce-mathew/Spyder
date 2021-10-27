import discord
from discord.ext import commands
from main import prefix

from Data.functions import create_embed


class Help(commands.Cog):

    # The first thing that happens when this class is called
    def __init__(self, client):
        self.client = client

    @commands.command(name="Help", description="Returns all the available commmands")
    async def help(self, ctx):
        embed = create_embed(
            "Help Command",
            f"These are the avaliable commands for **{ctx.message.guild.name}**\nThe client prefix is: `{prefix}`"
        )

        for command in self.client.commands:
            embed.add_field(name=f"**❯ {command.name}**", value=f"```{command.description}```", inline=True)

        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Help(client))
