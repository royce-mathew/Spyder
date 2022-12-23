import discord
from discord.ext import commands
from modules.data_handler import UserData

from random import randrange

from modules.utils import get_fact, create_embed


class Fun(commands.Cog):
    def __init__(self, client: discord.Client):
        self.client = client

    @commands.command(name="GetFact", description="Provides a random fact using requests")
    async def get_fact(self, ctx: commands.Context):
        embed = create_embed("Fact", f"```{get_fact()}```")
        await ctx.send(embed=embed)

    @commands.command(name="PersonalityTest", description="Tells you your masculine and feminine percentage")
    async def get_personality_test(self, ctx, member: discord.Member = None):
        user_id = str(ctx.message.author.id)  if (member is None) else str(member.id)
        main_array = UserData.get_user_data(user_id)

        if (main_array is not None) and (main_array.get("name", None) is not None):
            personality = main_array.get("personality", None)

            if personality is None:
                # Create a new dictionary
                personality = main_array["personality"] = {}

                male_percent = randrange(0, 101)
                female_percent = 100 - male_percent

                main_array["personality"]["male"] = male_percent
                main_array["personality"]["female"] = female_percent

                UserData.set_user_data(user_id=user_id, key="personality", value=personality)

            embed = create_embed("Personality", f"`{main_array['name']}`'s personality:")
            embed.add_field(name="Masculinity", value=personality["male"], inline=True)
            embed.add_field(name="Femininity", value=personality["female"], inline=True)

            await ctx.send(embed=embed)
        else:
            embed = create_embed("Error", "User is unregistered. Please register by running the "
                                          "!register command")
            await ctx.send(embed=embed)


async def setup(client):
    await client.add_cog(Fun(client))
