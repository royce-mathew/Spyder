import discord
from discord.ext import tasks, commands

# Import time for time stat
import datetime
from pytz import timezone
from modules.data_handler import GuildData # Get instance of guild data

# Covid Stats
from lxml import html
import requests

from modules.utils import create_embed, get_fact

# List containing all the titles that we will get the data for
text_list = ["Currently Infected", "Mild Condition", "Serious or Critical",
             "Cases with Outcome", "Recovered/Discharged", "Deaths"]
timezones = ["US/Central", "US/Pacific", "Canada/Eastern", 
            "Asia/Calcutta", "Turkey", "EST", "UTC",
            "US/Mountain", "Egypt", "Europe/Amsterdam"]

embed_const = "```{}```"

timezones.sort() # Sort the list


class Stats(commands.Cog):

    # The first thing that happens when this class is called
    def __init__(self, client: discord.Client):
        self.client = client
        self.stat.start()
        self.get_fact_of_day.start()

    # Ping command - Tells the ping of the bot
    @commands.command(name="Ping", description="Ping")
    async def ping(self, ctx: commands.Context):
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
        # New Brunswick Time
        nb_time = (source.astimezone(timezone("Canada/Eastern")) + datetime.timedelta(hours=1)).strftime("%I:%M %p")

        # Get the message with message id
        for guild in self.client.guilds:

            # Guild Checks
            if (current_guild_settings := GuildData.get_guild_data(guild_obj=guild)) is None:
                continue;
            if (stats_channel_id := current_guild_settings["stats_channel_id"]) == 0: # Skip this guild if stats_channel was not filled
                continue;
            if (stats_message_id := current_guild_settings["stats_message_id"]) == 0:
                continue;

            # Create discord Embed
            embed = create_embed(
                "Server Status",
                f"""Members: `{guild.member_count}`
                ID: {guild.id}\n
                **Server Time**""",
            )

            # Add NB
            embed.add_field(
                name="New_Brunswick (Manual)",
                value=embed_const.format(nb_time),
                inline=True
            )

            # For each timezone in the timezones list
            for tz in timezones:
                # Add a field in the embed
                embed.add_field(
                    name=tz,
                    value=embed_const.format(source.astimezone(timezone(tz)).strftime("%I:%M %p")),
                    inline=True
                )

            
            try: # Fetch the message
                stat_channel = self.client.get_channel(int(stats_channel_id)) # Get the stat channel
                msg = await stat_channel.fetch_message(int(stats_message_id))
            except discord.NotFound: # Message not found
                msg = await stat_channel.send("stats") # Send an empty message
                GuildData.edit_guild_settings(guild,
                    {"stats_message_id": msg.id}
                )
            except Exception as err:
                print(err)
                return
    
            # edit the message
            await msg.edit(embed=embed)


    @stat.before_loop
    async def before_stat(self):
        # Wait until the client is ready before starting the loop
        await self.client.wait_until_ready()

    @tasks.loop(minutes=1440)
    async def get_fact_of_day(self):
        embed = create_embed("Fact of the Day", f"```{get_fact()}```")
        # Loop through guilds and send fact of the day for guild
        for guild in self.client.guilds:
            if (fact_channel_id := GuildData.get_value(guild, "fact_channel_id")) is not None:
                if (channel := guild.get_channel(int(fact_channel_id))) is not None:
                    await channel.send(embed=embed)

    @get_fact_of_day.before_loop
    async def before_fod(self):
        await self.client.wait_until_ready()




    @commands.command(name="CovidStats", description="Give the covid statistics", aliases=["covid", "cstats"])
    async def covidstats(self, ctx: commands.Context):
        page = requests.get("https://www.worldometers.info/coronavirus/coronavirus-cases/")
        tree = html.fromstring(page.content)

        # The numbers list will keep data which will correspond to indexes in the text_list
        numbers = [elem.text for elem in tree.xpath('//div[@class="number-table"]')]

        embed = create_embed(
            "Covid Stats"
        )

        # zip assigns a text for each number, dict makes it a dictionary, then we loop through the items
        for k, v in dict(zip(text_list, numbers)).items():
            embed.add_field(
                name=k,
                value=embed_const.format(v),
                inline=True
            )

        await ctx.send(embed=embed)


async def setup(client: discord.Client):
    await client.add_cog(Stats(client))
