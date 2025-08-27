import discord
from discord.ext import commands

import os
from dotenv import load_dotenv

load_dotenv()

channel_suggestions = int(os.getenv("channel_suggestions"))

class EditThreadNameModal(discord.ui.Modal, title="Rename thread"):
    def __init__(self, message_id):
        super().__init__()

        self.message_id = message_id

        self.changename = discord.ui.TextInput(
            label="Thread name",
            style=discord.TextStyle.short,
            placeholder="Summarize your suggestion in a few words",
            required=True,
            max_length=100,
        )
        self.add_item(self.changename)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.channel.edit(name=self.changename.value)

        msg = await interaction.channel.fetch_message(self.message_id)
        await msg.delete()

        embed = discord.Embed(description="**Thread renamed, thanks for your help !**",
        colour=discord.Color.green())

        await interaction.response.send_message(embed=embed, ephemeral=True)


class EditThreadNameView(discord.ui.View):
    def __init__(self, bot, user: discord.User):
        super().__init__(timeout=None)
        self.bot = bot
        self.user = user
        self.message_id = None

    @discord.ui.button(label="Rename thread", custom_id="change_thread_name", style=discord.ButtonStyle.primary)
    async def rename_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user == self.user:
            modal = EditThreadNameModal(self.message_id)
            await interaction.response.send_modal(modal)

class SuggestionsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(bot):
        print("[SuggestionsCog] Loaded!")

    async def cog_unload(bot):
        print("[SuggestionsCog] Unloaded")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.channel.id == channel_suggestions:
            await message.add_reaction("👍")
            await message.add_reaction("👎")

            thread = await message.create_thread(name=f"Suggestion by {message.author.display_name}")

            view = EditThreadNameView(self.bot, message.author)

            embed = discord.Embed(description=f"**{message.author.mention} Please rename the thread !**",
            colour=discord.Color.blue())

            msg = await thread.send(embed=embed, view=view)
            
            view.message_id = msg.id


async def setup(bot):
    await bot.add_cog(SuggestionsCog(bot))
