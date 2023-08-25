import discord
from discord.ext import commands
from modules.utils import create_embed
from modules.data_handler import GuildData

valid_prefixes = ["!", "@", "#", "$", "%", "^", "&", "*", "-", "_", "+", "=", "~"]


class Settings(commands.Cog):
    def __init__(self, client: discord.Client):
        self.client = client

    @commands.hybrid_group(
        name="set",
        with_app_command=True,
        description="Set the current server for the bot",
        aliases=["set_value"],
    )
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def server_set(self, ctx: commands.Context, specific_command: str = None, set_to: str = None):
        """Set a setting value for a key for the current guild"""
        if specific_command is not None and set_to is not None:
            # Set the server's data to the specific command that was passed
            if GuildData.edit_guild_settings(ctx.guild, {specific_command: set_to}) == False:
                # Invalid Key set
                embed_obj = create_embed(
                    "Invalid Arguments",
                    f"The argument that you passed was invalid.\n\nValid Keys:",
                )
                for key, value in GuildData.get_valid_keys().items():
                    embed_obj.add_field(
                        name=f"** ❯ {key.replace('_', ' ').capitalize()} **",
                        value=f"Key: `{key}`\tType: `{value}`",
                        inline=True,
                    )
                await ctx.send(embed=embed_obj)
            else:
                await ctx.send(embed=create_embed("Success", f"The key `{specific_command}` was set to `{set_to}`"))
        else:
            embed_obj = create_embed(
                "Invalid Arguments",
                f"Please pass two arguments to this command: (`command_to_set`, `value_to_set_to`).\n\n```Valid Keys:```",
            )
            for key, value in GuildData.get_valid_keys().items():
                embed_obj.add_field(
                    name=f"** ❯ {key.replace('_', ' ').capitalize()} **",
                    value=f"Key: `{key}`\nDefault: `{value}`",
                    inline=True,
                )

            await ctx.send(embed=embed_obj)

    @server_set.command(name="prefix", description="Set the prefix for the current guild")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def prefix(self, ctx: commands.Context, new_prefix: str = None):
        """Set the prefix for the current guild"""
        if new_prefix is None:
            await ctx.send(embed=create_embed("Invalid Parameter", "Please supply this command with a `prefix`"))
            return

        if len(new_prefix) != 1 or new_prefix not in valid_prefixes:
            await ctx.send(embed=create_embed("Invalid Prefix", f"The valid prefixes are: `{valid_prefixes}`"))
            return

        GuildData.edit_guild_settings(ctx.guild, {"prefix": new_prefix})
        await ctx.send(embed=create_embed("Success", f"Successfully set the prefix to `{new_prefix}`"))

    @server_set.command(name="mute", description="Create a muted role for the current guild")
    @commands.has_permissions(administrator=True)
    async def mute_role(self, ctx: commands.Context):
        """Create a mute role for the current guild"""
        await ctx.guild.create_role(name="Muted", permissions=discord.Permissions(send_messages=False))
        await ctx.send(embed=create_embed("Success", f"Successfully created Muted Role"))

    @commands.hybrid_command(
        name="settings",
        with_app_command=True,
        description="View the current settings in your server",
    )
    @commands.has_permissions(administrator=True)
    async def settings(self, ctx: commands.Context):
        """Prints out the settings of the current guild"""
        embed_obj = create_embed(
            "Settings",
            f"These are the following settings for this guild. To change the settings for your server, use the `setup` command.",
        )
        local_data = GuildData.get_guild_data(ctx.guild)
        for key, default_value in GuildData.get_valid_keys().items():
            if (value := local_data.get(key, None)) is None:  # The key does not exist
                value = default_value

            embed_obj.add_field(
                name=f"❯ {key.replace('_', ' ').capitalize()}",
                value=f"```{value}```",
                inline=True,
            )

        await ctx.send(embed=embed_obj)

    @commands.hybrid_command(with_app_command=True, description="Sync App Commands With Guild")
    @commands.has_permissions(administrator=True)
    async def sync_local(self, ctx: commands.Context):
        """Sync the commands locally to a guild"""
        try:
            self.client.tree.copy_global_to(guild=ctx.guild)
            synced = await self.client.tree.sync(guild=ctx.guild)
            await ctx.reply(embed=create_embed("Synced", f"Synced {len(synced)} command(s)"))
        except Exception as e:
            await ctx.reply(embed=create_embed("Unable to Sync", f"```{e}```"))
            
    # Load Command : Loads the Cog Specified
    @commands.hybrid_command(name="load", with_app_command=True, description="Loads a command")
    @commands.is_owner()
    async def load(self, ctx: commands.Context, extension: str):
        """Load a Cog"""
        await self.client.load_extension(f"cogs.{extension}")  # Load the file
        embed = create_embed("Loaded", f"Command `{extension}` has been loaded.")  # Create and send embed
        await ctx.send(embed)
        print(f"Loaded {extension}")  # Print and tell the console that the command was loaded


    # Unload Command: Unloads the Cog specified
    @commands.hybrid_command(name="unload", with_app_command=True, description="Unloads a command")
    @commands.is_owner()
    async def unload(self, ctx: commands.Context, extension: str):  # Unload Method
        """Unload a Cog"""
        await self.client.unload_extension(f"cogs.{extension}")  # Unload the file
        embed = create_embed("Unloaded", f"Command `{extension}` has been unloaded.")
        await ctx.send(embed=embed)
        print(f"Unloaded {extension}")  # Tell the console that the command was unloaded


    # Reload Command: Reloads the Cog Specified
    @commands.hybrid_command(name="reload", with_app_command=True, description="Reloads a command")
    @commands.is_owner()
    async def reload(self, ctx: commands.Context, extension: str):
        """Reload a Cog"""
        await self.client.reload_extension(f"cogs.{extension}")  # Reload the file
        embed = create_embed("Reloaded", f"Command `{extension}` has been reloaded.")
        await ctx.send(embed=embed)
        print(f"Reloaded {extension}")


    @commands.hybrid_command(name="sync", with_app_command=True, description="Sync App Commands Globally")
    @commands.is_owner()
    async def sync(self, ctx: commands.Context):
        """Sync the commands globally"""
        try:
            synced = await self.client.tree.sync(guild=None)
            await ctx.reply(embed=create_embed("Synced", f"Synced {len(synced)} command(s)"))
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            await ctx.reply(embed=create_embed("Unable to Sync", f"```{e}```"))


async def setup(client: discord.Client):
    await client.add_cog(Settings(client))
