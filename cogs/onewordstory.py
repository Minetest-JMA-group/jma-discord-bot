import discord
from discord.ext import commands
import re
import os
from dotenv import load_dotenv

load_dotenv()

role_onewordmanager = int(os.getenv("role_onewordmanager"))
channel_onewordstory = int(os.getenv("channel_onewordstory"))
channel_onewordstorylog = int(os.getenv("channel_onewordstorylog"))

class OneWordStoryCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_author_id = None
        self.word_count = 0
        self.story_ended = False
        self.story_message = None
        self.story_content = []
        self.approved_message_ids = set()

    async def cog_load(self):
        print("[OneWordStoryCog] Loaded!")

    async def cog_unload(self):
        print("[OneWordStoryCog] Unloaded")
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if message.channel.id != channel_onewordstory:
            return

        if self.story_ended:
            await message.delete()
            return

        # If the same user sends two words in a row -> delete
        if message.author.id == self.last_author_id:
            await message.delete()
            return

        # Only letters allowed, or "." to end
        if not re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ]+|\.", message.content.strip()):
            await message.delete()
            return

        word = message.content.strip()

        # End of story
        if word == ".":
            if self.word_count < 50:
                await message.delete()
                return
            else:
                self.story_ended = True
                full_story = " ".join(self.story_content)

                log_channel = await self.bot.fetch_channel(channel_onewordstorylog)
                if self.story_message:
                    finished_embed = discord.Embed(
                        title="📖 One Word Story Completed",
                        description=full_story,
                        color=discord.Color.blue()
                    )
                    await self.story_message.edit(embed=finished_embed)

                # Send the final story in one word story channel
                story_channel = await self.bot.fetch_channel(channel_onewordstory)
                final_embed = discord.Embed(
                    title="📖 One Word Story Finished",
                    description=full_story,
                    color=discord.Color.blue()
                )
                await story_channel.send(embed=final_embed)

                # Restart a new story
                self.last_author_id = None
                self.word_count = 0
                self.story_ended = False
                self.story_message = None
                self.story_content = []

                return

        # Accept word
        self.word_count += 1
        self.last_author_id = message.author.id
        self.story_content.append(word)
        self.approved_message_ids.add(message.id)

        log_channel = await self.bot.fetch_channel(channel_onewordstorylog)

        embed = discord.Embed(
            title="📖 One Word Story in progress",
            description=" ".join(self.story_content),
            color=discord.Color.blue()
        )

        if self.story_message is None:
            self.story_message = await log_channel.send(embed=embed)
        else:
            await self.story_message.edit(embed=embed)

    #@commands.hybrid_command()
    #async def onewordstory_reset(self, ctx):
    #    """
    #   Reset the One Word Story
    #
    #    Parameters
    #    ----------
    #    ctx: commands.Context
    #        The context of the command invocation
    #    """
    #    if not discord.utils.get(ctx.author.roles, id=role_onewordmanager):
    #        return await ctx.send("🚫 You don't have permission!", delete_after=5)
    #
    #    self.last_author_id = None
    #    self.word_count = 0
    #    self.story_ended = False
    #    self.story_message = None
    #    self.story_content = []
    #
    #    await ctx.send("✅ One Word Story has been reset!", delete_after=5)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot:
            return
        if message.channel.id != channel_onewordstory:
            return

        if message.id not in self.approved_message_ids:
            return

        word = message.content.strip()
        if not re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ]+|\.", word):
            return
        if word == "." and self.word_count < 50:
            return

        await message.channel.send(f"{message.author.mention} : {word}")

async def setup(bot):
    await bot.add_cog(OneWordStoryCog(bot))
