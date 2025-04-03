import discord
from discord.ext import commands

class PurgeConfirmView(discord.ui.View):
    def __init__(self, ctx, message):
        super().__init__(timeout=30)  # Auto timeout after 30 seconds
        self.ctx = ctx
        self.message = message
        self.response = None  # Store user choice

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("Only the command sender can confirm!", ephemeral=True)
            return

        await self.ctx.typing()

        try:
            deleted = await self.ctx.channel.purge(after=self.message)
            await self.ctx.send(f"Deleted {len(deleted)} messages.", delete_after=10)
            self.response = True
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
        self.stop()

class PurgeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(bot):
        print("[PurgeCog] Loaded!")

    async def cog_unload(bot):
        print("[PurgeCog] Unloaded")

    
    @commands.hybrid_command()
    async def purge(self, ctx: commands.Context, message_id: int):
        """
        Clears all messages after a given message ID, after confirmation.

        Parameters
        ----------
        ctx: commands.Context
            The context of the command invocation
        message_id: int
            The ID of the message after which to delete all messages
        """
        try:
            message = await ctx.channel.fetch_message(message_id)
        except discord.NotFound:
            await ctx.send("Message not found. Please provide a valid message ID.")
            return
        except discord.Forbidden:
            await ctx.send("I don't have permission to fetch messages in this channel.")
            return
        except discord.HTTPException:
            await ctx.send("An error occurred while fetching the message.")
            return

        view = PurgeConfirmView(ctx, message)
        await ctx.send("Are you sure you want to delete all messages after this?", view=view)
        await view.wait()

async def setup(bot):
    await bot.add_cog(PurgeCog(bot))