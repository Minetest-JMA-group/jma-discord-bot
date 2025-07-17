import discord
from discord.ext import commands

phrases = {
    "hello": "👋 Hello there!",
    "relaylogin": "To login to the relays, DM the relay bot (**not the channel!**) `!login yourUsername yourPassword`",
    "relay": "To chat in the relays, follow the instructions in https://discord.com/channels/1002108415511896095/1390797710638055505",
    "pingsupport": "Please don't ping staff members unnecessarily!\nIf you require assistance, please open a ticket at https://discord.com/channels/1002108415511896095/1002110888859418725",
    "support": "If you require assistance, please open a ticket at https://discord.com/channels/1002108415511896095/1002110888859418725",
}

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

            for phrase in phrases:
                if phrase in message.content.lower():
                    target = message.reference.resolved if message.reference else message
                    await target.reply(phrases[phrase])
                    return

    @commands.hybrid_command()
    async def list_ping_reactions(self, ctx):
        """
        Lists all the different ping reactions

        Parameters
        ----------
        ctx: commands.Context
            The context of the command invocation
        """

        prompts = ""
        for phrase in phrases:
            prompts = prompts + phrase + ", "
        
        await ctx.send(f"Here are all the prompts I'll respond to: {prompts}")

async def setup(bot):
    await bot.add_cog(PingReactCog(bot))