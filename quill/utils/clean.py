"""
Utilities for cleaning output directories.
"""

import os
import shutil
from pathlib import Path
from typing import List, Tuple


def clean_directory(directory: Path) -> Tuple[int, List[str]]:
    """
    Clean a single output directory by removing all JSON and HTML files.

    Args:
        directory: Path to the output directory to clean

    Returns:
        Tuple of (number of files removed, list of file paths)
    """
    if not directory.exists() or not directory.is_dir():
        return 0, []

    files_removed = []

    # Remove all JSON and HTML files in the directory
    for file_path in directory.glob("*.json"):
        file_path.unlink()
        files_removed.append(str(file_path))

    for file_path in directory.glob("*.html"):
        file_path.unlink()
        files_removed.append(str(file_path))

    return len(files_removed), files_removed


def clean_all_runs(runs_dir: Path) -> Tuple[int, List[str]]:
    """
    Clean all run directories under the specified runs directory.

    Args:
        runs_dir: Path to the runs directory

    Returns:
        Tuple of (number of files removed, list of file paths)
    """
    if not runs_dir.exists() or not runs_dir.is_dir():
        return 0, []

    total_removed = 0
    all_files_removed = []

    # Clean each subdirectory in the runs directory
    for subdir in runs_dir.iterdir():
        if subdir.is_dir():
            count, files = clean_directory(subdir)
            total_removed += count
            all_files_removed.extend(files)

    return total_removed, all_files_removed
