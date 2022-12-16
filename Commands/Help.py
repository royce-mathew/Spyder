import discord
from discord.ext import commands
from Data.functions import create_embed

from modules.json_handler import GuildData

guild_data = GuildData()


class Help(commands.Cog):

    # The first thing that happens when this class is called
    def __init__(self, client):
        self.client = client

    @commands.command(name="Help", description="Returns all the available commmands")
    async def help(self, ctx):
        prefix = guild_data.get_guild_data(ctx.message.guild)["prefix"]
        embed = create_embed(
            "Help Command",
            f"These are the avaliable commands for **{ctx.message.guild.name}**\nThe client prefix is: `{prefix}`"
        )

        for command in self.client.commands:
            embed.add_field(name=f"**❯ {command.name}**", value=f"```{command.description}```", inline=True)

        await ctx.send(embed=embed)


async def setup(client):
    await client.add_cog(Help(client))
