import os
import sys
from pathlib import Path

def get_resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller
    """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    
    possible_paths = [
        Path(base_path) / relative_path,  
        Path.cwd() / relative_path,  
        Path.cwd() / "resources" / relative_path,  
        Path(__file__).parent.parent.parent / "resources" / relative_path, 
    ]
    
    for path in possible_paths:
        if path.exists():
            return str(path)
    
    raise FileNotFoundError(f"Resource not found: {relative_path}")
