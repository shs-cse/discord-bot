guild_eee_faculty = 815535685959811083

max_depth_assessment_for_autocomplete = 5

class_types = ['theory', 'lab']

sec_marks_sheet_name_format = "Sec {:02d}"

sec_category_name_format = {
    class_types[0]: "Section {:02d} Theory",
    class_types[1]: "Section {:02d} Lab"
}

sec_role_name_format = {
    class_types[0]: "sec-{:02d}",
    class_types[1]: "sec-{:02d}-lab"
}


regex_course = {
    "course_code": r"CSE[0-9]{3}",
    "course_name": r"(?!<).+",
    "semester": r"(Fall|Spring|Summer) 20[0-9]{2}"
}

regex_student = {
    "id": r"[0-9]{8}",
    "name": r"\[[0-9]{8}\].*"
}

regex_file_folder_id = r"(?<=/)[\w_-]{15,}|^[\w_-]{15,}"

# with space
regex_marks_group = r"^\[\s*(\s*(\s*\[\s*([1-9][0-9]*\s*,\s*)*[1-9][0-9]*\s*\]\s*,\s*)*\[\s*([1-9][0-9]*\s*,\s*)*[1-9][0-9]*\s*\]\s*)?\]$"
# r"^\[((\[([1-9][0-9]*,)*[1-9][0-9]*\],)*\[([1-9][0-9]*,)*[1-9][0-9]*\])?\]$" # without space


template = {
    "guild": "https://discord.new/RVh3qBrGcsxA",
    "enrolment": "1HzCwb68D3L2sC4WFEBYajz4co5sQvtgSpp2fIf8aMqc",
    "marks": "1wfamZfPPXvYxHegBEngxonPtBmJBiFT5D0WAvwLchY0"
}

row_dict = {'Helper Text': 3, 'Parent Column': 8, 'Self Column': 13, 'Depth': 22,
            'Total Marks': 4, 'Publish?': 0, 'Actual Marks?': 21}
