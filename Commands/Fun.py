from discord.ext import commands

from Data.functions import get_fact, create_embed


class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="GetFact", description="Provides a random fact using requests")
    async def get_fact(self, ctx):
        embed = create_embed("Fact", f"```{get_fact()}```")
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Fun(client))
