import discord
from discord.ext import commands
import asyncio

class PurgeConfirmView(discord.ui.View):
    def __init__(self, ctx, amount):
        super().__init__(timeout=30)
        self.ctx = ctx
        self.amount = amount
        self.response = None
        self.confirmation_msg = None

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("Only the command sender can confirm!", ephemeral=True)
            return

        await interaction.response.defer()

        try:
            deleted = await self.ctx.channel.purge(limit=self.amount + 1)

            countdown_msg = await self.ctx.send("This message will be deleted in 10s ⏱")
            for remaining in range(10, 0, -1):
                await countdown_msg.edit(content=f"This message will be deleted in {remaining}s ⏱")
                await asyncio.sleep(1)
            await countdown_msg.delete()

            self.response = True
            if self.confirmation_msg:
                try:
                    await self.confirmation_msg.delete()
                except discord.NotFound:
                    pass
            self.stop()
        except discord.errors.Forbidden:
            await self.ctx.send("Whoops, I don't have permissions to do that.", delete_after=10)

    @discord.ui.button(label="No", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("Only the command sender can cancel!", ephemeral=True)
            return

        await interaction.response.send_message("Operation canceled.", ephemeral=True)
        self.response = False
        if self.confirmation_msg:
            try:
                await self.confirmation_msg.delete()
            except discord.NotFound:
                pass
        self.stop()

class PurgeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        print("[PurgeCog] Loaded!")

    async def cog_unload(self):
        print("[PurgeCog] Unloaded")

    @commands.hybrid_command()
    async def purge(self, ctx: commands.Context, amount: int):
        """
        Clears a given number of messages, after confirmation.
        """
        if not ctx.author.guild_permissions.manage_messages:
            await ctx.send("You do not have permission to manage messages!", delete_after=5)
            return

        if amount < 1:
            await ctx.send("You must delete at least 1 message.", delete_after=5)
            return

        view = PurgeConfirmView(ctx, amount)
        view.confirmation_msg = await ctx.send(
            f"Are you sure you want to delete the last {amount} messages?",
            view=view,
            reference=None 
        )
        await view.wait()

async def setup(bot):
    await bot.add_cog(PurgeCog(bot))
