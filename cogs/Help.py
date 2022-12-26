import discord
from discord.ext import commands
from modules.utils import create_embed
from modules.data_handler import GuildData


ignore_cogs = ["ErrorHandler", "Help"]

class Help(commands.Cog):

    # The first thing that happens when this class is called
    def __init__(self, client: discord.Client):
        self.client = client

    @commands.command(name="Help", description="Returns all the available commmands", help="This command can be run with a optional parameter (Cog name or Command name)")
    async def help(self, ctx: commands.Context, command_name: str = None):
        embed_local: discord.Embed;

        if command_name is None:
            prefix = GuildData.get_value(ctx.guild, "prefix")
            embed_local = create_embed(
                "Help Command",
                f"These are the avaliable modules for **{ctx.guild.name}**\nThe client prefix is: `{prefix}`\n\nTo get help on a specific module, run: `{prefix}help ModuleName`"
            )

            # Run checks whether user has access to these commands
            # Get Command String
            command_dict = {} # Dictionary with all cogs and their commands 

            for cog_name in self.client.cogs:
                if cog_name in ignore_cogs:
                    continue;
                
                # Check if user can run commands in this cog, add those commands to the dictionary
                command_dict[cog_name] = [(await x.can_run(ctx) and x.name) for x in self.client.get_cog(cog_name).get_commands()]
            
                if len(command_dict[cog_name]) == 0:
                    continue;

                embed_local.add_field(name=cog_name, value="```" + ("\n".join(command_dict[cog_name])) + "```", inline=True)

        else:
            # Get Command help 
            if (command := self.client.get_command(command_name)) is not None:
                embed_local = create_embed(command.name, f"**Help**\n```{command.help}```\n**Description**\n```{command.description}```")
            else:
                # Display All Commands
                embed_local = create_embed(
                    "All Commands",
                    f"These are the avaliable commands for **{ctx.guild.name}**\nThe client prefix is: `{prefix}`"
                )
                for command in self.client.commands:
                    embed_local.add_field(name=f"{command.name}", value=f"```{command.description}```", inline=True)


        await ctx.send(embed=embed_local)


async def setup(client: discord.Client):
    await client.add_cog(Help(client))
