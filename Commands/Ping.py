import discord
from discord.ext import commands

class Ping(commands.Cog):

    # The first thing that happens when this class is called
    def __init__(self, client):
        self.client = client
    
    @commands.command(name="Ping",description="Ping")
    async def ping(self, ctx):

        msg = await ctx.message.channel.send("Ping?")
        strtime = str(msg.created_at - ctx.message.created_at)
        timestamp = strtime.strip("0:.")
        timestamp = int(timestamp)
        await msg.edit(content=f"Latency is {timestamp}ms")

def setup(client):
    client.add_cog(Ping(client))
