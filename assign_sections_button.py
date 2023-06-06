# pylint: disable=unsubscriptable-object
import discord
import re
import vars
import literals
from discord.ui import Button, View  # upm package(py-cord)

# ui elements


class AssignSectionsButtonView(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timeout = None
        self.add_item(AssignSectionsButton(label="Get Section Access"))


class AssignSectionsButton(Button):
    def __init__(self, label, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = label
        self.style = discord.ButtonStyle.blurple
        self.timeout = None

    async def callback(self, interaction):
        user = interaction.user
        await interaction.response.defer(ephemeral=True)
        embed = await assign_sections(user)
        await interaction.followup.send(embeds=[embed], ephemeral=True)


async def assign_sections(member):
    if vars.faculty_role not in member.roles:
        embed = discord.Embed(
            title=":x: Error", description="You are not a faculty member", color=discord.Color.red())
        return embed
    if not re.search(r"^\[[A-Z0-9]{3}\].*", member.display_name):
        embed = discord.Embed(title=":x: Error", color=discord.Color.red())
        embed.description = "Your nickname is not set properly. Please change your nickname to `[INITIAL] Full Name` format first."
        return embed
    else:
        initial = re.search(
            r"^\[([A-Z0-9]{3})\].*", member.display_name).group(1)
        print(f"Assigning section roles to {initial}")
        # remove exisiting section role, if any
        section_roles = [
            role for role in member.roles if role in vars.all_sec_roles]
        await member.remove_roles(*section_roles)
        await member.remove_roles(*vars.thoery_and_lab_faculty_roles.values())

        embed = discord.Embed(
            title=":white_check_mark: Success", color=discord.Color.green())
        embed.description = f"You have been given the following sections:\n"

        for ctype in literals.class_types:
            filt = vars.df_routine[f"{ctype.title()} Teacher"].str.contains(
                initial)
            ctype_sections = vars.df_routine.loc[filt, "Section"].values
            ctype_roles = [vars.sec_roles[sec][ctype]
                           for sec in ctype_sections]
            all_ctype_roles = "\u200b" if not ctype_roles else ", ".join(
                r.mention for r in ctype_roles)
            embed.add_field(
                name=f"{ctype.title()} Sections", value=all_ctype_roles)
            await member.add_roles(*ctype_roles)
            if ctype_sections.any():
                await member.add_roles(vars.thoery_and_lab_faculty_roles[ctype])

        return embed
