#!/usr/bin/env python3
"""
Integration tests for complex feature combinations.
Tests multiple features working together in realistic scenarios.
"""

import unittest
import tempfile
from pathlib import Path
import sys
import os
import subprocess

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
import repo2notebook


class TestComplexScenarios(unittest.TestCase):
    """Test complex combinations of multiple features."""

    def setUp(self):
        """Create temporary directory structure for tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        self.output_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)
        shutil.rmtree(self.output_dir)

    def test_multiple_exclusion_methods_together(self):
        """Test all exclusion methods working together with correct priority."""
        # Create directory structure
        (self.temp_path / "src").mkdir()
        (self.temp_path / "build").mkdir()
        (self.temp_path / "docs").mkdir()
        
        # Create .repo2notebookignore (highest priority)
        ignore_file = self.temp_path / ".repo2notebookignore"
        ignore_file.write_text("priority.txt\n*.priority\n")
        
        # Create .gitignore
        gitignore = self.temp_path / ".gitignore"
        gitignore.write_text("build/\n*.tmp\n")
        
        # Create test files
        files_to_create = {
            "priority.txt": "should be excluded by .repo2notebookignore",
            "test.priority": "should be excluded by .repo2notebookignore",
            ".env": "should be excluded by default patterns",
            "src/app.py": "should be included",
            "build/out.js": "should be excluded by .gitignore",
            "test.tmp": "should be excluded by .gitignore",
            "image.png": "should be excluded as binary",
            "keystore.jks": "should be excluded as binary",
            "custom.exclude": "will be excluded by CLI",
            "docs/README.md": "should be included"
        }
        
        for filepath, content in files_to_create.items():
            full_path = self.temp_path / filepath
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
        
        # Write binary content to binary files
        (self.temp_path / "image.png").write_bytes(b"\x89PNG\r\n\x1a\n" * 10)
        (self.temp_path / "keystore.jks").write_bytes(b"\xFE\xED\xFE\xED" * 10)
        
        # Collect files with custom exclude pattern
        files, stats, excluded = repo2notebook.collect_files(
            self.temp_path,
            exclude_patterns=["*.exclude"]
        )
        
        file_names = [f.name for f in files]
        
        # Verify inclusions
        self.assertIn("app.py", file_names, "Source file should be included")
        self.assertIn("README.md", file_names, "Documentation should be included")
        
        # Verify exclusions
        self.assertNotIn("priority.txt", file_names, ".repo2notebookignore failed")
        self.assertNotIn("test.priority", file_names, ".repo2notebookignore pattern failed")
        self.assertNotIn(".env", file_names, "Default pattern failed")
        self.assertNotIn("out.js", file_names, ".gitignore failed")
        self.assertNotIn("test.tmp", file_names, ".gitignore pattern failed")
        self.assertNotIn("image.png", file_names, "Binary detection failed")
        self.assertNotIn("keystore.jks", file_names, "Java keystore detection failed")
        self.assertNotIn("custom.exclude", file_names, "Custom exclude failed")
        
        # Verify exclusion tracking (at least some files in each category)
        self.assertGreater(len(excluded["repo2notebookignore"]), 0, "Should have .repo2notebookignore exclusions")
        self.assertGreater(len(excluded["default_patterns"]), 0, "Should have default pattern exclusions")
        self.assertGreater(len(excluded["binary"]), 0, "Should have binary exclusions")
        self.assertGreater(len(excluded["custom"]), 0, "Should have custom exclusions")

    def test_large_repo_with_report_generation(self):
        """Test processing large repo with multiple file types and report generation."""
        # Create complex directory structure
        directories = ["src", "tests", "docs", "build", "node_modules", ".git"]
        for dir_name in directories:
            (self.temp_path / dir_name).mkdir()
        
        # Create .repo2notebookignore
        ignore_file = self.temp_path / ".repo2notebookignore"
        ignore_file.write_text("internal/\n*.internal\n")
        
        # Create .gitignore
        gitignore = self.temp_path / ".gitignore"
        gitignore.write_text("build/\nnode_modules/\n")
        
        # Create many test files of different types
        test_files = [
            # Source files (should be included)
            ("src/main.py", "print('hello')" * 10),
            ("src/utils.py", "def util(): pass" * 10),
            ("src/config.py", "CONFIG = {}" * 10),
            ("src/validator.py", "def validate(): pass" * 10),  # Avoid test_ prefix (excluded by default)
            
            # Documentation (should be included)
            ("docs/README.md", "# Documentation" * 10),
            ("docs/API.md", "## API" * 10),
            
            # Binary files (should be excluded)
            ("src/logo.png", b"\x89PNG\r\n\x1a\n" * 10),
            ("docs/diagram.jpg", b"\xFF\xD8\xFF" * 10),
            ("build/app.exe", b"MZ" * 10),
            
            # Build artifacts (should be excluded by .gitignore)
            ("build/output.js", "compiled" * 10),
            ("node_modules/lib.js", "library" * 10),
            
            # Git files (should be excluded)
            (".git/config", "git config" * 10),
            (".git/HEAD", "ref: refs/heads/main"),
            
            # Sensitive files (should be excluded)
            (".env", "SECRET=123" * 10),
            ("keystore.p12", b"\x30\x82" * 10),
            
            # Custom ignored (should be excluded)
            ("config.internal", "internal" * 10),
        ]
        
        # Create internal/ directory
        (self.temp_path / "internal").mkdir()
        test_files.append(("internal/data.txt", "internal" * 10))
        
        for filepath, content in test_files:
            full_path = self.temp_path / filepath
            full_path.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(content, bytes):
                full_path.write_bytes(content)
            else:
                full_path.write_text(content)
        
        # Process repository
        files, stats, excluded = repo2notebook.collect_files(self.temp_path)
        
        # Generate report
        report_path = repo2notebook.generate_excluded_report(
            self.temp_path,
            excluded,
            self.output_dir
        )
        
        # Verify included files
        file_names = [f.name for f in files]
        self.assertIn("main.py", file_names)
        self.assertIn("utils.py", file_names)
        self.assertIn("validator.py", file_names)
        self.assertIn("README.md", file_names)
        
        # Verify excluded files
        self.assertNotIn("logo.png", file_names)
        self.assertNotIn("app.exe", file_names)
        self.assertNotIn("output.js", file_names)
        self.assertNotIn(".env", file_names)
        self.assertNotIn("keystore.p12", file_names)
        self.assertNotIn("data.txt", file_names)
        
        # Verify report exists and has content
        self.assertTrue(report_path.exists())
        report_content = report_path.read_text()
        
        self.assertIn("# Excluded Files Report", report_content)
        self.assertIn("logo.png", report_content)
        self.assertIn(".env", report_content)
        self.assertIn("keystore.p12", report_content)
        
        # Verify statistics
        total_excluded = sum(len(files) for files in excluded.values())
        self.assertGreater(total_excluded, 5, "Should have excluded multiple files")

    def test_enterprise_java_project(self):
        """Test processing enterprise Java project with keystores and Oracle files."""
        # Create Java project structure
        (self.temp_path / "src" / "main" / "java").mkdir(parents=True)
        (self.temp_path / "src" / "main" / "resources").mkdir(parents=True)
        (self.temp_path / "target").mkdir()
        (self.temp_path / "config").mkdir()
        
        # Java source files
        (self.temp_path / "src" / "main" / "java" / "App.java").write_text(
            "public class App { public static void main(String[] args) {} }"
        )
        (self.temp_path / "src" / "main" / "java" / "Service.java").write_text(
            "public class Service { public void process() {} }"
        )
        
        # Configuration files
        (self.temp_path / "pom.xml").write_text("<project></project>")
        (self.temp_path / "src" / "main" / "resources" / "application.properties").write_text(
            "server.port=8080"
        )
        
        # Java keystores (should be excluded)
        (self.temp_path / "config" / "keystore.jks").write_bytes(b"\xFE\xED\xFE\xED" * 100)
        (self.temp_path / "config" / "truststore.jks").write_bytes(b"\xFE\xED\xFE\xED" * 100)
        (self.temp_path / "config" / "cert.p12").write_bytes(b"\x30\x82" * 100)
        
        # Oracle Forms files (should be excluded)
        (self.temp_path / "forms").mkdir()
        (self.temp_path / "forms" / "menu.fmb").write_bytes(b"\x00\x01\x02\x03" * 100)
        (self.temp_path / "forms" / "report.rdf").write_bytes(b"\x00\x01\x02\x03" * 100)
        
        # Build artifacts
        (self.temp_path / "target" / "app.jar").write_bytes(b"PK\x03\x04" * 100)
        
        files, stats, excluded = repo2notebook.collect_files(self.temp_path)
        
        file_names = [f.name for f in files]
        
        # Verify Java sources are included
        self.assertIn("App.java", file_names)
        self.assertIn("Service.java", file_names)
        self.assertIn("pom.xml", file_names)
        self.assertIn("application.properties", file_names)
        
        # Verify keystores are excluded
        self.assertNotIn("keystore.jks", file_names)
        self.assertNotIn("truststore.jks", file_names)
        self.assertNotIn("cert.p12", file_names)
        
        # Verify Oracle files are excluded
        self.assertNotIn("menu.fmb", file_names)
        self.assertNotIn("report.rdf", file_names)
        
        # Verify build artifacts are excluded
        self.assertNotIn("app.jar", file_names)
        
        # Generate and verify report
        report_path = repo2notebook.generate_excluded_report(
            self.temp_path,
            excluded,
            self.output_dir
        )
        
        report_content = report_path.read_text()
        self.assertIn("keystore.jks", report_content)
        self.assertIn("Binary files", report_content)

    def test_wrapper_script_integration(self):
        """Test wrapper script execution with various options."""
        # Create simple test repository
        (self.temp_path / "README.md").write_text("# Test Project")
        (self.temp_path / "app.py").write_text("print('hello')")
        (self.temp_path / ".env").write_text("SECRET=123")
        
        # Get wrapper script path
        wrapper_script = Path(__file__).parent.parent.parent / "repo2notebook-wrapper.sh"
        
        if wrapper_script.exists():
            # Test wrapper execution (dry-run or basic check)
            result = subprocess.run(
                [str(wrapper_script), "--help"],
                capture_output=True,
                text=True
            )
            
            self.assertEqual(result.returncode, 0, "Wrapper script should run")
            self.assertIn("Usage:", result.stdout, "Should show help text")
        else:
            self.skipTest("Wrapper script not found")

    def test_stress_test_many_files(self):
        """Stress test with many files of different types."""
        # Create 100+ files
        for i in range(50):
            (self.temp_path / f"source_{i}.py").write_text(f"# File {i}\nprint({i})")
            (self.temp_path / f"data_{i}.json").write_text(f'{{"id": {i}}}')
            (self.temp_path / f"custom_{i}.xyz").write_text(f"Custom {i}")  # Use .xyz for truly custom exclusion
        
        # Add some binary files
        for i in range(10):
            (self.temp_path / f"image_{i}.png").write_bytes(b"\x89PNG\r\n\x1a\n" * 10)
        
        # Collect with custom excludes for .xyz files
        files, stats, excluded = repo2notebook.collect_files(
            self.temp_path,
            exclude_patterns=["*.xyz"]
        )
        
        # Verify counts - should have .py and .json files
        file_names = [f.name for f in files]
        py_count = sum(1 for name in file_names if name.endswith('.py'))
        json_count = sum(1 for name in file_names if name.endswith('.json'))
        
        self.assertEqual(py_count, 50, "Should include all 50 .py files")
        self.assertEqual(json_count, 50, "Should include all 50 .json files")
        
        # Verify .xyz files excluded by custom pattern
        xyz_count = sum(1 for name in file_names if name.endswith('.xyz'))
        self.assertEqual(xyz_count, 0, "Should exclude all .xyz files")
        
        # Verify PNG files excluded as binary
        png_count = sum(1 for name in file_names if name.endswith('.png'))
        self.assertEqual(png_count, 0, "Should exclude all .png files")
        
        # Verify exclusion categories
        self.assertGreater(len(excluded["binary"]), 0, "Should exclude PNG files")
        self.assertGreater(len(excluded["custom"]), 0, "Should exclude .xyz files")


if __name__ == '__main__':
    unittest.main()
