from typing import Callable
from util.json_reader import JSONReader
from util.util import get_course_number

from z3 import *

#SCB
#multi
#linear
#ODEs + PDEs
#optimization
#2 1000+ APMA not 1650 1910 1920 1090 indep study
#1 1000+ APMA or MATH not 1650 1910 1920 1090 indep study
#intro
#foundations + prob
#3 1000+ technical CSCI
#capstone (CS cap, apma 1360, 193*/194*, 1970/1971)
	# NO OVERLAP

class NewAPMACS():
    def  __init__(self, year: int, courses: list[str], reader: JSONReader, constraint_dict: dict[str, bool], printing: bool=True):
        #set up our class
        self.s = Solver()
        self.constraint_dict = constraint_dict
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
        #Only degree types are SCB
        assert degree_type == "SCB"
        self.__my_print("new APMA+CS " + degree_type)

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
            # Gather all courses used for this bucket
            used_courses = [c for c in self.courses if is_true(m.evaluate(self.assignment_vars[c][req]))]
            all_used_courses.extend(used_courses)

            #just print everything as a standard list
            self.__my_print(f"{req}: {used_courses}")

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
            case "multi":
                return self.__newMultiConstraint
            case "linear":
                return self.__newLinearConstraint
            case "technical":
                return self.__newTechnicalConstraint
            case "optimization":
                return self.__newOptimizationConstraint
            case "differential":
                return self.__newDifferentialConstraint
            case "apma-upper-div":
                return self.__newApmaUpperDivConstraint
            case "math-apma-upper-div":
                return self.__newMathOrApmaUpperDivConstraint
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
    
    def __newMultiConstraint(self, degree_type: str) -> BoolRef:
        multi_allowed = {"MATH 0180", "MATH 0200", "MATH 0350", "APMA 0260"}

        total_multi_conditions = []

        #for each course...
        for course in self.courses:
            #get the z3 variable for that course
            multi_var = self.assignment_vars[course]["multi"]

            #add a condition to count the requirement if allowed
            if (course in multi_allowed) or course.startswith("Unknown"):
                total_multi_conditions.append(If(multi_var, 1, 0))
            else:
                #and disallow the assignment for this requirement if not.
                self.s.add(Not(multi_var))

        #We only need one multi course in the degree
        final_multi_constraint = Sum(*([0] + total_multi_conditions)) == 1
        return final_multi_constraint # type: ignore
    
    def __newLinearConstraint(self, degree_type: str) -> BoolRef:
        linear_allowed = {"MATH 0520", "MATH 0540", "CSCI 0530", "APMA 1170", "APMA 0260"}
        
        # if APMA 0260 is used for both multi and linear, then we need an additional 1000+ APMA or MATH
        # if APMA 0260 isn't in the degree or multi constraint isn't on, just default to False
        multi_260_var = self.assignment_vars.get("APMA 0260", {}).get("multi", BoolVal(False))
        linear_260_var = self.assignment_vars.get("APMA 0260", {}).get("linear", BoolVal(False))
        is_double_dipping = And(multi_260_var, linear_260_var)

        all_linear_vars = []
        strictly_replacement_vars = [] 
        valid_replacement_vars = []    

        # Categorize all courses
        for course in self.courses:
            linear_var = self.assignment_vars[course]["linear"]
            
            is_standard = course in linear_allowed or course.startswith("Unknown")
            
            is_replacement = False
            if course.startswith("MATH") or course.startswith("APMA"):
                if get_course_number(course) >= 1000:
                    is_replacement = True
            
            # Unknowns are wildcards and can act as replacements too
            if course.startswith("Unknown"):
                is_replacement = True
                
            # Lock out completely invalid courses
            if not is_standard and not is_replacement:
                self.s.add(Not(linear_var))
            else:
                all_linear_vars.append(linear_var)
                
            # Track our replacement options
            if is_replacement:
                valid_replacement_vars.append(linear_var)
            if is_replacement and not is_standard:
                strictly_replacement_vars.append(linear_var)

        # tally the assignments
        total_linear = Sum([0] + [If(v, 1, 0) for v in all_linear_vars])
        total_strict_rep = Sum([0] + [If(v, 1, 0) for v in strictly_replacement_vars])
        total_valid_rep = Sum([0] + [If(v, 1, 0) for v in valid_replacement_vars])
        
        # SCENARIO A: APMA 0260 is assigned to BOTH Multi and Linear
        # The Linear bucket now requires exactly 2 courses: APMA 0260 and 1 valid replacement.
        scenario_double_dip = Implies(is_double_dipping, 
                                      And(total_linear == 2, total_valid_rep == 1))
                                      
        # SCENARIO B: Normal behavior (No double dipping)
        # The Linear bucket requires exactly 1 standard course, and strict replacements are banned.
        scenario_normal = Implies(Not(is_double_dipping), 
                                  And(total_linear == 1, total_strict_rep == 0))
                                  
        return And(scenario_double_dip, scenario_normal) # type: ignore

    def __newFoundationsConstraint(self, degree_type: str) -> BoolRef:
        #Get the groups of foundations courses
        foundations_requirements = self.reader.get_new_apma_cs_foundations()

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
        final_constraint = And(total_foundations == 3, total_branches == 3)

        return final_constraint # type: ignore

    def __newOptimizationConstraint(self, degree_type: str) -> BoolRef:
        optimization_allowed = {"APMA 1160", "APMA 1170", "APMA 1180", "APMA 1690", "APMA 1740"}

        total_optimization_conditions = []

        #for each course...
        for course in self.courses:
            #get the z3 variable for that course
            optimization_var = self.assignment_vars[course]["optimization"]

            #add a condition to count the requirement if allowed
            if (course in optimization_allowed) or course.startswith("Unknown"):
                total_optimization_conditions.append(If(optimization_var, 1, 0))
            else:
                #and disallow the assignment for this requirement if not.
                self.s.add(Not(optimization_var))

        #We only need 1 optimization in degree
        final_optimization_constraint = Sum(*([0] + total_optimization_conditions)) == 1
        return final_optimization_constraint # type: ignore
    

    def __newDifferentialConstraint(self, degree_type: str) -> BoolRef:
        differential_1_allowed = {"APMA 0355"}
        # technically, bridgework is allowed to use these past 2025 matriculators, but
        # we are ignoring this for now
        if self.year <= 2029:
            differential_1_allowed.add("APMA 0330")
            differential_1_allowed.add("APMA 0350")
        differential_2_allowed = {"APMA 0365"}
        if self.year <= 2029:
            differential_2_allowed.add("APMA 0340")
            differential_2_allowed.add("APMA 0360")

        # if there are at least 4 1000-level apma courses that are not 1910, 1920, or 
        # research/independent study courses (1970/1971), in the transcript,
        # MATH 1110 and MATH 1120 can be used for ODEs and PDEs respectively

        # NOTE: we are NOT handling this with unknowns because it would add a LOT of additional 
        # tracking which very few people would use anyways
        excluded = ("1910", "1920", "1970", "1971")

        count_apma_1000s = sum(
            1 for c in self.courses
            if c.startswith("APMA") and not c.split()[1].startswith(excluded)
        )

        if count_apma_1000s >= 4:
            differential_1_allowed.add("MATH 1110")
            differential_2_allowed.add("MATH 1120")

        total_differential_1_conditions = []
        total_differential_2_conditions = []

        #for each course...
        for course in self.courses:
            #get the z3 variable for that course
            differential_var = self.assignment_vars[course]["differential"]

            #add a condition to count the requirement if allowed
            if (course in differential_1_allowed) or course.startswith("Unknown"):
                total_differential_1_conditions.append(If(differential_var, 1, 0))
            elif (course in differential_2_allowed) or course.startswith("Unknown"):
                total_differential_2_conditions.append(If(differential_var, 1, 0))
            else:
                #and disallow the assignment for this requirement if not.
                self.s.add(Not(differential_var))

        #We need all differential in degree
        final_differential_constraint = Sum(*([0] + total_differential_1_conditions + total_differential_2_conditions)) == 2
        return final_differential_constraint # type: ignore
    
    def __newApmaUpperDivConstraint(self, degree_type: str) -> BoolRef:
        apma_disallowed = {"APMA 1910", "APMA 1920", "APMA 1970(1)", "APMA 1970(2)", "APMA 1971"}
        if self.year >= 2029:
            # APMA 1650 allowed if matriculating before Fall 2025
            # technically, bridgework can be done, however. We are not considering this
            apma_disallowed.add("APMA 1650")
        total_apma_conditions = []

        #for each course...
        for course in self.courses:
            #get the z3 variable for that course
            apma_var = self.assignment_vars[course]["apma-upper-div"]

            course_num = get_course_number(course)

            #add a condition to count the requirement if allowed
            if ((course not in apma_disallowed and
                course.startswith("APMA") and 
                course_num >= 1000) or 
                course.startswith("Unknown")):
                total_apma_conditions.append(If(apma_var, 1, 0))
            else:
                #and disallow the assignment for this requirement if not.
                self.s.add(Not(apma_var))

        #We need 2 upper level APMA in degree
        final_apma_constraint = Sum(*([0] + total_apma_conditions)) == 2
        return final_apma_constraint # type: ignore
    
    def __newMathOrApmaUpperDivConstraint(self, degree_type: str) -> BoolRef:
        math_apma_disallowed = {"APMA 1910", "APMA 1920", "MATH 1090", "MATH 1910", "APMA 1970(1)", "APMA 1970(2)", "MATH 1970(1)", "MATH 1970(2)", "APMA 1971"}
        if self.year >= 2029:
            # APMA 1650 allowed if matriculating before Fall 2025
            # technically, bridgework can be done, however
            math_apma_disallowed.add("APMA 1650")
        total_math_apma_conditions = []

        #for each course...
        for course in self.courses:
            #get the z3 variable for that course
            math_apma_var = self.assignment_vars[course]["math-apma-upper-div"]

            course_num = get_course_number(course)

            #add a condition to count the requirement if allowed
            if ((course not in math_apma_disallowed and
                 (course.startswith("MATH") or
                course.startswith("APMA")) and 
                course_num >= 1000) or 
                course.startswith("Unknown")):
                total_math_apma_conditions.append(If(math_apma_var, 1, 0))
            else:
                #and disallow the assignment for this requirement if not.
                self.s.add(Not(math_apma_var))

        #We only need 1 MATH/APMA upper level in degree
        final_math_apma_constraint = Sum(*([0] + total_math_apma_conditions)) == 1
        return final_math_apma_constraint # type: ignore

    def __newTechnicalConstraint(self, degree_type: str) -> BoolRef:
        
        #get the list of humanities courses to check against
        humanities_courses: list[str] = self.reader.get_humanities_courses()

        valid_conditions = []
        idp_conditions = []
        
        for course in self.courses:
            #get the corresponding z3 variable for each course
            technical_var = self.assignment_vars[course]["technical"]
            
            # 1. Parse the course code (e.g., "CSCI 1450" -> 1450)
            course_num = get_course_number(course)
                
            # 2. Basic Check: Must be a CSCI course >= 1000 and not humanities
            if ((course.startswith("CSCI") and 
                course_num >= 1000 and
                course not in humanities_courses) or
                course == "EEPS 1340" or
                course.startswith("Unknown")):

                valid_conditions.append(If(technical_var, 1, 0))

                #if the course is an independent study, track this
                if course.startswith("CSCI 1970"):
                    idp_conditions.append(If(technical_var, 1, 0))

            else:
                # Force invalid courses (e.g., ENGN courses or < 1000 or IDP or humanities) to False
                self.s.add(Not(technical_var))

        return And(Sum(*([0] + valid_conditions)) == 3, Sum(*([0] + idp_conditions)) <= 1) # type: ignore

    
    def __newCapstoneConstraint(self, degree_type: str) -> BoolRef:
        #get the list of capstones
        cs_capstone_courses: list[str] = self.reader.get_capstone_courses()
        apma_capstone_courses = {"APMA 1360", "APMA 1971"}

        valid_capstones = []

        #for each course...
        for course in self.courses:
            #get the capstone z3 variable for the course
            var = self.assignment_vars[course]["capstone"]

            # 1. Add if course is in the list of capstone-able courses
            if (course in cs_capstone_courses or 
            course in apma_capstone_courses or 
            course.startswith("APMA 193") or
            course.startswith("APMA 194") or
            course.startswith("APMA 1970") or
            course.startswith("Unknown")):
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
            
            # get the booleans for all remaining restricted requirements
            limited_course_bools = [self.assignment_vars[course][req] for req in active_reqs]
            
            # count how many restricted buckets (requirement sets) this course is placed into
            limited_course_use_count = Sum(*[If(b, 1, 0) for b in limited_course_bools])

            if course == "APMA 0260": # APMA 0260 can be used for both multi and linear, but if it is used for both, then an additional 1000+ APMA or MATH course is required
                self.s.add(limited_course_use_count <= 2)
            else: 
                # do not allow these buckets to overlap AT ALL
                self.s.add(limited_course_use_count <= 1)
        
        # for each of these sets of courses, only one of the courses can be used for concentration credit
        limited_course_sets = [{"APMA 1000", "APMA 1001", "MATH 1000", "MATH 1001"},
                               {"APMA 1650", "APMA 1655", "CSCI 1450", "MATH 1210", "MATH 1610", "ENGN 1630"},
                               {"CSCI 0300", "CSCI 0330"},
                               {"CSCI 0410", "CSCI 1410", "CSCI 1411"},
                               {"EEPS 1340", "CSCI 1951A"}]
        for limited_course_set in limited_course_sets:
            limited_courses_used = limited_course_set.intersection(self.courses)
            if len(limited_courses_used) >= 2:
                limited_course_bools = [self.assignment_vars[course][req] for course in limited_courses_used for req in active_reqs]
                limited_course_use_count = Sum(*[If(b, 1, 0) for b in limited_course_bools])
                self.s.add(limited_course_use_count <= 1)