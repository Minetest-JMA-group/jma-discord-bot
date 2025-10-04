import discord
from discord.ext import commands
from discord import app_commands
import sqlite3


# --- SQLITE SETUP ---
conn = sqlite3.connect("variables.db")
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS variables (title TEXT PRIMARY KEY, value TEXT)")
conn.commit()


# --- MODALS ---
class AddVariableModal(discord.ui.Modal, title="Add a Variable"):
    def __init__(self, cog, value):
        super().__init__()
        self.cog = cog
        self.value = value

        self.title_input = discord.ui.TextInput(
            label="Variable Title",
            placeholder="Enter variable name...",
            required=True,
            max_length=50
        )
        self.add_item(self.title_input)

    async def on_submit(self, interaction: discord.Interaction):
        title = self.title_input.value.strip()
        value = str(self.value).strip()

        cur.execute("SELECT 1 FROM variables WHERE title=?", (title,))
        if cur.fetchone():
            embed = discord.Embed(description=f"Variable **{title}** already exists.", colour=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        cur.execute("INSERT INTO variables (title, value) VALUES (?, ?)", (title, value))
        conn.commit()

        embed = discord.Embed(
            title="Variable Added",
            description=f"**{title}** → `{value}`",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

        if hasattr(self.cog, "add_menu_message") and self.cog.add_menu_message:
            try:
                await self.cog.add_menu_message.delete()
                self.cog.add_menu_message = None
            except Exception:
                pass

        await self.cog.refresh_menu()


# --- MODIFY ---
class ModifyVariableModal(discord.ui.Modal, title="Modify Variable"):
    def __init__(self, cog, current_title, new_value, parent_message=None):
        super().__init__()
        self.cog = cog
        self.current_title = current_title
        self.parent_message = parent_message

        self.name_input = discord.ui.TextInput(
            label="Variable Name",
            style=discord.TextStyle.short,
            required=True,
            max_length=50,
            default=current_title
        )

        self.value_input = discord.ui.TextInput(
            label="Variable Value",
            style=discord.TextStyle.short,
            required=True,
            max_length=200,
            default=str(new_value)
        )

        self.add_item(self.name_input)
        self.add_item(self.value_input)

    async def on_submit(self, interaction: discord.Interaction):
        new_name = self.name_input.value.strip()
        new_value = self.value_input.value.strip()

        if new_name != self.current_title:
            cur.execute("SELECT 1 FROM variables WHERE title=?", (new_name,))
            if cur.fetchone():
                embed = discord.Embed(
                    description=f"Variable **{new_name}** already exists.",
                    colour=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

        cur.execute(
            "UPDATE variables SET title=?, value=? WHERE title=?",
            (new_name, new_value, self.current_title)
        )
        conn.commit()

        embed = discord.Embed(
            description=f"Variable **{self.current_title}** updated to **{new_name}** with value `{new_value}`",
            colour=discord.Color.green()
        )

        if self.parent_message:
            new_embed = discord.Embed(
                description=f"🔧 Choose a new value type for **{new_name}**",
                color=discord.Color.blurple()
            )
            await self.parent_message.edit(embed=new_embed)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        await self.cog.refresh_menu()

        if hasattr(self.cog, "modify_menu_message") and self.cog.modify_menu_message:
            try:
                await self.cog.modify_menu_message.delete()
                self.cog.modify_menu_message = None
            except Exception:
                pass


class ModifyChooseValueView(discord.ui.View):
    def __init__(self, cog, var_name, old_value):
        super().__init__(timeout=60)
        self.cog = cog
        self.var_name = var_name
        self.old_value = old_value
        self.parent_message = None

    def set_parent_message(self, message):
        self.parent_message = message

    @discord.ui.select(cls=discord.ui.ChannelSelect, placeholder="Choose new channel")
    async def select_channel(self, interaction: discord.Interaction, select: discord.ui.ChannelSelect):
        channel = select.values[0]
        await interaction.response.send_modal(
            ModifyVariableModal(self.cog, self.var_name, channel.id, parent_message=self.parent_message)
        )

    @discord.ui.select(cls=discord.ui.MentionableSelect, placeholder="Choose new role/user")
    async def select_mentionable(self, interaction: discord.Interaction, select: discord.ui.MentionableSelect):
        mentionable = select.values[0]
        await interaction.response.send_modal(
            ModifyVariableModal(self.cog, self.var_name, mentionable.id, parent_message=self.parent_message)
        )

    @discord.ui.button(label="Custom Value", style=discord.ButtonStyle.primary)
    async def custom_value(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(
            ModifyVariableModal(self.cog, self.var_name, self.old_value, parent_message=self.parent_message)
        )


# --- DELETE ---
class DeleteConfirmView(discord.ui.View):
    def __init__(self, cog, var_name):
        super().__init__(timeout=30)
        self.cog = cog
        self.var_name = var_name

    @discord.ui.button(label="Confirm Delete", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        cur.execute("DELETE FROM variables WHERE title=?", (self.var_name,))
        conn.commit()
        embed = discord.Embed(description=f"Variable **{self.var_name}** deleted.", colour=discord.Color.green())
        await interaction.response.edit_message(embed=embed, view=None)
        await self.cog.refresh_menu()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(description=f"Delete of **{self.var_name}** cancelled.", colour=discord.Color.red())
        await interaction.response.edit_message(embed=embed, view=None)


# --- VALUE PICKER FOR CREATION ---
class ChooseValueView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=60)
        self.cog = cog

    @discord.ui.select(cls=discord.ui.ChannelSelect, placeholder="Choose a channel")
    async def select_channel(self, interaction: discord.Interaction, select: discord.ui.ChannelSelect):
        channel = select.values[0]
        await interaction.response.send_modal(AddVariableModal(self.cog, value=channel.id))

    @discord.ui.select(cls=discord.ui.MentionableSelect, placeholder="Choose a user or role")
    async def select_mentionable(self, interaction: discord.Interaction, select: discord.ui.MentionableSelect):
        mentionable = select.values[0]
        await interaction.response.send_modal(AddVariableModal(self.cog, value=mentionable.id))


# --- MODIFY / DELETE VIEW ---
class ModifyVariableSelect(discord.ui.Select):
    def __init__(self, cog):
        self.cog = cog
        cur.execute("SELECT title, value FROM variables")
        rows = cur.fetchall()

        if rows:
            options = [
                discord.SelectOption(label=r[0], description=f"{r[1]}") for r in rows
            ]
            disabled = False
        else:
            options = [discord.SelectOption(label="No variables available", description="Add one first", default=True)]
            disabled = True

        super().__init__(
            placeholder="Modify variable",
            min_values=1,
            max_values=1,
            options=options,
            disabled=disabled
        )

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You don't have permission.", ephemeral=True)
            return

        var_name = self.values[0]
        cur.execute("SELECT value FROM variables WHERE title=?", (var_name,))
        var_value = cur.fetchone()[0]

        view = ModifyChooseValueView(self.cog, var_name, var_value)
        embed = discord.Embed(
            description=f"🔧 Choose a new value type for **{var_name}**",
            color=discord.Color.blurple()
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        sent_message = await interaction.original_response()
        view.set_parent_message(sent_message)
        self.cog.modify_menu_message = sent_message


class DeleteVariableSelect(discord.ui.Select):
    def __init__(self, cog):
        self.cog = cog
        cur.execute("SELECT title, value FROM variables")
        rows = cur.fetchall()

        if rows:
            options = [
                discord.SelectOption(label=r[0], description=f"{r[1]}") for r in rows
            ]
            disabled = False
        else:
            options = [discord.SelectOption(label="No variables available", description="Add one first", default=True)]
            disabled = True

        super().__init__(
            placeholder="Delete variable",
            min_values=1,
            max_values=1,
            options=options,
            disabled=disabled
        )

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You don't have permission.", ephemeral=True)
            return

        var_name = self.values[0]
        view = DeleteConfirmView(self.cog, var_name)
        embed = discord.Embed(
            description=f"⚠️ Are you sure you want to delete **{var_name}**?",
            color=discord.Color.yellow()
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


# --- MAIN MENU VIEW ---
class AdminVarsView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

        self.add_item(ModifyVariableSelect(cog))
        self.add_item(DeleteVariableSelect(cog))

    @discord.ui.button(label="Add variable", style=discord.ButtonStyle.primary)
    async def add_var(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You don't have permission.", ephemeral=True)
            return

        view = ChooseValueView(self.cog)
        embed = discord.Embed(
            description="Choose how you want to set the value:",
            color=discord.Color.blurple()
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        self.cog.add_menu_message = await interaction.original_response()


# --- COG ---
class AdminVarsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.menu_message = None
        self.add_menu_message = None
        self.modify_menu_message = None

    async def cog_load(self):
        print("[AdminVarsCog] Loaded!")

    async def cog_unload(self):
        print("[AdminVarsCog] Unloaded!")

    def build_admin_variable_embed(self):
        cur.execute("SELECT title, value FROM variables")
        variables = cur.fetchall()
        if variables:
            desc = "\n".join([f"**{title}** : `{value}`" for title, value in variables])
        else:
            desc = "*No variables yet.*"
        return discord.Embed(title="Admin Variables Menu", description=desc, color=discord.Color.blue())

    async def refresh_menu(self):
        if self.menu_message:
            embed = self.build_admin_variable_embed()
            view = AdminVarsView(self)
            await self.menu_message.edit(embed=embed, view=view)

    @app_commands.command(name="admin-vars", description="Admin variable manager")
    @app_commands.default_permissions(administrator=True)
    async def admin_vars(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You don't have permission.", ephemeral=True)
            return

        embed = self.build_admin_variable_embed()
        view = AdminVarsView(self)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        self.menu_message = await interaction.original_response()


async def setup(bot):
    await bot.add_cog(AdminVarsCog(bot))
