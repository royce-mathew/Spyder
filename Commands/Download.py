import os
import urllib.request
from selenium import webdriver
from pytube import YouTube

import discord
from discord.ext import commands

current_path = os.path.dirname(os.path.realpath(__file__))
exc_path = current_path + '/geckodriver'


class Download(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="download",
                      description="Downloads a video from the specified list")
    async def download(self, ctx, arg1, arg2):
        # 2 args need to be passed:
        # The host: Instagram, facebook
        # The link
        msg = await ctx.send("Loading...")
        host = arg1.lower()
        url = arg2

        if host == "instagram" or host == "insta":
            # Handle driver
            driver = webdriver.Firefox(executable_path=r'%s' % exc_path)
            driver.get(url)

            try:
                # Get url
                element_name = driver.find_elements_by_class_name("tWeCl")
                src_url = element_name[0].get_attribute("src")
                video_name = (url.split('/'))[4]
                url_link = src_url

                # Open the file as f
                filename, headers = urllib.request.urlretrieve(url_link, current_path + "\\" + video_name + '.mp4')

                await msg.delete()

                msg = await ctx.send("Sending. Please wait...")

                try:
                    await ctx.send(file=discord.File(filename))

                except Exception:
                    await ctx.send("There was an error. Possibly due to large file size.")

                await msg.delete()
                os.remove(filename)

            except Exception:
                await ctx.send("There was an error. Possibly due to the link format not being right.\n\t- You must use the copy link feature provided by Instagram.\n\t- Is this file an video?")

            driver.quit()

        #elif host == "yt" or host == "youtube":


def setup(client):
    client.add_cog(Download(client))
