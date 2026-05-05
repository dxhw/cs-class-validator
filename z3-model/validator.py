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

from argparse import ArgumentParser


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

# reader = JSONReader()
# schedules = ScheduleFetcher()
# d_courses = schedules.get_json("doren_schedule")
# d2_courses = schedules.get_json("dior_schedule")
# t3_courses = schedules.get_json("test_schedule3")
# l_courses = schedules.get_json("last_minute_ai")
# comp_bio_courses = schedules.get_json("comp_bio1")
# old_validator = OldCS(2026, l_courses, reader, DEFAULT_OLD_CONSTRAINTS_DICT)
# old_validator.validate("AB")
# print("\n+=============================+\n")

# new_validator = NewCS(2026, d2_courses, reader, DEFAULT_NEW_CONSTRAINTS_DICT)
# new_validator.validate("AB")
# print("\n+=============================+\n")

# some_courses = schedules.get_json("working_new_scb")
# newer_validator = NewCS(2026, some_courses, reader, DEFAULT_NEW_CONSTRAINTS_DICT)
# newer_validator.validate("SCB")

def parse_args():
    parser = ArgumentParser(description="This program helps you validate a CS degree! Please put in additional parameters to customize your validation")
    parser.add_argument('--year', dest='year', help="your graduation year", default=2026, type=int)
    parser.add_argument('--degree_type', dest='degree_type', help="your degree type (AB/SCB), default is SCB", choices=["SCB", "AB"], default="SCB", type=str)
    parser.add_argument("--degree", dest="degree", help="the degree you're getting", choices=["CS", "CompBio", "CS+Econ", "MATH+CS", "APMA+CS"], default="CS")
    parser.add_argument('--requirement_version', dest="requirement_version", help="The version of requirements that you are using (Old/New)", choices=["Old", "New", "Either"], default="Old")
    parser.add_argument('--courses', dest="course_json_file", help="the JSON file with the courses you'd like to evaluate", default='dhw_old_scb', type=str)

    return parser.parse_args()

def main():
    """
    Main function to initialize and run the course plan validator.
    """
    reader = JSONReader()
    schedules = ScheduleFetcher()

    args = parse_args()
    print(args)
    
    courses = schedules.get_json(args.course_json_file)
    
    old_solver = None
    new_solver = None
    match args.degree:
        case "CS":
            if args.requirement_version == "Old" or args.requirement_version == "Either":
                old_solver = OldCS(args.year, courses, reader, DEFAULT_OLD_CONSTRAINTS_DICT)
            if args.requirement_version == "New" or args.requirement_version == "Either":
                new_solver = NewCS(args.year, courses, reader, DEFAULT_NEW_CONSTRAINTS_DICT)
        case "CompBio":
            NotImplementedError("CompBio requiremnts not implemented yet")
        case "CS+Econ":
            NotImplementedError("CS+Econ requiremnts not implemented yet")
        case "Math+CS":
            NotImplementedError("MATH+CS requiremnts not implemented yet")
        case "APMA+CS":
            NotImplementedError("APMA+CS requiremnts not implemented yet")
        case _:
            ValueError("Invalid Degree Requested")
    
    if old_solver != None:
        old_solver.validate(args.degree_type)

    if old_solver != None and new_solver != None:
        print("\n+=============================+\n")

    if new_solver != None:
        new_solver.validate(args.degree_type)


if __name__ == "__main__":
    main()
