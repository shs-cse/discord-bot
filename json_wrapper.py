import re
import os
import literals
import json
from pygsheets_wrapper import copy_sheet, get_sheet
from utils_wrapper import get_sheet_id_from_link, get_link_from_sheet_id


def check_and_load(file):
    # use the `json_passed` file to indicate of all the fields are okay
    # useful for first run
    if os.path.exists("./json_passed"):
        os.remove("./json_passed")

    # google sheets credentials
    assert os.path.exists(
        "./credentials.json"), "Google sheets credentials.json file was not provided in the directory."

    info = read_json(file)

    # course info check
    for field, pattern in literals.regex_course.items():
        assert re.match(
            pattern, info[field]), f"Invalid '{field}': '{info[field]}' in {file}"

    assert info['n_sections'] > 0, "Number of sections must be positive"
    if missing := info['missing_sections']:
        assert set(missing).issubset(
            range(1, info['n_sections'])), "Missing sections that don't exist"

    # enrolment sheet check
    if not info['enrolment']:
        print(
            f"Enrolment sheet ID is not specified in {file}, creating a new one...")
        sheet_id = create_from_template('enrolment', info)
        routine_sheet = get_sheet(sheet_id, "Routine")
        print(f"\033[1;31m"  # bold red
              f"Please ALLOW ACCESS at: {routine_sheet.url}"
              f"\033[0;0m"  # normal text
              )
        info['enrolment'] = sheet_id
        update_json(info, file)
        routine_sheet.spreadsheet.share('', role='reader', type='anyone')
    else:
        routine_sheet = get_sheet(info['enrolment'], "Routine")

    # marks sheets check
    # grouping
    try:
        # # ask for marks_groups if empty []
        # if not info['marks_groups']:
        #     marks_groups = input(
        #         "Enter list of lists for marks sheet group (e.g. [[1,2],[10]]): ")
        #     info['marks_groups'] = json.loads(marks_groups)
        
        # fetch marks groups by theory faculty from routine sheet
        if not info['marks_groups']:
            info['marks_groups'] = json.loads(routine_sheet.get_value("L2"))
        # assert that marks_groups is of type list[list[int]]
        assert all(isinstance(marks_group, list)
                   for marks_group in info['marks_groups'])
        for marks_group in info['marks_groups']:
            assert all(isinstance(sec, int) for sec in marks_group)
        # map each section to it's uniquely assigned group
        marks_sheets_map = {sec: None for sec in range(
            1, info['n_sections']+1) if sec not in info['missing_sections']}
        for marks_group in info['marks_groups']:
            for sec in marks_group:
                assert marks_sheets_map[sec] is None
                if sec > min(marks_group):
                    marks_sheets_map[sec] = min(marks_group)
        print("Grouping marks sheets from input...")
    except:
        info['marks_groups'] = []
        marks_sheets_map = {sec: None for sec in range(
            1, info['n_sections']+1) if sec not in info['missing_sections']}
        print("Invalid marks grouping. Proceeding without any marks grouping...")
    finally:
        update_json(info, file)

    # create section wise marks sheets
    print("Checking existence of all marks sheets...")
    marks_folder_id = None
    for sec, map_to_sec in marks_sheets_map.items():
        if str(sec) not in info['marks']:  # not listed in info
            if map_to_sec is None:  # completely new group/section spreadsheet
                # print(
                #     f"Marks section sheet for section {sec} is not specified in {file}, creating a new one...")
                if not marks_folder_id:
                    marks_folder_id = input(
                        "Enter the Google Drive folder ID where the new marks spreadsheets will be created: ")
                print(
                    f"Sec {sec} ▶️ Marks ▶️ Spreadsheet ▶️ Not in {file} ▶️ Creating a new spreadsheet...", end=' ')
                marks_folder_id = get_sheet_id_from_link(marks_folder_id)
                sheet_id = create_from_template('marks', info,
                                                [s for s, m in marks_sheets_map.items(
                                                ) if m == sec or s == sec],
                                                marks_folder_id)
            else:  # grouped with a previous section
                # print(
                #     f"Marks sheet for section {sec} is grouped with section {map_to_sec}. using that spreadsheet...")
                print(
                    f"Sec {sec} ▶️ Marks ▶️ Spreadsheet ▶️ Using Sec {map_to_sec}'s spreadsheet", end=' ')
                sheet_id = info['marks'][str(map_to_sec)]
            info['marks'][str(sec)] = sheet_id
            update_json(info, file)
        else:  # listed in info
            if map_to_sec is None:  # spreadsheet already exists and is the first section sheet there
                # print(
                #     f"Marks spreadsheet for section {sec} already exists and is the first section sheet there.")
                print(
                    f"Sec {sec} ▶️ Marks ▶️ Spreadheet ▶️ Already exists", end=' ')
            else:
                if info['marks'][str(sec)] == info['marks'][str(map_to_sec)]:
                    # print(
                    #     f"Marks spreadsheet for section {sec} already exists in the same spreadsheet as {map_to_sec}.")
                    print(
                        f"Sec {sec} ▶️ Marks ▶️ Spreadsheet ▶️ Using Sec {map_to_sec}'s spreadsheet", end=' ')
                else:
                    # print(
                    #     f"Marks spreadsheet for section {sec} already exists. Can't group with {map_to_sec}.")
                    print(
                        f"Sec {sec} ▶️ Marks ▶️ Spreadsheet ▶️ Already exists in another spreadsheet. Can't group with {map_to_sec}", end=' ')
            sheet_id = info['marks'][str(sec)]
        # create separate marks sheet for a section
        try:
            sec_sheet = get_sheet(
                sheet_id, literals.sec_marks_sheet_name_format.format(sec))
            # print(
            #     f"Marks sheet for section {sec} already exists. Not deleting. (may contain important data)")
            print(
                f"▶️ Sheet ▶️ Already exists, may contain data.")
        except:
            print(
                f"▶️ Sheet ▶️ Creating new sheet...")
            template_sec_sheet = get_sheet(
                sheet_id, literals.sec_marks_sheet_name_format.format(0))
            sec_sheet = template_sec_sheet.copy_to(sheet_id)
            sec_sheet.hidden = False
            sec_sheet.title = literals.sec_marks_sheet_name_format.format(sec)

    # guild info check
    assert info['bot_token'], f"Bot token is not specified in {file}"
    assert info['guild_id'] > 0, f"""
                Guild ID is not specified in {file}.
                Please create a server using the template {literals.template['guild']}
                Follow the naming format: <course_code> <semester> <year>. e.g: CSE251 Fall 2022
                Then, add the bot to the server, give admin permission,
                move it's role to the very top  and copy the server ID and paste it in {file}
                """

    # passed all tests
    with open("json_passed", 'w') as f:
        f.write("Passed!\n")
    # # finally print all fields
    # for field in info:
    #     print(f"{field} = {info[field]}")
    return info


def create_from_template(sheet, info, sections_list=None, folder_id=None):
    set_sheet_cells = build_edit_buffer(sheet, info)
    template_id = literals.template[sheet]
    if sections_list:
        sections_str = '-' + ', '.join(f"{sec:02d}" for sec in sections_list)
    else:
        sections_str = ''
    title = f"{info['course_code']}{sections_str} {info['semester']} {sheet.title()} Sheet"
    if not folder_id:
        folder_id = input(
            "Enter the Google Drive folder ID where the new spreadsheet will be created: ")
    folder_id = get_sheet_id_from_link(folder_id)
    return copy_sheet(template_id, title, folder_id, set_sheet_cells)


# ------------------------------------------
# WARNING: HARD CODED CELL RANGE
# ------------------------------------------
def build_edit_buffer(sheet, info):
    if sheet == 'enrolment':
        return {
            "Course Info": {
                'B2': info['course_code'],
                'B3': info['course_name'],
                'B6': info['semester'],
                'B4': info['n_sections'],
                'B5': ','.join(str(ms) for ms in info['missing_sections']),
                'B16': get_sheet_id_from_link(input("Enter the Routine sheet ID: "))
            }
        }
    elif sheet == 'marks':
        return {
            "Meta": {
                'K2': info['enrolment']
            }
        }


# read and write to json file
def read_json(file):
    with open(file) as f:
        return json.load(f)


def update_json(data, file):
    with open(file, 'w') as f:
        s = json.dumps(data, indent=4)
        # (janky) intentional spaces in json file for mental separation
        for key in ['course_code', 'enrolment', 'guild_id']:
            s = re.sub(fr'(.*,)(\n\s*"{key}".*)',  r'\1\n\n\2', s)
        f.write(s)
