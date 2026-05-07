from typing import Callable
from util.json_reader import JSONReader
from util.util import get_course_number

from z3 import *

#SCB
# -prob and stats 
# -cs intro 
# -2 of (500, 410, 300/320/330) 
# -3 1000 CSCI technical w at most 1 1970 and foundations 
# -econ 1130 (micro) 
# -econ 1210 (macro) 
# -econ 1630 (metrics) 
# -3 math econ or 2000+ 
# -2 1000+ econ not 1620, 1960, 1970 
# -capstone 

#AB
# -prob and stats 
# -cs intro 
# -2 of (500, 410, 300/320/330) 
# -2 1000 CSCI technical w at most 1 1970 and foundations 
# -econ 1130 
# -econ 1210 
# -econ 1630 
# -3 math econ or 2000+ 



class NewCSEcon():
    def  __init__(self, year: int, courses: list[str], reader: JSONReader, constraint_dict: dict[str, bool]):
        #set up our class
        self.s = Solver()
        self.constraint_dict = constraint_dict
        self.year = year 
        self.courses = courses
        self.reader = reader


    def validate_sat(self, degree_type: str, unknowns: int = 0, limit_of_unknowns: int = 5) -> CheckSatResult:
        if self.validate(degree_type, unknowns, limit_of_unknowns)[0]:
            return sat
        else:
            return unsat
    
    def validate_unknowns(self, degree_type: str, unknowns: int = 0, limit_of_unknowns: int = 5) -> int:
        return self.validate(degree_type, unknowns, limit_of_unknowns)[1]


    def validate(self, degree_type: str, unknowns: int = 0, limit_of_unknowns: int = 5) -> tuple[bool, int]:
        #Only degree types are AB/SCB
        assert degree_type == "SCB" or degree_type == "AB"

        print("Looking for CS+Econ " + degree_type + " requirements")

        self.s.push()


        # Create the boolean matrix
        # for each course, there is a set of reqs it may or may not fulfill, so make a table of them
        # assignment_vars[course][req] = Z3 Bool
        self.assignment_vars = {}
        active_reqs = [req for req, is_active in self.constraint_dict.items() if is_active]

        # set up an empty mapping of Z3 bools for each course
        for course in self.courses:
            self.assignment_vars[course] = {}
            for req in active_reqs:
                # Create a uniquely named Z3 boolean for every course-req pair
                self.assignment_vars[course][req] = Bool(f"use_{course}_for_{req}")

        # apply all of the requirement constraints
        for req in active_reqs:
            constraint_func = self.__constraint_func_mapper(req)
            self.s.add(constraint_func(degree_type))

        # no double dipping (except capstone)
        self.__doubleDippingConstraint()

        is_sat = (self.s.check() == sat, unknowns)
        
        # Print the actual course assignments if satisfied
        if is_sat[0]:
            if unknowns == 0:
                self.__print_results()
            #are there unknowns involved? also print alternatives. 
            else:
                print(f"Found a valid course plan with {unknowns} unknown courses")
                self.__generate_unknown_alternatives()

            self.s.pop()
        else:
            print(f"cannot form a valid {degree_type} degree")
            self.s.pop()
            is_sat = self.__try_with_unknowns(degree_type, unknowns, limit_of_unknowns)

        return is_sat
    
        # this function assumes the constraints are SAT!
    def __print_results(self):

        # print("IM BROKEN FIX ME")
        # return

        active_reqs = [req for req, is_active in self.constraint_dict.items() if is_active]
        m = self.s.model()
        print("\n--- Valid Course Assignment ---")
        all_used_courses = []
        
        for req in active_reqs:
            if req == "humanities-limit":
                continue
            
            # Gather all courses used for this bucket
            used_courses = [c for c in self.courses if is_true(m.evaluate(self.assignment_vars[c][req]))]
            all_used_courses.extend(used_courses)

            #just print everything as a standard list
            print(f"{req}: {used_courses}")

        # --- Humanities Printing ---
        humanities_list = self.reader.get_humanities_courses()
        humanities_included_in_degree = [course for course in all_used_courses if course in humanities_list]
        
        # Use a set to remove duplicates (in case a humanity was used in multiple buckets)
        unique_humanities = list(set(humanities_included_in_degree))
        print(f"humanities courses used in degree: {unique_humanities}")
    
    ################################### UNKNOWN HANDLING #######################################
    
    def __try_with_unknowns(self, degree_type: str, num_unknowns: int, limit_of_unknowns: int = 6):
        if num_unknowns > limit_of_unknowns - 1:
            print("Too many unknowns to build a degree!")
            return (False, num_unknowns)
        
        count = num_unknowns + 1
        self.courses.append(f"Unknown {count}")
        print(f"trying with {count} inserted unknown class(es)")
        is_sat = self.validate(degree_type, num_unknowns + 1, limit_of_unknowns)

        return is_sat
        

    def __generate_unknown_alternatives(self, limit: int = 5):
        print("\nSearching for Unknown course placements...")
        
        # Get active requirements
        active_reqs = [req for req, is_active in self.constraint_dict.items() if is_active]

        # Get a static list of the unknown courses
        unknown_courses = [c for c in self.courses if c.startswith("Unknown")]

        count = 0
        while self.s.check() == sat and count < limit:
            m = self.s.model()
            count += 1
            print(f"\n--- Alternative {count} ---")
            
            unknowns_used = False
            
            # This list will hold equations defining the CURRENT distribution of Unknowns.
            # e.g., [Sum(Unknowns in intro) == 1, Sum(Unknowns in pathways) == 1, ...]
            current_distribution_equations = []

            # 1. Check the main requirement buckets
            for req in active_reqs:
                
                # Gather the booleans for ALL unknowns in THIS specific requirement
                unknowns_in_this_req = [If(self.assignment_vars[c][req], 1, 0) for c in unknown_courses]
                
                # Create a Z3 expression for the sum
                sum_expr = Sum(*([0] + unknowns_in_this_req))
                
                # Evaluate the actual integer sum in the current model
                actual_count = m.evaluate(sum_expr)
                
                # We enforce the exact count for THIS bucket to our signature
                current_distribution_equations.append(sum_expr == actual_count)

                # For printing purposes, we only care if the count is > 0
                if actual_count.as_long() > 0:
                    unknowns_used = True
                    print(f"- {actual_count} Unknown(s) filling requirement: {req}")

            self.__print_results()

            # 2. Block this specific numerical distribution and loop again
            if unknowns_used:
                # Tell Z3: "You cannot use this EXACT distribution of Unknowns again."
                self.s.add(Not(And(*current_distribution_equations)))
            else:
                print("- No Unknowns were needed to graduate! The real transcript is sufficient.")
                break # Stop searching if they can graduate without help
                
        if self.s.check() != sat:
            print("out of possible placements")
        else:
            print(f"hit unknown placement limit")
        print(f"{count} alternative placements found")
        print("done!")
    
    ############################# CONSTRAINTS ########################################
    
    def __constraint_func_mapper(self, constraint: str) -> Callable[[str], BoolRef]:
        match (constraint):
            case "intro":
                return self.__newIntroConstraint
            case "foundations":
                return self.__newFoundationsConstraint
            case "prob-and-stats":
                return self.__newProbAndStatsConstraint
            case "micro-macro-metrics":
                return self.__newMicroMacroMetricsConstraint
            case "technical":
                return self.__newTechnicalConstraint
            case "math-econ":
                return self.__newMathEconConstraint
            case "econ-elective":
                return self.__newEconElectiveConstraint
            case "capstone":
                return self.__newCapstoneConstraint
            case _: 
                raise RuntimeError(f"invalid constraint name: {constraint}")
            
            
    def __newIntroConstraint(self, degree_type: str) -> BoolRef:
        intro_1_standard = {"CSCI 0111", "CSCI 0150", "CSCI 0170"}
        intro_1_accel = "CSCI 0190"
        intro_2_standard = "CSCI 0200"

        # Trackers for our algebraic equation
        total_intros = []
        path1_intro1_pool = []
        path2_intro2_pool = []
        
        taken_0200 = False  # Will hold the Z3 variable if they took it
        taken_0190 = False  # Will hold the Z3 variable if they took it

        for course in self.courses:
            intro_var = self.assignment_vars[course]["intro"]
            total_intros.append(If(intro_var, 1, 0))

            # Extract the course number to check the ">= 0200" rule
            # (e.g., "CSCI 0320" -> 320)
            course_num = get_course_number(course)

            is_cs_course = course.startswith("CSCI")

            # --- Build Path 1 variables: standard ---
            if course in intro_1_standard:
                path1_intro1_pool.append(If(intro_var, 1, 0))
            if course == intro_2_standard:
                taken_0200 = intro_var

            # --- Build Path 2 variables: accel ---
            if course == intro_1_accel:
                taken_0190 = intro_var
            if (course_num >= 200 and is_cs_course) or course.startswith("Unknown"):
                path2_intro2_pool.append(If(intro_var, 1, 0))

        # Safely handle if the student didn't take 0190 or 0200 at all
        # If they didn't take it, we pass Z3 a hardcoded False
        var_0200 = taken_0200 if taken_0200 is not False else BoolVal(False)
        var_0190 = taken_0190 if taken_0190 is not False else BoolVal(False)


        # If took both 19 and 200, use those as the intro courses no matter what
        took_both = taken_0200 is not False and taken_0190 is not False
        
        # If they took both, we require both of their intro variables to be True. 
        # Otherwise, we just pass True (which has no effect in an And statement).
        override_rule = And(var_0190, var_0200) if took_both else BoolVal(True)

        # Rule 1: We must select EXACTLY 2 courses for the intro requirement globally.
        # (Adding a literal 0 to the lists prevents Z3 from crashing if the student 
        # took no valid courses and the lists are completely empty).
        rule_exactly_two = Sum([0] + total_intros) == 2

        # Rule 2: Path 1 (Standard)
        # Exactly 1 from {0111, 0150, 0170} AND 0200 must be True
        path1_valid = And(Sum([0] + path1_intro1_pool) == 1, var_0200)

        # Rule 3: Path 2 (Accelerated)
        # 0190 must be True AND exactly 1 course >= 0200 must be True
        path2_valid = And(var_0190, Sum([0] + path2_intro2_pool) == 1)

        # The overall requirement is satisfied if we have exactly 2 courses 
        # AND one of the paths is valid.
        return And(rule_exactly_two, Or(path1_valid, path2_valid), override_rule) # type: ignore
    
    def __newProbAndStatsConstraint(self, degree_type: str) -> BoolRef:
        pas_allowed = {"CSCI 1450", "APMA 1650", "APMA 1655"}

        total_pas_conditions = []

        #for each course...
        for course in self.courses:
            #get the z3 variable for that course
            pas_var = self.assignment_vars[course]["prob-and-stats"]

            #add a condition to count the requirement if allowed
            if (course in pas_allowed) or course.startswith("Unknown"):
                total_pas_conditions.append(If(pas_var, 1, 0))
            else:
                #and disallow the assignment for this requirement if not.
                self.s.add(Not(pas_var))

        #We only need one PAS course in the degree
        final_pas_constraint = Sum(*([0] + total_pas_conditions)) == 1
        return final_pas_constraint # type: ignore
    

    def __newFoundationsConstraint(self, degree_type: str) -> BoolRef:
        #Get the groups of foundations courses [same as normal CS]
        foundations_requirements = self.reader.get_new_foundations()

        valid_foundations_courses = set()
        all_slot_sums = []
        category_active_vars = []

        unknown_courses = [c for c in self.courses if c.startswith("Unknown")]
        # Maps an unknown course to a list of Z3 Bools representing its placement in each slot
        unknown_slot_vars = {u: [] for u in unknown_courses}

        # 1. Parse JSON and build logical slots    
        for idx, category_data in enumerate(foundations_requirements):
            course_groups = category_data["Courses"]
            cat_slot_sums = []

            # iterate through each group
            for group in course_groups:
                slot_vars = []
                #extract all of the courses for the group
                for course in group:
                    valid_foundations_courses.add(course)
                    
                    #add an foundations variable for each course
                    if course in self.courses:
                        var = self.assignment_vars[course]["foundations"]
                        slot_vars.append(If(var, 1, 0))

                for u in unknown_courses:
                    # Create a specific Z3 boolean for this unknown course in this slot
                    u_slot_var = Bool(f"{u}_foundations_slot_{idx}")
                    unknown_slot_vars[u].append(u_slot_var)
                    slot_vars.append(If(u_slot_var, 1, 0))

                if slot_vars:
                    # Enforce that a student gets AT MOST 1 credit per sub-list
                    slot_sum = Sum(*slot_vars)
                    self.s.add(slot_sum <= 1)
                    
                    cat_slot_sums.append(slot_sum)
                    all_slot_sums.append(slot_sum)

            # 2. Track if this specific category is active
            if cat_slot_sums:
                cat_total = Sum(*cat_slot_sums)
                # If they fulfilled at least 1 slot in this category, the branch counts as 1
                category_active_vars.append(If(cat_total > 0, 1, 0))

        # 3. Exclude invalid courses
        for course in self.courses:
            if course not in valid_foundations_courses and not course.startswith("Unknown"):
                var = self.assignment_vars[course]["foundations"]
                self.s.add(Not(var))

        # 4. Calculate global totals + enforce unknowns
        for u in unknown_courses:
            u_global_var = self.assignment_vars[u]["foundations"]
            u_slot_sum = Sum(*[If(v, 1, 0) for v in unknown_slot_vars[u]])
            
            # An unknown course cannot fulfill more than 1 foundations bucket
            self.s.add(u_slot_sum <= 1)
            
            # The global foundations variable for this unknown course is True 
            # if and only if it is assigned to exactly one slot inside the buckets
            self.s.add(u_global_var == (u_slot_sum == 1))
        
        # Adding [0] ensures we don't crash if the lists are completely empty
        total_foundations = Sum(*([0] + all_slot_sums))
        total_branches = Sum(*([0] + category_active_vars))

        #3 foundations courses are needed, which span the 3 branches
        final_constraint = And(total_foundations == 2, total_branches == 2)

        return final_constraint # type: ignore
    
    def __newMicroMacroMetricsConstraint(self, degree_type: str) -> BoolRef:
        mmm_allowed = {"ECON 1130", "ECON 1210", "ECON 1630"}

        total_mmm_conditions = []

        #for each course...
        for course in self.courses:
            #get the z3 variable for that course
            mmm_var = self.assignment_vars[course]["micro-macro-metrics"]

            #add a condition to count the requirement if allowed
            if (course in mmm_allowed) or course.startswith("Unknown"):
                total_mmm_conditions.append(If(mmm_var, 1, 0))
            else:
                #and disallow the assignment for this requirement if not.
                self.s.add(Not(mmm_var))

        #We only need all micro/macro/metrics in degree
        final_mmm_constraint = Sum(*([0] + total_mmm_conditions)) == 3
        return final_mmm_constraint # type: ignore
    
    def __newTechnicalConstraint(self, degree_type: str) -> BoolRef:
        
        #get the list of humanities courses to check against
        humanities_courses: list[str] = self.reader.get_humanities_courses()
        foundations_requirements: list[str] = self.reader.get_new_foundations()


        valid_conditions = []
        idp_conditions = []
        foundations_conditions = []
        
        for course in self.courses:
            #get the corresponding z3 variable for each course
            technical_var = self.assignment_vars[course]["technical"]
            
            # 1. Parse the course code (e.g., "CSCI 1450" -> 1450)
            course_num = get_course_number(course)
                
            # 2. Basic Check: Must be a CSCI course >= 1000 and not humanities
            if ((course.startswith("CSCI") and 
                course_num >= 1000 and
                course not in humanities_courses) or 
                (course in foundations_requirements) or
                course.startswith("Unknown")):

                valid_conditions.append(If(technical_var, 1, 0))

                #if the course is an independent study, track this
                if course.startswith("CSCI 1970"):
                    idp_conditions.append(If(technical_var, 1, 0))
                
                #if the course is a foundations, track this
                if course in foundations_requirements:
                    foundations_conditions.append(If(technical_var, 1, 0))

            else:
                # Force invalid courses (e.g., ENGN courses or < 1000 or IDP or humanities) to False
                self.s.add(Not(technical_var))

        if degree_type == "SCB":
            # We need exactly 3 upper-level courses, only one of which can be 1970 and another a foundations course
            return And(Sum(*([0] + valid_conditions)) == 3, Sum(*([0] + idp_conditions)) <= 1, Sum(*([0] + foundations_conditions)) <= 1)
        else:
            # We need exactly 2 upper-level courses, only one of which can be 1970 and another a foundations course
            return And(Sum(*([0] + valid_conditions)) == 2, Sum(*([0] + idp_conditions)) <= 1, Sum(*([0] + foundations_conditions)) <= 1)

    def __newMathEconConstraint(self, degree_type: str) -> BoolRef:
        math_econ_allowed: list[str] = self.reader.get_new_math_econ()

        total_math_econ_conditions = []

        #for each course...
        for course in self.courses:
            #get the z3 variable for that course
            math_econ_var = self.assignment_vars[course]["math-econ"]

            course_num = get_course_number(course)

            #add a condition to count the requirement if allowed
            if ((course in math_econ_allowed) or 
                (course.startswith("ECON") and course_num >= 2000) or 
                course.startswith("Unknown")):
                total_math_econ_conditions.append(If(math_econ_var, 1, 0))
            else:
                #and disallow the assignment for this requirement if not.
                self.s.add(Not(math_econ_var))

        #We only need 3 math econ in degree
        final_math_econ_constraint = Sum(*([0] + total_math_econ_conditions)) == 3
        return final_math_econ_constraint # type: ignore
    
    def __newEconElectiveConstraint(self, degree_type: str) -> BoolRef:
        if degree_type == "AB": #this isn't a req for ABs
            for course in self.courses:
                self.s.add(Not(self.assignment_vars[course]["econ-elective"]))
            return BoolVal(True)
        
        econ_elect_disallowed = {"ECON 1620", "ECON 1960", "ECON 1970"}
        total_econ_elect_conditions = []
        low_level_econ_conditions = []

        #for each course...
        for course in self.courses:
            #get the z3 variable for that course
            econ_elect_var = self.assignment_vars[course]["econ-elective"]
            
            course_num = get_course_number(course)

            #add a condition to count the requirement if allowed
            if (((course not in econ_elect_disallowed) and 
                course.startswith("ECON") and 
                course_num >= 1000) or 
                course.startswith("Unknown")):
                total_econ_elect_conditions.append(If(econ_elect_var, 1, 0))

                if (course_num < 1100):
                    low_level_econ_conditions.append(If(econ_elect_var, 1, 0))
            else:
                #and disallow the assignment for this requirement if not.
                self.s.add(Not(econ_elect_var))

        #We only need 2 econ electives in degree, only 1 can be 1000-1099
        final_econ_elect_constraint = And(Sum(*([0] + total_econ_elect_conditions)) == 2, Sum(*([0] + low_level_econ_conditions)) <= 1)
        return final_econ_elect_constraint # type: ignore
    
    def __newCapstoneConstraint(self, degree_type: str) -> BoolRef:
        if degree_type == "AB": #this isn't a req for ABs
            for course in self.courses:
                self.s.add(Not(self.assignment_vars[course]["capstone"]))
            return BoolVal(True)

        #get the list of capstones
        cs_capstone_courses: list[str] = self.reader.get_capstone_courses()
        econ_capstone_courses: list[str] = self.reader.get_econ_capstone_courses()
        #So, technically, this can be a TA position or any 1000+ econ if you can argue for it. 
        #But we're taking a course-first vision of the world so I'm not dealing with that. argue with the wall 🧱

        valid_capstones = []

        #for each course...
        for course in self.courses:
            #get the capstone z3 variable for the course
            var = self.assignment_vars[course]["capstone"]

            # 1. Add if course is in the list of capstone-able courses
            if course in cs_capstone_courses or course in econ_capstone_courses or course.startswith("Unknown"):
                valid_capstones.append(If(var, 1, 0))

            # 2. Not in the capstone list (which includes 1970). Cannot be used for capstone!
            else:
                self.s.add(Not(var))

        # We require exactly 1 capstone course always
        # (Adding [0] prevents crashing if valid_capstones is totally empty)
        return Sum(*([0] + valid_capstones)) == 1 # type: ignore


    def __doubleDippingConstraint(self):
        #get the list of active requirement categories
        active_reqs = [req for req, is_active in self.constraint_dict.items() if is_active]
        
        #for each course...
        for course in self.courses:
            # capstones and humanities requirements can overlap with anything, so take them out of the restricted pool
            restricted_reqs = [req for req in active_reqs if (req != "capstone" and req != "humanities-limit")]
            
            # get the booleans for all remaining restricted requirements
            restricted_bools = [self.assignment_vars[course][req] for req in restricted_reqs]
            
            # count how many restricted buckets (requirement sets) this course is placed into
            restricted_count = Sum(*[If(b, 1, 0) for b in restricted_bools])

            # do not allow these buckets to overlap AT ALL
            self.s.add(restricted_count <= 1)
