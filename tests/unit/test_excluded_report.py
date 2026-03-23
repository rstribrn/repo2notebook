#!/usr/bin/env python3
"""
Unit tests for EXCLUDED.md report generation.
Tests the generate_excluded_report() function.
"""

import unittest
import tempfile
from pathlib import Path
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
import repo2notebook


class TestExcludedReport(unittest.TestCase):
    """Test EXCLUDED.md report generation."""

    def setUp(self):
        """Create temporary directory for test files."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        self.output_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)
        shutil.rmtree(self.output_dir)

    def test_report_generation(self):
        """Test basic report generation."""
        excluded_files = {
            "binary": [
                self.temp_path / "image.png",
                self.temp_path / "archive.zip"
            ],
            "default_patterns": [
                self.temp_path / ".env",
                self.temp_path / "node_modules" / "lib.js"
            ],
            "repo2notebookignore": [
                self.temp_path / "custom.txt"
            ],
            "custom": [],
            "gitignore": [],
            "non_text": []
        }
        
        report_path = repo2notebook.generate_excluded_report(
            self.temp_path,
            excluded_files,
            self.output_dir
        )
        
        self.assertTrue(report_path.exists(), "Report file not created")
        self.assertEqual(report_path.name, "EXCLUDED.md")
        
        content = report_path.read_text()
        self.assertIn("# Excluded Files Report", content)
        self.assertIn("image.png", content)
        self.assertIn("archive.zip", content)
        self.assertIn(".env", content)
        self.assertIn("custom.txt", content)

    def test_report_organization_by_extension(self):
        """Test that report organizes files by extension."""
        excluded_files = {
            "binary": [
                self.temp_path / "file1.png",
                self.temp_path / "file2.jpg",
                self.temp_path / "file3.png"
            ],
            "default_patterns": [],
            "repo2notebookignore": [],
            "custom": [],
            "gitignore": [],
            "non_text": []
        }
        
        report_path = repo2notebook.generate_excluded_report(
            self.temp_path,
            excluded_files,
            self.output_dir
        )
        
        content = report_path.read_text()
        
        # Check for extension sections (using ### format)
        self.assertIn("### .jpg", content)
        self.assertIn("### .png", content)
        
        # Check PNG files are grouped together
        png_section = content.split("### .png")[1].split("###")[0]
        self.assertIn("file1.png", png_section)
        self.assertIn("file3.png", png_section)

    def test_report_shows_exclusion_reason(self):
        """Test that report shows reason for exclusion."""
        excluded_files = {
            "binary": [self.temp_path / "image.png"],
            "default_patterns": [self.temp_path / ".env"],
            "repo2notebookignore": [self.temp_path / "custom.txt"],
            "custom": [self.temp_path / "excluded.log"],
            "gitignore": [self.temp_path / "build" / "out.js"],
            "non_text": []
        }
        
        report_path = repo2notebook.generate_excluded_report(
            self.temp_path,
            excluded_files,
            self.output_dir
        )
        
        content = report_path.read_text()
        
        # Check format matches actual output
        self.assertIn("Binary files", content)
        self.assertIn(".gitignore", content)
        self.assertIn("Custom patterns", content)
        self.assertIn(".repo2notebookignore", content)
        self.assertIn("Default patterns", content)

    def test_report_alphabetical_sorting(self):
        """Test that files within extension groups are sorted alphabetically."""
        excluded_files = {
            "binary": [
                self.temp_path / "zebra.png",
                self.temp_path / "apple.png",
                self.temp_path / "monkey.png"
            ],
            "default_patterns": [],
            "repo2notebookignore": [],
            "custom": [],
            "gitignore": [],
            "non_text": []
        }
        
        report_path = repo2notebook.generate_excluded_report(
            self.temp_path,
            excluded_files,
            self.output_dir
        )
        
        content = report_path.read_text()
        png_section = content.split("### .png")[1].split("###")[0]
        
        # Find positions in the content
        apple_pos = png_section.find("apple.png")
        monkey_pos = png_section.find("monkey.png")
        zebra_pos = png_section.find("zebra.png")
        
        self.assertTrue(apple_pos < monkey_pos < zebra_pos,
                       "Files not sorted alphabetically")

    def test_report_statistics(self):
        """Test that report includes summary statistics."""
        excluded_files = {
            "binary": [self.temp_path / "image.png"],
            "default_patterns": [self.temp_path / ".env"],
            "repo2notebookignore": [self.temp_path / "custom.txt"],
            "custom": [],
            "gitignore": [],
            "non_text": []
        }
        
        report_path = repo2notebook.generate_excluded_report(
            self.temp_path,
            excluded_files,
            self.output_dir
        )
        
        content = report_path.read_text()
        
        self.assertIn("Total excluded:", content)
        self.assertIn("3", content)  # Total count

    def test_empty_exclusions(self):
        """Test report generation when no files are excluded."""
        excluded_files = {
            "binary": [],
            "default_patterns": [],
            "repo2notebookignore": [],
            "custom": [],
            "gitignore": [],
            "non_text": []
        }
        
        report_path = repo2notebook.generate_excluded_report(
            self.temp_path,
            excluded_files,
            self.output_dir
        )
        
        # Should return None when no files excluded
        self.assertIsNone(report_path, "Should return None when no files are excluded")

    def test_files_without_extension(self):
        """Test handling of files without extensions."""
        excluded_files = {
            "binary": [self.temp_path / "Makefile"],
            "default_patterns": [self.temp_path / "LICENSE"],
            "repo2notebookignore": [],
            "custom": [],
            "gitignore": [],
            "non_text": []
        }
        
        report_path = repo2notebook.generate_excluded_report(
            self.temp_path,
            excluded_files,
            self.output_dir
        )
        
        content = report_path.read_text()
        
        # Files without extensions should be grouped together
        self.assertIn("(no extension)", content)
        self.assertIn("Makefile", content)
        self.assertIn("LICENSE", content)


if __name__ == '__main__':
    unittest.main()
