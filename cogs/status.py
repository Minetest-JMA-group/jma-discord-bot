import discord
from discord.ext import commands

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
        Clears all messages after a given message ID, after confirmation.

        Parameters
        ----------
        ctx: commands.Context
            The context of the command invocation
        activity_type: int
            The status activity type
        """
        if activity_type == "playing":
            await bot.change_presence(activity=discord.Game(name=activity_name))
        elif activity_type == "listening":
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=activity_name))
        elif activity_type == "watching":
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=activity_name))
        else:
            await ctx.send("Invalid activity type!")
        await ctx.send(f"Status set to {activity_type} {activity_name}")

async def setup(bot):
    await bot.add_cog(StatusCog(bot))