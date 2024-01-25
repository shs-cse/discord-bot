import vars
import literals
import re
from utils_wrapper import get_role, get_channel
from json_wrapper import update_json
from discord_sec_manager import check_discord_sec, get_sec_role
from pygsheets_wrapper import get_sheet_data, update_sheet_values, get_sheet
import pandas as pd
from marks import update_sec_marks


async def sync_init(bot, info):
    vars.guild = bot.get_guild(info['guild_id'])
    vars.eee_guild = bot.get_guild(literals.guild_eee_faculty)
    vars.available_sections = [sec for sec in range(1, info['n_sections']+1)
                               if sec not in info['missing_sections']]

    if not info['invite']:
        welcome = get_channel("👏🏻welcome✌🏻")
        invite = await welcome.create_invite(max_age=0, max_uses=0)
        info['invite'] = invite.url
        update_json(info, vars.json_file)


async def sync_roles(info):
    vars.faculty_role = get_role("faculty")
    vars.thoery_and_lab_faculty_roles[literals.class_types[0]] = get_role(
        "theory-faculty")
    vars.thoery_and_lab_faculty_roles[literals.class_types[1]] = get_role(
        "lab-faculty")
    vars.st_role = get_role("student-tutor")
    vars.admin_role = get_role("admin")
    vars.bot_admin_role = get_role("bot-admin")
    vars.student_role = get_role("student")

    await check_discord_sec(info)
    for sec in vars.available_sections:
        vars.sec_roles[sec] = {ctype: get_sec_role(sec, ctype)
                               for ctype in literals.class_types}

    vars.all_sec_roles = {roles[ctype]
                          for roles in vars.sec_roles.values()
                          for ctype in literals.class_types}


async def sync_sheets(info):
    # pull
    print("Pulling data from sheets...")
    vars.df_student = get_sheet_data(
        info["enrolment"], "StudentList").set_index("Student ID")
    vars.df_student = vars.df_student[vars.df_student.index != '']
    vars.df_routine = get_sheet_data(info["enrolment"], "Routine")
    # TODO: uncomment. commented for debugging.
    # for tracking which student's mark is in which section's sheet
    vars.df_marks_section = vars.df_student[['Discord ID']]
    vars.df_marks_section.insert(1, 'Marks Section', 0)  # new column
    vars.df_marks_section.set_index(
        [vars.df_marks_section.index, 'Discord ID'], inplace=True)
    for sec in vars.available_sections:
        await update_sec_marks(info, sec)

    # push
    print("Pushing discord data to sheets...")
    get_sheet(info['enrolment'], 'Discord').clear('C2:H')
    arr_updated = []
    for k, mem in enumerate(vars.guild.members):
        arr_updated.append([])
        arr_updated[k] += [mem.name, str(mem.id), mem.display_name, mem.roles[0].name]
        # primary and secondary roles
        sorted_roles = [role.name for role in mem.roles[1:]]
        sorted_roles.sort()
        role_one = "" if not sorted_roles[:1] else sorted_roles[0]
        role_two = "" if not sorted_roles[1:] else ", ".join(sorted_roles[1:])
        arr_updated[k] += [role_one, role_two]
    update_sheet_values({"C2": arr_updated},
                        sheet_id=info["enrolment"], sheet_name="Discord")


def sync_usis_before(info, filenames):
    # read Enrolment sheet > USIS (before)
    usis_sheet = get_sheet(info['enrolment'], 'USIS (before)')
    usis_data = usis_sheet.get_as_df(
        start='B1', end='D', include_tailing_empty_rows=False)
    usis_data = usis_data.rename(columns={usis_data.columns[0]: 'Section'})
    # read ATTENDANCE_SHEET_i.xls
    for filename in filenames:
        # get section number
        metadata = pd.read_excel(filename).iloc[0, 1]
        section_no = re.search(r"\nSection :  ([0-9]{2})\n", metadata)[1]
        section_no = int(section_no)
        print(f"updating student list of {section_no = }")
        # get students in that section
        section_students = pd.read_excel(filename, header=2)[["ID", "Name"]]
        section_students.insert(0, 'Section', section_no)
        section_students.columns = usis_data.columns
        # update usis dataframe
        usis_data = usis_data[usis_data['Section'] != section_no]
        usis_data = pd.concat([usis_data, section_students], ignore_index=True)
        usis_data = usis_data.sort_values(
            by=['Section', 'Student ID'], ignore_index=True)
    # update Enrolment sheet > USIS (before)
    end = usis_sheet.rows
    usis_sheet.clear('A2', f'A{end}')
    update_sheet_values(
        {f'A2:A{end}': usis_data.iloc[:, :1].values.tolist()}, usis_sheet)
    usis_sheet.clear('C2', f'D{end}')
    update_sheet_values(
        {f'C2:D{end}': usis_data.iloc[:, 1:].values.tolist()}, usis_sheet)
    vars.df_student = get_sheet_data(
        info["enrolment"], "StudentList").set_index("Student ID")
    vars.df_student = vars.df_student[vars.df_student.index != '']
