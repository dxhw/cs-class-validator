"""
JSON Reader Module

This module provides utilities to read and parse all JSON data files from the data directory
and convert them into Python data structures.
"""

import json
from typing import Any, Dict, List
from pathlib import Path


class JSONReader:
    """
    A class to read and manage all JSON data files from the data directory.
    Provides convenient access to course data, pathways, and related information.
    """
    
    def __init__(self, data_dir: str = None):
        """
        Initialize the JSONReader with the data directory path.
        
        Args:
            data_dir: Path to the data directory. If None, assumes it's in ../data
                      relative to this file's location.
        """
        if data_dir is None:
            # Get the directory of this file and go up one level, then into data/
            current_dir = Path(__file__).parent.parent
            data_dir = current_dir / "data"
        
        self.data_dir = Path(data_dir)
        
        # Validate that data directory exists
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Data directory not found: {self.data_dir}")
        
        # Initialize data storage
        self._data = {}
        
    def load_all(self) -> Dict[str, Any]:
        """
        Load all JSON files from the data directory.
        
        Returns:
            A dictionary containing all loaded data keyed by file name (without extension).
        """
        json_files = self.data_dir.glob("*.json")
        
        for json_file in json_files:
            file_key = json_file.stem  # Get filename without extension
            self._data[file_key] = self._load_json_file(json_file)
        
        return self._data
    
    def _load_json_file(self, file_path: Path) -> Any:
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
    
    def get(self, key: str) -> Any:
        """
        Get data by key (file name without extension).
        
        Args:
            key: The key corresponding to a JSON file name
            
        Returns:
            The loaded data, or None if key doesn't exist
        """
        return self._data.get(key)
    
    def get_pathways(self) -> List[Dict]:
        """Get pathway information."""
        return self.get("pathway_info") or []
    
    def get_capstone_courses(self) -> List[str]:
        """Get list of capstone courses."""
        return self.get("capstone") or []
    
    def get_intermediate(self) -> List[Dict]:
        """Get intermediate course requirements (by category)."""
        return self.get("intermediate") or []
    
    def get_new_intermediate(self) -> List[Dict]:
        """Get new intermediate course requirements."""
        return self.get("new_intermediate") or []
    
    def get_humanities_courses(self) -> List[str]:
        """Get list of humanities courses."""
        return self.get("humanities") or []
    
    def get_non_cs_courses(self) -> List[str]:
        """Get list of non-CS courses."""
        return self.get("non_cs_courses") or []
    
    def __repr__(self) -> str:
        """Return string representation of loaded data."""
        keys = list(self._data.keys())
        return f"JSONReader(data_dir={self.data_dir}, loaded_keys={keys})"


def load_all_data(data_dir: str = None) -> Dict[str, Any]:
    """
    Convenience function to quickly load all JSON data.
    
    Args:
        data_dir: Optional path to data directory
        
    Returns:
        Dictionary containing all loaded data
    """
    reader = JSONReader(data_dir)
    return reader.load_all()


if __name__ == "__main__":
    # Example usage
    try:
        reader = JSONReader()
        data = reader.load_all()
        
        print("Loaded JSON files:")
        for key, value in data.items():
            if isinstance(value, list):
                print(f"  {key}: list with {len(value)} items")
            elif isinstance(value, dict):
                print(f"  {key}: dict with {len(value)} keys")
            else:
                print(f"  {key}: {type(value).__name__}")
        
        print("\n" + "="*50)
        print("Sample data:")
        print("="*50)
        
        # Show sample pathway
        pathways = reader.get_pathways()
        if pathways:
            print(f"\nFirst pathway: {pathways[0].get('Pathway', 'N/A')}")
            print(f"  Core courses: {len(pathways[0].get('Core Courses', []))} courses")
        
        # Show sample capstone courses
        capstone = reader.get_capstone_courses()
        print(f"\nCapstone courses: {len(capstone)} total")
        print(f"  Examples: {capstone[:3]}")
        
        # Show sample humanities courses
        humanities = reader.get_humanities_courses()
        print(f"\nHumanities courses: {len(humanities)} total")
        print(f"  Examples: {humanities[:3]}")
        
        # Show intermediate structure
        intermediate = reader.get_intermediate()
        if intermediate:
            print(f"\nIntermediate categories: {len(intermediate)}")
            for cat in intermediate:
                print(f"  - {cat.get('Category', 'N/A')}: {len(cat.get('Courses', []))} course groups")
        
    except Exception as e:
        print(f"Error: {e}")
