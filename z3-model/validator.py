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

from cs_econ_new_validator import NewCSEcon
from apma_cs_new_validator import NewAPMACS
from math_cs_new_validator import NewMATHCS



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

DEFAULT_NEW_CS_ECON_CONSTRAINTS_DICT = {
    "intro": True,
    "foundations": True,
    "prob-and-stats": True,
    "micro-macro-metrics": True,
    "technical": True,
    "math-econ": True,
    "econ-elective": True,
    "capstone": True,
}

DEFAULT_NEW_APMA_CS_CONSTRAINTS_DICT = {
    "intro": True,
    "foundations": True,
    "multi": True,
    "linear": True,
    "technical": True,
    "optimization": True,
    "differential": True,
    "restricted-upper-div": True,
    "unrestricted-upper-div": True,
    "capstone": True,
}

DEFAULT_NEW_MATH_CS_CONSTRAINTS_DICT = {
    "intro": True,
    "foundations": True,
    "multi": True,
    "linear": True,
    "technical": True,
    "abstract": True,
    "upper-math": True,
    "elective": True,
    "capstone": True,
}



            #             case "intro":
            #     return self.__newIntroConstraint
            # case "foundations":
            #     return self.__newFoundationsConstraint
            # case "multi":
            #     return self.__newMultiConstraint
            # case "linear":
            #     return self.__newLinearConstraint
            # case "technical":
            #     return self.__newTechnicalConstraint
            # case "abstract":
            #     return self.__newAbstractConstraint
            # case "upper-math":
            #     return self.__newUpperMathConstraint
            # case "elective":
            #     return self.__newElectiveConstraint
            # case "capstone":
            #     return self.__newCapstoneConstraint

reader = JSONReader()
schedules = ScheduleFetcher()
d_courses = schedules.get_json("doren_schedule")
t3_courses = schedules.get_json("test_schedule3")
# old_validator = OldCS(2026, d_courses, reader, DEFAULT_OLD_CONSTRAINTS_DICT)
# old_validator.validate("SCB")
# print("\n+=============================+\n")

# old_validator = OldCS(2026, t3_courses, reader, DEFAULT_OLD_CONSTRAINTS_DICT)
# old_validator.validate("SCB")
# print("\n+=============================+\n")

# t3_courses = schedules.get_json("test_schedule3")

# new_validator = NewCS(2028, t3_courses, reader, DEFAULT_NEW_CONSTRAINTS_DICT)
# new_validator.validate("SCB")
# print("\n+=============================+\n")

# econ_courses = schedules.get_json("working_cs_econ_scb")

# new_cs_econ_validator = NewCSEcon(2028, econ_courses, reader, DEFAULT_NEW_CS_ECON_CONSTRAINTS_DICT)
# new_cs_econ_validator.validate("SCB")
# print("\n+=============================+\n")

# apma_courses = schedules.get_json("working_apma_cs_scb")

# new_apma_cs_validator = NewAPMACS(2028, apma_courses, reader, DEFAULT_NEW_APMA_CS_CONSTRAINTS_DICT)
# new_apma_cs_validator.validate("SCB")
# print("\n+=============================+\n")

math_courses = schedules.get_json("working_math_cs_scb")

new_math_cs_validator = NewMATHCS(2028, math_courses, reader, DEFAULT_NEW_MATH_CS_CONSTRAINTS_DICT)
new_math_cs_validator.validate("SCB")
print("\n+=============================+\n")

# some_courses = schedules.get_json("working_new_scb")
# newer_validator = NewCS(2026, some_courses, reader, DEFAULT_NEW_CONSTRAINTS_DICT)
# newer_validator.validate("SCB")
