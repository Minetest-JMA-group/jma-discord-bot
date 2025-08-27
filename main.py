import os
import datetime
import traceback

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
channel_botlog = int(os.getenv("channel_botlog"))
server_sync = int(os.getenv("server_sync"))
role_botmanager = int(os.getenv("role_botmanager"))

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
tree = bot.tree

cogs = [
    "cogs.debug",
    "cogs.purge",
    "cogs.serverstatus",
    "cogs.dmuser",
    "cogs.onewordstory",
    "cogs.status",
    "cogs.pingreact",
    "cogs.suggestions",
]

"""@bot.hybrid_command()
async def say(ctx: commands.Context, message: str):
    \"""
    Says a message.

    Parameters
    ----------
    ctx: commands.Context
        The context of the command invocation
    message: str
        The message to say
    \"""
    await ctx.send(message)
"""

@bot.hybrid_command()
async def reload(ctx: commands.Context):
    """
    Reload all cogs.

    Parameters
    ----------
    ctx: commands.Context
        The context of the command invocation
    """
    if not discord.utils.get(ctx.author.roles, id=role_botmanager):
        await ctx.send(":notes: Never gonna give you up, never gonna let you down... :notes:", delete_after=2)
    else:
        total = 0
        for c in cogs:
            await bot.reload_extension(c)
            total = total + 1
        embed = discord.Embed(title=f"Reloaded `{total}` extensions",
        colour=discord.Color.blue())

        await ctx.send(embed=embed, delete_after=5)

@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.CommandNotFound):
        return
    if not isinstance(error, commands.CommandOnCooldown):
        ctx.command.reset_cooldown(ctx)
    await ctx.send("Whoops, an error occurred! Please try again later", delete_after=5)
    description = "Unknown error occurred while using the command"
    if isinstance(error, commands.CommandInvokeError):
        if isinstance(error.original, ZeroDivisionError):
            description = "Can't divide by zero"
        else:
            error_data = "".join(traceback.format_exception(type(error), error, error.__traceback__))
            description = f"Invoke error\n```py\n{error_data[:1000]}\n```"
    elif isinstance(error, commands.CommandOnCooldown):
        description = f"This command is on cooldown. You need to wait {error.retry_after:.2f} to use that command"
    #elif isinstance(error, AuthorHasLowerRole):
    #    description = "You can't manage this member because he has a better role than yours"
    elif isinstance(error, commands.BotMissingPermissions):
        description = f"I am missing required permissions to do that"
        embed.add_field(name="List of permissions", value=', '.join(error.missing_permissions))
    elif isinstance(error, commands.MissingPermissions):
        description = f"You are missing required permissions to do that"
        embed.add_field(name="List of permissions", value=', '.join(error.missing_permissions))
    elif isinstance(error, commands.BadArgument):
        if isinstance(error, commands.MemberNotFound):
            description = f"Member `{error.argument}` not found"
        elif isinstance(error, commands.ChannelNotFound):
            description = f"Channel `{error.argument}` not found"
        else:
            description = f"Argument `{error.argument}` not found"
    elif isinstance(error, commands.MissingRequiredArgument):
        description = f"Missing required argument: `{error.param.name}`"
    else:
        error_data = "".join(traceback.format_exception(type(error), error, error.__traceback__))
        description = f"Unknown error\n```py\n{error_data[:1000]}\n```"

    embed = discord.Embed(
        title=f"Error in command {ctx.command}!",
        description=description,
        color=discord.Color.red(),
        timestamp=datetime.datetime.now(datetime.UTC)
    )
    channel = await bot.fetch_channel(channel_botlog)
    await channel.send(embed=embed)

@bot.event
async def setup_hook() -> None:
    print("Running setup hook...")
    for c in cogs:
        await bot.load_extension(c)

@bot.event
async def on_ready() -> None:
    print(f"Logged in as {bot.user}")

    guild = discord.Object(id=server_sync)
    tree.copy_global_to(guild=guild)
    synced = await tree.sync(guild=guild)

    await bot.change_presence(activity=discord.Game(name="JMA Capture the Flag"))

bot.run(TOKEN)
