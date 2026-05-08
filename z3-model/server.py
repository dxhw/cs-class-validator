import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from copy import deepcopy

# Import validator classes and utilities
from util.json_reader import JSONReader
from util.schedule_fetcher import ScheduleFetcher
from old_validator import OldCS
from new_validator import NewCS
from cs_econ_new_validator import NewCSEcon
from apma_cs_new_validator import NewAPMACS
from math_cs_new_validator import NewMATHCS
from comp_bio_new_validator import NewCompBio

# Initialize JSON reader
reader = JSONReader()
schedule_fetcher = ScheduleFetcher()

# Pydantic models for request/response
class ValidateRequest(BaseModel):
    """Request model for degree validation"""
    year: int
    degree_type: str  # "AB" or "SCB"
    degree: str = "CS"  # "CS", "CompBio", "CS+ECON", "MATH+CS", "APMA+CS"
    requirement_version: str = "New"  # "Old", "New", "Either"
    courses: List[str]  # List of course codes
    capstone_incomplete: bool = False
    old_constraints: Optional[Dict[str, bool]] = None
    new_constraints: Optional[Dict[str, bool]] = None
    max_unknowns: int = 20


class ValidateResponse(BaseModel):
    """Response model for validation results"""
    success: bool
    degree_type: str
    degree: str
    requirement_version: str
    old_result: Optional[Dict[str, Any]] = None
    new_result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# Default constraint dictionaries
DEFAULT_CONSTRAINTS = {
    "CS": {
        "Old": {
            "intro": True,
            "intermediate": True,
            "pathways": True,
            "upper-level": True,
            "additional": True,
            "capstone": True,
            "humanities-limit": True
        },
        "New": {
            "intro": True,
            "foundations": True,
            "math": True,
            "elective": True,
            "technical": True,
            "capstone": True,
            "humanities-limit": True
        }
    },
    "CompBio": {
        "New": {
            "intro": True,
            "prob-and-stats": True,
            "discrete": True,
            "bio-core": True,
            "chem-core": True,
            "comp-bio-core": True,
            "track": True,
            "elective": True,
            "capstone": True,
        }
    },
    "CS+ECON": {
        "New": {
            "intro": True,
            "foundations": True,
            "prob-and-stats": True,
            "micro-macro-metrics": True,
            "technical": True,
            "math-econ": True,
            "econ-elective": True,
            "capstone": True,
        }
    },
    "MATH+CS": {
        "New": {
            "intro": True,
            "foundations": True,
            "multi": True,
            "linear": True,
            "technical": True,
            "abstract": True,
            "upper-math": True,
            "elective": True,
            "capstone": True,
        }
    },
    "APMA+CS": {
        "New": {
            "intro": True,
            "foundations": True,
            "multi": True,
            "linear": True,
            "technical": True,
            "optimization": True,
            "differential": True,
            "apma-upper-div": True,
            "math-apma-upper-div": True,
            "capstone": True,
        }
    }
}

app = FastAPI(
    title="Brown University CS Concentration Validator",
    description="API for validating Brown University CS Concentration degree plans.",
    version="1.0.0",
)

origins = [
    "http://localhost:3000",  # Common for React
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # List of allowed origins
    allow_credentials=True,           # Allow cookies/authentication headers
    allow_methods=["*"],              # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],              # Allow all request headers
)

@app.get("/degrees")
def get_degrees() -> Dict[str, List[str]]:
    """Get list of available degree programs."""
    return {
        "supported degrees": ["CS", "CompBio", "CS+ECON", "MATH+CS", "APMA+CS"]
    }


@app.get("/degree-types")
def get_degree_types() -> Dict[str, List[str]]:
    """Get list of available degree types."""
    return {
        "degree types": ["AB", "SCB"]
    }


@app.get("/requirement-versions")
def get_requirement_versions() -> Dict[str, List[str]]:
    """Get list of available requirement versions."""
    return {
        "requirement versions": ["Old", "New", "Either"]
    }


@app.get("/constraints/{degree}")
def get_constraints(degree: str) -> Dict[str, Any]:
    """
    Get default constraints for a specific degree and requirement version.
    Returns the constraints that can be customized via the validate endpoint.
    """
    if degree not in DEFAULT_CONSTRAINTS:
        raise HTTPException(status_code=400, detail=f"Unknown degree: {degree}")
    
    return DEFAULT_CONSTRAINTS[degree]


@app.get("/constraints/{degree}/{requirement_version}")
def get_constraints_by_version(degree: str, requirement_version: str) -> Dict[str, bool]:
    """
    Get constraints for a specific degree and requirement version.
    Each constraint can be set to true or false to enable/disable that requirement.
    
    Example:
        GET /constraints/CS/New
        Returns: {"intro": true, "foundations": true, "math": true, ...}
        
    You can then pass custom constraints in the validate endpoint:
        POST /validate
        {"constraints": {"intro": true, "foundations": false, ...}}
    """
    if degree not in DEFAULT_CONSTRAINTS:
        raise HTTPException(status_code=400, detail=f"Unknown degree: {degree}")
    
    if requirement_version not in DEFAULT_CONSTRAINTS[degree]:
        raise HTTPException(
            status_code=400,
            detail=f"requirement_version '{requirement_version}' not available for degree '{degree}'"
        )
    
    return DEFAULT_CONSTRAINTS[degree][requirement_version]


@app.get("/docs/constraints")
def constraints_documentation() -> Dict[str, Any]:
    """
    Documentation on how to use custom constraints with the validation API.
    """
    return {
        "title": "Custom Constraints Usage",
        "description": "You can customize which requirements apply to your degree validation by passing a 'constraints' object in your validate request.",
        "usage_examples": {
            "example_1": {
                "description": "Validate CS degree with intro requirement disabled",
                "request": {
                    "year": 2026,
                    "degree_type": "AB",
                    "degree": "CS",
                    "requirement_version": "New",
                    "courses": ["CSCI0150", "CSCI0190"],
                    "constraints": {
                        "intro": False
                    }
                },
                "note": "Constraints you don't specify will use their default values (all True by default)"
            },
            "example_2": {
                "description": "Validate with multiple constraints disabled",
                "request": {
                    "year": 2026,
                    "degree_type": "SCB",
                    "degree": "CS",
                    "requirement_version": "New",
                    "courses": ["CSCI0150", "CSCI0190"],
                    "constraints": {
                        "intro": False,
                        "foundations": False,
                        "capstone": True
                    }
                }
            }
        },
        "available_constraints": DEFAULT_CONSTRAINTS,
        "endpoints": {
            "get_all_constraints": "GET /constraints/{degree}",
            "get_constraints_by_version": "GET /constraints/{degree}/{requirement_version}",
            "validate_with_custom_constraints": "POST /validate (include 'constraints' field)"
        }
    }


def _get_constraints_for_degree(degree: str, requirement_version: str, custom_constraints: Optional[tuple[Optional[Dict[str, bool]], Optional[Dict[str, bool]]]] = None) -> tuple[Optional[Dict[str, bool]], Optional[Dict[str, bool]]]:
    """
    Get constraints for a degree, optionally merged with custom constraints.
    
    Args:
        degree: The degree program
        requirement_version: "Old", "New", or "Either"
        custom_constraints: Optional custom constraints to override defaults
    
    Returns:
        Tuple of (old_constraints, new_constraints) - either may be None if not applicable
    """
    old_constraints = None
    new_constraints = None
    
    if degree == "CS":
        if requirement_version in ["Old", "Either"]:
            old_constraints = DEFAULT_CONSTRAINTS["CS"]["Old"].copy()
            if custom_constraints and custom_constraints[1]:
                for k, v in custom_constraints[1].items():
                    if k in old_constraints:
                        old_constraints[k] = v
        
        if requirement_version in ["New", "Either"]:
            new_constraints = DEFAULT_CONSTRAINTS["CS"]["New"].copy()
            if custom_constraints and custom_constraints[0]:
                for k, v in custom_constraints[0].items():
                    if k in new_constraints:
                        new_constraints[k] = v
    
    elif degree == "CompBio":
        if requirement_version in ["New", "Either"]:
            new_constraints = DEFAULT_CONSTRAINTS["CompBio"]["New"].copy()
            if custom_constraints and custom_constraints[0]:
                new_constraints.update(custom_constraints[0])
    
    elif degree == "CS+ECON":
        if requirement_version in ["New", "Either"]:
            new_constraints = DEFAULT_CONSTRAINTS["CS+ECON"]["New"].copy()
            if custom_constraints and custom_constraints[0]:
                new_constraints.update(custom_constraints[0])
    
    elif degree == "MATH+CS":
        if requirement_version in ["New", "Either"]:
            new_constraints = DEFAULT_CONSTRAINTS["MATH+CS"]["New"].copy()
            if custom_constraints and custom_constraints[0]:
                new_constraints.update(custom_constraints[0])
    
    elif degree == "APMA+CS":
        if requirement_version in ["New", "Either"]:
            new_constraints = DEFAULT_CONSTRAINTS["APMA+CS"]["New"].copy()
            if custom_constraints and custom_constraints[0]:
                new_constraints.update(custom_constraints[0])
    
    return old_constraints, new_constraints


@app.post("/validate")
def validate_degree(request: ValidateRequest) -> ValidateResponse:
    """
    Validate a course plan against degree requirements.
    
    Args:
        request: ValidateRequest with year, degree_type, degree, requirement_version, courses, constraints, etc.
    
    Returns:
        ValidateResponse with validation results
    
    Example request with custom constraints:
    {
        "year": 2026,
        "degree_type": "AB",
        "degree": "CS",
        "requirement_version": "New",
        "courses": ["CSCI0150", "CSCI0190", ...],
        "constraints": {
            "intro": true,
            "foundations": false,
            "capstone": true
        }
    }
    """
    try:
        # Validate input parameters
        if request.degree_type not in ["AB", "SCB"]:
            raise HTTPException(status_code=400, detail="degree_type must be 'AB' or 'SCB'")
        
        if request.requirement_version not in ["Old", "New", "Either"]:
            raise HTTPException(status_code=400, detail="requirement_version must be 'Old', 'New', or 'Either'")
        
        if request.degree not in DEFAULT_CONSTRAINTS:
            raise HTTPException(status_code=400, detail=f"Unknown degree: {request.degree}")
        
        if not request.courses:
            raise HTTPException(status_code=400, detail="courses list cannot be empty")
        
        response = ValidateResponse(
            success=False,
            degree_type=request.degree_type,
            degree=request.degree,
            requirement_version=request.requirement_version
        )
        
        # Get constraints (with custom overrides if provided)
        old_constraints, new_constraints = _get_constraints_for_degree(
            request.degree,
            request.requirement_version,
            (request.new_constraints, request.old_constraints)
        )
        
        # Create solvers based on requirement_version and degree
        old_solver = None
        new_solver = None

        request.courses = schedule_fetcher.fix_1970_courses(request.courses)
        
        try:
            if request.degree == "CS":
                if old_constraints is not None:
                    old_solver = OldCS(
                        request.year,
                        deepcopy(request.courses),
                        reader,
                        old_constraints,
                        request.capstone_incomplete,
                        printing=False
                    )
                
                if new_constraints is not None:
                    new_solver = NewCS(
                        request.year,
                        deepcopy(request.courses),
                        reader,
                        new_constraints,
                        request.capstone_incomplete,
                        printing=False
                    )
            
            elif request.degree == "CompBio":
                if new_constraints is not None:
                    new_solver = NewCompBio(
                        request.year,
                        request.courses,
                        reader,
                        new_constraints,
                        request.capstone_incomplete,
                        printing=False
                    )
            
            elif request.degree == "CS+ECON":
                if new_constraints is not None:
                    new_solver = NewCSEcon(
                        request.year,
                        request.courses,
                        reader,
                        new_constraints,
                        request.capstone_incomplete,
                        printing=False
                    )
            
            elif request.degree == "MATH+CS":
                if new_constraints is not None:
                    new_solver = NewMATHCS(
                        request.year,
                        request.courses,
                        reader,
                        new_constraints,
                        request.capstone_incomplete,
                        printing=False
                    )
            
            elif request.degree == "APMA+CS":
                if new_constraints is not None:
                    new_solver = NewAPMACS(
                        request.year,
                        request.courses,
                        reader,
                        new_constraints,
                        request.capstone_incomplete,
                        printing=False
                    )
        
        except Exception as e:
            response.error = f"Failed to initialize validator: {str(e)}"
            return response
        
        # Run validation
        try:
            if old_solver:
                old_result = old_solver.validate_with_results(request.degree_type, limit_of_unknowns=request.max_unknowns)
                response.old_result = {
                    "valid": old_result[0][0],
                    "unknowns": old_result[0][1],
                    "results_dict": old_result[1]
                }
            
            if new_solver:
                new_result = new_solver.validate_with_results(request.degree_type, limit_of_unknowns=request.max_unknowns)
                response.new_result = {
                    "valid": new_result[0][0],
                    "unknowns": new_result[0][1],
                    "results_dict": new_result[1]
                }
            
            # Overall success if any solver says valid
            response.success = (
                (response.old_result != None and response.old_result["valid"]) or
                (response.new_result != None and response.new_result["valid"])
            )
        
        except Exception as e:
            response.error = f"Validation failed: {str(e)}"
            return response
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("server:app", host=host, port=port, reload=True)