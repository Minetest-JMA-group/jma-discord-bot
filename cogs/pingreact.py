import discord
from discord.ext import commands

class PingReactCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(bot):
        print("[PingReactCog] Loaded!")

    async def cog_unload(bot):
        print("[PingReactCog] Unloaded")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if self.bot.user in message.mentions:
            await message.add_reaction("👀")

            if "hello" in message.content.lower():
                target = message.reference.resolved if message.reference else message
                await target.reply("👋 Hello there!")

        await self.bot.process_commands(message)
            

async def setup(bot):
    await bot.add_cog(PingReactCog(bot))