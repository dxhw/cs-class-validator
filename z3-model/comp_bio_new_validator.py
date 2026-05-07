from typing import Callable
from util.json_reader import JSONReader
from util.util import get_course_number
from copy import deepcopy

from z3 import *

#SCB 
#bio core (biol 470 and (280 OR 500))
#chem core (chem 330 or 350)
#discrete
#cs intro
#prob and stats
#comp bio core (apma 1080 & csci 1810)
#tracks (CS, BIO, APMA)
#capstone

#AB
#bio core (biol 470 and (280 OR 500))
#chem core (chem 330 or 350)
#cs intro
#prob and stats
#comp bio core (apma 1080 & csci 1810)
#electives (list)
#capstone

class NewCompBio():
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

        self.__my_print("Looking for comp bio " + degree_type + " requirements")

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

            #just print everything as a standard list
            self.__my_print(f"{req}: {used_courses}")

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
            case "prob-and-stats":
                return self.__newProbAndStatsConstraint
            case "discrete":
                return self.__newDiscreteConstraint
            case "bio-core":
                return self.__newBioCoreConstraint
            case "chem-core":
                return self.__newChemCoreConstraint
            case "comp-bio-core":
                return self.__newCompBioCoreConstraint
            case "track":
                return self.__newTrackConstraint
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
        pas_allowed = {"APMA 1655", "CSCI 1450", "MATH 1210", "APMA 1650"}
        #there's a bridgework exam for apma 1650 so it can fulfill this

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
    
    def __newDiscreteConstraint(self, degree_type: str) -> BoolRef:
        if degree_type == "AB": #this isn't a req for ABs
            for course in self.courses:
                self.s.add(Not(self.assignment_vars[course]["discrete"]))
            return BoolVal(True)
        
        discrete_allowed = {"CSCI 0220"}

        total_discrete_conditions = []

        #for each course...
        for course in self.courses:
            #get the z3 variable for that course
            discrete_var = self.assignment_vars[course]["discrete"]

            #add a condition to count the requirement if allowed
            if (course in discrete_allowed) or course.startswith("Unknown"):
                total_discrete_conditions.append(If(discrete_var, 1, 0))
            else:
                #and disallow the assignment for this requirement if not.
                self.s.add(Not(discrete_var))

        #We only need one discrete course in the degree
        final_discrete_constraint = Sum(*([0] + total_discrete_conditions)) == 1
        return final_discrete_constraint # type: ignore
    
    def __newBioCoreConstraint(self, degree_type: str) -> BoolRef:
        genetics_allowed = {"BIOL 0470"}
        cellchem_allowed = {"BIOL 0280", "BIOL 0500"}

        total_bio_core_conditions = []
        genetics_conditions = []
        cellchem_conditions = []

        #for each course...
        for course in self.courses:
            #get the z3 variable for that course
            bio_core_var = self.assignment_vars[course]["bio-core"]

            if course in genetics_allowed or course in cellchem_allowed or course.startswith("Unknown"):
                total_bio_core_conditions.append(If(bio_core_var, 1, 0))

                #add a condition to count the requirement if allowed
                if course in genetics_allowed or course.startswith("Unknown"):
                    genetics_conditions.append(If(bio_core_var, 1, 0))
                
                if course in cellchem_allowed or course.startswith("Unknown"):
                    cellchem_conditions.append(If(bio_core_var, 1, 0))

            else:
                #and disallow the assignment for this requirement if not.
                self.s.add(Not(bio_core_var))

        #We need 2 bio core, one from each category
        final_bio_core_constraint = And(Sum(*([0] + total_bio_core_conditions)) == 2, Sum(*([0] + genetics_conditions)) == 1, Sum(*([0] + cellchem_conditions)) == 1)
        return final_bio_core_constraint # type: ignore
    

    def __newChemCoreConstraint(self, degree_type: str) -> BoolRef:      
        chem_core_allowed = {"CHEM 0330", "CHEM 0350"}

        total_chem_core_conditions = []

        #for each course...
        for course in self.courses:
            #get the z3 variable for that course
            chem_core_var = self.assignment_vars[course]["chem-core"]

            #add a condition to count the requirement if allowed
            if (course in chem_core_allowed) or course.startswith("Unknown"):
                total_chem_core_conditions.append(If(chem_core_var, 1, 0))
            else:
                #and disallow the assignment for this requirement if not.
                self.s.add(Not(chem_core_var))

        #We only need one chem core course in the degree
        final_chem_core_constraint = Sum(*([0] + total_chem_core_conditions)) == 1
        return final_chem_core_constraint # type: ignore
    
    def __newCompBioCoreConstraint(self, degree_type: str) -> BoolRef:      
        comp_bio_core_allowed = {"APMA 1080", "CSCI 1810"}

        total_comp_bio_core_conditions = []

        #for each course...
        for course in self.courses:
            #get the z3 variable for that course
            comp_bio_core_var = self.assignment_vars[course]["comp-bio-core"]

            #add a condition to count the requirement if allowed
            if (course in comp_bio_core_allowed) or course.startswith("Unknown"):
                total_comp_bio_core_conditions.append(If(comp_bio_core_var, 1, 0))
            else:
                #and disallow the assignment for this requirement if not.
                self.s.add(Not(comp_bio_core_var))

        #We need both comp bio core courses in the degree
        final_comp_bio_core_constraint = Sum(*([0] + total_comp_bio_core_conditions)) == 2
        return final_comp_bio_core_constraint # type: ignore
    

    
    def __newElectiveConstraint(self, degree_type: str) -> BoolRef:
        if degree_type == "SCB": #this isn't a req for SCBs
            for course in self.courses:
                self.s.add(Not(self.assignment_vars[course]["elective"]))
            return BoolVal(True)
        
        elective_courses: list[str] = self.reader.get_new_comp_bio_electives()

        total_elective_conditions = []

        #for each course...
        for course in self.courses:
            #get the z3 variable for that course
            elective_var = self.assignment_vars[course]["elective"]

            #add a condition to count the requirement if allowed
            if (course in elective_courses) or course.startswith("Unknown"):
                total_elective_conditions.append(If(elective_var, 1, 0))
            else:
                #and disallow the assignment for this requirement if not.
                self.s.add(Not(elective_var))

        #We only need 2 elective in degree
        final_elective_constraint = Sum(*([0] + total_elective_conditions)) == 2
        return final_elective_constraint # type: ignore
    

    def __newTrackConstraint(self, degree_type: str) -> BoolRef:
        if degree_type == "AB": #this isn't a req for SCBs
            for course in self.courses:
                self.s.add(Not(self.assignment_vars[course]["track"]))
            return BoolVal(True)
        
        valid_elective_courses = set()
        all_slot_sums = []
        category_active_vars = []
        
        track_requirements = self.reader.get_new_comp_bio_tracks()

        for category_data in track_requirements:
            t_name = category_data["Track"] 
            course_groups = category_data["Courses"] 
            cat_slot_sums = []

            for group in course_groups:                
                slot_vars = []
                for course in self.courses:
                    var = self.assignment_vars[course]["track"]
                    
                    if course.startswith("Unknown"):
                        slot_vars.append(If(var, 1, 0))
                        
                    elif course in group:
                        valid_elective_courses.add(course)
                        slot_vars.append(If(var, 1, 0))

                if slot_vars:
                    slot_sum = Sum(*slot_vars)
                    # if (category_data["Track"] == "Biology"):
                    #     self.s.add(slot_sum == 2)
                    # else:
                    #     self.s.add(slot_sum == 3)
                    cat_slot_sums.append(slot_sum)
                    all_slot_sums.append(slot_sum)

            # the biol track takes virtually any bio-related 1000+ course, 
            # so we need to treat that as a separate "slot" for the track
            if (category_data["Track"] == "Biology"):
                slot_vars = []

                for course in self.courses:
                    var = self.assignment_vars[course]["track"]

                    course_num = get_course_number(course)

                    #add a condition to count the requirement if allowed

                    if course.startswith("Unknown"):
                        slot_vars.append(If(var, 1, 0))

                    if (course_num >= 1000 and 
                         (course.startswith("BIOL") or 
                          course.startswith("EEPS") or 
                          course.startswith("NEUR") or 
                          course.startswith("ENVS") or 
                          course.startswith("CHEM") or 
                          course.startswith("PHP") or 
                          course.startswith("CPSY") or 
                          course.startswith("CLPS")) and
                          course not in course_groups[0]):
                        valid_elective_courses.add(course)
                        slot_vars.append(If(var, 1, 0))

                if slot_vars:
                    slot_sum = Sum(*slot_vars)
                    # self.s.add(slot_sum == 4) #we need 4 of these courses
                    cat_slot_sums.append(slot_sum)
                    all_slot_sums.append(slot_sum)

            
            # 2. Track if this specific Category (branch) is active
            if cat_slot_sums:
                # self.__my_print(cat_slot_sums)

                valid_cat_logic = BoolVal(False)

                # self.__my_print(len(cat_slot_sums))
                if len(cat_slot_sums) > 1:
                    match t_name:
                        case "Computer Science":
                            valid_cat_logic = And(cat_slot_sums[0] == 3, cat_slot_sums[1] == 3)
                        case "Applied Math":
                            valid_cat_logic = And(cat_slot_sums[0] == 3, cat_slot_sums[1] == 3)
                        case "Biology":
                            valid_cat_logic = And(cat_slot_sums[0] == 2, cat_slot_sums[1] == 4)

                # self.__my_print(valid_cat_logic)



                cat_total = Sum(*cat_slot_sums)
                # If they fulfilled both slots in this category, the branch counts as 1
                category_active_vars.append(If(valid_cat_logic, 1, 0))

        # 3. Exclude invalid courses
        for course in self.courses:
            if course not in valid_elective_courses and not course.startswith("Unknown"):
                var = self.assignment_vars[course]["track"]
                self.s.add(Not(var))

        # 4. Calculate global totals
        # Adding [0] ensures we don't crash if the lists are completely empty
        total_electives = Sum(*([0] + all_slot_sums))
        total_branches = Sum(*([0] + category_active_vars))

        # 6 intermediates covering 1 track
        final_constraint = total_branches == 1
            
        return final_constraint # type: ignore

    
    def __newCapstoneConstraint(self, degree_type: str) -> BoolRef:
        #get the list of capstones
        cs_capstone_courses: list[str] = self.reader.get_capstone_courses()
        #there are only CS capstones...

        valid_capstones = []

        #for each course...
        for course in self.courses:
            #get the capstone z3 variable for the course
            var = self.assignment_vars[course]["capstone"]

            course_num = get_course_number(course)

            # 1. Add if course is in the list of capstone-able courses
            if (course.startswith("BIOL 1950") or #BIOL IDP
                course.startswith("BIOL 1960") or
                course.startswith("APMA 1970") or #APMA IDP
                course.startswith("CSCI 1970") or #CSCI IDP
                course.startswith("NEUR 1970") or #NEUR IDP
                course.startswith("CHEM 1970") or #CHEM IDP
                (
                    (course.startswith("CSCI") or 
                     course.startswith("BIOL") or 
                     course.startswith("APMA")) and 
                     course_num >= 2000) #GRAD COURSES
                     or
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
