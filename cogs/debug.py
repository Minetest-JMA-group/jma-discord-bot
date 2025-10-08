import discord
from discord.ext import commands
import sqlite3


def get_variable_value(title):
    conn = sqlite3.connect('variables.db')
    cursor = conn.cursor()

    cursor.execute("SELECT value FROM variables WHERE title = ?", (title,))
    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]
    else:
        raise KeyError(f"Variable '{title}' not found in the database.")


def get_role_botmanager():
    return int(get_variable_value("Bot manager role"))


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
        role_botmanager = get_role_botmanager()

        if not discord.utils.get(ctx.author.roles, id=role_botmanager):
            embed = discord.Embed(description="**You're not allowed to use debug commands!**\nIn fact, I'll give you even more bugs now :bug::bug::bug:",
            colour=discord.Color.red())

            await ctx.send(embed=embed, delete_after=5)
            return
        else:
            roles = ctx.guild.roles
            role_list = "\n".join([f"{role.name} - `{role.id}`" for role in roles])

            embed = discord.Embed(title="Server Roles", description=role_list, color=discord.Color.blue())
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(DebugCog(bot))
