"""
Utility functions for the Traffic License Plate Detector
"""

import os
from pathlib import Path
import yaml
from typing import Dict, Any


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from YAML file
    
    Args:
        config_path (str): Path to the configuration file
        
    Returns:
        Dict[str, Any]: Configuration dictionary
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        return config
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML configuration: {e}")


def ensure_directory_exists(directory_path: str) -> None:
    """
    Ensure that a directory exists, create it if it doesn't
    
    Args:
        directory_path (str): Path to the directory
    """
    os.makedirs(directory_path, exist_ok=True)


def get_project_root() -> Path:
    """
    Return the absolute path to the project root directory.

    The project root is considered to be two levels up from this file:
    .../project_root/src/utils.py -> project_root
    """
    return Path(__file__).resolve().parent.parent


def resolve_path(path_str: str) -> str:
    """
    Resolve a potentially relative path string to an absolute path based on the project root.

    Args:
        path_str (str): The input path (relative or absolute)

    Returns:
        str: Absolute path string
    """
    if not path_str:
        return path_str

    path = Path(path_str)
    if path.is_absolute():
        return str(path)

    root = get_project_root()
    return str((root / path).resolve())


def validate_roi_coordinates(x1: int, y1: int, x2: int, y2: int) -> bool:
    """
    Validate ROI coordinates
    
    Args:
        x1, y1, x2, y2 (int): ROI coordinates
        
    Returns:
        bool: True if coordinates are valid
    """
    return x1 < x2 and y1 < y2 and x1 >= 0 and y1 >= 0


def format_confidence(confidence: float) -> str:
    """
    Format confidence score for display
    
    Args:
        confidence (float): Confidence score
        
    Returns:
        str: Formatted confidence string
    """
    return f"{confidence:.2f}"
