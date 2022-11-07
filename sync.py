import vars, literals, re
from utils_wrapper import get_role, get_channel
from json_wrapper import update_json
from discord_sec_manager import check_discord_sec, get_sec_role
from pygsheets_wrapper import get_sheet_data, update_sheet_values
import pandas as pd


async def sync_init(bot, info):
    vars.guild = bot.get_guild(info['guild_id'])
    vars.eee_guild = bot.get_guild(literals.guild_eee_faculty)
    vars.available_sections = [sec for sec in range(1,info['n_sections']+1)
                                   if sec not in info['missing_sections']]

    if not info['invite']:
        welcome = get_channel("👏🏻welcome✌🏻")
        invite = await welcome.create_invite(max_age=0, max_uses=0)
        info['invite'] = invite.url
        update_json(info, vars.json_file)



async def sync_roles(info):
    vars.faculty_role = get_role("faculty")
    vars.st_role = get_role("student-tutor")
    vars.admin_role = get_role("admin")
    vars.bot_admin_role = get_role("bot-admin")
    vars.student_role = get_role("student")

    await check_discord_sec(info)
    for sec in vars.available_sections:
        vars.sec_roles[sec] = {ctype : get_sec_role(sec, ctype) 
                                for ctype in literals.class_types}

    vars.all_sec_roles = {roles[ctype] 
                            for roles in vars.sec_roles.values()
                            for ctype in literals.class_types}
        
    
    

async def sync_sheets(info):
    # pull
    print("Pulling data from sheets...")
    vars.df_student = get_sheet_data(info["enrolment"], "StudentList").set_index("Student ID")
    vars.df_routine = get_sheet_data(info["enrolment"], "Routine")

    # push
    print("Pushing discord data to sheets...")
    # erase exisiting data
    blank_arr = [[""]*6]*(1000)
    update_sheet_values({"C2":blank_arr}, sheet_id=info["enrolment"], sheet_name="Discord")
    arr_updated = []
    for k, mem in enumerate(vars.guild.members):
        arr_updated.append([])
        arr_updated[k] += [mem.name, str(mem.id), mem.nick, mem.roles[0].name]

        sorted_roles = [role.name for role in mem.roles[1:]]
        sorted_roles.sort()
        role_one = "" if not sorted_roles[:1] else sorted_roles[0]
        role_two = "" if not sorted_roles[1:] else ", ".join(sorted_roles[1:])
        arr_updated[k] += [role_one, role_two]
    update_sheet_values({"C2":arr_updated}, sheet_id=info["enrolment"], sheet_name="Discord")

# -------------------------------------
# Added by Abid, not tested
# -------------------------------------
def sync_usis_before(info, valid_filenames):
    # Hard coded, assumes maximum 40 students per section

    # First, clean corresponding sections
    set_value = {}
    for filename in valid_filenames:
        metadata = pd.read_excel(filename).iloc[0, 1]
        section_no = re.search(r"\nSection :  ([0-9]{2})\n", metadata).group(1)
        row_start = 40*(int(section_no) - 1) + 1

        blank_arr1 = [[""]]*(40)
        blank_arr2 = [[""]*2]*(40)

        set_value[f"A{row_start}"] = blank_arr1
        set_value[f"C{row_start}"] = blank_arr2
    update_sheet_values(set_value, sheet_id=info["enrolment"], sheet_name="USIS (before)")
    
    # Then, update section values
    set_value = {}
    for filename in valid_filenames:
        metadata = pd.read_excel(filename).iloc[0, 1]
        section_no = re.search(r"\nSection :  ([0-9]{2})\n", metadata).group(1)
        row_start = 40*(int(section_no) - 1) + 1

        student_list = pd.read_excel(filename, header=2)[["ID", "Name"]]
        n_rows_to_append = 40 - student_list.shape[0]
        blank_rows = pd.DataFrame({"ID":[""]*n_rows_to_append, "Name":[""]*n_rows_to_append})
        student_list = student_list.append(blank_rows, ignore_index=True)
        
        set_value[f"A{row_start}"] = section_no
        set_value[f"C{row_start}"] = student_list.values.tolist()

    update_sheet_values(set_value, sheet_id=info["enrolment"], sheet_name="USIS (before)")
        
