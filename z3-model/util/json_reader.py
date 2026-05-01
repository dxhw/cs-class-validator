"""
JSON Reader Module

This module provides utilities to read and parse all JSON data files from the data directory
and convert them into Python data structures. Data is cached in-memory to prevent repeated I/O operations.
"""

import json
from typing import Any, Dict, List, Optional
from pathlib import Path

# Module-level cache for the convenience function
_GLOBAL_DATA_CACHE = {}

class JSONReader:
    """
    A class to read and manage all JSON data files from the data directory.
    Provides convenient access to course data, pathways, and related information.
    Caches data in-memory after the first read.
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize the JSONReader with the data directory path.
        
        Args:
            data_dir: Path to the data directory. If None, assumes it's in ../data
                      relative to this file's location.
        """
        if data_dir is None:
            # Get the directory of this file and go up one level, then into data/
            current_dir = Path(__file__).parent.parent
            self.data_dir = Path(current_dir / "data")
        else:
            self.data_dir = Path(data_dir)
        
        # Validate that data directory exists
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Data directory not found: {self.data_dir}")
        
        # Initialize data storage and caching flags
        self._data = {}
        self._all_loaded = False
        
    def load_all(self, force_reload: bool = False) -> Dict[str, Any]:
        """
        Load all JSON files from the data directory. Uses cached data if already loaded.
        
        Args:
            force_reload: If True, bypasses the cache and forces a re-read from disk.
            
        Returns:
            A dictionary containing all loaded data keyed by file name (without extension).
        """
        if self._all_loaded and not force_reload:
            return self._data
            
        json_files = self.data_dir.glob("*.json")
        
        for json_file in json_files:
            file_key = json_file.stem  # Get filename without extension
            # Only load if we are forcing a reload or if it hasn't been lazy-loaded yet
            if force_reload or file_key not in self._data:
                self._data[file_key] = self._load_json_file(json_file)
        
        self._all_loaded = True
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
    
    def get(self, key: str, force_reload: bool = False) -> Any:
        """
        Get data by key (file name without extension). Features lazy-loading caching.
        
        Args:
            key: The key corresponding to a JSON file name
            force_reload: If True, bypasses the cache and re-reads the specific file.
            
        Returns:
            The loaded data, or None if key doesn't exist
        """
        # Lazy load the specific file if it's not in cache, or if reload is forced
        if force_reload or key not in self._data:
            file_path = self.data_dir / f"{key}.json"
            if file_path.exists():
                self._data[key] = self._load_json_file(file_path)
            else:
                return None
                
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
    
    def get_new_foundations(self) -> List[Dict]:
        """Get new foundations course requirements."""
        return self.get("new_foundations") or []
    
    def get_humanities_courses(self) -> List[str]:
        """Get list of humanities courses."""
        return self.get("humanities") or []
    
    def get_non_cs_courses(self) -> List[str]:
        """Get list of non-CS courses."""
        return self.get("non_cs_courses") or []
    
    def clear_cache(self) -> None:
        """Clear the instance's internal data cache."""
        self._data.clear()
        self._all_loaded = False
    
    def __repr__(self) -> str:
        """Return string representation of loaded data."""
        keys = list(self._data.keys())
        return f"JSONReader(data_dir={self.data_dir}, cached_keys={keys}, all_loaded={self._all_loaded})"


def load_all_data(data_dir: Optional[str] = None, force_reload: bool = False) -> Dict[str, Any]:
    """
    Convenience function to quickly load all JSON data. Uses a global cache to 
    prevent repeated disk reads across multiple function calls.
    
    Args:
        data_dir: Optional path to data directory
        force_reload: If True, bypasses global cache and re-reads from disk
        
    Returns:
        Dictionary containing all loaded data
    """
    global _GLOBAL_DATA_CACHE
    
    # Create a unique cache key based on the directory path
    cache_key = str(Path(data_dir).resolve()) if data_dir else "default_data_dir"
    
    if not force_reload and cache_key in _GLOBAL_DATA_CACHE:
        return _GLOBAL_DATA_CACHE[cache_key]
        
    reader = JSONReader(data_dir)
    _GLOBAL_DATA_CACHE[cache_key] = reader.load_all()
    
    return _GLOBAL_DATA_CACHE[cache_key]


def clear_global_cache() -> None:
    """Clears the module-level global cache."""
    global _GLOBAL_DATA_CACHE
    _GLOBAL_DATA_CACHE.clear()


if __name__ == "__main__":
    # Example usage
    try:
        reader = JSONReader()
        
        # 1. Test Lazy Loading (Hits disk once for 'capstone', then caches)
        print("Testing lazy load...")
        capstone1 = reader.get_capstone_courses()
        print(f"Loaded capstone (from disk): {len(capstone1)} items")
        
        capstone2 = reader.get_capstone_courses()
        print(f"Loaded capstone (from cache): {len(capstone2)} items")
        
        # 2. Test Load All (Skips 'capstone' because it's already cached, loads the rest)
        print("\nLoading all remaining files...")
        data = reader.load_all()
        print(f"Total cached keys: {len(data)}")
        
        # 3. Test Global Cache via convenience function
        print("\nTesting global cache function...")
        all_data_1 = load_all_data()
        print(f"Global cache keys (first call): {len(all_data_1)}")
        all_data_2 = load_all_data() # This call is instant
        print(f"Global cache keys (second call): {len(all_data_2)}")
        
    except Exception as e:
        print(f"Error: {e}")