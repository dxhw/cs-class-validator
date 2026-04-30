# things we need to consider outside of JSONS:
# intro
# math 1000s
# 1970
# 1000+s 

# manual check for new requirements SCB systems != 32


import json

# pull in the JSONS

# get user class year

# get user data (demo with JSON)

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

# Method 1: Create a reader instance
reader = JSONReader()
data = reader.load_all()  # Load all files at once

# Access specific data
pathways = reader.get_pathways()
capstone_courses = reader.get_capstone_courses()
print(capstone_courses)

# Method 2: Use the convenience function
all_data = load_all_data()
print(all_data)

