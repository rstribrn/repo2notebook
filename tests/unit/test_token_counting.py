#!/usr/bin/env python3
"""
Test token counting integration in generate_markdown.
"""

import tempfile
from pathlib import Path
import re
import sys

# Add parent directory to path to import repo2notebook
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import functions under test
from repo2notebook import generate_markdown

def test_generate_markdown_with_tokens():
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir) / "test_repo"
        repo.mkdir()
        # Create sample files
        (repo / "a.py").write_text("print('hello world')")
        (repo / "README.md").write_text("# Readme\nThis is a test with several words.")
        files = [repo / "a.py", repo / "README.md"]

        # Generate with token counting
        content, word_count, token_count = generate_markdown(
            repo, files, count_tokens=True, token_ratio=0.75
        )

        # Basic checks
        assert word_count > 0, "Word count should be positive"
        assert token_count > 0, "Token count should be positive"
        assert "Total tokens (est):" in content, "Missing token estimate line"
        # Verify token count appears as number
        match = re.search(r"Total tokens \(est\): ([\d,]+)", content)
        assert match, "Token count not formatted correctly"
        reported_tokens = int(match.group(1).replace(',', ''))
        assert reported_tokens == token_count, f"Reported tokens {reported_tokens} != calculated {token_count}"

        print(f"✅ Token counting works: words={word_count}, tokens={token_count}")

def test_generate_markdown_without_tokens():
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir) / "test_repo"
        repo.mkdir()
        (repo / "file.txt").write_text("Simple text file.")
        files = [repo / "file.txt"]

        content, word_count, token_count = generate_markdown(
            repo, files, count_tokens=False
        )

        assert "Total tokens (est):" not in content, "Token line should not appear when count_tokens=False"
        assert token_count == 0, "Token count should be 0 when disabled"
        print("✅ Token counting disabled works.")

if __name__ == '__main__':
    try:
        test_generate_markdown_with_tokens()
        test_generate_markdown_without_tokens()
        print("\nAll token counting tests passed.")
        sys.exit(0)
    except AssertionError as e:
        print(f"Test failed: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
