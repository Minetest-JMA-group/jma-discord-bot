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
            embed = discord.Embed(description="**Only the command sender can confirm !**",
            colour=discord.Color.red())

            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer()

        try:
            deleted = await self.ctx.channel.purge(limit=self.amount + 1)

            embed = discord.Embed(
                title=f"Deleted `{len(deleted) - 1}` messages", # Maybe add the success emoji ?
                color=discord.Color.green()
            )
            await self.ctx.send(embed=embed, delete_after=5)

            self.response = True
            if self.confirmation_msg:
                try:
                    await self.confirmation_msg.delete()
                except discord.NotFound:
                    pass
            self.stop()
        except discord.errors.Forbidden:
            await self.ctx.send("Whoops, I don't have permissions to do that.", delete_after=5)

    @discord.ui.button(label="No", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            embed = discord.Embed(description="**Only the command sender can cancel !**",
            colour=discord.Color.red())

            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        embed = discord.Embed(
            title=f"Operation canceled.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
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
            embed = discord.Embed(description="**You do not have permission to manage messages !**",
            colour=discord.Color.red())

            await ctx.send(embed=embed, delete_after=5)
            return

        if amount < 1:
            embed = discord.Embed(description="You must delete at least 1 message.",
            colour=discord.Color.red())

            await ctx.send(embed=embed, delete_after=5)
            return
        
        view = PurgeConfirmView(ctx, amount)

        embed = discord.Embed(
            title=f"Are you sure you want to delete the last {amount} messages ?",
            color=discord.Color.yellow()
        )

        view.confirmation_msg = await ctx.send(
            embed=embed,
            view=view,
            reference=None
        )
        await view.wait()


async def setup(bot):
    await bot.add_cog(PurgeCog(bot))
