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
        
    def get_json(self, file_name: str) -> Any:
        """
        Get json data by file name.
        
        Args:
            file_name: The JSON file name (without .json)
            
        Returns:
            The loaded data, or None if file doesn't exist
        """
        file_path = self.schedule_dir / f"{file_name}.json"
        return self.__load_json_file(file_path)
    