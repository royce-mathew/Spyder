import discord
from discord.ext import commands
from modules.functions import create_embed

from modules.data_handler import GuildData


class Help(commands.Cog):

    # The first thing that happens when this class is called
    def __init__(self, client: discord.Client):
        self.client = client

    @commands.command(name="Help", description="Returns all the available commmands")
    async def help(self, ctx: commands.Context):
        local_guild_data = GuildData.get_guild_data(ctx.guild)
        prefix = local_guild_data["prefix"]
        embed = create_embed(
            "Help Command",
            f"These are the avaliable commands for **{ctx.guild.name}**\nThe client prefix is: `{prefix}`"
        )

        for command in self.client.commands:
            embed.add_field(name=f"**❯ {command.name}**", value=f"```{command.description}```", inline=True)

        await ctx.send(embed=embed)


async def setup(client: discord.Client):
    await client.add_cog(Help(client))
