import discord
from discord.ext import commands

import os
from dotenv import load_dotenv

load_dotenv()

role_botmanager = int(os.getenv("role_botmanager"))

class OneWordStoryCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(bot):
        print("[OneWordStoryCog] Loaded!")

    async def cog_unload(bot):
        print("[OneWordStoryCog] Unloaded")
    
    @commands.hybrid_command()
    async def list_roles(self, ctx):
        """
        Lists all roles (and their IDs) in the server.

        Parameters
        ----------
        ctx: commands.Context
            The context of the command invocation
        """
        if ctx.channel.id != allowed_channel_id:
            await ctx.send("You're not allowed to use debug commands!\nIn fact, I'll give you even more bugs now :bug::bug::bug:")
        else:
            roles = ctx.guild.roles  # Get all roles in the server
            role_list = "\n".join([f"{role.name} - `{role.id}`" for role in roles])  # Format the roles

            embed = discord.Embed(title="Server Roles", description=role_list, color=discord.Color.blue())
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(OneWordStoryCog(bot))