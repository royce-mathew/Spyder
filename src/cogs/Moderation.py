import asyncio
from modules.utils import create_embed
import discord
from discord.ext import commands
from discord import app_commands
from modules.data_handler import UserData, GuildData
import random


def check(
    author: discord.Message.author,
):  # Check if the author is the author of the original message (For Verification)
    def inner_check(message: discord.Message):
        return message.author == author

    return inner_check


class Moderation(commands.Cog):
    def __init__(self, client: discord.Client):
        self.client = client

    @commands.hybrid_command(description="Mute a user")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @app_commands.describe(
        member="The guild member to mute",
    )
    # member: discord.Member = None basically checks if the member has type discord.Member, if not then let it be None
    async def mute(self, ctx: commands.Context, member: discord.Member = None):
        # If member has the default value
        if member is None:
            await ctx.send(embed=create_embed("Error", "User was not passed"))
            return

        role = discord.utils.get(member.guild.roles, name="Muted")
        if role is None:  # Role is not found | role does not exist
            await ctx.send(
                embed=create_embed(
                    "Error",
                    "Muted role was not found. Please run the `/set mute` command or create a Role called `Muted` and assign it the permissions you want.",
                )
            )
            return

        moderation_string = f"User `{member.name}` was muted by `{ctx.message.author.name}`"
        moderation_embed = create_embed(
            "Muted",
            moderation_string,
        )
        await member.add_roles(role)
        GuildData.edit_guild_settings(
            ctx.guild,
            {
                "moderation_logs": {
                    "type": "moderation",
                    "data": moderation_string,
                    "author": ctx.message.author.id,
                    "target": member.id,
                }
            },
        )
        await ctx.send(embed=moderation_embed)
        await GuildData.send_log_message(ctx.guild, moderation_embed)

    @commands.hybrid_command(description="Unmute a user")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @app_commands.describe(
        member="The guild member to unmute",
    )
    async def unmute(self, ctx: commands.Context, member: discord.Member = None):
        if member is None:
            await ctx.send(embed=create_embed("Error", "User was not passed"))
            return

        role = discord.utils.get(member.guild.roles, name="Muted")
        await member.remove_roles(role)
        moderation_string = f"User `{member.name}` was unmuted by `{ctx.message.author.name}`"
        moderation_embed = create_embed(
            "Unmuted",
            moderation_string,
        )
        GuildData.edit_guild_settings(
            ctx.guild,
            {
                "moderation_logs": {
                    "type": "moderation",
                    "data": moderation_string,
                    "author": ctx.message.author.id,
                    "target": member.id,
                }
            },
        )
        await ctx.send(embed=moderation_embed)
        await GuildData.send_log_message(ctx.guild, moderation_embed)

    @commands.hybrid_command(name="nick", description="Give user nickname", aliases=["nickname", "rename"])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @app_commands.describe(
        member="The guild member to rename",
        new_nickname="The new nickname to give the user",
    )
    async def nick(
        self,
        ctx: commands.Context,
        member: discord.Member = None,
        new_nickname=f"User_{random.randrange(1000, 100000)}",  # Default value for nickname
    ):
        if member is None:
            await ctx.send(embed=create_embed("Error", "Member / Nickname was not passed"))
            return

        moderation_string: str = (f"User `{member.name}` was renamed to `{new_nickname}` by `{ctx.message.author.name}`",)
        moderation_embed = create_embed(
            "Set Nickname",
            moderation_string,
        )
        await member.edit(nick=new_nickname)
        await ctx.send(embed=moderation_embed)

        # Add it to moderation logs
        GuildData.edit_guild_settings(
            ctx.guild,
            {
                "moderation_logs": {
                    "type": "moderation",
                    "data": moderation_string,
                    "author": ctx.message.author.id,
                    "target": member.id,
                }
            },
        )

        await GuildData.send_log_message(ctx.guild, moderation_embed)

    @commands.hybrid_command(description="Ban a user")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @app_commands.describe(
        member="The guild member to ban",
        reason="The reason for the ban",
        delete_message_days="The number of days to delete messages for",
    )
    async def ban(
        self,
        ctx: commands.Context,
        member: discord.Member = None,
        reason: str = "No reason provided",
        delete_message_days: int = 0,
    ):
        author: discord.Message.author = ctx.message.author
        if member is None:
            await ctx.send(embed=create_embed("Error", "User was not passed"))
            return

    @commands.hybrid_command(description="See the moderation logs for this server / user if specified", aliases=["modlogs"])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @app_commands.describe(member="The guild member to see the moderation logs for")
    async def logs(
        self,
        ctx: commands.Context,
        member: discord.Member = None,
    ):
        if member:
            guild_data = GuildData.get_guild_data_from_id(ctx.guild.id)
            current_logs = []
            for mod_log in guild_data["moderation_logs"]:
                if mod_log["target"] == member.id:
                    current_logs.append(mod_log["data"])

            await ctx.send(
                embed=create_embed(
                    "Moderation Logs",
                    f"{len(current_logs)} Moderation Logs for {member.name}\n- " + "\n- ".join(current_logs),
                )
            )

            return

    @commands.hybrid_command(
        description="Register inside the Bot's Database to use commands that store data",
        aliases=["verify"],
    )
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def register(self, ctx: commands.Context):
        author: discord.Message.author = ctx.message.author  # Message Author
        user_id: str = str(author.id)  # Author ID converted to String
        role: discord.Role = discord.utils.find(lambda r: r.name == "Verified", ctx.guild.roles)  # Find verified role in the Guild
        local_data = UserData.get_user_data(user_id)  # Get User Data
        # Check if user already has role
        if (name := local_data.get("name", None)) is not None and name != "":
            if role in author.roles:
                await ctx.send(embed=create_embed("Registered", "You are already registered"))
                ctx.command.reset_cooldown(ctx)
                return
            

        # Send initial message
        bot_message: discord.Message = await ctx.send(embed=create_embed("Registration Process", "This process may take a while."))
        await asyncio.sleep(0.5)  # Wait 2 seconds

        # Name Prompt
        await bot_message.edit(
            embed=create_embed(
                "Name",
                "Enter username, has to be an ascii character [A-Z,a-z] and under 10 characters",
            )
        )
        try:
            client_response: discord.Message = await self.client.wait_for("message", check=check(author), timeout=30)  # Wait for client input
        except asyncio.exceptions.TimeoutError:
            await bot_message.edit(
                embed=create_embed(
                    "Timeout",
                    "You took too long to respond. Please run the command again.",
                )
            )
            ctx.command.reset_cooldown(ctx)
            return

        name: str = client_response.content

        # Check if name is valid
        if not name.isalpha() or len(name) > 10:
            await bot_message.edit(
                embed=create_embed(
                    "Invalid Characters in Name",
                    "Characters must be [A-Z,a-z] (Max 10 characters) \nRun the !register command again.",
                )
            )
            ctx.command.reset_cooldown(ctx)
            return

        # Terms And Conditions
        if (terms := GuildData.get_value_default(ctx.guild, "terms_and_conditions", "")) != "":
            await bot_message.edit(
                embed=create_embed(
                    "Terms and Conditions",
                    f"{terms}\n\nDo you agree with these conditions? [Y | N] [Yes | No]",
                )
            )
            try:
                client_response: discord.Message = await self.client.wait_for("message", check=check(author), timeout=30)
            except asyncio.exceptions.TimeoutError:
                await bot_message.edit(
                    embed=create_embed(
                        "Timeout",
                        "You took too long to respond. Please run the command again.",
                    )
                )
                ctx.command.reset_cooldown(ctx)
                return

            if client_response.content.lower() not in [
                "y",
                "yes",
            ]:  # Check if user agrees
                await bot_message.edit(embed=create_embed("Error", "You did not agree to the Terms of Conditions."))
                ctx.command.reset_cooldown(ctx)
                return

        # Register User
        embed = create_embed(
            "Successfully Registered",
            f"You were registered as {name}. Welcome to the Server.",
        )
        await bot_message.edit(embed=embed)
        UserData.set_user_data(user_id, key="name", value=name)
        # Set user data regardless of role

        if role is not None:
            member = discord.utils.find(lambda m: m.id == author.id, ctx.guild.members)
            await member.add_roles(role, reason=f"Spyder Verified, {name}")
            print(f"Verified {name}")

        ctx.command.reset_cooldown(ctx)
        GuildData.send_log_message(ctx.guild, create_embed("Verified", f"User `{member.name}` was Verified"))


async def setup(client: discord.Client):
    await client.add_cog(Moderation(client))
