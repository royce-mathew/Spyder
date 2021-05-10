import discord, os
from discord.ext import commands


class Help(commands.Cog):

    # The first thing that happens when this class is called
    def __init__(self, client):
        self.client = client


    @commands.command(name="Help", description="Returns all the available commmands")
    async def help(self, ctx):
        # If there is a guild it is in
        embed = discord.Embed(
            colour=0x000
        )
        embed.title = "**Help Command**"
        embed.description = f"These are the avaliable commands for **{ctx.message.guild.name}**\nThe client prefix is: `/`"
        for command in self.client.commands:
            embed.add_field(name=f"**❯ {command.name}**", value=f"`{command.description}`", inline=True)
        embed.timestamp = ctx.message.created_at
        embed.set_footer(text="Spyder", icon_url=self.client.user.avatar_url)
        await ctx.message.channel.send(embed=embed) 

        

def setup(client):
    client.add_cog(Help(client))
