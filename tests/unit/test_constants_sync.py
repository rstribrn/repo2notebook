#!/usr/bin/env python3
"""
Test to ensure that constants.py is complete and synchronized.
"""

import sys
from pathlib import Path

# Add parent directory to path to import constants
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_constants_exist():
    """Check that all expected constants are defined in constants module."""
    import constants

    required = [
        'OUTPUT_DIR',
        'GITHUB_URL',
        'MAX_WORDS_PER_FILE',
        'MAX_FILE_SIZE_MB',
        'MAX_FILE_COUNT',
        'MAX_TOTAL_SIZE_MB',
        'MAX_SINGLE_FILE_MB',
        'DEFAULT_TOKEN_RATIO',
        'ALWAYS_EXCLUDE_DIRS',
        'ALWAYS_EXCLUDE_FILES',
        'ALWAYS_EXCLUDE_PATTERNS',
        'EXT_TO_LANG',
        'BINARY_EXTENSIONS',
        'SENSITIVE_PATTERNS',
        'DEFAULT_EXCLUDE_PATTERNS',
        'DEFAULT_EXCLUDE_FILES',
        'DEFAULT_EXCLUDE_DIRS',
    ]

    missing = [name for name in required if not hasattr(constants, name)]
    assert not missing, f"Missing constants: {', '.join(missing)}"

    # Check types
    assert isinstance(constants.ALWAYS_EXCLUDE_DIRS, (set, list, tuple))
    assert isinstance(constants.ALWAYS_EXCLUDE_FILES, (set, list, tuple))
    assert isinstance(constants.ALWAYS_EXCLUDE_PATTERNS, (list, tuple))
    assert isinstance(constants.EXT_TO_LANG, dict)
    assert isinstance(constants.BINARY_EXTENSIONS, (list, tuple))
    assert isinstance(constants.SENSITIVE_PATTERNS, (list, tuple))
    assert isinstance(constants.DEFAULT_EXCLUDE_PATTERNS, (list, tuple))
    assert isinstance(constants.DEFAULT_EXCLUDE_FILES, (list, tuple))
    assert isinstance(constants.DEFAULT_EXCLUDE_DIRS, (list, tuple))

    # Check that critical values are present and correct
    assert constants.MAX_WORDS_PER_FILE == 400000
    assert constants.MAX_FILE_SIZE_MB == 45
    assert constants.OUTPUT_DIR == "_repo2notebook"
    assert constants.DEFAULT_TOKEN_RATIO == 0.75

    print("All constants are present and have expected types.")

if __name__ == '__main__':
    test_constants_exist()
