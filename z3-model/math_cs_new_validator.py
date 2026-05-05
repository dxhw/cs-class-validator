from typing import Callable
from util.json_reader import JSONReader

from z3 import *

#SCB
#calc
#linear
#abstract
#intro 
#foundations
#3 1000+ MATH
#3 1000+ CSCI technical or 1 foundation or 1 humanities
#3 MATH or APMA or CSCI
#capstone

class NewMATHCS():
    def  __init__(self, year: int, courses: list[str], reader: JSONReader, constraint_dict: dict[str, bool]):
        #set up our class
        self.s = Solver()
        self.constraint_dict = constraint_dict
        self.year = year 
        self.courses = courses
        self.reader = reader

    def validate(self, degree_type: str, unknowns: int=0):
        #Only degree types are SCB
        assert degree_type == "SCB"
        print("new " + degree_type)

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

        is_sat = self.s.check() == sat
        
        # Print the actual course assignments if satisfied
        if is_sat:
            if unknowns == 0:
                self.__print_results()
            #are there unknowns involved? also print alternatives. 
            else:
                print(f"Found a valid course plan with {unknowns} unknown courses")
                self.__generate_unknown_alternatives()

            self.s.pop()
        else:
            print(f"cannot form a valid {degree_type} degree")
            print(f"trying with {unknowns + 1} inserted unknown class(es)")
            self.s.pop()
            self.__try_with_unknowns(degree_type, unknowns)



        return is_sat
    
        # this function assumes the constraints are SAT!
    def __print_results(self):

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
    
    def __try_with_unknowns(self, degree_type: str, num_unknowns: int, limit_of_unknown: int = 5):
        if num_unknowns > limit_of_unknown:
            print("Too many unknowns to build a degree!")
            return False
        
        count = num_unknowns + 1
        self.courses.append(f"Unknown {count}")
        is_sat = self.validate(degree_type, num_unknowns + 1)

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
            case "multi":
                return self.__newMultiConstraint
            case "linear":
                return self.__newLinearConstraint
            case "technical":
                return self.__newTechnicalConstraint
            case "abstract":
                return self.__newAbstractConstraint
            case "upper-math":
                return self.__newUpperMathConstraint
            case "elective":
                return self.__newElectiveConstraint
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
            try:
                course_num = int(''.join(filter(str.isdigit, course)))
            except ValueError:
                course_num = 0

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
        multi_allowed = {"MATH 0090", "MATH 0100", "MATH 0180", "MATH 0200", "MATH 0350"}

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

        #We need 3 calc... but we can stop at 180 if we start at 90, but we go to 350 if we start at 180
        final_multi_constraint = Sum(*([0] + total_multi_conditions)) == 3
        return final_multi_constraint # type: ignore
    

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

        #2 foundations courses are needed, which span the 2 branches
        final_constraint = And(total_foundations == 2, total_branches == 2)

        return final_constraint # type: ignore
    
    def __newLinearConstraint(self, degree_type: str) -> BoolRef:
        linear_allowed = {"MATH 0520", "MATH 0540", "CSCI 0530"}

        total_linear_conditions = []

        #for each course...
        for course in self.courses:
            #get the z3 variable for that course
            linear_var = self.assignment_vars[course]["linear"]

            #add a condition to count the requirement if allowed
            if (course in linear_allowed) or course.startswith("Unknown"):
                total_linear_conditions.append(If(linear_var, 1, 0))
            else:
                #and disallow the assignment for this requirement if not.
                self.s.add(Not(linear_var))

        #We only need 1 linear in degree
        final_linear_constraint = Sum(*([0] + total_linear_conditions)) == 1
        return final_linear_constraint # type: ignore
    
    def __newAbstractConstraint(self, degree_type: str) -> BoolRef:
        abstract_allowed = {"MATH 1530"}

        total_abstract_conditions = []

        #for each course...
        for course in self.courses:
            #get the z3 variable for that course
            abstract_var = self.assignment_vars[course]["abstract"]

            #add a condition to count the requirement if allowed
            if (course in abstract_allowed) or course.startswith("Unknown"):
                total_abstract_conditions.append(If(abstract_var, 1, 0))
            else:
                #and disallow the assignment for this requirement if not.
                self.s.add(Not(abstract_var))

        #We only need 1 abstract in degree
        final_abstract_constraint = Sum(*([0] + total_abstract_conditions)) == 1
        return final_abstract_constraint # type: ignore
    

    def __newUpperMathConstraint(self, degree_type: str) -> BoolRef:
        total_upper_math_conditions = []

        #for each course...
        for course in self.courses:
            #get the z3 variable for that course
            upper_math_var = self.assignment_vars[course]["upper-math"]

            try:
                # Filter out the letters and grab the numbers
                course_num = int(''.join(filter(str.isdigit, course)))
            except ValueError:
                course_num = 0

            #add a condition to count the requirement if allowed
            if (course.startswith("MATH") and course_num >= 1000) or course.startswith("Unknown"):
                total_upper_math_conditions.append(If(upper_math_var, 1, 0))
            else:
                #and disallow the assignment for this requirement if not.
                self.s.add(Not(upper_math_var))

        #We only need 3 upper math in degree
        final_upper_math_constraint = Sum(*([0] + total_upper_math_conditions)) == 3
        return final_upper_math_constraint # type: ignore
    
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
            try:
                # Filter out the letters and grab the numbers
                course_num = int(''.join(filter(str.isdigit, course)))
            except ValueError:
                course_num = 0
                
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

        return And(Sum(*([0] + valid_conditions)) == 3, Sum(*([0] + idp_conditions)) <= 1, Sum(*([0] + foundations_conditions)) <= 1)


    def __newElectiveConstraint(self, degree_type: str) -> BoolRef:
        total_elective_conditions = []

        #for each course...
        for course in self.courses:
            #get the z3 variable for that course
            elective_var = self.assignment_vars[course]["elective"]

            #add a condition to count the requirement if allowed
            if (course.startswith("MATH") or course.startswith("APMA") or course.startswith("CSCI")) or course.startswith("Unknown"):
                total_elective_conditions.append(If(elective_var, 1, 0))
            else:
                #and disallow the assignment for this requirement if not.
                self.s.add(Not(elective_var))

        #We only need 3 elective in degree
        final_elective_constraint = Sum(*([0] + total_elective_conditions)) == 3
        return final_elective_constraint # type: ignore

    
    def __newCapstoneConstraint(self, degree_type: str) -> BoolRef:
        #get the list of capstones
        cs_capstone_courses: list[str] = self.reader.get_capstone_courses()
        #there are only CS capstones...

        valid_capstones = []

        #for each course...
        for course in self.courses:
            #get the capstone z3 variable for the course
            var = self.assignment_vars[course]["capstone"]

            # 1. Add if course is in the list of capstone-able courses
            if (course in cs_capstone_courses or 
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
            #  humanities requirements can overlap with anything, so take them out of the restricted pool
            restricted_reqs = [req for req in active_reqs if (req != "capstone" and req != "humanities-limit")]
            
            # get the booleans for all remaining restricted requirements
            restricted_bools = [self.assignment_vars[course][req] for req in restricted_reqs]
            
            # count how many restricted buckets (requirement sets) this course is placed into
            restricted_count = Sum(*[If(b, 1, 0) for b in restricted_bools])

            # do not allow these buckets to overlap AT ALL
            self.s.add(restricted_count <= 1)
