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

role_Manage_Threads = int(os.getenv("role_Manage_Threads"))

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

        try:
            await self.message_to_delete.delete()
        except:
            pass

        embed = discord.Embed(description="**:white_check_mark: Thread renamed**",
                              colour=discord.Color.green())

        view = FullButtonsView(interaction.client, self.suggestion_author, self.suggestion_message)
        await interaction.response.send_message(embed=embed, view=view)

# --- VIEWS ---
class RenameOnlyView(discord.ui.View):
    def __init__(self, bot, user: discord.User, suggestion_message: discord.Message):
        super().__init__(timeout=None)
        self.bot = bot
        self.user = user
        self.suggestion_message = suggestion_message

    @discord.ui.button(label="Change Threadname", custom_id="change_thread_name_initial", style=discord.ButtonStyle.primary)
    async def rename_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if (interaction.user.id == self.user.id) or (role_Manage_Threads in [r.id for r in interaction.user.roles]):
            modal = EditThreadNameModal(interaction.message, self.suggestion_message, self.user)
            await interaction.response.send_modal(modal)
        else:
            embed = discord.Embed(description="**You don’t have permission to rename this thread.**",
                                  colour=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)

class FullButtonsView(discord.ui.View):
    def __init__(self, bot, user: discord.User, suggestion_message: discord.Message):
        super().__init__(timeout=None)
        self.bot = bot
        self.user = user
        self.suggestion_message = suggestion_message

    @discord.ui.button(label="Change Threadname", custom_id="change_thread_name_full", style=discord.ButtonStyle.primary)
    async def rename_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if (role_Manage_Threads in [r.id for r in interaction.user.roles]):
            modal = EditThreadNameModal(interaction.message, self.suggestion_message, self.user)
            await interaction.response.send_modal(modal)
        else:
            embed = discord.Embed(
                description="**You don’t have permission to rename this thread.**",
                colour=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Mark as noted", custom_id="mark_noted", style=discord.ButtonStyle.secondary)
    async def mark_noted(self, interaction: discord.Interaction, button: discord.ui.Button):
        #developer_role = get_developer_role()
        if interaction.user.guild_permissions.administrator or (developer_role and developer_role in [r.id for r in interaction.user.roles]):
            await self.suggestion_message.clear_reactions()
            await self.suggestion_message.add_reaction("⏳")
            button.disabled = True
            await interaction.response.edit_message(view=self)
            embed = discord.Embed(description="**Suggestion marked as noted.**", colour=discord.Color.yellow())
            await interaction.channel.edit(name=f"Noted - {interaction.channel.name}")
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(description="**You don’t have permission to mark as noted.**", colour=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Mark as approved/done", custom_id="mark_approved", style=discord.ButtonStyle.success)
    async def mark_approved(self, interaction: discord.Interaction, button: discord.ui.Button):
        #developer_role = get_developer_role()
        if interaction.user.guild_permissions.administrator or (developer_role and developer_role in [r.id for r in interaction.user.roles]):
            await self.suggestion_message.clear_reactions()
            await self.suggestion_message.add_reaction("✅")
            button.disabled = True
            await interaction.response.edit_message(view=self)

            old_name = interaction.channel.name
            clean_name = old_name.removeprefix("Noted - ")
            await interaction.channel.edit(name=f"Fixed - {clean_name}")

            embed = discord.Embed(description="**Suggestion marked as approved/done.**", colour=discord.Color.green())
            await interaction.followup.send(embed=embed, ephemeral=True)

            # --- ARCHIVE ---
            if isinstance(interaction.channel, discord.Thread):
                await interaction.channel.edit(archived=True)

                archive_channel = interaction.guild.get_channel(channel_suggestions_archive)
                thread_link = f"https://discord.com/channels/{interaction.guild.id}/{interaction.channel.id}"
                if archive_channel:
                    archive_embed = discord.Embed(
                        description=f"**Thread '{interaction.channel.name}' has been marked as approved/done and archived.**\nYou can access here: {thread_link}",
                        colour=discord.Color.green()
                    )
                    await archive_channel.send(embed=archive_embed)
        else:
            embed = discord.Embed(description="**You don’t have permission to mark as approved/done.**", colour=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)

"""    @discord.ui.button(label="Mark as approved/done", custom_id="mark_approved", style=discord.ButtonStyle.success)
    async def mark_approved(self, interaction: discord.Interaction, button: discord.ui.Button):
        developer_role = get_developer_role()
        if interaction.user.guild_permissions.administrator or (developer_role and developer_role in [r.id for r in interaction.user.roles]):
            await self.suggestion_message.clear_reactions()
            await self.suggestion_message.add_reaction("✅")
            button.disabled = True
            await interaction.response.edit_message(view=self)

            # --- ARCHIVE ---
            if isinstance(interaction.channel, discord.Thread):
                new_name = f"Fixed - {interaction.channel.name}"
                await interaction.channel.edit(name=new_name, archived=True)

                archive_channel = interaction.guild.get_channel(channel_suggestions_archive)
                thread_link = f"https://discord.com/channels/{interaction.guild.id}/{interaction.channel.id}"
                if archive_channel:
                    archive_embed = discord.Embed(
                        description=f"**Thread '{new_name}' has been marked as approved/done and archived.**\nYou can access it here: {thread_link}",
                        colour=discord.Color.green()
                    )
                    await archive_channel.send(embed=archive_embed)

            embed = discord.Embed(description="**Suggestion marked as approved/done and archived.**", colour=discord.Color.green())
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(description="**You don’t have permission to mark as approved/done.**", colour=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)"""
    
# --- COG ---
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
            if message.thread is None:
                thread = await message.create_thread(name=f"Suggestion by {message.author.display_name}")
            else:
                thread = message.thread
            #embed = discord.Embed(description=f"**{message.author.mention} Please rename the thread !**", colour=discord.Color.blue())
            expire_timestamp = int(time.time()) + 600
            embed = discord.Embed(
                description=f"**{message.author.mention} The suggestion and the thread will be deleted <t:{expire_timestamp}:R> if you don't rename the thread.**",
                colour=discord.Color.blue()
            )

            view = RenameOnlyView(self.bot, message.author, message)
            await thread.send(embed=embed, view=view)
            
            asyncio.create_task(self.check_rename_timeout(thread, message))
        
    async def check_rename_timeout(self, thread: discord.Thread, suggestion_message: discord.Message):
        await asyncio.sleep(600)

        try:
            updated_thread = await thread.guild.fetch_channel(thread.id)
        except discord.NotFound:
            return

        if not updated_thread.name.startswith("Suggestion by"):
            return

        try:
            await updated_thread.delete()
        except:
            pass

        try:
            await suggestion_message.delete()
        except:
            pass

async def setup(bot):
    await bot.add_cog(SuggestionsCog(bot))
