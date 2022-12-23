import discord
from discord.ext import commands
from modules.utils import create_embed
from modules.data_handler import GuildData

valid_prefixes = ['!', '@', '#', '$', '%', '^', '&', '*','-', '_', '+', '=', '~']

class Settings(commands.Cog):
    def __init__(self, client: discord.Client):
        self.client = client


    @commands.command(name="Setup", description="Setup the current server for the bot", aliases=["set"])
    @commands.has_permissions(administrator = True)
    async def setup(self, ctx: commands.Context, specific_command: str = None, set_to: str = None):
        if specific_command is not None and set_to is not None:
            # Set the server's data to the specific command that was passed
            if GuildData.edit_guild_settings(ctx.guild, {  specific_command: set_to }) == 0:
                # Invalid Key set
                embed_obj = create_embed("Invalid Arguments", f"The argument that you passed was invalid.\n\nValid Keys:")
                for key, value in GuildData.get_valid_keys().items():
                    embed_obj.add_field(name=f"** ❯ {key.replace('_', ' ').capitalize()} **", value=f"Key: `{key}`\tType: `{value}`", inline=True)
                await ctx.send(embed=embed_obj)
            else:
                await ctx.send(embed=create_embed("Success", f"The key {specific_command} was set to {set_to}"))
        else:
            embed_obj = create_embed("Invalid Arguments", f"Please pass two arguments to this command: (`command_to_set`, `value_to_set_to`).\n\n```Valid Keys:```")
            for key, value in GuildData.get_valid_keys().items():
                embed_obj.add_field(name=f"** ❯ {key.replace('_', ' ').capitalize()} **", value=f"Key: `{key}`\nDefault: `{value}`", inline=True)

            await ctx.send(embed=embed_obj)

    @commands.command(name="Settings", description="View the current settings in your server")
    @commands.has_permissions(administrator=True)
    async def settings(self, ctx: commands.Context):
        embed_obj = create_embed("Settings", f"These are the following settings for this guild. To change the settings for your server, use the `setup` command.")
        local_data = GuildData.get_guild_data(ctx.guild)
        for key, default_value in GuildData.get_valid_keys().items():

            if (value := local_data.get(key, None)) is None: # The key does not exist
                value = default_value

            embed_obj.add_field(name=f"❯ {key.replace('_', ' ').capitalize()}", value=f"```{value}```", inline=True)

        await ctx.send(embed=embed_obj)

    @commands.command(name="SetPrefix",  description="Sets the prefix for the current guild")
    async def set_prefix(self, ctx: discord.Client, newPrefix: str = None):
        if newPrefix is None:
            await ctx.send(embed=create_embed("Invalid Parameter", "Please supply this command with a `prefix`"))
            return;

        if len(newPrefix) != 1 or newPrefix not in valid_prefixes:
            await ctx.send(embed=create_embed("Invalid Prefix", f"The valid prefixes are: `{valid_prefixes}`"))
            return;

        GuildData.edit_guild_settings(ctx.guild, {"prefix": newPrefix})
        await ctx.send(embed=create_embed("Success", f"Successfully set the prefix to `{newPrefix}`"))
        


async def setup(client: discord.Client):
    await client.add_cog(Settings(client))
