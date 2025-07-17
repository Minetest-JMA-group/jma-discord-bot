import discord
from discord.ext import commands

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

    
    @commands.hybrid_command()
    async def set_status(self, ctx: commands.Context, activity_type: str, activity_name: str):
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

        has_role = any(role.id == role_botmanager for role in ctx.message.author.roles)
        if not has_role:
            await ctx.send("Hey, you don't have permissions to do that!", delete_after=5)
            return

        if activity_type.lower() == "playing":
            await self.bot.change_presence(activity=discord.Game(name=activity_name))
        elif activity_type.lower() == "listening":
            await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=activity_name))
        elif activity_type.lower() == "watching":
            await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=activity_name))
        else:
            await ctx.send("Invalid activity type!")
            return
        await ctx.send(f"Status set to **{activity_type.lower()} {activity_name}**")

async def setup(bot):
    await bot.add_cog(StatusCog(bot))