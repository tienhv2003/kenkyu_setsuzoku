"""
Utility functions for Step 02 - Edge Detection & Super Resolution
"""

import os
import yaml
from pathlib import Path
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
    Return the absolute path to the step02 project root directory.
    
    Returns:
        Path: Project root path
    """
    # modules/utils.py -> step02_use_edge_detection/
    return Path(__file__).resolve().parent.parent


def resolve_path(path_str: str, base_dir: str = None) -> str:
    """
    Resolve a potentially relative path string to an absolute path.
    
    Args:
        path_str (str): The input path (relative or absolute)
        base_dir (str): Base directory for relative paths (default: project root)
        
    Returns:
        str: Absolute path string
    """
    if not path_str:
        return path_str
    
    path = Path(path_str)
    if path.is_absolute():
        return str(path)
    
    if base_dir:
        base = Path(base_dir)
    else:
        base = get_project_root()
    
    return str((base / path).resolve())


def count_images_in_folder(folder_path: str) -> int:
    """
    Count number of image files in a folder
    
    Args:
        folder_path (str): Path to folder
        
    Returns:
        int: Number of image files
    """
    if not os.path.exists(folder_path):
        return 0
    
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp', '.tif', '.tiff'}
    count = 0
    
    for file in os.listdir(folder_path):
        if os.path.splitext(file.lower())[1] in image_extensions:
            count += 1
    
    return count


def get_image_files(folder_path: str) -> list:
    """
    Get list of image file paths in a folder
    
    Args:
        folder_path (str): Path to folder
        
    Returns:
        list: List of image file paths
    """
    if not os.path.exists(folder_path):
        return []
    
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp', '.tif', '.tiff'}
    image_files = []
    
    for file in os.listdir(folder_path):
        if os.path.splitext(file.lower())[1] in image_extensions:
            image_files.append(os.path.join(folder_path, file))
    
    return sorted(image_files)

