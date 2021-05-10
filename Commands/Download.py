import os
from discord.ext import commands

# current_path = os.path.dirname(os.path.realpath(__file__))
# exc_path = current_path + '/geckodriver'


class Download(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="Download",
                      description="Downloads a video from the specified list")
    async def download(self, ctx, arg1, arg2):
        # 2 args need to be passed:
        # The host: Instagram, facebook
        # The link
        # msg = await ctx.send("Loading...")
        host = arg1.lower()
        url = arg2
        pass

        #if host == "instagram" or host == "insta":


        #elif host == "yt" or host == "youtube":


def setup(client):
    client.add_cog(Download(client))
