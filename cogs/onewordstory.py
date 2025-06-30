import discord
from discord.ext import commands

import os
from dotenv import load_dotenv

load_dotenv()

role_onewordmanager = int(os.getenv("role_onewordmanager"))
channel_onewordstory = int(os.getenv("channel_onewordstory"))
channel_onewordstorylog = int(os.getenv("channel_onewordstorylog"))

class OneWordStoryEditModal(discord.ui.Modal, title="Edit the story"):
    def __init__(self, story: str = ""):
        super().__init__()

        self.newstory = discord.ui.TextInput(
            label="Content",
            style=discord.TextStyle.long,
            placeholder="You should probably close the form without saving now that you've deleted everything...",
            default=story,  # Pre-filling the feedback field
            required=False,
            max_length=9999,
        )
        self.add_item(self.newstory)

    async def on_submit(self, interaction: discord.Interaction):
        async for message in self.bot.fetch_channel(channel_onewordstorylog).history(limit=1):
            if message.author == bot.user:
                await message.edit(content=self.newstory.value)
                await interaction.response.send_message("✅ Changed story successfully.", ephemeral=True)
                return

        await interaction.response.send_message(f"Something went wrong...", ephemeral=True)

class OneWordStoryCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(bot):
        print("[OneWordStoryCog] Loaded!")

    async def cog_unload(bot):
        print("[OneWordStoryCog] Unloaded")
    
    @commands.hybrid_command()
    async def onewordstory_manage(self, ctx):
        """
        Edit the current One Word story

        Parameters
        ----------
        ctx: commands.Context
            The context of the command invocation
        """
        if not discord.utils.get(ctx.author.roles, id=role_onewordmanager):
            await ctx.send("`This move can’t be used until you get the `<:pokebadge:1357731030441660517>` Bot Developer badge!`", delete_after=5)
        elif ctx.channel.id != channel_onewordstory:
            await ctx.send("`Oak's words echoed... There's a time and place for everything!`", delete_after=5)
        else:
            channel = await self.bot.fetch_channel(channel_onewordstorylog)
            async for message in channel.history(limit=1):
                if message.author == bot.user:
                    modal = OneWordStoryEditModal(default_name=name, default_feedback=message.content)
                    await interaction.response.send_modal(modal)
                    return

            await ctx.send(f"Something went wrong, couldn't find current story!", ephemeral=True)
            

async def setup(bot):
    await bot.add_cog(OneWordStoryCog(bot))