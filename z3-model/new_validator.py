from typing import Callable
from util.json_reader import JSONReader
from util.util import get_course_number
from copy import deepcopy

from z3 import *

class NewCS():
    def  __init__(self, year: int, courses: list[str], reader: JSONReader, constraint_dict: dict[str, bool], printing: bool=True):
        #set up our class
        self.s = Solver()
        self.constraint_dict = deepcopy(constraint_dict)
        self.year = year 
        self.courses = courses
        self.reader = reader
        self.printing = printing


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

        self.__my_print("Looking for new CS " + degree_type + " requirements")

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
                self.__my_print(f"Found a valid course plan with {unknowns} unknown courses")
                self.__generate_unknown_alternatives()

            self.s.pop()
        else:
            self.__my_print(f"cannot form a valid {degree_type} degree")
            self.s.pop()
            is_sat = self.__try_with_unknowns(degree_type, unknowns, limit_of_unknowns)

        return is_sat
    
        # this function assumes the constraints are SAT!
    def __print_results(self):
        active_reqs = [req for req, is_active in self.constraint_dict.items() if is_active]
        m = self.s.model()
        self.__my_print("\n--- Valid Course Assignment ---")
        all_used_courses = []
        
        for req in active_reqs:
            if req == "humanities-limit":
                continue
            
            # Gather all courses used for this bucket
            used_courses = [c for c in self.courses if is_true(m.evaluate(self.assignment_vars[c][req]))]
            all_used_courses.extend(used_courses)
            
            # Print everything EXCEPT foundations as a standard list
            if req != "foundations":
                self.__my_print(f"{req}: {used_courses}")
            elif req == "foundations":
                self.__my_print("foundations:")
                foundations_requirements = self.reader.get_new_foundations()
                unknowns_used_for_foundations = [c for c in used_courses if c.startswith("Unknown")]
                for foundations_category in foundations_requirements:
                    # the 0 index is kind of gross, but is because we have used standard formatting for our JSONs
                    course_used_for_category = [c for c in used_courses if c in foundations_category["Courses"][0]]
                    if not course_used_for_category: # need to use an unknown
                        course_used_for_category = [unknowns_used_for_foundations.pop()]
                        
                    self.__my_print(f"     {foundations_category['Category']}: {course_used_for_category[0]}")

        # --- Humanities Printing ---
        humanities_list = self.reader.get_humanities_courses()
        humanities_included_in_degree = [course for course in all_used_courses if course in humanities_list]
        
        # Use a set to remove duplicates (in case a humanity was used in multiple buckets)
        unique_humanities = list(set(humanities_included_in_degree))
        self.__my_print(f"humanities courses used in degree: {unique_humanities}")

    def __my_print(self, *args, **kwargs):
        if self.printing:
            print(*args, **kwargs)
    
    ################################### UNKNOWN HANDLING #######################################
    
    def __try_with_unknowns(self, degree_type: str, num_unknowns: int, limit_of_unknowns: int = 6):
        if num_unknowns > limit_of_unknowns - 1:
            self.__my_print("Too many unknowns to build a degree!")
            return (False, num_unknowns)
        
        count = num_unknowns + 1
        self.courses.append(f"Unknown {count}")
        self.__my_print(f"trying with {count} inserted unknown class(es)")
        is_sat = self.validate(degree_type, num_unknowns + 1, limit_of_unknowns)

        return is_sat
        

    def __generate_unknown_alternatives(self, limit: int = 5):
        self.__my_print("\nSearching for Unknown course placements...")
        
        # Get active requirements
        active_reqs = [req for req, is_active in self.constraint_dict.items() if is_active]
        pathway_requirements = self.reader.get_pathways() if "pathways" in active_reqs else []

        # Get a static list of the unknown courses
        unknown_courses = [c for c in self.courses if c.startswith("Unknown")]

        count = 0
        while self.s.check() == sat and count < limit:
            m = self.s.model()
            count += 1
            self.__my_print(f"\n--- Alternative {count} ---")
            
            unknowns_used = False
            
            # This list will hold equations defining the CURRENT distribution of Unknowns.
            # e.g., [Sum(Unknowns in intro) == 1, Sum(Unknowns in pathways) == 1, ...]
            current_distribution_equations = []

            # 1. Check the main requirement buckets
            for req in active_reqs:
                if req == "humanities-limit":
                    continue
                
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
                    self.__my_print(f"- {actual_count} Unknown(s) filling requirement: {req}")

            self.__print_results()

            # 2. Block this specific numerical distribution and loop again
            if unknowns_used:
                # Tell Z3: "You cannot use this EXACT distribution of Unknowns again."
                self.s.add(Not(And(*current_distribution_equations)))
            else:
                self.__my_print("- No Unknowns were needed to graduate! The real transcript is sufficient.")
                break # Stop searching if they can graduate without help
                
        if self.s.check() != sat:
            self.__my_print("out of possible placements")
        else:
            self.__my_print(f"hit unknown placement limit")
        self.__my_print(f"{count} alternative placements found")
        self.__my_print("done!")
    
    ############################# CONSTRAINTS ########################################
    
    def __constraint_func_mapper(self, constraint: str) -> Callable[[str], BoolRef]:
        match (constraint):
            case "intro":
                return self.__newIntroConstraint
            case "foundations":
                return self.__newFoundationsConstraint
            case "math":
                return self.__newMathConstraint
            case "elective":
                return self.__newElectiveConstraint
            case "technical":
                return self.__newTechnicalConstraint
            case "capstone":
                return self.__newCapstoneConstraint
            case "humanities-limit":
                return self.__humanitiesLimitConstraint
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
    

    def __newMathConstraint(self, degree_type: str) -> BoolRef:
        math_allowed = {"CSCI 0220", "MATH 1530"} #technically more courses can do this, but the dept is vague about it so no

        total_math_conditions = []

        #for each course...
        for course in self.courses:
            #get the z3 variable for that course
            math_var = self.assignment_vars[course]["math"]

            #add a condition to count the requirement if allowed
            if (course in math_allowed) or course.startswith("Unknown"):
                total_math_conditions.append(If(math_var, 1, 0))
            else:
                #and disallow the assignment for this requirement if not.
                self.s.add(Not(math_var))

        #We only need one math foundations course in the degree
        final_math_constraint = Sum(*([0] + total_math_conditions)) == 1
        return final_math_constraint # type: ignore
    

    def __newFoundationsConstraint(self, degree_type: str) -> BoolRef:
        #Get the groups of foundations courses
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
                    #ignore 0320 if SCB
                    if not(course == "CSCI 0320" and degree_type == "SCB"):
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
        final_constraint = And(total_foundations == 3, total_branches == 3)

        return final_constraint # type: ignore


    def __newTechnicalConstraint(self, degree_type: str) -> BoolRef: 
        #get the list of humanities courses to check against
        humanities_courses: list[str] = self.reader.get_humanities_courses()

        valid_conditions = []
        
        for course in self.courses:
            #get the corresponding z3 variable for each course
            technical_var = self.assignment_vars[course]["technical"]
            
            # 1. Parse the course code (e.g., "CSCI 1450" -> 1450)
            course_num = get_course_number(course)
                
            # 2. Basic Check: Must be a CSCI course >= 1000 and not CSCI 1970 and not humanities
            if ((course.startswith("CSCI") and 
                course_num >= 1000 and 
                not course.startswith("CSCI 1970") and
                course not in humanities_courses) or 
                course.startswith("Unknown")):
                valid_conditions.append(If(technical_var, 1, 0))
            else:
                # Force invalid courses (e.g., ENGN courses or < 1000 or IDP or humanities) to False
                self.s.add(Not(technical_var))
                
        # We need exactly 5 or 2 upper-level courses dep. on the degree
        if degree_type == "SCB":
            return Sum(*([0] + valid_conditions)) == 5 # type: ignore
        else:
            return Sum(*([0] + valid_conditions)) == 2 # type: ignore
        

    def __newElectiveConstraint(self, degree_type: str) -> BoolRef:
        # build up our group of allowable courses
        valid_electives = []
        non_cs_courses: list[str] = self.reader.get_non_cs_courses()
        linear_alg_courses = ["MATH 0520", "MATH 0540", "APMA 0260"]
        idp_study_courses = ["CSCI 1970(1)", "CSCI 1970(2)"] # this is picked up by the general requirement, but it's nice to spell out
        additional_systems_courses = ["CSCI 0320"]
        if degree_type == "AB":
            additional_systems_courses.extend(["CSCI 0300", "CSCI 0330"]) #AB allows any systems course

        valid_electives.extend(non_cs_courses)
        valid_electives.extend(linear_alg_courses)
        valid_electives.extend(idp_study_courses)
        valid_electives.extend(additional_systems_courses)

        total_assigned_conditions = []
        non_cs_conditions = []
        systems_conditions = []

        #for each course...
        for course in self.courses:
            #get the corresponding variable for that course
            elective_var = self.assignment_vars[course]["elective"]

            # Extract course number to check the "1000 or 2000-level" rule
            course_num = get_course_number(course)

            #check if the course is a valid elective
            is_valid_course = (
                course in valid_electives or # course is approved
                ((course.startswith("CSCI") or course.startswith("MATH")) and course_num >= 1000) or #course is CSCI/MATH 1000+
                course.startswith("Unknown")
            )

            if is_valid_course:
                # If valid, we add it to the total pool of selectable courses
                total_assigned_conditions.append(If(elective_var, 1, 0))

                # If it's specifically a systems course, track it in the systems pool too
                if course in additional_systems_courses:
                    systems_conditions.append(If(elective_var, 1, 0))

                # If it's specifically a CS/lin alg course, track it in the non-CS pool too
                if not(course.startswith("CSCI") and course not in linear_alg_courses):
                    non_cs_conditions.append(If(elective_var, 1, 0))

            else:
                #otherwise, this course is not a valid elective
                self.s.add(Not(elective_var))

        #count the number of courses in each group
        total_assigned = Sum(*([0] + total_assigned_conditions))
        total_non_cs = Sum(*([0] + non_cs_conditions))
        total_systems = Sum(*([0] + systems_conditions))


        if degree_type == "SCB":
            # 4 total courses, no more than 3 non-cs, no more than 1 systems
            final_constraint = And(total_assigned == 4, total_non_cs <= 3, total_systems <= 1)
                
        elif degree_type == "AB":
            # 2 total courses, and no more than 1 non-cs, no more than 1 systems
            final_constraint = And(total_assigned == 2, total_non_cs <= 1, total_systems <= 1)

        return final_constraint # type: ignore
    
    def __newCapstoneConstraint(self, degree_type: str) -> BoolRef:
        #get the list of capstones
        capstone_courses: list[str] = self.reader.get_capstone_courses()

        valid_capstones = []

        #for each course...
        for course in self.courses:
            #get the capstone z3 variable for the course
            var = self.assignment_vars[course]["capstone"]

            # 1. Add if course is in the list of capstone-able courses
            if course in capstone_courses or course.startswith("Unknown"):
                valid_capstones.append(If(var, 1, 0))

            # 2. Not in the capstone list (including 1970). Cannot be used for capstone!
            else:
                self.s.add(Not(var))

        # We require exactly 1 capstone course always
        # (Adding [0] prevents crashing if valid_capstones is totally empty)
        return Sum(*([0] + valid_capstones)) == 1 # type: ignore


    def __humanitiesLimitConstraint(self, degree_type: str) -> BoolRef:
        # get the list of humanities courses to check against
        humanities_courses: list[str] = self.reader.get_humanities_courses()
        
        used_humanities_conditions = []
        
        # Get a list of all the REAL requirement buckets (exclude this one)
        real_req_buckets = [
            req for req, is_active in self.constraint_dict.items() 
            if is_active and req != "humanities-limit"
        ]

        for course in self.courses:
            # 1. Lock down the dummy bucket so Z3 can't hide courses here
            dummy_var = self.assignment_vars[course]["humanities-limit"]
            self.s.add(Not(dummy_var))

            # 2. If the course is a humanities course, we must track it
            if course in humanities_courses:
                
                # Gather the boolean variables for this course across all REAL buckets
                assigned_to_buckets = []
                for req in real_req_buckets:
                    assigned_to_buckets.append(self.assignment_vars[course][req])
                
                # Create a rule: Is this course used ANYWHERE in the degree?
                is_used_anywhere = Or(*assigned_to_buckets)
                
                # If it is used anywhere, it adds 1 to our global humanities tally
                used_humanities_conditions.append(If(is_used_anywhere, 1, 0))

        # 3. Sum up the total number of humanities courses used across the whole degree
        total_humanities_used = Sum(*([0] + used_humanities_conditions))

        # 4. Enforce the degree limits
        if degree_type == "SCB":
            # Max 3 humanities allowed to count towards the degree
            final_constraint = total_humanities_used <= 3
        elif degree_type == "AB":
            # Max 1 humanities allowed to count towards the degree
            final_constraint = total_humanities_used <= 1

        return final_constraint # type: ignore
    

    def __doubleDippingConstraint(self):
        #get the list of active requirement categories
        active_reqs = [req for req, is_active in self.constraint_dict.items() if is_active]
        
        #for each course...
        for course in self.courses:
            # capstones and humanities requirments can overlap with anything, so take them out of the restricted pool
            restricted_reqs = [req for req in active_reqs if (req != "capstone" and req != "humanities-limit")]
            
            # get the booleans for all remaining restricted requirements
            restricted_bools = [self.assignment_vars[course][req] for req in restricted_reqs]
            
            # count how many restricted buckets (requirement sets) this course is placed into
            restricted_count = Sum(*[If(b, 1, 0) for b in restricted_bools])

            # do not allow these buckets to overlap AT ALL
            self.s.add(restricted_count <= 1)
