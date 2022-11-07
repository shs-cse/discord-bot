guild_eee_faculty = 815535685959811083

class_types = ['theory', 'lab']

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

template = {
    "guild": "https://discord.new/RVh3qBrGcsxA",
    "enrolment": "15SMhTv5SnjXn3UjE5BlH8e6wOVD5ThpEC6PWO_3jWvY",
    "marks": "1VnFyMzAkPQGRhzHy77mEEHCdp3z8P_XI85-Bhjta8cM"
}