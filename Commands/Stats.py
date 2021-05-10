import discord
from discord.ext import tasks, commands

# Import time for time stat
import datetime
from pytz import timezone
from main import maincolor, stats_message_id, stats_channel_id, guild_id


# Covid Stats
from lxml import html
import requests

# List containing all the titles that we will get the data for
text_list = ["Currently Infected", "Mild Condition", "Serious or Critical",
             "Cases with Outcome", "Recovered/Discharged", "Deaths"]

class Stats(commands.Cog):

    # The first thing that happens when this class is called
    def __init__(self, client):
        self.client = client
        self.stat.start()

    def cog_unload(self):
        self.stat.cancel()

    # Ping command - Tells the ping of the bot
    @commands.command(name="Ping", description="Ping")
    async def ping(self, ctx):
        msg = await ctx.message.channel.send("Ping?")
        str_time = str(msg.created_at - ctx.message.created_at)
        timestamp = str_time.strip("0:.")
        timestamp = int(timestamp)
        await msg.edit(content=f"Latency is {timestamp}ms")

    # Give the time - Updates the time every minute
    @tasks.loop(minutes=1)
    async def stat(self):
        # Get current time
        source_date = datetime.datetime.now()
        source = timezone("Canada/Eastern").localize(source_date)

        timezones = ["US/Central", "US/Pacific", "Canada/Eastern", "Asia/Calcutta", "Turkey", "EST", "UTC",
                     "US/Mountain", "Egypt", "Europe/Amsterdam"]

        # Sort the list
        timezones.sort()

        # Create discord Embed
        embed = discord.Embed(
            title="Server Status",
            description="Members: {}\nhttps://discord.gg/ZCvcu36\nRegion: {}\n\n**Server Time**".format(
                self.guild.member_count,
                self.guild.region),
            color=maincolor
        )

        # For each timezone in the timezones list
        for tz in timezones:
            # Add a field in the embed
            embed.add_field(
                name=tz,
                value="```{}```".format(source.astimezone(timezone(tz)).strftime("%I:%M %p")),
                inline=True
            )

        # Get the message with message id
        msg = await self.stat_channel.fetch_message(stats_message_id)
        # edit the message
        await msg.edit(embed=embed)

    # Wait until bot is ready
    @stat.before_loop
    async def before_stat(self):
        # Wait until the client is ready before starting the loop
        await self.client.wait_until_ready()

        # Set here because these lines can onlt be run after the client is ready
        self.guild = self.client.get_guild(guild_id)
        self.stat_channel = self.client.get_channel(stats_channel_id)

    @commands.command(name="CovidStats", description="Give the covid statistics")
    async def covidstats(self, ctx):
        page = requests.get("https://www.worldometers.info/coronavirus/coronavirus-cases/")
        tree = html.fromstring(page.content)

        # The numbers list will keep data which will correspond to indexes in the text_list
        numbers = [elem.text for elem in tree.xpath('//div[@class="number-table"]')]

        embed = discord.Embed(
            title="Covid Stats",
            color=maincolor
        )

        # zip assigns a text for each number, dict makes it a dictionary, then we loop through the items
        for k, v in dict(zip(text_list, numbers)).items():
            embed.add_field(
                name=k,
                value="```{}```".format(v),
                inline=True
            )

        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Stats(client))
