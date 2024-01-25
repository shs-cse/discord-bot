import vars
import discord
import re
import literals
from discord import utils, default_permissions, ui
from discord.ext import commands


def get_role(name):
    print(f"... fetching role: {name}")
    return utils.get(vars.guild.roles, name=name)


def get_category(name):
    return utils.get(vars.guild.categories, name=name)


def get_channel(name):
    return utils.get(vars.guild.channels, name=name)


def get_member(id):
    return utils.get(vars.guild.members, id=int(id))

# sheets id -> link


def get_link_from_sheet_id(sheet_id):
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}"

# link -> sheets id


def get_sheet_id_from_link(link):
    return re.search(literals.regex_file_folder_id, link).group()


# decorator for slash command permissions
roles_hierarchy = ['student-tutor', 'faculty', 'bot-admin', 'admin']

bot_admin_permissions = {'manage_guild': True}
bot_admin_and_higher_roles = roles_hierarchy[2:]


def bot_admin_and_higher():
    checks = [commands.is_owner(), commands.has_any_role(
        *bot_admin_and_higher_roles)]

    def deco(func):
        return commands.check_any(*checks)(default_permissions(**bot_admin_permissions))(func)
    return deco


faculty_permissions = {'manage_nicknames': True}
faculty_and_higher_roles = roles_hierarchy[1:]


def faculty_and_higher():
    checks = [commands.is_owner(), commands.has_any_role(
        *faculty_and_higher_roles)]

    def deco(func):
        return commands.check_any(*checks)(default_permissions(**faculty_permissions))(func)
    return deco


# button for opening forms
class OpenFormButton(ui.Button):
    def __init__(self, label, form_to_open, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = label
        self.style = discord.ButtonStyle.blurple
        self.form_to_open = form_to_open
        self.timeout = None

    async def callback(self, interaction):
        await interaction.response.send_modal(self.form_to_open)
