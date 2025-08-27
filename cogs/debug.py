import discord
from discord.ext import commands

import os
from dotenv import load_dotenv

load_dotenv()

role_botmanager = int(os.getenv("role_botmanager"))

class DebugCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(bot):
        print("[DebugCog] Loaded!")

    async def cog_unload(bot):
        print("[DebugCog] Unloaded")
    
    @commands.hybrid_command()
    async def list_roles(self, ctx):
        """
        Lists all roles (and their IDs) in the server.

        Parameters
        ----------
        ctx: commands.Context
            The context of the command invocation
        """
        if not discord.utils.get(ctx.author.roles, id=role_botmanager):
            embed = discord.Embed(description="**You're not allowed to use debug commands!**\nIn fact, I'll give you even more bugs now :bug::bug::bug:",
            colour=discord.Color.red())

            await ctx.send(embed=embed, delete_after=5)
        else:
            roles = ctx.guild.roles  # Get all roles in the server
            role_list = "\n".join([f"{role.name} - `{role.id}`" for role in roles])  # Format the roles

            embed = discord.Embed(title="Server Roles", description=role_list, color=discord.Color.blue())
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(DebugCog(bot))
