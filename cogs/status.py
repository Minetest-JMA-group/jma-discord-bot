import discord
from discord.ext import commands
from discord import app_commands
import os
import sqlite3
from dotenv import load_dotenv

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
        Sets the bot's status.

        Parameters
        ----------
        ctx: commands.Context
            The context of the command invocation
        activity_type: str
            The status activity type
        activity_name: str
            Will be displayed as "Playing activity_name"
        """

        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(description="**Hey, you don't have permissions to do that!**",
            colour=discord.Color.red())

            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if activity_type.value.lower() == "playing":
            await self.bot.change_presence(activity=discord.Game(name=activity_name))
        elif activity_type.value.lower() == "listening":
            await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=activity_name))
        elif activity_type.value.lower() == "watching":
            await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=activity_name))
        #else:
        #    await interaction.response.send_message("Invalid activity type!")
        #    return

        embed = discord.Embed(description=f"Status set to **{activity_type.value.lower()} {activity_name}**",
        colour=discord.Color.green())

        await interaction.response.send_message(embed=embed, delete_after=5)
async def setup(bot):
    await bot.add_cog(StatusCog(bot))
