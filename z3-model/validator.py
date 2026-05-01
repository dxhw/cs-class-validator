# things we need to consider outside of JSONS:
# intro
# math 1000s
# 1970
# 1000+s 

# manual check for new requirements SCB systems != 32

# pull in the JSONS

# get user class year

# get user data (demo with JSON)
# for multiple instances of CSCI1970, turn the first one into CSCI1970A, the second into CSCI1970B, and drop remaining ones
# (you can count up to two instances of 1970 towards a degree)
# then, we will need to reconvert that back at the end

# get which constraints user cares about (default all TRUE dictionary)

# Constraints:
#   OLD:
#       SCB:
            # intro sequence (2 courses)
            # intermediate (5 courses) - 1 from each category
            # 2 pathways
            # additional 1000+ (not in pathways)
            # three additional courses
            # humanities requirement (4)
            # 1970 repetition requirement
            # capstone (in pathway)
        # AB:
            # intro sequence (2 courses)
            # intermediate (3 courses) - 2 categories+
            # 1 pathways
            # additional 1000+ (not in pathway)
            # one additional course
            # humanities requirement (2)
            # 1970 repetition requirement

from util.json_reader import JSONReader, load_all_data
from big_matrix_old_validator import OldCS

# Method 1: Create a reader instance
reader = JSONReader()
courses = ...
old_validator = OldCS(2026, courses, reader)
old_validator.validate("SCB")


