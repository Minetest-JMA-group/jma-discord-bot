import discord
from discord.ext import commands

import os
from dotenv import load_dotenv, set_key

load_dotenv()

role_botmanager = int(os.getenv("role_botmanager"))

class EnvEditCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(bot):
        print("[EnvEditCog] Loaded!")

    async def cog_unload(bot):
        print("[EnvEditCog] Unloaded")

    @commands.hybrid_command()
    async def env_edit(self, ctx, variable: str, value: str):
        """
        Edit a .env variable

        Parameters
        ----------
        ctx: commands.Context
            The context of the command invocation
        variable: str
            The variable to edit
        value: str
            The new value of the variable
        """

        has_role = any(role.id == role_botmanager for role in ctx.author.roles)
        if ctx.author.guild_permissions.administrator or has_role:
            change_variable = os.getenv(variable)
            if change_variable is None or variable == "TOKEN":
                await ctx.send(":x: That variable does not exist. Please contact the developer if you want to add it.", delete_after=20)
            else:
                print("[EnvEditCog] "+str(ctx.author.id)+" changed variable `"+variable+"` from `"+change_variable+"` to `"+value+"`")
                set_key(".env", variable, value, quote_mode="never")
                await ctx.send(":white_check_mark: Successfully changed variable `"+variable+"` to `"+value+"`")

async def setup(bot):
    await bot.add_cog(EnvEditCog(bot))