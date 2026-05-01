from typing import Callable
from util.json_reader import JSONReader

from z3 import *

# Constraints
    # intro sequence (2 courses)
    # intermediate (5 courses) - 1 from each category
    # 2 pathways
    # additional 1000+ (not in pathways)
    # three additional courses
    # humanities requirement (4)
    # capstone (in pathway)


DEFAULT_DICT = {
    "intro": True,
    "intermediate": True,
    "pathways": True,
    "upper-level": True,
    "additional": True,
    "capstone": True,
    "humanities-limit": True
}

class OldCS():
    def  __init__(self, year: int, courses: list[str], reader: JSONReader, constraint_dict: dict[str, bool] = DEFAULT_DICT):
        # pull in the degree JSONS

        self.s = Solver()
        self.constraint_dict = constraint_dict
        self.year = year
        self.courses = courses
        self.reader = reader

    def validate(self, degree_type: str):
        assert degree_type == "SCB" or degree_type == "AB"
        
        print("old " + degree_type)
        self.s.push()

        # Create the boolean matrix
        # assignment_vars[course][req] = Z3 Bool
        self.assignment_vars = {}
        active_reqs = [req for req, is_active in self.constraint_dict.items() if is_active]

        for course in self.courses:
            self.assignment_vars[course] = {}
            for req in active_reqs:
                # Create a uniquely named Z3 boolean for every course-req pair
                self.assignment_vars[course][req] = Bool(f"use_{course}_for_{req}")

        # apply all of the requirement constraints
        for req in active_reqs:
            constraint_func = self.__constraint_func_mapper(req)
            self.s.add(constraint_func(degree_type))

        # no double dipping (except intermediates and capstone)
        self.__doubleDippingConstraint()

        is_sat = self.s.check() == sat
        
        # Optional: Print the actual course assignments if satisfied
        if is_sat:
            m = self.s.model()
            print("\n--- Valid Course Assignment ---")
            for req in active_reqs:
                used_courses = [c for c in self.courses if is_true(m.evaluate(self.assignment_vars[c][req]))]
                print(f"{req}: {used_courses}")

        self.s.pop()
        return is_sat
    
    def __constraint_func_mapper(self, constraint: str) -> Callable[[str], BoolRef]:
        match (constraint):
            case "intro":
                return self.__oldIntroConstraint
            case "intermediate":
                return self.__oldIntermediateConstraint
            case "pathways":
                return self.__oldPathwaysConstraint
            case "upper-level":
                return self.__oldUpperLevelConstraint
            case "additional":
                return self.__oldAdditionalCoursesConstraint
            case "capstone":
                return self.__capstoneConstraint
            case "humanities-limit":
                return self.__humanitiesLimitConstraint
            case _: 
                raise RuntimeError(f"invalid constraint name: {constraint}")
            
    def __oldIntroConstraint(self, degree_type: str) -> BoolRef:
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
            var = self.assignment_vars[course]["intro"]
            total_intros.append(If(var, 1, 0))

            # Extract the course number to check the ">= 0200" rule
            # (e.g., "CSCI 0320" -> 320)
            try:
                course_num = int(''.join(filter(str.isdigit, course)))
            except ValueError:
                course_num = 0

            is_cs_course = course.startswith("CSCI")

            # --- Build Path 1 variables ---
            if course in intro_1_standard:
                path1_intro1_pool.append(If(var, 1, 0))
            if course == intro_2_standard:
                taken_0200 = var

            # --- Build Path 2 variables ---
            if course == intro_1_accel:
                taken_0190 = var
            if course_num >= 200 and is_cs_course:
                path2_intro2_pool.append(If(var, 1, 0))

        # Safely handle if the student didn't take 0190 or 0200 at all
        # If they didn't take it, we pass Z3 a hardcoded False
        var_0200 = taken_0200 if taken_0200 is not False else BoolVal(False)
        var_0190 = taken_0190 if taken_0190 is not False else BoolVal(False)

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
        
        return And(rule_exactly_two, Or(path1_valid, path2_valid)) # type: ignore

    def __oldIntermediateConstraint(self, degree_type: str) -> BoolRef:
        intermediate_requirements = self.reader.get_intermediate()

        valid_intermediate_courses = set()
        all_slot_sums = []
        category_active_vars = []

        # 1. Parse JSON and build logical slots
        for category_data in intermediate_requirements:
            course_groups = category_data["Courses"]
            cat_slot_sums = []

            for group in course_groups:
                slot_vars = []
                for course in group:
                    valid_intermediate_courses.add(course)
                    
                    if course in self.courses:
                        var = self.assignment_vars[course]["intermediate"]
                        slot_vars.append(If(var, 1, 0))

                if slot_vars:
                    # Enforce that a student gets AT MOST 1 credit per sub-list
                    slot_sum = Sum(*slot_vars)
                    self.s.add(slot_sum <= 1)
                    
                    cat_slot_sums.append(slot_sum)
                    all_slot_sums.append(slot_sum)

            # 2. Track if this specific Category (branch) is active
            if cat_slot_sums:
                cat_total = Sum(*cat_slot_sums)
                # If they fulfilled at least 1 slot in this category, the branch counts as 1
                category_active_vars.append(If(cat_total > 0, 1, 0))

        # 3. Exclude invalid courses
        for course in self.courses:
            if course not in valid_intermediate_courses:
                var = self.assignment_vars[course]["intermediate"]
                self.s.add(Not(var))

        # 4. Calculate global totals
        # Adding [0] ensures we don't crash if the lists are completely empty
        total_intermediates = Sum(*([0] + all_slot_sums))
        total_branches = Sum(*([0] + category_active_vars))

        # 5. Apply degree-specific rules
        if degree_type == "SCB":
            # SCB: 5 intermediates covering 3 different branches
            final_constraint = And(total_intermediates == 5, total_branches == 3)
            
        elif degree_type == "AB":
            # AB: 3 intermediates covering 2 different branches
            # Using >= 2 in case a student takes 3 courses across all 3 branches
            final_constraint = And(total_intermediates == 3, total_branches >= 2)

        return final_constraint # type: ignore
    
    def __oldPathwaysConstraint(self, degree_type: str) -> BoolRef:
        pathway_requirements = self.reader.get_pathways()

        pathway_active_vars = []
        
        # 1. THE SUB-MATRIX
        # course_pathway_vars[course][pathway_name] = Bool
        course_pathway_vars = {c: {} for c in self.courses}

        for pathway in pathway_requirements:
            p_name = pathway["Pathway"]
            
            # A boolean representing if the student completed this entire pathway
            p_active = Bool(f"pathway_{p_name}_active")
            pathway_active_vars.append(p_active)

            core_set = set(pathway["Core Courses"])
            valid_set = core_set | set(pathway["Graduate Courses"]) | set(pathway["Related Courses"])

            core_conditions = []
            total_conditions = []

            for course in self.courses:
                # Create the specific variable for this course -> this pathway
                var_p = Bool(f"use_{course}_for_pathway_{p_name}")
                course_pathway_vars[course][p_name] = var_p

                if course in valid_set:
                    total_conditions.append(If(var_p, 1, 0))
                    if course in core_set:
                        core_conditions.append(If(var_p, 1, 0))
                else:
                    # Invalid courses cannot be assigned to this pathway
                    self.s.add(Not(var_p))

            # 2. STATIC INTERMEDIATE CHECK
            # Because intermediates can overlap, they don't consume our Z3 variables.
            # We just need to check if the student's transcript has them.
            intermediates_met = True
            for req in pathway["Intermediate Courses"]:
                if not any(c in self.courses for c in req):
                    intermediates_met = False
                    break

            # 3. PATHWAY COMPLETION LOGIC
            if intermediates_met:
                # To activate, we need >= 1 core, and EXACTLY 2 total classes 
                # (1 core + 1 additional) so we don't waste courses.
                pathway_valid_logic = And(
                    Sum(*([0] + core_conditions)) >= 1,
                    Sum(*([0] + total_conditions)) == 2
                )
                
                # Link the active boolean to the completion of the logic
                self.s.add(p_active == pathway_valid_logic)

                # CRITICAL: If the pathway is NOT active, force the assigned courses to 0.
                # This stops Z3 from assigning 1 course to a dead pathway and wasting it.
                self.s.add(Implies(Not(p_active), Sum(*([0] + total_conditions)) == 0))
                
            else:
                # If they didn't take the intermediates, this pathway is impossible
                self.s.add(Not(p_active))
                for course in self.courses:
                    self.s.add(Not(course_pathway_vars[course][p_name]))

        # 4. LINK SUB-MATRIX TO GLOBAL MATRIX
        for course in self.courses:
            sub_vars = [course_pathway_vars[course][p["Pathway"]] for p in pathway_requirements]

            # Rule: A single course cannot be shared across multiple pathways
            self.s.add(Sum(*[If(v, 1, 0) for v in sub_vars]) <= 1)

            # Rule: The global "pathways" bucket is True if it was assigned to ANY specific pathway
            global_var = self.assignment_vars[course]["pathways"]
            self.s.add(global_var == Or(*sub_vars))

        # 5. DEGREE SPECIFIC RULES
        total_active_pathways = Sum(*([0] + [If(p, 1, 0) for p in pathway_active_vars]))

        if degree_type == "SCB":
            final_constraint = total_active_pathways == 2
        elif degree_type == "AB":
            final_constraint = total_active_pathways == 1

        return final_constraint # type: ignore
    
    def __oldUpperLevelConstraint(self, degree_type: str) -> BoolRef:
        pathway_requirements = self.reader.get_pathways()
        
        valid_conditions = []
        
        for course in self.courses:
            var = self.assignment_vars[course]["upper-level"]
            
            # 1. Parse the course code (e.g., "CSCI 1450" -> 1450)
            try:
                # Filter out the letters and grab the numbers
                course_num = int(''.join(filter(str.isdigit, course)))
            except ValueError:
                course_num = 0
                
            # 2. Basic Check: Must be a CSCI course >= 1000
            if course.startswith("CSCI") and course_num >= 1000:
                valid_conditions.append(If(var, 1, 0))
                
                # 3. The Breadth Rule: Exclude courses from chosen pathways
                for pathway in pathway_requirements:
                    p_name = pathway["Pathway"]
                    
                    # Combine all the pathway's courses into one set for easy checking
                    all_pathway_courses = (
                        set(pathway["Core Courses"]) | 
                        set(pathway["Graduate Courses"]) | 
                        set(pathway["Related Courses"])
                    )
                    
                    if course in all_pathway_courses:
                        # Re-create the exact Z3 boolean variable from your pathways constraint!
                        p_active = Bool(f"pathway_{p_name}_active")
                        
                        # Tell Z3: "If this pathway is True, then this course MUST be False here"
                        self.s.add(Implies(p_active, Not(var)))
                        
            else:
                # Force invalid courses (e.g., ENGN courses or < 1000) to False
                self.s.add(Not(var))
                
        # We need exactly 1 upper-level course
        return Sum(*([0] + valid_conditions)) == 1 # type: ignore

    def __oldAdditionalCoursesConstraint(self, degree_type: str) -> BoolRef:
            non_cs_courses: list[str] = self.reader.get_non_cs_courses()
            intermediate_data = self.reader.get_intermediate()

            # 1. Flatten the intermediate JSON into a single easily searchable set
            all_intermediates = set()
            for category in intermediate_data:
                for group in category["Courses"]:
                    for course in group:
                        all_intermediates.add(course)

            total_assigned_conditions = []
            upper_level_conditions = []

            for course in self.courses:
                var = self.assignment_vars[course]["additional"]

                # 2. Extract course number to check the "1000 or 2000-level" rule
                try:
                    course_num = int(''.join(filter(str.isdigit, course)))
                except ValueError:
                    course_num = 0

                # 3. Define the booleans for our rules
                is_allowed_dept = (
                    course.startswith("CSCI") or 
                    course.startswith("MATH") or 
                    (course in non_cs_courses)
                )
                is_intermediate = course in all_intermediates
                is_upper_level = 1000 <= course_num < 3000

                # 4. Categorize valid courses
                if is_allowed_dept and (is_intermediate or is_upper_level):
                    # If valid, we add it to the total pool of selectable courses
                    total_assigned_conditions.append(If(var, 1, 0))
                    
                    # If it's specifically an upper-level course, track it in the upper-level pool too
                    if is_upper_level:
                        upper_level_conditions.append(If(var, 1, 0))
                else:
                    # Otherwise, ban it
                    self.s.add(Not(var))

            # 5. Build the algebraic totals
            total_assigned = Sum(*([0] + total_assigned_conditions))
            total_upper_level = Sum(*([0] + upper_level_conditions))

            # 6. Apply degree rules
            if degree_type == "SCB":
                # 3 total courses, and AT LEAST 2 must be upper-level
                # (This naturally limits strictly-intermediate courses to AT MOST 1)
                final_constraint = And(total_assigned == 3, total_upper_level >= 2)
                
            elif degree_type == "AB":
                # Just 1 course total (the valid pool already enforces it must be intermed/upper)
                final_constraint = total_assigned == 1

            return final_constraint # type: ignore

    def __capstoneConstraint(self, degree_type: str) -> BoolRef:
            # Handle AB Degree
            if degree_type == "AB":
                # Force all capstone assignment variables to False so Z3 doesn't waste 
                # the student's courses on a requirement they don't have.
                for course in self.courses:
                    self.s.add(Not(self.assignment_vars[course]["capstone"]))
                return BoolVal(True)

            capstone_courses: list[str] = self.reader.get_capstone_courses()
            pathway_requirements = self.reader.get_pathways()

            valid_capstones = []

            for course in self.courses:
                var = self.assignment_vars[course]["capstone"]

                # 1. Universally valid capstones (1970A and 1970B)
                if course in ["CSCI 1970A", "CSCI 1970B"]:
                    valid_capstones.append(If(var, 1, 0))
                    continue

                # 2. Standard capstones (must be tied to an active pathway)
                if course in capstone_courses:
                    active_pathway_conditions = []
                    
                    for pathway in pathway_requirements:
                        p_name = pathway["Pathway"]
                        
                        all_pathway_courses = (
                            set(pathway["Core Courses"]) | 
                            set(pathway["Graduate Courses"]) | 
                            set(pathway["Related Courses"])
                        )
                        
                        if course in all_pathway_courses:
                            # Re-create the exact Z3 boolean variable from pathways constraint
                            p_active = Bool(f"pathway_{p_name}_active")
                            active_pathway_conditions.append(p_active)

                    if active_pathway_conditions:
                        # Tell Z3: "If you decide to set `var` to True, then AT LEAST ONE 
                        # of the pathways this course belongs to MUST be active."
                        self.s.add(Implies(var, Or(*active_pathway_conditions)))
                        
                        # Add to our pool of selectable capstones
                        valid_capstones.append(If(var, 1, 0))
                    else:
                        # Failsafe: It's in the capstone list, but belongs to zero pathways.
                        # This is actually a problem for a couple of courses that offer a capstone
                        # e.g., ENGN 1001 (it is viable for new requirement capstones)
                        self.s.add(Not(var))
                        
                else:
                    # 3. Not 1970, and not in the capstone list. Cannot be used.
                    self.s.add(Not(var))

            # We require exactly 1 capstone course for an SCB
            # (Adding [0] prevents crashing if valid_capstones is totally empty)
            return Sum(*([0] + valid_capstones)) == 1 # type: ignore

    def __humanitiesLimitConstraint(self, degree_type: str) -> BoolRef:
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
            # Max 4 humanities allowed to count towards the degree
            final_constraint = total_humanities_used <= 4
        elif degree_type == "AB":
            # Max 2 humanities allowed to count towards the degree
            final_constraint = total_humanities_used <= 2

        return final_constraint # type: ignore
    
    def __doubleDippingConstraint(self):
        active_reqs = [req for req, is_active in self.constraint_dict.items() if is_active]
        
        for course in self.courses:
            # capstones and humanities can overlap with anything, so take them out of the restricted pool
            restricted_reqs = [req for req in active_reqs if (req != "capstone" and req != "humanities-limit")]
            
            # get the booleans for all remaining restricted requirements
            restricted_bools = [self.assignment_vars[course][req] for req in restricted_reqs]
            
            # count how many restricted buckets this course is placed into
            restricted_count = Sum(*[If(b, 1, 0) for b in restricted_bools])
            
            # pathways can have intermediate courses that are used as intermediates
            if "pathways" in restricted_reqs and "intermediate" in restricted_reqs:
                
                is_in_pathway = self.assignment_vars[course]["pathways"]
                is_in_intermediate = self.assignment_vars[course]["intermediate"]
                
                # If it is used for BOTH an intermediate AND a pathway, the limit is 2. 
                # Otherwise, it must be strictly <= 1."
                self.s.add(
                    If(
                        And(is_in_pathway, is_in_intermediate),
                        restricted_count <= 2,
                        restricted_count <= 1
                    )
                )
            else:
                # Fallback if pathways or intermediates aren't active in this validation
                self.s.add(restricted_count <= 1)
