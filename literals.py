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

info_row_dict = {'Helper Text': 4, 'Parent Column': 9, 'Self Column': 14, 'Depth': 23,
                 'Total Marks': 5, 'Publish?': 1, 'Actual Marks?': 22, 'Children Columns': 17}

messages = {
    'general_rules':
        ":star2: **__General Rules__**:star2:"
        ":small_blue_diamond: Be respectful towards the faculties and your classmates. Note that you can be friendly while being respectful. "
        "\n\n"
        ":small_blue_diamond: **Any sort of bullying and sexual harassment will be severely punished ** "
        "\n\n"
        ":small_blue_diamond: As per the new policy from the registrar, we will be conducting regular online live classes as per USIS schedule. Attendance in the live classes **are mandatory**. In addition, the faculties will be providing online consultation hours, and you are highly encouraged to join these sessions to clear out any confusion you might have. "
        "\n\n"
        ":small_blue_diamond: The buX videos are made to be as easy-to-understand as possible. Additionally, we will upload some reading materials, solved problems, recorded version of regular live classes, etc., for further clarification. If you still have any questions or if you feel like you didn't understand a particular topic, feel free to post here in the #queries channel. We will reply to your queries during our consultation hours."
        "\n\n"
        ":small_blue_diamond:We always try to be supportive and friendly. Given the pandemic situation, we also try to be considerate  while setting the questions and lenient while grading. I, personally, always reward hard-work and honesty over \"talent\". If you stay honest and put the **minimum** effort, you will pass this course with flying colors. However, there is one thing we won't tolerate - cheating. Don't join any cheating groups (messenger or Discord) and don't take help from your friends during any **individual** assessment."
        "\n\n"
        "**Any form of cheating/copying will be severely punished**"
        "\n\n"
        "Leave any type of cheating group you have joined. \"I wasn't active\", \"My notifications were turned off\" - these types of excuses won't be accepted.",

    'faculty_assign':
        "@faculty Your nickname and section access should be assigned on joining this server (pulled from `Electrical Courses Team` server). ***If not set automatically:***"
        "\n"
        ":one: __Set your nicknames __in this server to this format: `[ABC] Full Name`. Here `ABC` is your 3-letter initial mentioned in your class routine spreadsheet."
        "\n"
        ":two: Press this button below",

    'student_verify':
        ":star2: **__Verification Process:__**:star2:"
        "\n"
        "Click the button below and submit your 8-digit **Student ID**",

    'welcome_faculty':
        "Welcome! You have been given the faculty role to the {course_code} {semester} Discord server! "
        "\n"
        "Please change your **__nickname__** for the server to `[Initial] Full Name` format, e.g., `[SHS] Shadman Shahriar`",

    'welcome_student':
        "Welcome to the {course_code} {semester} Discord server! "
        "\n"
        "Please verify yourself by visiting {welcome_mention} and read the rules in {rules_mention}. "
        "\n"
        "Otherwise, you will not be able to access the server."
}
