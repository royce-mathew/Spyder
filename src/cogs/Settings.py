import discord
from discord.ext import commands
from modules.utils import create_embed
from modules.data_handler import GuildData

valid_prefixes = ["!", "@", "#", "$", "%", "^", "&", "*", "-", "_", "+", "=", "~"]


class Settings(commands.Cog):
    def __init__(self, client: discord.Client):
        self.client = client

    @commands.hybrid_command(
        name="setup",
        with_app_command=True,
        description="Setup the current server for the bot",
        aliases=["set"],
    )
    @commands.has_permissions(administrator=True)
    async def setup(self, ctx: commands.Context, specific_command: str = None, set_to: str = None):
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

    @commands.hybrid_command(
        name="settings",
        with_app_command=True,
        description="View the current settings in your server",
    )
    @commands.has_permissions(administrator=True)
    async def settings(self, ctx: commands.Context):
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

    @commands.hybrid_command(
        name="prefix",
        with_app_command=True,
        description="Sets the prefix for the current guild",
    )
    async def prefix(self, ctx: commands.Context, new_prefix: str = None):
        if new_prefix is None:
            await ctx.send(embed=create_embed("Invalid Parameter", "Please supply this command with a `prefix`"))
            return

        if len(new_prefix) != 1 or new_prefix not in valid_prefixes:
            await ctx.send(embed=create_embed("Invalid Prefix", f"The valid prefixes are: `{valid_prefixes}`"))
            return

        GuildData.edit_guild_settings(ctx.guild, {"prefix": new_prefix})
        await ctx.send(embed=create_embed("Success", f"Successfully set the prefix to `{new_prefix}`"))

    @commands.hybrid_command(with_app_command=True, description="Sync App Commands With Guild")
    @commands.has_permissions(administrator=True)
    async def sync_local(self, ctx: commands.Context):
        try:
            self.client.tree.copy_global_to(guild=ctx.guild)
            synced = await self.client.tree.sync(guild=ctx.guild)
            await ctx.reply(embed=create_embed("Synced", f"Synced {len(synced)} command(s)"))
        except Exception as e:
            await ctx.reply(embed=create_embed("Unable to Sync", f"```{e}```"))


async def setup(client: discord.Client):
    await client.add_cog(Settings(client))
