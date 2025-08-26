import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

load_dotenv()

role_botmanager = int(os.getenv("role_botmanager"))

class StatusCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(bot):
        print("[StatusCog] Loaded!")

    async def cog_unload(bot):
        print("[StatusCog] Unloaded")

    @app_commands.command()
    @app_commands.describe(activity_name="Will be displayed as 'Playing activity_name'")
    @app_commands.choices(activity_type=[
        app_commands.Choice(name="Playing", value="playing"),
        app_commands.Choice(name="Listening", value="listening"),
        app_commands.Choice(name="Watching", value="watching")
    ])
    async def set_status(self, interaction: discord.Interaction, activity_type: app_commands.Choice[str], activity_name: str):
        """
        Sets the bot's status

        Parameters
        ----------
        ctx: commands.Context
            The context of the command invocation
        activity_type: str
            The status activity type
        activity_name: str
            Will be displayed as "Playing activity_name"
        """

        has_role = any(role.id == role_botmanager for role in interaction.user.roles)
        if not has_role:
            await interaction.response.send_message("Hey, you don't have permissions to do that!", ephemeral=True)
            return

        if activity_type.value.lower() == "playing":
            await self.bot.change_presence(activity=discord.Game(name=activity_name))
        elif activity_type.value.lower() == "listening":
            await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=activity_name))
        elif activity_type.value.lower() == "watching":
            await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=activity_name))
        else:
            await interaction.response.send_message("Invalid activity type!")
            return

        await interaction.response.send_message(f"Status set to **{activity_type.value.lower()} {activity_name}**")

async def setup(bot):
    await bot.add_cog(StatusCog(bot))
