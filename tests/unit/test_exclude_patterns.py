#!/usr/bin/env python3
"""
Unit tests for exclude pattern functionality.
Tests pattern matching for CLI excludes, default patterns, and .repo2notebookignore.
"""

import unittest
import tempfile
from pathlib import Path
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
import repo2notebook


class TestExcludePatterns(unittest.TestCase):
    """Test exclude pattern matching functionality."""

    def setUp(self):
        """Create temporary directory for test files."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_exact_filename_match(self):
        """Test exclusion of exact filename matches."""
        patterns = ['.env', 'secrets.json', 'config.yml']
        for pattern in patterns:
            test_file = self.temp_path / pattern
            test_file.write_text("content")
            
            files, stats, excluded = repo2notebook.collect_files(
                self.temp_path,
                exclude_patterns=[pattern]
            )
            
            self.assertNotIn(
                test_file,
                files,
                f"Failed to exclude exact match: {pattern}"
            )

    def test_wildcard_pattern(self):
        """Test exclusion using wildcard patterns."""
        # Create test files
        (self.temp_path / "test.log").write_text("log")
        (self.temp_path / "debug.log").write_text("log")
        (self.temp_path / "file.txt").write_text("text")
        
        files, stats, excluded = repo2notebook.collect_files(
            self.temp_path,
            exclude_patterns=["*.log"]
        )
        
        # Check .log files are excluded
        file_names = [f.name for f in files]
        self.assertNotIn("test.log", file_names)
        self.assertNotIn("debug.log", file_names)
        self.assertIn("file.txt", file_names)

    def test_directory_pattern(self):
        """Test exclusion of entire directories."""
        # Create directory structure
        (self.temp_path / "node_modules").mkdir()
        (self.temp_path / "node_modules" / "package.js").write_text("code")
        (self.temp_path / "src").mkdir()
        (self.temp_path / "src" / "app.js").write_text("code")
        
        files, stats, excluded = repo2notebook.collect_files(
            self.temp_path,
            exclude_patterns=["node_modules/"]
        )
        
        file_paths = [str(f.relative_to(self.temp_path)) for f in files]
        self.assertNotIn("node_modules/package.js", file_paths)
        self.assertIn("src/app.js", file_paths)

    def test_recursive_wildcard(self):
        """Test recursive wildcard pattern (**)."""
        # Create nested structure
        (self.temp_path / "src").mkdir()
        (self.temp_path / "src" / "test").mkdir()
        (self.temp_path / "src" / "test.spec.js").write_text("test")
        (self.temp_path / "src" / "test" / "unit.spec.js").write_text("test")
        (self.temp_path / "src" / "app.js").write_text("code")
        
        files, stats, excluded = repo2notebook.collect_files(
            self.temp_path,
            exclude_patterns=["**/*.spec.js"]
        )
        
        file_names = [f.name for f in files]
        self.assertNotIn("test.spec.js", file_names)
        self.assertNotIn("unit.spec.js", file_names)
        self.assertIn("app.js", file_names)

    def test_default_exclude_patterns(self):
        """Test that default exclude patterns work."""
        # Create files matching default patterns
        (self.temp_path / ".git").mkdir()
        (self.temp_path / ".git" / "config").write_text("git")
        (self.temp_path / "node_modules").mkdir()
        (self.temp_path / "node_modules" / "lib.js").write_text("code")
        (self.temp_path / ".env").write_text("SECRET=123")
        (self.temp_path / "app.py").write_text("code")
        
        files, stats, excluded = repo2notebook.collect_files(self.temp_path)
        
        file_paths = [str(f.relative_to(self.temp_path)) for f in files]
        self.assertNotIn(".git/config", file_paths)
        self.assertNotIn("node_modules/lib.js", file_paths)
        self.assertNotIn(".env", file_paths)
        self.assertIn("app.py", file_paths)

    def test_multiple_exclude_patterns(self):
        """Test multiple exclude patterns work together."""
        (self.temp_path / "test.log").write_text("log")
        (self.temp_path / "debug.tmp").write_text("tmp")
        (self.temp_path / "app.py").write_text("code")
        
        files, stats, excluded = repo2notebook.collect_files(
            self.temp_path,
            exclude_patterns=["*.log", "*.tmp"]
        )
        
        file_names = [f.name for f in files]
        self.assertNotIn("test.log", file_names)
        self.assertNotIn("debug.tmp", file_names)
        self.assertIn("app.py", file_names)

    def test_case_sensitive_patterns(self):
        """Test that patterns are case-sensitive."""
        (self.temp_path / "Test.LOG").write_text("log")
        (self.temp_path / "test.log").write_text("log")
        
        files, stats, excluded = repo2notebook.collect_files(
            self.temp_path,
            exclude_patterns=["*.log"]
        )
        
        file_names = [f.name for f in files]
        # Case-sensitive: *.log should not match *.LOG
        self.assertIn("Test.LOG", file_names)
        self.assertNotIn("test.log", file_names)


class TestRepo2NotebookIgnore(unittest.TestCase):
    """Test .repo2notebookignore file functionality."""

    def setUp(self):
        """Create temporary directory for test files."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_parse_ignore_file(self):
        """Test parsing of .repo2notebookignore file."""
        ignore_content = """
# This is a comment
*.log
*.tmp

# Directory pattern
build/
node_modules/

# Empty lines should be ignored

secrets.json
"""
        ignore_file = self.temp_path / ".repo2notebookignore"
        ignore_file.write_text(ignore_content)
        
        patterns = repo2notebook.parse_repo2notebookignore(self.temp_path)
        
        self.assertIn("*.log", patterns)
        self.assertIn("*.tmp", patterns)
        self.assertIn("build/", patterns)
        self.assertIn("node_modules/", patterns)
        self.assertIn("secrets.json", patterns)
        self.assertNotIn("# This is a comment", patterns)
        self.assertNotIn("", patterns)

    def test_ignore_file_takes_precedence(self):
        """Test that .repo2notebookignore patterns are applied."""
        # Create .repo2notebookignore
        ignore_file = self.temp_path / ".repo2notebookignore"
        ignore_file.write_text("custom.txt\n*.custom\n")
        
        # Create test files
        (self.temp_path / "custom.txt").write_text("data")
        (self.temp_path / "test.custom").write_text("data")
        (self.temp_path / "normal.txt").write_text("data")
        
        files, stats, excluded = repo2notebook.collect_files(self.temp_path)
        
        file_names = [f.name for f in files]
        self.assertNotIn("custom.txt", file_names)
        self.assertNotIn("test.custom", file_names)
        self.assertIn("normal.txt", file_names)
        
        # Check exclusion tracking
        excluded_by_ignore = [str(f) for f in excluded.get("repo2notebookignore", [])]
        self.assertTrue(any("custom.txt" in f for f in excluded_by_ignore))

    def test_missing_ignore_file(self):
        """Test behavior when .repo2notebookignore doesn't exist."""
        patterns = repo2notebook.parse_repo2notebookignore(self.temp_path)
        self.assertEqual(patterns, [])


if __name__ == '__main__':
    unittest.main()
