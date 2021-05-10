import discord
from discord.ext import commands

command_format = "\n\nPlease check your format:\n\t- Are the values formatted in (a b c) and not (a + b + c)?\n\t- Are the values seperated by spaces?\n\t- Are there actual numbers?\n\t- Are (a b c) coefficients of the quadratic?\n\t- Is a an actual value?"

class Math(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(name="GetFactor", description="Give three numbers seperated by spaces to get the factor of a trinomial")
    async def getFactor(self, ctx, arg0, arg1, arg2):
        try:
            # Convert args to int
            arg0, arg1, arg2 = int(arg0), int(arg1), int(arg2)

            a = arg0
            b = arg1
            c = arg2

            # The numbers that will be added and multiplied
            add_num = b
            mult_num = a*c

            # Check the smallest num
            # mult_num is also added since we needed to check any numbers between the mult num too
            smallest_num = min(arg0, arg1, arg2, mult_num)
            biggest_num = max(arg0, arg1, arg2, mult_num)

            """
            Loop from the smallest number to the biggest number, 
                providing all possible combinations of numbers
            
            It is biggest num + 1 because in python,
                the loop goes from smallest_num to biggest_num - 1
            
            """
            for i in range(smallest_num, biggest_num + 1):
                for x in range(biggest_num, i + 1, -1):
                    if i+x == add_num and i*x == mult_num:
                        if a != 1:
                            await ctx.send("`{}x^2` + `{}x` + `{}x` + `{}`".format(a, i, x, c))
                        else:
                            await ctx.send("`(x + {})(x + {})`".format(i, x))
                        return;

            await ctx.send("The passed values cannot be factored."+command_format)


        except Exception:
            await ctx.send(command_format)
        

                
        


def setup(client):
    client.add_cog(Math(client))
