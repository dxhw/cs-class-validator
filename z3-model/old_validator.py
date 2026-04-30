            # intro sequence (2 courses)
            # intermediate (5 courses) - 1 from each category
            # 2 pathways
            # additional 1000+ (not in pathways)
            # three additional courses
            # humanities requirement (4)
            # 1970 repetition requirement
            # capstone (in pathway)

constraints = {
    "intro": True,
    "intermediate": True,
    "pathways": True,
    "upper-level": True,
    "additional": True,
    "humanities-limit": True,
    "1970-repetition": True,
    "capstone": True 
}

#(constraint: str) -> (list[str] -> Z3 thing)
def constraint_func_mapper(constraint: str):
    match (constraints):
        case "intro": ...
        case "intermediate": ...
        case _: 
            raise(RuntimeError("invalid constraint name"))