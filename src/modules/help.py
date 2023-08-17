from discord.ext import commands
from modules.utils import create_embed
from modules.data_handler import GuildData


ignore_cogs = ["ErrorHandler", "Help"]


class Help(commands.HelpCommand):
    # help
    async def send_bot_help(self, mapping: list):
        prefix = GuildData.get_value(self.context.guild, "prefix")
        embed_local = create_embed(
            "Help Command",
            f"These are the avaliable modules for **{self.context.guild.name}**\nThe client prefix is: `{prefix}`\n\nTo get help on a specific module, run: `{prefix}help ModuleName`",
        )

        # Run checks whether user has access to these commands
        # Get Command String
        for cog, commands in mapping.items():
            if cog is None:
                continue
            cog_name = cog.qualified_name
            if cog_name in ignore_cogs:
                continue

            embed_local.add_field(
                name=cog_name,
                value="```" + ("\n".join(x.name for x in commands)) + "```",
                inline=True,
            )

        await self.context.send(embed=embed_local)

    # help <command>
    async def send_command_help(self, command: commands.Command):
        # Get Command help
        embed_local = create_embed(
            command.name,
            f"**Help**\n```{command.help}```\n**Description**\n```{command.description}```",
        )
        await self.context.send(embed=embed_local)

    # help <cog>
    async def send_cog_help(self, cog: commands.Cog):
        # Display All Commands
        prefix = GuildData.get_value(self.context.guild, "prefix")
        embed_local = create_embed(
            "All Commands",
            f"These are the available commands for **{self.context.guild.name}**\nThe client prefix is: `{prefix}`",
        )
        for command in cog.walk_commands(guild=self.context.guild):
            embed_local.add_field(
                name=f"{command.name}",
                value=f"```{command.description}```",
                inline=True,
            )
        await self.context.send(embed=embed_local)
