# things we need to consider outside of JSONS:
# intro
# math 1000s
# 1970
# 1000+s 

# manual check for new requirements SCB systems != 32

# pull in the JSONS

# get user class year

# get user data (demo with JSON)
# for multiple instances of CSCI1970, turn the first one into CSCI1970(1), the second into CSCI1970(2), and drop remaining ones
# (you can count up to two instances of 1970 towards a degree)
# then, we will need to reconvert that back at the end

# get which constraints user cares about (default all TRUE dictionary)

from util.json_reader import JSONReader
from util.schedule_fetcher import ScheduleFetcher

from old_validator import OldCS
from new_validator import NewCS


DEFAULT_OLD_CONSTRAINTS_DICT = {
    "intro": True,
    "intermediate": True,
    "pathways": True,
    "upper-level": True,
    "additional": True,
    "capstone": True,
    "humanities-limit": True
}

DEFAULT_NEW_CONSTRAINTS_DICT = {
    "intro": True,
    "foundations": True,
    "math": True,
    "elective": True,
    "technical": True,
    "capstone": True,
    "humanities-limit": True
}

reader = JSONReader()
schedules = ScheduleFetcher()
d_courses = schedules.get_json("doren_schedule")
old_validator = OldCS(2026, d_courses, reader, DEFAULT_OLD_CONSTRAINTS_DICT)
old_validator.validate("SCB")
print("\n+=============================+\n")

new_validator = NewCS(2026, d_courses, reader, DEFAULT_NEW_CONSTRAINTS_DICT)
new_validator.validate("SCB")
print("\n+=============================+\n")

some_courses = schedules.get_json("working_new_scb")
newer_validator = NewCS(2026, some_courses, reader, DEFAULT_NEW_CONSTRAINTS_DICT)
newer_validator.validate("SCB")
