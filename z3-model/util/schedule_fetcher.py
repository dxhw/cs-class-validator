import json
from pathlib import Path
from typing import Any, Dict, List, Optional

class ScheduleFetcher():
    """
    A class to read and manage schedules - both artificial ones from the test_schedules directory.
    and real ones.
    """
    
    def __init__(self, schedule_dir: Optional[str] = None):
        """
        Initialize the JSONReader with the data directory path.
        
        Args:
            schedule_dir: Path to the test_schedules directory. If None, assumes it's in ../test_schedules
                      relative to this file's location.
        """
        if schedule_dir is None:
            # Get the directory of this file and go up one level, then into test_schedules/
            current_dir = Path(__file__).parent.parent
            self.schedule_dir = Path(current_dir / "test_schedules")
        else:
            self.schedule_dir = Path(schedule_dir)
        
        # Validate that test schedule directory exists
        if not self.schedule_dir.exists():
            raise FileNotFoundError(f"Schedules directory not found: {self.schedule_dir}")
        
        # Initialize data storage
        self._data = {}

    def __load_json_file(self, file_path: Path) -> Any:
        """
        Load a single JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            The parsed JSON data (dict, list, etc.)
            
        Raises:
            json.JSONDecodeError: If the file contains invalid JSON
        """
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Error parsing JSON file {file_path.name}: {e.msg}",
                e.doc,
                e.pos
            )
        except FileNotFoundError as e:
            raise ValueError(f"Could not find file {file_path.name}") from None

    def __fix_1970_courses(self, courses: list[str]) -> list[str]:
        # A dictionary to track the counts of 1970 courses per department prefix
        prefix_counts = {}

        for i, course in enumerate(courses):
            # Check if the course ends with " 1970"
            if course.endswith(" 1970"):
                # Extract the potential prefix by slicing off the last 5 characters (" 1970")
                prefix = course[:-5]
                
                # Verify the prefix is either 3 or 4 characters long
                # This is just a check to make sure nothing weird happens
                # the prefixes are department codes, which are all 3-4 characters
                if len(prefix) in (3, 4):
                    # Increment the count for this specific prefix
                    prefix_counts[prefix] = prefix_counts.get(prefix, 0) + 1
                    count = prefix_counts[prefix]
                    
                    if count == 1:
                        courses[i] = f"{prefix} 1970(1)"
                    elif count == 2:
                        courses[i] = f"{prefix} 1970(2)"
                    else:
                        courses[i] = "UNUSABLE"
        
        return courses
                
    def get_json(self, file_name: str) -> list[str]:
        """
        Get json data by file name.
        
        Args:
            file_name: The JSON file name (without .json)
            
        Returns:
            The loaded data, or None if file doesn't exist
        """
        intermediate_folder = None
        if file_name.startswith("inc"):
            intermediate_folder = "incomplete_degrees"
        elif file_name.startswith("working"):
            intermediate_folder = "working_degrees"
        elif file_name.startswith("test"):
            pass
        else:
            intermediate_folder = "real_degrees"
        if intermediate_folder == None:
            file_path = self.schedule_dir / f"{file_name}.json"
        else:
            file_path = self.schedule_dir / intermediate_folder / f"{file_name}.json"
        loaded_json: list[str] = self.__load_json_file(file_path)
        return self.__fix_1970_courses(loaded_json)
