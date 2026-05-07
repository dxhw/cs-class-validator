from typing import Callable
from util.json_reader import JSONReader
from util.util import get_course_number

from z3 import *

class OldCS():
    def  __init__(self, year: int, courses: list[str], reader: JSONReader, constraint_dict: dict[str, bool], printing: bool=True):
        # pull in the degree JSONS

        # We are using an optimizer rather than a solver here so that we can get unknowns to prefer
        # elective positions instead of pathways, which makes for more flexible degree suggestions
        self.s = Optimize()
        self.constraint_dict = constraint_dict
        self.year = year # if you are above class of 2027, these requirements are not available
        self.courses = courses
        self.reader = reader
        self.printing = printing
        
        # c/o 2026 has no capstones
        if self.year == 2026:
            self.constraint_dict["capstone"] = False

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

        self.__my_print("Looking for old " + degree_type + " requirements")

        # Old requirements are only allowed for c/o 2027 and earlier
        if self.year > 2027:
            self.__my_print("These requirements are only available to students in classes 2024-2027, so this student is not eligible for them")
            return (False, 0)
        
        # capstones are not required for ABs
        if degree_type == "AB":
            self.constraint_dict["capstone"] = False

        self.s.push()

        # if there are any unknown courses, we need to track their identities if they are
        # intermediates specifically because that cuts across multiple constraints
        if any([c.startswith("Unknown") for c in self.courses]):
            self.__build_intermediate_unknown_identities()

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

        # Optimization so that we prioritize using real classes to fill pathways
        real_courses = [c for c in self.courses if not c.startswith("Unknown")]
        optimization_scores = []
        
        for c in real_courses:
            for req in active_reqs:
                if req == "humanities-limit":
                    continue # Ignore dummy bounds
                
                # Weight core/pathways heavily to pull real courses here first
                if req in ["intermediate", "pathways", "capstone"]:
                    weight = 10
                # Give electives a lower weight so they become the dump-stat for Unknowns
                elif req == "upper-level":
                    weight = 2
                elif req in ["additional", "intro"]:
                    weight = 1
                else:
                    weight = 1
                    
                # If a real course is used for this requirement, it adds the weight to the score
                optimization_scores.append(If(self.assignment_vars[c][req], weight, 0))

        if optimization_scores:
            # Tell Z3 to maximize the total weight across the course plan
            self.s.maximize(Sum(*([0] + optimization_scores)))

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
            
            # Print everything EXCEPT pathways as a standard list
            if req != "pathways":
                self.__my_print(f"{req}: {used_courses}")

        # --- Structured Pathways Printing ---
        if "pathways" in active_reqs:
            self.__my_print("pathways:")
            pathway_requirements = self.reader.get_pathways()
            
            for pathway in pathway_requirements:
                p_name = pathway["Pathway"]
                
                # Check if this specific pathway was activated by Z3
                is_active = is_true(m.evaluate(Bool(f"pathway_{p_name}_active")))
                
                if is_active:
                    self.__my_print(f"  - {p_name}:")
                    
                    # Find the exactly 2 courses assigned to THIS pathway
                    assigned_courses = []
                    for c in self.courses:
                        if is_true(m.evaluate(Bool(f"use_{c}_for_pathway_{p_name}"))):
                            assigned_courses.append(c)
                            
                    # Separate into Core and Additional
                    core_set = set(pathway["Core Courses"])
                    cores_used = [c for c in assigned_courses if c in core_set]
                    
                    # The first core course satisfies the "Core" slot
                    core_course = cores_used[0] if cores_used else "None"
                    
                    # The remaining course (which could be a 2nd core, grad, or related) is the additional
                    additional_courses = [c for c in assigned_courses if c != core_course]
                    additional_course = additional_courses[0] if additional_courses else "None"

                    if core_course == "None" and len(additional_courses) == 2:
                        core_course = additional_courses[1]
                    
                    self.__my_print(f"      Core: {core_course}")
                    self.__my_print(f"      Additional: {additional_course}")
                    
                    # Find which transcript courses Z3 used for the intermediate prerequisites
                    intermediates_used = []
                    for idx, req_group in enumerate(pathway["Intermediate Courses"]):
                        for c in self.courses:

                            # if the course plan included the course already, we did it statically
                            # so we can't use Z3 variables for this
                            if c in req_group:
                                intermediates_used.append(c)
                                break
                            
                            # The course was an unknown
                            # Reconstruct the string name of the Z3 variable
                            var_intermed = Bool(f"use_{c}_for_pathway_{p_name}_intermed_{idx}")
                            
                            # Ask the model if this course was chosen
                            if is_true(m.evaluate(var_intermed)):
                                intermediates_used.append(c)
                                break
                                
                    self.__my_print(f"      Intermediates fulfilling prerequisites: {intermediates_used}")

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

    def __build_intermediate_unknown_identities(self):
        """Creates a restricted Z3 boolean matrix assigning a specific or 'OTHER' identity to each Unknown."""
        
        # 1. Set of intermediate courses
        all_intermediates = self.reader.get_flat_intermediates()

        # 2. Setup the identity mapping
        self.unknown_identities = {} # dictionary for mapping unknowns to course identities
        unknown_courses = [c for c in self.courses if c.startswith("Unknown")]
        real_taken_courses = [c for c in self.courses if not c.startswith("Unknown")]

        for u in unknown_courses:
            self.unknown_identities[u] = {}
            
            # Add variables for the specific catalog courses
            for inter in all_intermediates:
                var = Bool(f"identity_{u}_is_{inter}")
                self.unknown_identities[u][inter] = var
                
                # Rule A: Cannot be a course the student already took
                if inter in real_taken_courses:
                    self.s.add(Not(var))

            # WILDCARD (we don't care about tracking other courses)
            # This represents any course in the universe NOT in our catalog
            var_other = Bool(f"identity_{u}_is_OTHER")
            self.unknown_identities[u]["OTHER"] = var_other

            # Rule B: Every Unknown must resolve to EXACTLY ONE identity (including OTHER)
            all_identities = list(self.unknown_identities[u].values())
            self.s.add(Sum([If(var, 1, 0) for var in all_identities]) == 1)

        # Rule C: Unknowns cannot duplicate SPECIFIC courses 
        # (But multiple Unknowns CAN be "OTHER"!)
        for inter in all_intermediates:
            self.s.add(Sum([If(self.unknown_identities[u][inter], 1, 0) for u in unknown_courses]) <= 1)

    def __try_with_unknowns(self, degree_type: str, num_unknowns: int, limit_of_unknowns: int = 6):
        if num_unknowns > limit_of_unknowns - 1:
            self.__my_print("Too many unknowns to build a degree!")
            return (False, num_unknowns)
        
        count = num_unknowns + 1
        self.courses.append(f"Unknown {count}")
        self.__my_print(f"trying with {count} inserted unknown class(es)")
        is_sat = self.validate(degree_type, num_unknowns + 1, limit_of_unknowns)
        self.__my_print(is_sat)

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

            # 2. Check the specific Pathway sub-matrix
            if "pathways" in active_reqs:
                for pathway in pathway_requirements:
                    p_name = pathway["Pathway"]
                    
                    # Gather the booleans for ALL unknowns in THIS pathway (Core/Additional)
                    unknowns_in_this_pathway = [
                        If(Bool(f"use_{c}_for_pathway_{p_name}"), 1, 0) for c in unknown_courses
                    ]
                    
                    sum_expr = Sum(*([0] + unknowns_in_this_pathway))
                    actual_count = m.evaluate(sum_expr)
                    
                    current_distribution_equations.append(sum_expr == actual_count)
                    
                    if actual_count.as_long() > 0:
                        self.__my_print(f"  -> {actual_count} Unknown(s) specifically in the '{p_name}' pathway")

                    intermediates_statically_met = True
                    for req in pathway["Intermediate Courses"]:
                        if not any(c in self.courses for c in req):
                            intermediates_statically_met = False
                            break

                    # Track Unknowns used for pathway intermediates
                    if not intermediates_statically_met:
                        for idx, req_group in enumerate(pathway["Intermediate Courses"]):
                            # if statically met, skip
                            if any(c in req_group for c in self.courses):
                                continue

                            unknowns_in_this_intermed = [
                                If(Bool(f"use_{c}_for_pathway_{p_name}_intermed_{idx}"), 1, 0) for c in unknown_courses
                            ]
                            sum_expr_int = Sum(*([0] + unknowns_in_this_intermed))
                            actual_count_int = m.evaluate(sum_expr_int)
                            
                            # Enforce this count for the blocker signature
                            current_distribution_equations.append(sum_expr_int == actual_count_int)
                            
                            if actual_count_int.as_long() > 0:
                                self.__my_print(f"  -> {actual_count_int} Unknown(s) specifically in '{p_name}' intermediate prereq {idx+1}")
                
            self.__print_results()

            # 3. Block this specific numerical distribution and loop again
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
        # we are ignoring the existence of 112 for this model
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

    def __oldIntermediateConstraint(self, degree_type: str) -> BoolRef:
        intermediate_requirements = self.reader.get_intermediate()
        all_intermediates = self.reader.get_flat_intermediates()

        valid_intermediate_courses = set()
        all_slot_sums = []
        category_active_vars = []

        # 1. Parse JSON and build logical slots
        # The categories are Foundations/Math/Systems
        for category_data in intermediate_requirements:
            
            # the courses in these groups cannot be used together (e.g., MATH 520 + 540)
            course_groups = category_data["Courses"] 
            cat_slot_sums = []

            for group in course_groups:
                slot_vars = []
                for course in self.courses:
                    var = self.assignment_vars[course]["intermediate"]
                    
                    if course.startswith("Unknown"):
                        # Does this Unknown's assigned identity exist in this group?
                        is_in_group = Or([
                            self.unknown_identities[course][c] 
                            for c in group if c in all_intermediates
                        ])
                        # If the course is used for intermediate AND its identity matches, it counts!
                        slot_vars.append(If(And(var, is_in_group), 1, 0))
                        
                    elif course in group:
                        valid_intermediate_courses.add(course)
                        slot_vars.append(If(var, 1, 0))

                if slot_vars:
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
            if course not in valid_intermediate_courses and not course.startswith("Unknown"):
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
        all_intermediates = self.reader.get_flat_intermediates()

        pathway_active_vars = []
        
        # 1. THE SUB-MATRIX
        # course_pathway_vars[course][pathway_name] = Bool
        course_pathway_vars = {c: {} for c in self.courses}

        for pathway in pathway_requirements:
            p_name = pathway["Pathway"]
            
            # A boolean representing if the student completed this entire pathway
            p_active = Bool(f"pathway_{p_name}_active")
            pathway_active_vars.append(p_active)

            # do some set unions to know what's in the pathway
            core_set = set(pathway["Core Courses"])
            valid_set = core_set | set(pathway["Graduate Courses"]) | set(pathway["Related Courses"])

            core_conditions = []
            total_conditions = []

            for course in self.courses:
                # Create the specific variable for this course -> this pathway
                var_p = Bool(f"use_{course}_for_pathway_{p_name}")
                course_pathway_vars[course][p_name] = var_p

                if course in valid_set or course.startswith("Unknown"):
                    total_conditions.append(If(var_p, 1, 0))
                    if course in core_set or course.startswith("Unknown"):
                        core_conditions.append(If(var_p, 1, 0))
                else:
                    # Invalid courses cannot be assigned to this pathway
                    self.s.add(Not(var_p))

            # If we can meet intermediate requirements without unknowns, we prefer that
            # because it makes our processing easy and static
            # 2a. STATIC INTERMEDIATE CHECK
            intermediates_met = True
            for req in pathway["Intermediate Courses"]:
                if not any(c in self.courses for c in req):
                    intermediates_met = False
                    break
            pathway_intermed_logic = []
            if not intermediates_met:
                # 2. DYNAMIC INTERMEDIATE CHECK - allow unknown intermediates
                for idx, req_group in enumerate(pathway["Intermediate Courses"]):

                    # we can statically fulfill this requirement, so skip it
                    if any(c in self.courses for c in req_group):
                        # TODO: how does this affect printing?
                        continue

                    group_conditions = []
                    # check if there is an unknown that can fulfill this requirement
                    for course in [c for c in self.courses if c.startswith("Unknown")]:
                        var_intermed = Bool(f"use_{course}_for_pathway_{p_name}_intermed_{idx}")
                        
                        # Does this Unknown's identity match the pathway's requirement?
                        is_in_group = Or([
                            self.unknown_identities[course][c] 
                            for c in req_group if c in all_intermediates
                        ])
                        
                        group_conditions.append(If(var_intermed, 1, 0))
                        
                        # It can ONLY be assigned to this pathway intermed if its identity matches!
                        self.s.add(Implies(var_intermed, is_in_group))
                        
                        # all pathway intermediates are also intermediates in the course plan
                        intermediate_version = self.assignment_vars[course]["intermediate"]
                        self.s.add(Implies(var_intermed, intermediate_version))
                            
                    # We need EXACTLY 1 course to satisfy this prerequisite group
                    group_sum = Sum(*([0] + group_conditions))
                    
                    # Tie it to the pathway's activity so Z3 doesn't assign Unknowns to dead pathways
                    self.s.add(Implies(p_active, group_sum == 1))
                    self.s.add(Implies(Not(p_active), group_sum == 0))
                    
                    pathway_intermed_logic.append(group_sum == 1)

            # 3. PATHWAY COMPLETION LOGIC
            # To activate, we need >= 1 core, EXACTLY 2 total classes, AND all intermediates
            if intermediates_met:
                pathway_valid_logic = And(
                    Sum(*([0] + core_conditions)) >= 1,
                    Sum(*([0] + total_conditions)) == 2
                )
            else:
                pathway_valid_logic = And(
                    Sum(*([0] + core_conditions)) >= 1,
                    Sum(*([0] + total_conditions)) == 2,
                    *pathway_intermed_logic  # Unpack the intermediate Z3 conditions here!
                )
            
            # Link the active boolean to the completion of the logic
            self.s.add(p_active == pathway_valid_logic)

            # CRITICAL: If the pathway is NOT active, force the assigned courses to 0.
            # This stops Z3 from assigning 1 course to a dead pathway and wasting it.
            self.s.add(Implies(Not(p_active), Sum(*([0] + total_conditions)) == 0))

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
            course_num = get_course_number(course)
                
            # 2. Basic Check: Must be a CSCI course >= 1000
            if (course.startswith("CSCI") and course_num >= 1000) or course.startswith("Unknown"):
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
                        # same Z3 boolean variable from pathways constraint!
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
            
            # 1. Get all intermediate courses
            all_intermediates = self.reader.get_flat_intermediates()

            total_assigned_conditions = []
            upper_level_conditions = []

            for course in self.courses:
                var = self.assignment_vars[course]["additional"]

                # 2. Extract course number to check the "1000 or 2000-level" rule
                course_num = get_course_number(course)

                # 3. Define the booleans for our rules
                is_allowed_dept = (
                    course.startswith("CSCI") or 
                    course.startswith("MATH") or 
                    (course in non_cs_courses)
                )
                is_intermediate = course in all_intermediates # TODO: technically we should handle unknowns here
                is_upper_level = course_num >= 1000

                # 4. Categorize valid courses

                # this course cannot be CSCI 1970
                if course.startswith("CSCI 1970"):
                    self.s.add(Not(var))
                    continue

                if (is_allowed_dept and (is_intermediate or is_upper_level)) or course.startswith("Unknown"):
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

                # 1. Universally valid capstones (1970(1) and 1970(2))
                # we assume that students are doing research in something that is capstoneable
                if course in ["CSCI 1970(1)", "CSCI 1970(2)"]:
                    valid_capstones.append(If(var, 1, 0))
                    continue

                # 2. Standard capstones (must be tied to an active pathway)
                if course in capstone_courses or course.startswith("Unknown"):
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
            
            self.s.add(restricted_count <= 1)
