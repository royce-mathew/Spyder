import discord
from discord.ext import commands

from random import randrange

from Data.functions import get_fact, create_embed, get_main_array, set_main_array


class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="GetFact", description="Provides a random fact using requests")
    async def get_fact(self, ctx):
        embed = create_embed("Fact", f"```{get_fact()}```")
        await ctx.send(embed=embed)

    @commands.command(name="PersonalityTest", description="Tells you your masculine and feminine percentage")
    async def get_personality_test(self, ctx, member: discord.Member = None):
        user_id = ""
        if not member:
            user_id = str(ctx.message.author.id)  # Json keys only accept str values
        else:
            user_id = str(member.id)

        print(user_id)

        main_array = get_main_array(user_id)

        if main_array is not None:
            personality = main_array.get("personality", None)

            if personality is None:
                # Create a new dictionary
                personality = main_array["personality"] = {}

                male_percent = randrange(0, 101)
                female_percent = 100 - male_percent

                main_array["personality"]["male"] = male_percent
                main_array["personality"]["female"] = female_percent

                set_main_array(user_id, main_array)

            embed = create_embed("Personality", f"`{main_array['name']}`'s personality:")
            embed.add_field(name="Masculinity", value=personality["male"], inline=True)
            embed.add_field(name="Femininity", value=personality["female"], inline=True)

            await ctx.send(embed=embed)
        else:
            embed = create_embed("Error", "User is unregistered. Please register by running the "
                                          "!register command")
            await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Fun(client))
