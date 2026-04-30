from typing import Callable

from z3 import *

# Constraints
    # intro sequence (2 courses)
    # intermediate (5 courses) - 1 from each category
    # 2 pathways
    # additional 1000+ (not in pathways)
    # three additional courses
    # humanities requirement (4)
    # 1970 repetition requirement
    # capstone (in pathway)


DEFAULT_DICT = {
    "intro": True,
    "intermediate": True,
    "pathways": True,
    "upper-level": True,
    "additional": True,
    "humanities-limit": True,
    "1970-repetition": True,
    "capstone": True 
}
class OldCS():
    def  __init__(self, year: int, courses: list[str], constraint_dict: dict[str, bool] = DEFAULT_DICT):
        # pull in the degree JSONS

        self.s = Solver()
        self.constraint_dict = constraint_dict
        self.year = year
        self.courses = courses

    def validate(self, degree_type: str):
        print("old " + degree_type)
        
        self.s.push()

        for constraint in self.constraint_dict:
            if constraint:
                self.s.add(self.constraint_func_mapper(constraint)(self.courses, degree_type))

        is_sat = self.s.check() == sat
        self.s.pop()
        return is_sat
    
    def constraint_func_mapper(self, constraint: str) -> Callable[[list[str], str], BoolRef]:
        match (constraint):
            case "intro":
                return self.oldIntroConstraint
            case "intermediate": raise(RuntimeError("invalid constraint name"))
            case _: 
                raise(RuntimeError("invalid constraint name"))
            
    def oldIntroConstraint(self, courses: list[str], degree_type: str) -> BoolRef:
        ...

        # in courses, we have either (or both) 19 or 200
        # If 19, we have something else of any kind



