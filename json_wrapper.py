import re
import os
import literals
import json
from pygsheets_wrapper import copy_sheet


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

    # sheets info check
    for sheet in ['enrolment']:
        if not info[sheet]:
            print(
                f"{sheet.title()} sheet ID is not specified in {file}, creating a new one...")
            sheet_id = create_from_template(sheet, info)
            info[sheet] = sheet_id
            update_json(info, file)

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
    # finally print all fields
    # for field in info:
    #     print(f"{field} = {info[field]}")
    return info


def create_from_template(sheet, info):
    sheet_name, set_values = build_edit_buffer(sheet, info)
    template_id = literals.template[sheet]
    title = f"{info['course_code']} {info['semester']} {sheet.title()} Sheet"
    folder_id = input(
        "Enter the Google Drive folder ID where the new sheet will be created: ")
    folder_id = folder_id.split('/')[-1]
    return copy_sheet(template_id, title, folder_id, set_values, sheet_name)


# ------------------------------------------
# WARNING: HARD CODED CELL RANGE
# ------------------------------------------
def build_edit_buffer(sheet, info):
    if sheet == 'enrolment':
        sheet_name = "Course Info"
        set_values = {
            'B2': info['course_code'],
            'B3': info['course_name'],
            'B6': info['semester'],
            'B4': info['n_sections'],
            'B5': ','.join(str(ms) for ms in info['missing_sections'])
        }
    elif sheet == 'marks':
        sheet_name = "Meta"
        set_values = {
            'K2': info['enrolment']
        }
    return sheet_name, set_values


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
