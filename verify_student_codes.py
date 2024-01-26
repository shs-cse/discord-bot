from discord.ui import View, InputText, Modal, Button
from utils_wrapper import OpenFormButton
import discord
import vars
import literals
import re


class VerificationButtonView(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        studen_id_form = SutdentIDForm()
        self.timeout = None
        self.add_item(OpenFormButton(
            label="Verify Me", form_to_open=studen_id_form))


class SutdentIDForm(Modal):
    def __init__(self, *args, **kwargs) -> None:
        kwargs.pop('title', None)
        super().__init__(*args, title="Verification Form", **kwargs)
        self.timeout = None
        self.add_item(
            InputText(label="What's your ***Student ID***?",
                      placeholder="00000000",
                      min_length=8,
                      max_length=8,
                      required=True))
        self.add_item(
            InputText(label="Retype your ***Student ID***.",
                      placeholder="00000000",
                      min_length=8,
                      max_length=8,
                      required=True))

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        input_text = self.children[0].value
        reinput_text = self.children[1].value
        try:
            embed, view = await check_student(interaction.user, input_text, reinput_text)
        except:
            embed = discord.Embed(
                title=":x: You could not be verified", color=discord.Color.red())
            embed.description = "Something went wrong. Please try again later."
            view = View()  # empty view instead of None to prevent error
        await interaction.followup.send(view=view, embeds=[embed], ephemeral=True)


async def check_student(member, input_text, reinput_text=None):
    # possible cases:
    # 0. retyped input does not match
    # 1. id is not a valid student id
    # 2. id is valid but not in the sheet
    # 3. id is valid and in the sheet, but already taken (by another student/their old id. by another -> contact admin. by their old id -> remove old id from sheet)
    # 4. id is valid and in the sheet, but discord does not match with advising server id (you sure?)
    # 5. id is valid and in the sheet, no discord id in advising server/matches with advising id (success)

    # Handle case 0-4: failure
    embed = discord.Embed(
        title=":x: You could not be verified", color=discord.Color.red())
    view = View()  # empty view instead of None to prevent error
    
    # Case 0: retyped input does not match
    if reinput_text and reinput_text != input_text:
        embed.description = f"Please try again. Your inputs `{input_text}` and `{reinput_text}` does not match."
        return embed, view
    
    # Case 1: id is not a valid student id
    extract_id = re.search(literals.regex_student['id'], input_text)
    if not extract_id:
        embed.description = f"Please try again. `{input_text}` is not a valid student ID."
        return embed, view

    student_id = int(extract_id.group(0))
    # Case 2: id is valid but not in the sheet
    if student_id not in vars.df_student.index:
        embed.description = f"`{student_id}` is not in our database. Please double check your student ID and try again."
        return embed, view

    # Case 3: id is valid and in the sheet, but already taken (by another student/their old id)
    existing_mem = None
    for student in vars.student_role.members:
        if str(student_id) in student.display_name:
            existing_mem = student
            break

    if existing_mem: # taken by another student -> contact admin
        embed.description = f"`{student_id}` is already taken by {existing_mem.mention}. "
        embed.description += "If this is your old ID and you want to use this new one, please remove the old one first. "
        embed.description += "If someone else took your ID, Please contact an admin ASAP."
        return embed, view

    # Case 4: id is valid and in the sheet, but discord does not match with advising server id (you sure?)
    advising_id = vars.df_student.loc[student_id, "Discord ID (Adv. Verified)"]
    if advising_id != "" and advising_id != member.id:
        # member's account exists in enrolment sheet with a different student id (conflict_id)
        if member.id in vars.df_student["Discord ID (Adv. Verified)"]:
            conflict_id = vars.df_student[vars.df_student["Discord ID (Adv. Verified)"]
                                          == member.id].index[0]
            conflict_name = vars.df_student.loc[conflict_id, "Name"]
            student_name = vars.df_student.loc[student_id, "Name"]
            embed.description = f"Your discord account is verified as `[{conflict_id}] {conflict_name.title()[:21]}` in the advising server. "
            embed.description += f"However, you are trying to get verified as `[{student_id}] {student_name.title()[:21]}`. "
            embed.description += "If you think this is an error, please contact an admin with proper proof."
        # member probably has alt account -> sure?
        else:
            embed.description = f"`{student_id}` was used by account with discord account <@{advising_id}> in the advising server. "
            embed.description += f"Are you sure you want to use this account ({member.mention}) with student id `{student_id}` for this server? "
            embed.description += "We recommend using the same id for both servers."

            yes_button = Button(
                label="Yes", style=discord.ButtonStyle.green, custom_id="yes")
            no_button = Button(
                label="No", style=discord.ButtonStyle.red, custom_id="no")

            async def yes_button_callback(interaction):
                message_id = interaction.message.id
                await interaction.response.defer(ephemeral=True)
                try:
                    embed = await verify_student(member, student_id)
                except:
                    embed = discord.Embed(
                        title=":x: You could not be verified", color=discord.Color.red())
                    embed.description = "Something went wrong while calling `verify_student`. Please try again later."
                await interaction.followup.edit_message(message_id, view=None, embeds=[embed])

            async def no_button_callback(interaction):
                embed.description = "You selected no. Please try again with the correct account."
                await interaction.response.edit_message(view=None, embeds=[embed])

            yes_button.callback = yes_button_callback
            no_button.callback = no_button_callback

            view = View(timeout=None)
            view.add_item(yes_button)
            view.add_item(no_button)
            return embed, view


    # Case 5: id is valid and in the sheet, no discord id in advising server/matches with advising id (success)
    embed = await verify_student(member, student_id)
    return embed, view


async def verify_student(user, student_id):
    student_name = vars.df_student.loc[student_id, "Name"]
    section = vars.df_student.loc[student_id, "Section"]

    # set nickname
    nick_to_set = f"[{student_id}] {student_name.title()}"
    await user.edit(nick=nick_to_set[:32])

    # handle section role
    sec_roles_to_add = set(vars.sec_roles[section].values())
    existing_sec_roles = vars.all_sec_roles & set(user.roles)
    if not existing_sec_roles:
        await user.add_roles(*sec_roles_to_add)
    elif len(existing_sec_roles) != 2 or vars.sec_roles[section]["theory"] not in existing_sec_roles:
        await user.remove_roles(*existing_sec_roles)
        await user.add_roles(*sec_roles_to_add)

    # add @student role
    if vars.student_role not in user.roles:
        await user.add_roles(vars.student_role)

    embed = discord.Embed(
        title=":white_check_mark: You have been verified", color=discord.Color.green())
    embed.add_field(name="Student ID", value=str(student_id))
    embed.add_field(name="Student Name", value=student_name)
    embed.add_field(name="Section", value=f"{section:02d}")

    return embed
