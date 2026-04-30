from z3 import *

# things we need to consider outside of JSONS:
# intro
# math 1000s
# 1970
# 1000+s 

# New:
#     SCB:
#         intro sequence (2 courses): intro
#         math foundations (22): math
#         3 foundations (AI, systems, theory): foundations
#         5 1000+ levels - not artsy, not 1970: upperDiv
#         4 electives - basically anything (2 1970, linear, swe, 3 non-department): electives
#         capstone: capstone
    # AB: 
#         intro sequence (2 courses)
#         math foundations (22)
#         3 foundations (AI, systems, theory)
#         2 1000+ levels - not artsy, not 1970
#         2 electives - basically anything (2 1970, linear, swe, 3 non-department)
#         capstone

class NewCS(object):
    def validate_new_scb():
        print("new scb")
        
        self.s.push()

        for constraint in constraint_dict:
            if constaint:
                self.s.add(get_contraint_func(constraint)(courses))


        # {CONSTRAINTS HERE}


        is_sat = self.s.check() == sat
        self.s.pop()
        return is_sat
        




    def validate_new_ab():
        print("new ab")
        self.s.push()


        # {CONSTRAINTS HERE}


        is_sat = self.s.check() == sat
        self.s.pop()
        return is_sat

    def  __init__(self, year: int, courses: list[str]):
        # pull in the degree JSONS

        self.s = Solver()









