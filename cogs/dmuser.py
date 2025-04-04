import discord
from discord.ext import commands

import os
from dotenv import load_dotenv

load_dotenv()

role_botmail = int(os.getenv("role_botmail"))
role_botmanager = int(os.getenv("role_botmanager"))

class DmUserCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(bot):
        print("[DmUserCog] Loaded!")

    async def cog_unload(bot):
        print("[DmUserCog] Unloaded")

    
    @commands.hybrid_command()
    async def dm_user(self, ctx: commands.Context, user: discord.User, message: str):
        """
        Sends a DM to a user

        Parameters
        ----------
        ctx: commands.Context
            The context of the command invocation
        user: discord.User
            The user to send the message to
        message: str
            The message to send
        """

        # List of role IDs to check
        allowed_roles = [role_botmail, role_botmanager]

        # Check if the user has at least one of the roles
        has_role = any(role.id in allowed_roles for role in ctx.author.roles)

        if not has_role:
            await ctx.send("Nope! You don't have the roles to use this command.", delete_after=2)
        elif (not user.id) or (not message):
            await ctx.send("I didn't recieve the user or message correctly. Try using the slash command.", delete_after=2)
        else:
            status = discord.Embed(
                title="Sending DM...",
                description=f"**User:** <@{user.id}>\n**Message:** {message}",
                color=discord.Color.dark_grey()
            )
            statusmsg = await ctx.send("", embed=status)

            dmembed = discord.Embed(
                description=f"{message}",
                color=discord.Color.from_str("#0f2464")
            )
            dmembed.set_footer(text="Do not reply, we don't read messages sent to the bot! To contact, please open a ticket in our Discord server.")
            #dmembed.set_author(name="JMA Gaming")

            try:
                await user.send("", embed=dmembed)
                status.title = "Sent"
                status.color = discord.Color.green()
                await statusmsg.edit(embed=status)
            except discord.Forbidden:
                status.title = "Error"
                status.color = discord.Color.red()
                await statusmsg.edit(embed=status)

async def setup(bot):
    await bot.add_cog(DmUserCog(bot))