import discord
from discord.ext import commands
import re
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


def get_channel_onewordstory():
    return int(get_variable_value("One word story channel"))


def get_channel_onewordstorylog():
    return int(get_variable_value("One word story log channel"))


class OneWordStoryCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_author_id = None
        self.word_count = 0
        self.story_ended = False
        self.story_message = None
        self.story_content = []
        self.approved_message_ids = set()
        self.approved_messages = {}
        self.max_word_length = 20

    async def cog_load(self):
        print("[OneWordStoryCog] Loaded!")

    async def cog_unload(self):
        print("[OneWordStoryCog] Unloaded")
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if message.channel.id != get_channel_onewordstory():
            return

        if self.story_ended:
            await message.delete()
            return

        if message.author.id == self.last_author_id:
            await message.delete()
            return

        if not re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ]+|\.", message.content.strip()):
            await message.delete()
            return
        
        if len(message.content.strip()) > self.max_word_length:
            await message.delete()
            return

        word = message.content.strip()

        if word == ".":
            if self.word_count < 50:
                await message.delete()
                return
            else:
                self.story_ended = True
                full_story = " ".join(self.story_content)

                log_channel = await self.bot.fetch_channel(get_channel_onewordstorylog())
                if self.story_message:
                    finished_embed = discord.Embed(
                        title="📖 One Word Story Completed",
                        description=full_story,
                        color=discord.Color.blue()
                    )
                    await self.story_message.edit(embed=finished_embed)

                story_channel = await self.bot.fetch_channel(get_channel_onewordstory())
                final_embed = discord.Embed(
                    title="📖 One Word Story Finished",
                    description=full_story,
                    color=discord.Color.blue()
                )
                await story_channel.send(embed=final_embed)

                self.last_author_id = None
                self.word_count = 0
                self.story_ended = False
                self.story_message = None
                self.story_content = []
                self.approved_messages[message.id] = word

                return

        self.word_count += 1
        self.last_author_id = message.author.id
        self.story_content.append(word)
        self.approved_message_ids.add(message.id)

        log_channel = await self.bot.fetch_channel(get_channel_onewordstorylog())

        embed = discord.Embed(
            title="📖 One Word Story in progress",
            description=" ".join(self.story_content),
            color=discord.Color.blue()
        )

        if self.story_message is None:
            self.story_message = await log_channel.send(embed=embed)
        else:
            await self.story_message.edit(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot:
            return

        if message.channel.id != get_channel_onewordstory():
            return

        if message.id not in self.approved_message_ids:
            return

        word = message.content.strip()
        if not re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ]+|\.", word):
            return
        if word == "." and self.word_count < 50:
            return

        await message.channel.send(f"{message.author.mention} : {word}")
    
    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if after.author.bot:
            return
        if after.channel.id != get_channel_onewordstory():
            return
        if before.id not in self.approved_message_ids:
            return

        await after.delete()

        original_word = self.approved_messages.get(before.id)
        if original_word:
            await after.channel.send(f"{after.author.mention} : {original_word}")


async def setup(bot):
    await bot.add_cog(OneWordStoryCog(bot))
