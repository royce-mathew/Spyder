import discord
from discord.ext import commands
import os

# current_path = os.path.dirname(os.path.realpath(__file__))
# exc_path = current_path + '/geckodriver'


class Download(commands.Cog):
    def __init__(self, client: discord.Client):
        self.client = client

    @commands.command(name="Download",
                      description="Downloads a video from the specified list")
    async def download(self, ctx: discord.Client, arg1: str, arg2: str):
        # 2 args need to be passed:
        # The host: Instagram, facebook
        # The link
        # msg = await ctx.send("Loading...")
        host = arg1.lower()
        url = arg2
        pass

        #if host == "instagram" or host == "insta":


        #elif host == "yt" or host == "youtube":


async def setup(client: discord.Client):
    await client.add_cog(Download(client))
