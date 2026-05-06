def get_course_number(course_code: str) -> int:
    try:
        # Filter out the letters and grab the numbers
        course_num = int(''.join(filter(str.isdigit, course_code)))
    except ValueError:
        course_num = 0
    return course_num