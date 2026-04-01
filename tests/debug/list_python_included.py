#!/usr/bin/env python3
"""
Extract list of included files from Python repo2notebook.py
Saves to /tmp/python_included_files.txt
"""

import sys
from pathlib import Path
import fnmatch

# Add repo root to path
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))

from constants import (
    ALWAYS_EXCLUDE_DIRS,
    ALWAYS_EXCLUDE_FILES,
    ALWAYS_EXCLUDE_PATTERNS,
    BINARY_EXTENSIONS,
)

def should_exclude_dir(dir_name: str) -> bool:
    """Check if directory should be excluded."""
    return dir_name in ALWAYS_EXCLUDE_DIRS

def should_exclude_file(file_name: str) -> bool:
    """Check if file should be excluded based on name/pattern."""
    # Exact match
    if file_name in ALWAYS_EXCLUDE_FILES:
        return True
    
    # Pattern match
    for pattern in ALWAYS_EXCLUDE_PATTERNS:
        if fnmatch.fnmatch(file_name, pattern):
            return True
    
    return False

def is_binary_file(file_path: Path) -> bool:
    """Check if file is binary."""
    ext = file_path.suffix.lower()
    if ext in BINARY_EXTENSIONS:
        return True
    return False

def scan_repository(repo_dir: Path):
    """Scan repository and return included files."""
    included_files = []
    
    for root, dirs, files in repo_dir.walk():
        # Filter directories
        dirs[:] = [d for d in dirs if not should_exclude_dir(d)]
        
        rel_root = root.relative_to(repo_dir)
        
        for filename in files:
            # Check exclusions
            if should_exclude_file(filename):
                continue
            
            file_path = root / filename
            
            if is_binary_file(file_path):
                continue
            
            rel_path = rel_root / filename if str(rel_root) != "." else Path(filename)
            included_files.append(str(rel_path))
    
    return sorted(included_files)

if __name__ == "__main__":
    repo_dir = Path("/home/rstribrn/NESS_Projects/CZ_ISKN-2023_2026/Work/GIT_ISKN/iskn-container-support")
    
    print(f"Scanning: {repo_dir}")
    included = scan_repository(repo_dir)
    
    output_file = Path("/tmp/python_included_files.txt")
    with open(output_file, "w") as f:
        for file in included:
            f.write(f"{file}\n")
    
    print(f"Found {len(included)} included files")
    print(f"Saved to: {output_file}")
