import discord
from discord.ext import commands

import os
from dotenv import load_dotenv

load_dotenv()

role_developer = int(os.getenv("role_developer"))
role_botmanager = int(os.getenv("role_botmanager"))

role_status_ctf = int(os.getenv("role_status_ctf"))
role_status_mcl = int(os.getenv("role_status_mcl"))
role_status_creative = int(os.getenv("role_status_creative"))
role_status_voxelcraft = int(os.getenv("role_status_voxelcraft"))

channel_serverstatus = int(os.getenv("channel_serverstatus"))

class ServerChangeView(discord.ui.View):
    def __init__(self, bot, data_dict):
        super().__init__(timeout=None)
        self.bot = bot
        self.server_name = data_dict["servername"]
        self.role_id = data_dict["roleid"]

    @discord.ui.button(label="🕑", custom_id="updating", style=discord.ButtonStyle.secondary)
    async def updating_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_button_click(interaction, "updating")

    @discord.ui.button(label="🟩", custom_id="online", style=discord.ButtonStyle.secondary)
    async def online_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_button_click(interaction, "online")

    @discord.ui.button(label="🟥", custom_id="offline", style=discord.ButtonStyle.secondary)
    async def offline_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_button_click(interaction, "offline")

    @discord.ui.button(label="🚧", custom_id="maintenance", style=discord.ButtonStyle.secondary)
    async def maintenance_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_button_click(interaction, "maintenance")

    @discord.ui.button(label="🔐", custom_id="whitelist", style=discord.ButtonStyle.secondary)
    async def whitelist_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_button_click(interaction, "whitelist")

    async def handle_button_click(self, interaction: discord.Interaction, state_str: str):
        states = {
            "updating": "🕑",
            "online": "🟩",
            "offline": "🟥",
            "maintenance": "🚧",
            "whitelist": "🔐"
        }
        state = states[interaction.data["custom_id"]]
        has_role = any(role.id == role_developer for role in interaction.user.roles)
        # We keep the check here just in case
        if has_role:
            role = interaction.guild.get_role(self.role_id)

            if not role:
                await interaction.response.send_message(f"Hmm... role ID {self.role_id} wasn't found in this server", ephemeral=True)
            else:
                await role.edit(name=f"{state} {self.server_name}")
                
                if state == "🟩":
                    channel = await self.bot.fetch_channel(channel_serverstatus)
                    await channel.send(f"<@&{self.role_id}> is 🟩 online", delete_after=1)
                
                await interaction.response.send_message(f'Updated server status.\n{state} **{self.server_name}**', ephemeral=True)
        else:
            await interaction.response.send_message('Nice try, but Developer role is required', ephemeral=True)

class ServerSelectView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="CTF", custom_id="ctf", style=discord.ButtonStyle.primary)
    async def ctf_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_button_click(interaction, "ctf")

    @discord.ui.button(label="Mineclone", custom_id="mineclone", style=discord.ButtonStyle.primary)
    async def mineclone_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_button_click(interaction, "mineclone")

    @discord.ui.button(label="Creative", custom_id="creative", style=discord.ButtonStyle.primary)
    async def creative_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_button_click(interaction, "creative")

    @discord.ui.button(label="Voxelcraft [unused]", custom_id="voxelcraft", style=discord.ButtonStyle.secondary)
    async def voxelcraft_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_button_click(interaction, "voxelcraft")

    async def handle_button_click(self, interaction: discord.Interaction, button_id: str):
        has_role = any(role.id == role_developer for role in interaction.user.roles)
        # We keep the check here just in case
        if has_role:
            data = {"servername": "Unavailable", "roleid": 0}
            if button_id == "ctf": data = {"servername": "JMA CTF", "roleid": role_status_ctf}
            elif button_id == "mineclone": data = {"servername": "JMA Mineclone2", "roleid": role_status_mcl}
            elif button_id == "creative": data = {"servername": "JMA Creative", "roleid": role_status_creative}
            elif button_id == "voxelcraft": data = {"servername": "JMA Voxelcraft", "roleid": role_status_voxelcraft}
            embed = discord.Embed(
                title = data["servername"],
                description = f"You're modifying <@&{data['roleid']}>",
                color = discord.Color.yellow()
            )
            view = ServerChangeView(self.bot, data)
            await interaction.response.send_message('', embed=embed, view=view, ephemeral=True)
        else:
            await interaction.response.send_message('Nice try, but Developer role is required', ephemeral=True)

class ServerStatusView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label='Change status', style=discord.ButtonStyle.blurple, custom_id='serverstatus_view:change_status')
    async def change_status(self, interaction: discord.Interaction, button: discord.ui.Button):
        has_role = any(role.id == role_developer for role in interaction.user.roles)
        
        if has_role:
            view = ServerSelectView(self.bot)
            await interaction.response.send_message('Select server:', view=view, ephemeral=True)
        else:
            await interaction.response.send_message('Nice try, but Developer role is required', ephemeral=True)

class ServerStatusCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(bot):
        print("[ServerStatusCog] Loaded!")

    async def cog_unload(bot):
        print("[ServerStatusCog] Unloaded")

    
    @commands.hybrid_command()
    async def server_status_menu(self, ctx: commands.Context):
        """
        Sends a server status menu to the channel.

        Parameters
        ----------
        ctx: commands.Context
            The context of the command invocation
        """
        has_role = any(role.id == role_botmanager for role in interaction.user.roles)
        if not has_role:
            await ctx.send("Hey, you don't have permissions to do that!", delete_after=5)
            return

        embed = discord.Embed(
            description=f"""- <@&{role_status_ctf}>
- <@&{role_status_mcl}>
- <@&{role_status_creative}>
- <@&{role_status_voxelcraft}>
----------
Update status ⏬ <@&{role_developer}> are permitted""",
            timestamp=discord.utils.utcnow()
        )
        embed.set_footer(text="View updated > ")

        view = ServerStatusView(self.bot)
        await ctx.send("", embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(ServerStatusCog(bot))

    bot.add_view(ServerStatusView(bot))