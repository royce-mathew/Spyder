import discord
from discord.ext import commands

command_format = "\n\nPlease check your format:\n\t- Are the values formatted in (a b c) and not (a + b + c)?\n\t- Are the values seperated by spaces?\n\t- Are there actual numbers?\n\t- Are (a b c) coefficients of the quadratic?\n\t- Is a an actual value?"

class Math(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(name = "getFactor", description = "Give three numbers seperated by spaces to get the factor of a trinomial")
    async def getFactor(self, ctx, *args):
        if len(args) != 3:
            return ctx.send("The length of the trinomial is invalid"+command_format)      

        try:

            args = [int(i) for i in args] 
            
            add_num = args[1]
            mult_num = args[0] * args[2]

            for i in range((args[0] if args[0] < 0 else 0), mult_num):
                for x in range(mult_num , i, -1):
                    if i+x == add_num and i*x == mult_num:
                        if args[0] > 1:
                            await ctx.send("{}x^2 + {}x + {}x + {}".format(args[0], i, x, args[2]))
                        else:
                            await ctx.send("(x + {})(x + {})".format(i, x))
                        
                        return;

            await ctx.send("The passed values cannot be factored."+command_format)


        except ValueError:
            await ctx.send(command_format)
        

                
        


def setup(client):
    client.add_cog(Math(client))
