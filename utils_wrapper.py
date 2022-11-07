import vars, discord
from discord import utils, default_permissions, ui
from discord.ext import commands


def get_role(name):
    return utils.get(vars.guild.roles, name=name)

def get_category(name):
    return utils.get(vars.guild.categories, name=name)

def get_channel(name):
    return utils.get(vars.guild.channels, name=name)


# decorator for slash command permissions
roles_hierarchy = ['student-tutor', 'faculty', 'bot-admin', 'admin']

bot_admin_permissions = {'manage_guild' : True}
bot_admin_and_higher_roles = roles_hierarchy[2:]
def bot_admin_and_higher():
    checks = [commands.is_owner(), commands.has_any_role(*bot_admin_and_higher_roles)]
    def deco(func):
        return commands.check_any(*checks)(default_permissions(**bot_admin_permissions))(func)
    return deco

faculty_permissions = {'manage_nicknames' : True}
faculty_and_higher_roles = roles_hierarchy[1:]
def faculty_and_higher():
    checks = [commands.is_owner(), commands.has_any_role(*faculty_and_higher_roles)]
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