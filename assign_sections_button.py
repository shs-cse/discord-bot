# pylint: disable=unsubscriptable-object
import discord, re, vars, literals
from discord.ui import Button, View  #upm package(py-cord)

# ui elements
class AssignSectionsView(View):
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
        if vars.faculty_role not in user.roles:
            embed = discord.Embed(title=":x: Error", description="You are not a faculty member", color=discord.Color.red())
            await interaction.response.send_message(embeds=[embed], ephemeral=True)
            return
        if not re.search(r"^\[[A-Z0-9]{3}\].*", user.display_name):
            embed = discord.Embed(title=":x: Error", color=discord.Color.red())
            embed.description = "Your nickname is not set properly. Please change your nickname to `[INITIAL] Full Name` format first."
            await interaction.response.send_message(embeds=[embed], ephemeral=True)
            return
        else:
            initial = re.search(r"^\[([A-Z0-9]{3})\].*", user.display_name).group(1)
            # remove exisiting section role, if any
            section_roles = [role for role in user.roles if role in vars.all_sec_roles]
            await user.remove_roles(*section_roles)

            embed = discord.Embed(title=":white_check_mark: Success", color=discord.Color.green())
            embed.description = f"You have been given the following sections:\n"

            for ctype in literals.class_types:
                filt = vars.df_routine[f"{ctype.title()} Teacher"].str.contains(initial)
                ctype_sections = vars.df_routine.loc[filt, "Section"].values
                ctype_roles = [vars.sec_roles[sec][ctype] for sec in ctype_sections]
                all_ctype_roles = "\u200b" if not ctype_roles else ", ".join(r.mention for r in ctype_roles)
                embed.add_field(name=f"{ctype.title()} Sections", value=all_ctype_roles)
                # ctype_role_names = [role.name for role in ctype_roles]
                await user.add_roles(*ctype_roles)
            
            # # add theory section roles, if any
            # filt = vars.df_routine["Theory Teacher"].str.contains(initial)
            # theory_sections = vars.df_routine.loc[filt, "Section"].values
            # theory_roles = [vars.sec_roles[sec]['theory'] for sec in theory_sections]
            # theory_role_names = [role.name for role in theory_roles]
            # await user.add_roles(*theory_roles)

            # # add lab section roles, if any
            # filt = vars.df_routine["Lab Teacher"].str.contains(initial)
            # lab_sections = vars.df_routine.loc[filt, "Section"].values
            # lab_roles = [vars.sec_roles[sec]['lab'] for sec in lab_sections]
            # lab_role_names = [role.name for role in lab_roles]
            # await user.add_roles(*lab_roles)


            # embed = discord.Embed(title=":white_check_mark: Success", color=discord.Color.green())
            # embed.description = f"You have been given the following sections:\n"
            # all_theory_role_name = "\u200b" if theory_role_names == [] else ", ".join(theory_role_names)
            # all_lab_role_name = "\u200b" if lab_role_names == [] else ", ".join(lab_role_names)

            # embed.add_field(name="Theory Sections", value=all_theory_role_name)
            # embed.add_field(name="Lab Sections", value=all_lab_role_name)
            await interaction.response.send_message(embed=embed, ephemeral=True)