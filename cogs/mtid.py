import discord
from discord.ext import commands

import httpx

import os
from dotenv import load_dotenv

load_dotenv()

## TODO: ADD /LINK TO ACCESS REQUEST EMBED TOO

role_mtidadmin = int(os.getenv("role_mtidadmin"))
mtid_address = os.getenv("mtid_address")
mtid_token = os.getenv("mtid_token")
if mtid_address is None:
    print("[MTIDCog] No address specified for MTID API. Not registering cog.")

class MTIDCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(bot):
        print("[MTIDCog] Loaded!")

    async def cog_unload(bot):
        print("[MTIDCog] Unloaded")

    @commands.hybrid_command()
    async def link(self, ctx):
        """
        Link an in-game account

        Parameters
        ----------
        ctx: commands.Context
            The context of the command invocation
        """

        async with httpx.AsyncClient(headers={'Authorization': f'Bearer {mtid_token}'}) as client:
            response = await client.post(f"{mtid_address}/link/create?id={ctx.author.id}")
        if response.status_code == 200:
            embed=discord.Embed(title=":link: How to link your accounts", description=f"1. Open Luanti and log in to the server.\n2. Run the `/link` command.\n3. Enter the code `{response.json()["code"]}`.\nThis code will expire in 15 minutes.", color=0x00abf5)
            await ctx.send(embed=embed, ephemeral=True)
        else:
            await ctx.send(":x: Something went wrong, please try again.", ephemeral=True)

if not mtid_address is None:
    async def setup(bot):
        await bot.add_cog(MTIDCog(bot))