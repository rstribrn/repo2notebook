#!/usr/bin/env python3
"""
Unit tests for binary file detection functionality.
Tests the is_binary_file() function with various file types.
"""

import unittest
import tempfile
from pathlib import Path
import sys
import os

# Add parent directory to path to import repo2notebook
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
import repo2notebook


class TestBinaryDetection(unittest.TestCase):
    """Test binary file detection by extension and content."""

    def setUp(self):
        """Create temporary directory for test files."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_image_extensions(self):
        """Test detection of image file extensions."""
        image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.ico', '.webp']
        for ext in image_extensions:
            test_file = self.temp_path / f"test{ext}"
            test_file.write_bytes(b'\x00\x01\x02\x03')
            self.assertTrue(
                repo2notebook.is_binary_file(test_file),
                f"Failed to detect {ext} as binary"
            )

    def test_archive_extensions(self):
        """Test detection of archive file extensions."""
        archive_extensions = ['.zip', '.tar', '.gz', '.bz2', '.7z', '.rar', '.jar', '.war', '.ear']
        for ext in archive_extensions:
            test_file = self.temp_path / f"archive{ext}"
            test_file.write_bytes(b'\x50\x4B\x03\x04')  # ZIP signature
            self.assertTrue(
                repo2notebook.is_binary_file(test_file),
                f"Failed to detect {ext} as binary"
            )

    def test_executable_extensions(self):
        """Test detection of executable file extensions."""
        executable_extensions = ['.exe', '.dll', '.so', '.dylib', '.bin']
        for ext in executable_extensions:
            test_file = self.temp_path / f"program{ext}"
            test_file.write_bytes(b'\x4D\x5A')  # MZ header
            self.assertTrue(
                repo2notebook.is_binary_file(test_file),
                f"Failed to detect {ext} as binary"
            )

    def test_java_keystore_extensions(self):
        """Test detection of Java keystore file extensions."""
        keystore_extensions = ['.jks', '.keystore', '.truststore', '.p12', '.pfx', '.cer', '.crt', '.der']
        for ext in keystore_extensions:
            test_file = self.temp_path / f"keystore{ext}"
            test_file.write_bytes(b'\xFE\xED\xFE\xED')  # Java keystore signature
            self.assertTrue(
                repo2notebook.is_binary_file(test_file),
                f"Failed to detect {ext} as binary"
            )

    def test_oracle_middleware_extensions(self):
        """Test detection of Oracle Fusion Middleware file extensions."""
        oracle_extensions = ['.fmb', '.fmx', '.mmb', '.mmx', '.pll', '.plx', '.rdf', '.rep', '.rex', '.olb', '.ogd']
        for ext in oracle_extensions:
            test_file = self.temp_path / f"oracle{ext}"
            test_file.write_bytes(b'\x00\x01\x02\x03\x04\x05')
            self.assertTrue(
                repo2notebook.is_binary_file(test_file),
                f"Failed to detect {ext} as binary"
            )

    def test_text_files_not_binary(self):
        """Test that text files are not detected as binary."""
        text_extensions = ['.txt', '.py', '.js', '.java', '.md', '.json', '.xml', '.html']
        for ext in text_extensions:
            test_file = self.temp_path / f"text{ext}"
            test_file.write_text("This is a text file with normal content.")
            self.assertFalse(
                repo2notebook.is_binary_file(test_file),
                f"Incorrectly detected {ext} as binary"
            )

    def test_binary_content_detection(self):
        """Test detection of binary content in files without binary extension."""
        test_file = self.temp_path / "data.txt"
        # Create file with >30% non-text bytes (binary threshold)
        binary_content = b'\x00' * 40 + b'text' * 15  # 40 nulls, 60 text bytes = 40% binary
        test_file.write_bytes(binary_content)
        self.assertTrue(
            repo2notebook.is_binary_file(test_file),
            "Failed to detect binary content in .txt file"
        )

    def test_mostly_text_not_binary(self):
        """Test that files with <30% non-text bytes are not detected as binary."""
        test_file = self.temp_path / "data.txt"
        # Create file with <30% non-text bytes (excluding null bytes which have special handling)
        content = b'text' * 85 + b'\x01\x02\x03' * 5  # 340 text bytes, 15 non-null binary = 4% binary
        test_file.write_bytes(content)
        self.assertFalse(
            repo2notebook.is_binary_file(test_file),
            "Incorrectly detected mostly-text file as binary"
        )

    def test_empty_file_not_binary(self):
        """Test that empty files are not detected as binary."""
        test_file = self.temp_path / "empty.txt"
        test_file.write_text("")
        self.assertFalse(
            repo2notebook.is_binary_file(test_file),
            "Incorrectly detected empty file as binary"
        )


if __name__ == '__main__':
    unittest.main()
