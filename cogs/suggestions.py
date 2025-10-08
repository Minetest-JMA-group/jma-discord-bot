import discord
from discord.ext import commands
from discord import app_commands
import os
import sqlite3
from dotenv import load_dotenv
import asyncio
import time

load_dotenv()

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

channel_suggestions = int(get_variable_value("Suggestions channel"))
channel_suggestions_archive = int(get_variable_value("Suggestions archive channel"))
developer_role = int(get_variable_value("Developer role"))

# --- MODAL ---
class EditThreadNameModal(discord.ui.Modal, title="Rename thread"):
    def __init__(self, message_to_delete, suggestion_message, suggestion_author):
        super().__init__()
        self.message_to_delete = message_to_delete
        self.suggestion_message = suggestion_message
        self.suggestion_author = suggestion_author

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
        #try:
        #    await self.message_to_delete.delete()
        #except:
        #    pass
        await interaction.response.send_message(":white_check_mark: Thread renamed.", ephemeral=True)


# --- VIEWS ---
class RenameOnlyView(discord.ui.View):
    def __init__(self, bot, suggestion_message: discord.Message):
        super().__init__(timeout=None)
        self.bot = bot
        self.suggestion_message = suggestion_message
        self.already_renamed = False

    @discord.ui.button(label="Change Thread Name", style=discord.ButtonStyle.primary, custom_id="change_thread_name")
    async def rename_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.already_renamed:
            await interaction.response.send_message("This suggestion has already been renamed.", ephemeral=True)
            return

        if interaction.user.guild_permissions.manage_threads or interaction.user.guild_permissions.administrator:
            modal = EditThreadNameModal(interaction.message, self.suggestion_message, interaction.user)
            self.already_renamed = True
            button.disabled = True
            await interaction.response.send_modal(modal)

            try:
                await interaction.followup.edit_message(interaction.message.id, view=self)
            except:
                pass
        else:
            await interaction.response.send_message("You don’t have permission to rename this thread.", ephemeral=True)


class FullButtonsView(discord.ui.View):
    def __init__(self, bot, suggestion_message: discord.Message):
        super().__init__(timeout=None)
        self.bot = bot
        self.suggestion_message = suggestion_message
        self.already_renamed = False

    @discord.ui.button(label="Change Threadname", style=discord.ButtonStyle.primary, custom_id="change_thread_name")
    async def rename_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.already_renamed:
            await interaction.response.send_message("This suggestion has already been renamed.", ephemeral=True)
            return

        if interaction.user.guild_permissions.manage_threads or interaction.user.guild_permissions.administrator:
            modal = EditThreadNameModal(interaction.message, self.suggestion_message, interaction.user)
            self.already_renamed = True
            button.disabled = True
            await interaction.response.send_modal(modal)
            try:
                await interaction.followup.edit_message(interaction.message.id, view=self)
            except:
                pass
        else:
            await interaction.response.send_message("You don’t have permission to rename this thread.", ephemeral=True)

    @discord.ui.button(label="Mark as noted", style=discord.ButtonStyle.secondary, custom_id="mark_noted")
    async def mark_noted(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.guild_permissions.administrator or (developer_role in [r.id for r in interaction.user.roles]):
            await self.suggestion_message.clear_reactions()
            await self.suggestion_message.add_reaction("⏳")
            button.disabled = True
            await interaction.response.edit_message(view=self)
            await interaction.channel.edit(name=f"Noted - {interaction.channel.name}")
            await interaction.followup.send("Suggestion marked as noted.", ephemeral=True)
        else:
            await interaction.response.send_message("You don’t have permission to mark as noted.", ephemeral=True)

    @discord.ui.button(label="Mark as approved/done", style=discord.ButtonStyle.success, custom_id="mark_approved")
    async def mark_approved(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.guild_permissions.administrator or (developer_role in [r.id for r in interaction.user.roles]):
            await self.suggestion_message.clear_reactions()
            await self.suggestion_message.add_reaction("✅")
            button.disabled = True
            await interaction.response.edit_message(view=self)

            old_name = interaction.channel.name
            clean_name = old_name.removeprefix("Noted - ")
            await interaction.channel.edit(name=f"Fixed - {clean_name}")
            await interaction.followup.send("Suggestion marked as approved/done.", ephemeral=True)

            if isinstance(interaction.channel, discord.Thread):
                await interaction.channel.edit(archived=True)
                archive_channel = interaction.guild.get_channel(channel_suggestions_archive)
                thread_link = f"https://discord.com/channels/{interaction.guild.id}/{interaction.channel.id}"
                if archive_channel:
                    await archive_channel.send(
                        f"Thread **{interaction.channel.name}** has been marked as approved/done and archived.\nYou can access it here: {thread_link}"
                    )
        else:
            await interaction.response.send_message("You don’t have permission to mark as approved/done.", ephemeral=True)

    
# --- COG ---
class SuggestionsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(bot):
        print("[SuggestionsCog] Loaded!")

    async def cog_unload(bot):
        print("[SuggestionsCog] Unloaded")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if isinstance(message.channel, discord.Thread) and isinstance(message.channel.parent, discord.ForumChannel):
            if message.channel.parent.id != channel_suggestions:
                return

            if message.id == message.channel.id
                try:
                    await message.add_reaction("👍")
                    await message.add_reaction("👎")
                except:
                    pass

                msg_text = (
                    f"{message.author.mention}, this is your suggestion.\n"
                    f"Admins can rename or mark it using the buttons below."
                )
                view = FullButtonsView(self.bot, message)
                await message.channel.send(msg_text, view=view)

async def setup(bot):
    await bot.add_cog(SuggestionsCog(bot))
