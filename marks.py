from pygsheets_wrapper import get_sheet
import literals
import vars
import pandas as pd
from utils_wrapper import get_channel


def get_sec_marks(info, sec):
    print(f"Fetching marks from section {sec} marks sheet...", end=' ')
    meta_sheet = get_sheet(info['marks'][str(sec)], 'Meta')
    # forced refresh
    blank_cell = meta_sheet.get_named_range('BLANK')
    for _ in range(10):
        blank_cell.clear()

    sec_sheet = get_sheet(info['marks'][str(sec)],
                          literals.sec_marks_sheet_name_format.format(sec))
    # TODO: might have issues with not reaching the last column with columns with empty header

    sec_marks = sec_sheet.get_as_df(start='B1', has_header=False)
    print(f"extracting marks...", end=' ')

    sec_marks.columns = sec_marks.loc[2].copy()
    for row_name, row_no in literals.row_dict.items():
        sec_marks['Student ID'].loc[row_no] = row_name
    sec_marks.set_index('Student ID', inplace=True)
    sec_headers = sec_marks.loc[literals.row_dict.keys()]
    # get maximum entry count from sheet
    row_marks_count = int(meta_sheet.get_named_range(
        'ROW_DATA_COUNT').cells[0][0].value)
    # sec_bonus_marks = sec_marks[-2*row_marks_count-1:-row_marks_count-1]
    # sec_bonus_marks = sec_bonus_marks[sec_bonus_marks.index != '']
    sec_marks = sec_marks[-row_marks_count:]
    sec_marks = sec_marks[sec_marks.index != '']
    # map students to where their marks are stored (useful for students attending other sections)
    try:
        vars.df_marks_section.loc[sec_marks.index, 'Marks Section'] = sec
        print('Done.')
    except:
        print("Couldn't find some student ID's in Enrolment sheet.")
    sec_marks = pd.concat([sec_headers, sec_marks]).transpose()
    sec_marks['Publish?'] = sec_marks['Publish?'] == 'Publish?\n✔︎'
    return sec_marks


async def update_sec_marks(info, sec, ctx=None):
    sec_marks = get_sec_marks(info, sec)
    vars.dict_df_marks[sec] = sec_marks
    published_sec_marks = sec_marks['Total Marks'][
        sec_marks['Publish?'] & (
            pd.to_numeric(sec_marks['Depth']) <= literals.max_depth_assessment_for_autocomplete)
    ]
    published_numeric_sec_marks = pd.to_numeric(
        published_sec_marks, errors='coerce')
    published_numeric_sec_marks = published_numeric_sec_marks[
        published_numeric_sec_marks.notna()
    ]
    vars.dict_sec_marks_assessments[sec] = published_numeric_sec_marks.index.to_list(
    )
    if ctx:
        await ctx.followup.send(f"Updated section {sec} marks.", ephemeral=True)
    else:
        await get_channel("bot-config").send(f"Updated section {sec} marks.", delete_after=3.0)


def get_df_marks_by_student_id(student_id):
    try:
        marks_section = vars.df_marks_section.xs(
            student_id, level='Student ID')['Marks Section']
        marks_section = marks_section.values[0]  # int value
        marks_df = vars.dict_df_marks[marks_section][list(
            literals.row_dict) + [student_id]]
        return marks_df
    except:
        return None


def get_df_marks_by_discord_id(discord_id):
    try:
        student_id = vars.df_marks_section.xs(
            discord_id, level='Discord ID').index[0]
        return get_df_marks_by_student_id(student_id)
    except:
        return None


def get_df_marks_by_student_id_old(student_id):
    try:
        # marks_section = vars.df_student.loc[student_id]['Marks Section']
        marks_section = vars.df_marks_section.xs(
            student_id, level='Student ID')['Marks Section']
        marks_section = marks_section.values[0]  # int value
        marks_df = vars.dict_df_marks[marks_section].xs(
            student_id, level='Student ID')
        return marks_df
    except:
        return None


def get_df_marks_by_discord_id_old(discord_id):
    try:
        # marks_section = vars.df_student.loc[student_id]['Marks Section']
        marks_section = vars.df_marks_section.xs(
            discord_id, level='Discord ID')['Marks Section']
        marks_section = marks_section.values[0]  # int value
        marks_df = vars.dict_df_marks[marks_section].xs(
            discord_id, level='Discord ID')
        return marks_df
    except:
        return None


async def get_sec_marks_old(info, sec):
    print(f"Fetching marks from section {sec} marks sheet...", end=' ')
    meta_sheet = get_sheet(info['marks'][str(sec)], 'Meta')
    # forced refresh
    blank_cell = meta_sheet.get_named_range('BLANK')
    for _ in range(10):
        blank_cell.clear()

    sec_sheet = get_sheet(info['marks'][str(sec)],
                          literals.sec_marks_sheet_name_format.format(sec))
    # TODO: might have issues with not reaching the last column with columns with empty header

    sec_marks = sec_sheet.get_as_df(start='B1', has_header=False)
    print(f"extracting marks...", end=' ')
    # # subbed header row
    # sec_marks.rename(index={2: 'Subbed Header'}, inplace=True)
    sec_marks.columns = sec_marks.loc[2].copy()
    literals.row_dict = {'Header': 2, 'Helper Text': 3, 'Parent Column': 8, 'Self Column': 13,
                         'Total Marks': 4, 'Publish?': 0, 'Actual Marks?': 21}
    for row_name, row_no in literals.row_dict.items():
        sec_marks['Student ID'].loc[row_no] = row_name
    sec_marks.set_index('Student ID', inplace=True)
    sec_headers = sec_marks.loc[literals.row_dict.keys()]
    sec_marks.columns = pd.MultiIndex.from_arrays(
        sec_headers.values.tolist(), names=literals.row_dict.keys())
    # get maximum entry count from sheet
    row_marks_count = int(meta_sheet.get_named_range(
        'ROW_DATA_COUNT').cells[0][0].value)
    # sec_bonus_marks = sec_marks[-2*row_marks_count-1:-row_marks_count-1]
    # sec_bonus_marks = sec_bonus_marks[sec_bonus_marks.index != '']
    sec_marks = sec_marks[-row_marks_count:]
    sec_marks = sec_marks[sec_marks.index != '']
    # map students to where their marks are stored (useful for students attending other sections)
    try:
        vars.df_marks_section.loc[sec_marks.index, 'Marks Section'] = sec
        sec_marks.insert(
            0, 'Discord ID', vars.df_student['Discord ID'].loc[sec_marks.index])
        sec_marks.set_index([sec_marks.index, 'Discord ID'], inplace=True)
        print("Done.")
    except:
        print("Couldn't find some student ID's in Enrolment sheet.")
    # send messages to avoid bot dying
    await get_channel("bot-config").send(f"Updated section {sec} marks.", delete_after=3.0)
    return sec_marks
# use with try except block
# filter published columns
# sec_marks.xs("Publish?\n✔︎", level='Publish?', axis=1)
# filter columns with actual marks (not maximum)
# sec_marks.xs(1, level='Actual Marks?', axis=1)


async def update_sec_marks_old(info, sec):
    sec_marks = get_sec_marks(info, sec)
    vars.dict_df_marks[sec] = sec_marks
    published_sec_marks = sec_marks['Total Marks'][sec_marks['Publish?']]
    published_numeric_sec_marks = pd.to_numeric(
        published_sec_marks, errors='coerce').notna()
    published_numeric_sec_marks = published_numeric_sec_marks[published_numeric_sec_marks]
    vars.dict_sec_marks_assessments[sec] = published_numeric_sec_marks.index.to_list(
    )
    await get_channel("bot-config").send(f"Updated section {sec} marks.", delete_after=3.0)
