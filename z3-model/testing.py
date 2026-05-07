import unittest

from util.json_reader import JSONReader
from util.schedule_fetcher import ScheduleFetcher

from old_validator import OldCS
from new_validator import NewCS

from cs_econ_new_validator import NewCSEcon
from apma_cs_new_validator import NewAPMACS
from math_cs_new_validator import NewMATHCS
from comp_bio_new_validator import NewCompBio

from z3 import *

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
    "apma-upper-div": True,
    "math-apma-upper-div": True,
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

DEFAULT_NEW_COMP_BIO_CONSTRAINTS_DICT = {
    "intro": True,
    "prob-and-stats": True,
    "discrete": True,
    "bio-core": True,
    "chem-core": True,
    "comp-bio-core": True,
    "track": True,
    "elective": True,
    "capstone": True,
}

def test_basic_degrees_validate_cleanly():
    reader = JSONReader()
    schedules = ScheduleFetcher()

    o_scb_courses = schedules.get_json("working_old_scb")
    validator = OldCS(2026, o_scb_courses, reader, DEFAULT_OLD_CONSTRAINTS_DICT, False)
    output = validator.validate("SCB", limit_of_unknowns=0)
    assert output[0] == True
    assert output[1] == 0

    o_ab_courses = schedules.get_json("working_old_ab")
    validator = OldCS(2026, o_ab_courses, reader, DEFAULT_OLD_CONSTRAINTS_DICT, False)
    output = validator.validate("AB", limit_of_unknowns=0)
    assert output[0] == True
    assert output[1] == 0

    n_scb_courses = schedules.get_json("working_new_scb")
    validator = NewCS(2026, n_scb_courses, reader, DEFAULT_NEW_CONSTRAINTS_DICT, False)
    output = validator.validate("SCB", limit_of_unknowns=0)
    assert output[0] == True
    assert output[1] == 0

    n_ab_courses = schedules.get_json("working_new_ab")
    validator = NewCS(2026, n_ab_courses, reader, DEFAULT_NEW_CONSTRAINTS_DICT, False)
    output = validator.validate("AB", limit_of_unknowns=0)
    assert output[0] == True
    assert output[1] == 0

    mathcs_scb_courses = schedules.get_json("working_math_cs_scb")
    validator = NewMATHCS(2026, mathcs_scb_courses, reader, DEFAULT_NEW_MATH_CS_CONSTRAINTS_DICT, False)
    output = validator.validate("SCB", limit_of_unknowns=0)
    assert output[0] == True
    assert output[1] == 0

    csecon_scb_courses = schedules.get_json("working_cs_econ_scb")
    validator = NewCSEcon(2026, csecon_scb_courses, reader, DEFAULT_NEW_CS_ECON_CONSTRAINTS_DICT, False)
    output = validator.validate("SCB", limit_of_unknowns=0)
    assert output[0] == True
    assert output[1] == 0

    csecon_ab_courses = schedules.get_json("working_cs_econ_ab")
    validator = NewCSEcon(2026, csecon_ab_courses, reader, DEFAULT_NEW_CS_ECON_CONSTRAINTS_DICT, False)
    output = validator.validate("AB", limit_of_unknowns=0)
    assert output[0] == True
    assert output[1] == 0

    csecon_ab_courses = schedules.get_json("working_cs_econ_ab")
    validator = NewCSEcon(2026, csecon_ab_courses, reader, DEFAULT_NEW_CS_ECON_CONSTRAINTS_DICT, False)
    output = validator.validate("AB", limit_of_unknowns=0)
    assert output[0] == True
    assert output[1] == 0

    compbio_scb_courses = schedules.get_json("working_comp_bio_scb")
    validator = NewCompBio(2026, compbio_scb_courses, reader, DEFAULT_NEW_COMP_BIO_CONSTRAINTS_DICT, False)
    output = validator.validate("SCB", limit_of_unknowns=0)
    assert output[0] == True
    assert output[1] == 0

    compbio_ab_courses = schedules.get_json("working_comp_bio_ab")
    validator = NewCompBio(2026, compbio_ab_courses, reader, DEFAULT_NEW_COMP_BIO_CONSTRAINTS_DICT, False)
    output = validator.validate("AB", limit_of_unknowns=0)
    assert output[0] == True
    assert output[1] == 0

    apma_cs_courses = schedules.get_json("working_apma_cs_scb")
    validator = NewAPMACS(2026, apma_cs_courses, reader, DEFAULT_NEW_APMA_CS_CONSTRAINTS_DICT, False)
    output = validator.validate("SCB", limit_of_unknowns=0)
    assert output[0] == True
    assert output[1] == 0


def test_real_degrees_can_validate():
    reader = JSONReader()
    schedules = ScheduleFetcher()

    cdf_cb = schedules.get_json("cdf_old_comp_bio")
    validator = NewCompBio(2026, cdf_cb, reader, DEFAULT_NEW_COMP_BIO_CONSTRAINTS_DICT, False)
    output = validator.validate("SCB", limit_of_unknowns=5)
    assert output[0] == True
    assert output[1] == 1

    cdf_cb = schedules.get_json("cdf_old_comp_bio")
    validator = NewCompBio(2026, cdf_cb, reader, DEFAULT_NEW_COMP_BIO_CONSTRAINTS_DICT, False)
    output = validator.validate("AB", limit_of_unknowns=5)
    assert output[0] == True
    assert output[1] == 0

    cr_old_ab = schedules.get_json("cr_old_ab")
    validator = OldCS(2026, cr_old_ab, reader, DEFAULT_OLD_CONSTRAINTS_DICT, False)
    output = validator.validate("AB", limit_of_unknowns=5)
    assert output[0] == True
    assert output[1] == 0

    dhw_old_scb = schedules.get_json("dhw_old_scb")
    validator = OldCS(2026, dhw_old_scb, reader, DEFAULT_OLD_CONSTRAINTS_DICT, False)
    output = validator.validate("SCB", limit_of_unknowns=5)
    assert output[0] == True
    assert output[1] == 0

    dior_sched = schedules.get_json("dior_schedule")
    validator = OldCS(2026, dior_sched, reader, DEFAULT_OLD_CONSTRAINTS_DICT, False)
    output = validator.validate("AB", limit_of_unknowns=5)
    assert output[0] == True
    assert output[1] == 0

    dior_sched = schedules.get_json("dior_schedule")
    validator = NewCS(2026, dior_sched, reader, DEFAULT_NEW_CONSTRAINTS_DICT, False)
    output = validator.validate("AB", limit_of_unknowns=5)
    assert output[0] == True
    assert output[1] == 2

    dw_old_ab = schedules.get_json("dw_old_ab")
    validator = OldCS(2026, dw_old_ab, reader, DEFAULT_OLD_CONSTRAINTS_DICT, False)
    output = validator.validate("AB", limit_of_unknowns=5)
    assert output[0] == True
    assert output[1] == 0

    kl_old_scb = schedules.get_json("kl_old_scb")
    validator = OldCS(2027, kl_old_scb, reader, DEFAULT_OLD_CONSTRAINTS_DICT, False)
    output = validator.validate("SCB", limit_of_unknowns=5)
    assert output[0] == True
    assert output[1] == 1


def test_incomplete_produces_correct_unknown():
    reader = JSONReader()
    schedules = ScheduleFetcher()

    inc_old_scb = schedules.get_json("inc_old_scb")
    validator = OldCS(2026, inc_old_scb, reader, DEFAULT_OLD_CONSTRAINTS_DICT, False)
    output = validator.validate("SCB", limit_of_unknowns=5)
    assert output[0] == True
    assert output[1] == 2

    inc_old_ab = schedules.get_json("inc_old_ab")
    validator = OldCS(2026, inc_old_ab, reader, DEFAULT_OLD_CONSTRAINTS_DICT, False)
    output = validator.validate("AB", limit_of_unknowns=5)
    assert output[0] == True
    assert output[1] == 2

    inc_new_scb = schedules.get_json("inc_new_scb")
    validator = NewCS(2026, inc_new_scb, reader, DEFAULT_NEW_CONSTRAINTS_DICT, False)
    output = validator.validate("SCB", limit_of_unknowns=5)
    assert output[0] == True
    assert output[1] == 2

    inc_new_ab = schedules.get_json("inc_new_ab")
    validator = NewCS(2026, inc_new_ab, reader, DEFAULT_NEW_CONSTRAINTS_DICT, False)
    output = validator.validate("AB", limit_of_unknowns=5)
    assert output[0] == True
    assert output[1] == 3

    inc_math_cs_scb = schedules.get_json("inc_math_cs_scb")
    validator = NewMATHCS(2026, inc_math_cs_scb, reader, DEFAULT_NEW_MATH_CS_CONSTRAINTS_DICT, False)
    output = validator.validate("SCB", limit_of_unknowns=5)
    assert output[0] == True
    assert output[1] == 2

    
    inc_cs_econ_scb = schedules.get_json("inc_cs_econ_scb")
    validator = NewCSEcon(2026, inc_cs_econ_scb, reader, DEFAULT_NEW_CS_ECON_CONSTRAINTS_DICT, False)
    output = validator.validate("SCB", limit_of_unknowns=5)
    assert output[0] == True
    assert output[1] == 2

    inc_cs_econ_ab = schedules.get_json("inc_cs_econ_ab")
    validator = NewCSEcon(2026, inc_cs_econ_ab, reader, DEFAULT_NEW_CS_ECON_CONSTRAINTS_DICT, False)
    output = validator.validate("AB", limit_of_unknowns=5)
    assert output[0] == True
    assert output[1] == 2

    inc_comp_bio_scb = schedules.get_json("inc_comp_bio_scb")
    validator = NewCompBio(2026, inc_comp_bio_scb, reader, DEFAULT_NEW_COMP_BIO_CONSTRAINTS_DICT, False)
    output = validator.validate("SCB", limit_of_unknowns=5)
    assert output[0] == True
    assert output[1] == 2

    inc_comp_bio_ab = schedules.get_json("inc_comp_bio_ab")
    validator = NewCompBio(2026, inc_comp_bio_ab, reader, DEFAULT_NEW_COMP_BIO_CONSTRAINTS_DICT, False)
    output = validator.validate("AB", limit_of_unknowns=5)
    assert output[0] == True
    assert output[1] == 2

    inc_apma_cs_scb = schedules.get_json("inc_apma_cs_scb")
    validator = NewAPMACS(2026, inc_apma_cs_scb, reader, DEFAULT_NEW_APMA_CS_CONSTRAINTS_DICT, False)
    output = validator.validate("SCB", limit_of_unknowns=5)
    assert output[0] == True
    assert output[1] == 2




def test_not_enough_unknown_causes_fails():
    reader = JSONReader()
    schedules = ScheduleFetcher()

    inc_old_scb = schedules.get_json("inc_old_scb")
    validator = OldCS(2026, inc_old_scb, reader, DEFAULT_OLD_CONSTRAINTS_DICT, False)
    output = validator.validate("SCB", limit_of_unknowns=1)
    assert output[0] == False
    assert output[1] == 1

    inc_old_ab = schedules.get_json("inc_old_ab")
    validator = OldCS(2026, inc_old_ab, reader, DEFAULT_OLD_CONSTRAINTS_DICT, False)
    output = validator.validate("AB", limit_of_unknowns=1)
    assert output[0] == False
    assert output[1] == 1

    inc_new_scb = schedules.get_json("inc_new_scb")
    validator = NewCS(2026, inc_new_scb, reader, DEFAULT_NEW_CONSTRAINTS_DICT, False)
    output = validator.validate("SCB", limit_of_unknowns=1)
    assert output[0] == False
    assert output[1] == 1

    inc_new_ab = schedules.get_json("inc_new_ab")
    validator = NewCS(2026, inc_new_ab, reader, DEFAULT_NEW_CONSTRAINTS_DICT, False)
    output = validator.validate("AB", limit_of_unknowns=1)
    assert output[0] == False
    assert output[1] == 1

    inc_math_cs_scb = schedules.get_json("inc_math_cs_scb")
    validator = NewMATHCS(2026, inc_math_cs_scb, reader, DEFAULT_NEW_MATH_CS_CONSTRAINTS_DICT, False)
    output = validator.validate("SCB", limit_of_unknowns=1)
    assert output[0] == False
    assert output[1] == 1

    
    inc_cs_econ_scb = schedules.get_json("inc_cs_econ_scb")
    validator = NewCSEcon(2026, inc_cs_econ_scb, reader, DEFAULT_NEW_CS_ECON_CONSTRAINTS_DICT, False)
    output = validator.validate("SCB", limit_of_unknowns=1)
    assert output[0] == False
    assert output[1] == 1

    inc_cs_econ_ab = schedules.get_json("inc_cs_econ_ab")
    validator = NewCSEcon(2026, inc_cs_econ_ab, reader, DEFAULT_NEW_CS_ECON_CONSTRAINTS_DICT, False)
    output = validator.validate("AB", limit_of_unknowns=1)
    assert output[0] == False
    assert output[1] == 1

    inc_comp_bio_scb = schedules.get_json("inc_comp_bio_scb")
    validator = NewCompBio(2026, inc_comp_bio_scb, reader, DEFAULT_NEW_COMP_BIO_CONSTRAINTS_DICT, False)
    output = validator.validate("SCB", limit_of_unknowns=1)
    assert output[0] == False
    assert output[1] == 1

    inc_comp_bio_ab = schedules.get_json("inc_comp_bio_ab")
    validator = NewCompBio(2026, inc_comp_bio_ab, reader, DEFAULT_NEW_COMP_BIO_CONSTRAINTS_DICT, False)
    output = validator.validate("AB", limit_of_unknowns=1)
    assert output[0] == False
    assert output[1] == 1

    inc_apma_cs_scb = schedules.get_json("inc_apma_cs_scb")
    validator = NewAPMACS(2026, inc_apma_cs_scb, reader, DEFAULT_NEW_APMA_CS_CONSTRAINTS_DICT, False)
    output = validator.validate("SCB", limit_of_unknowns=1)
    assert output[0] == False
    assert output[1] == 1

def test_verify_minimum_courses_in_degree():
    reader = JSONReader()
    schedules = ScheduleFetcher()

    # validator = OldCS(2026, ["CSCI 0190"], reader, DEFAULT_OLD_CONSTRAINTS_DICT, False)
    # output = validator.validate("SCB", limit_of_unknowns=20)
    # assert output[0] == True
    # assert output[1] == ?

    validator = OldCS(2026, ["CSCI 0190"], reader, DEFAULT_OLD_CONSTRAINTS_DICT, False)
    output = validator.validate("AB", limit_of_unknowns=20)
    assert output[0] == True
    assert output[1] == 8 #AB should require 9 courses as per dept.

    # validator = NewCS(2026, ["CSCI 0190"], reader, DEFAULT_NEW_CONSTRAINTS_DICT, False)
    # output = validator.validate("AB", limit_of_unknowns=20)
    # assert output[0] == True
    # assert output[1] == ?

    # validator = NewCS(2026, ["CSCI 0190"], reader, DEFAULT_NEW_CONSTRAINTS_DICT, False)
    # output = validator.validate("SCB", limit_of_unknowns=20)
    # assert output[0] == True
    # assert output[1] == ?

    validator = NewMATHCS(2026, ["CSCI 0190"], reader, DEFAULT_NEW_MATH_CS_CONSTRAINTS_DICT, False)
    output = validator.validate("SCB", limit_of_unknowns=20)
    assert output[0] == True
    assert output[1] == 16 #We should expect 17 w/ cs19 + 2 sems of calc = 19 on bulletin

    # validator = NewCSEcon(2026, ["CSCI 0190"], reader, DEFAULT_NEW_CS_ECON_CONSTRAINTS_DICT, False)
    # output = validator.validate("SCB", limit_of_unknowns=20)
    # assert output[0] == True
    # assert output[1] == 12 #We should expect 17 w/ cs19 + 2 sems of calc = 19 on bulletin

    validator = NewCSEcon(2026, ["CSCI 0190"], reader, DEFAULT_NEW_CS_ECON_CONSTRAINTS_DICT, False)
    output = validator.validate("AB", limit_of_unknowns=20)
    assert output[0] == True
    assert output[1] == 12 #Bulletin claims 13

    # validator = NewCompBio(2026, ["CSCI 0190"], reader, DEFAULT_NEW_COMP_BIO_CONSTRAINTS_DICT, False)
    # output = validator.validate("SCB", limit_of_unknowns=20)
    # assert output[0] == True
    # assert output[1] == 15 #Bulletin claims 16

    # validator = NewCompBio(2026, ["CSCI 0190"], reader, DEFAULT_NEW_COMP_BIO_CONSTRAINTS_DICT, False)
    # output = validator.validate("AB", limit_of_unknowns=20)
    # assert output[0] == True
    # assert output[1] == 10 #Bulletin claims 11

    validator = NewAPMACS(2026, ["CSCI 0190"], reader, DEFAULT_NEW_APMA_CS_CONSTRAINTS_DICT, False)
    output = validator.validate("SCB", limit_of_unknowns=20)
    assert output[0] == True
    assert output[1] == 16 #Bulletin claims 17
    





def test_comp_bio_advisor_approvals_fail():
    reader = JSONReader()
    schedules = ScheduleFetcher()

    cdf_cb = schedules.get_json("cdf_old_comp_bio")
    validator = NewCompBio(2026, cdf_cb, reader, DEFAULT_NEW_COMP_BIO_CONSTRAINTS_DICT, False)
    output = validator.validate("SCB", limit_of_unknowns=5)
    assert output[0] == True
    assert output[1] != 0

    mt_comp_bio = schedules.get_json("mt_comp_bio")
    validator = NewCompBio(2027, mt_comp_bio, reader, DEFAULT_NEW_COMP_BIO_CONSTRAINTS_DICT, False)
    output = validator.validate("SCB", limit_of_unknowns=5)
    assert output[0] == True
    assert output[1] != 0

def main():
    print("testing basic degrees")
    test_basic_degrees_validate_cleanly()
    print("testing real degrees")
    test_real_degrees_can_validate()
    print("testing incomplete degrees - correct number of unknowns")
    test_incomplete_produces_correct_unknown()
    print("testing comp bio advisor approval fails")
    test_comp_bio_advisor_approvals_fail()
    print("all tests pass!")

if __name__ == "__main__":
    main()
