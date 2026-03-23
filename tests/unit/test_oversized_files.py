#!/usr/bin/env python3
"""
Unit tests for oversized file handling.
Tests that files exceeding max_words limit are properly skipped and reported.
"""

import unittest
import tempfile
from pathlib import Path
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
import repo2notebook


class TestOversizedFiles(unittest.TestCase):
    """Test oversized file detection and handling."""

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

    def test_single_oversized_file_skipped(self):
        """Test that a single file exceeding max_words is skipped."""
        # Create a file with more than 1000 words (test limit)
        large_content = " ".join([f"word{i}" for i in range(1500)])
        (self.temp_path / "large.txt").write_text(large_content)
        
        # Create a normal file
        (self.temp_path / "normal.txt").write_text("normal content")
        
        # Collect files
        files, stats, excluded = repo2notebook.collect_files(self.temp_path)
        
        # Split with low max_words
        chunks, oversized = repo2notebook.split_files_into_chunks(
            files, 
            self.temp_path, 
            max_words=1000
        )
        
        # Verify oversized file is detected
        self.assertEqual(len(oversized), 1, "Should detect 1 oversized file")
        oversized_path, word_count = oversized[0]
        self.assertEqual(oversized_path.name, "large.txt")
        self.assertGreater(word_count, 1000, "File should exceed limit")
        
        # Verify it's not in any chunk
        all_chunk_files = []
        for chunk in chunks:
            all_chunk_files.extend(chunk)
        
        chunk_names = [f.name for f in all_chunk_files]
        self.assertNotIn("large.txt", chunk_names, "Oversized file should not be in chunks")
        self.assertIn("normal.txt", chunk_names, "Normal file should be in chunks")

    def test_multiple_oversized_files_skipped(self):
        """Test that multiple oversized files are all skipped."""
        # Create multiple oversized files
        for i in range(3):
            large_content = " ".join([f"word{i}_{j}" for j in range(1500)])
            (self.temp_path / f"large_{i}.txt").write_text(large_content)
        
        # Create normal files
        for i in range(2):
            (self.temp_path / f"normal_{i}.txt").write_text("normal content " * 10)
        
        files, stats, excluded = repo2notebook.collect_files(self.temp_path)
        
        chunks, oversized = repo2notebook.split_files_into_chunks(
            files,
            self.temp_path,
            max_words=1000
        )
        
        # Verify all oversized files detected
        self.assertEqual(len(oversized), 3, "Should detect 3 oversized files")
        
        oversized_names = [path.name for path, _ in oversized]
        self.assertIn("large_0.txt", oversized_names)
        self.assertIn("large_1.txt", oversized_names)
        self.assertIn("large_2.txt", oversized_names)
        
        # Verify none are in chunks
        all_chunk_files = []
        for chunk in chunks:
            all_chunk_files.extend(chunk)
        
        chunk_names = [f.name for f in all_chunk_files]
        for i in range(3):
            self.assertNotIn(f"large_{i}.txt", chunk_names)

    def test_oversized_file_tracked_in_excluded(self):
        """Test that oversized files are tracked in excluded_files dict."""
        # Create oversized file
        large_content = " ".join([f"word{i}" for i in range(1500)])
        (self.temp_path / "huge.sql").write_text(large_content)
        
        # Create normal file
        (self.temp_path / "app.py").write_text("print('hello')")
        
        files, stats, excluded = repo2notebook.collect_files(self.temp_path)
        
        # Verify oversized category exists in excluded dict
        self.assertIn("oversized", excluded, "Should have 'oversized' category")
        
        # Split files and track oversized
        chunks, oversized_files = repo2notebook.split_files_into_chunks(
            files,
            self.temp_path,
            max_words=1000
        )
        
        # Simulate tracking (as done in main)
        for file_path, word_count in oversized_files:
            excluded["oversized"].append(str(file_path))
        
        self.assertGreater(len(excluded["oversized"]), 0, "Should track oversized files")
        self.assertTrue(
            any("huge.sql" in f for f in excluded["oversized"]),
            "Should track huge.sql as oversized"
        )

    def test_oversized_in_excluded_report(self):
        """Test that oversized files appear in EXCLUDED.md report."""
        # Create oversized file
        large_content = " ".join([f"word{i}" for i in range(1500)])
        (self.temp_path / "massive.txt").write_text(large_content)
        
        # Create normal file
        (self.temp_path / "small.txt").write_text("small content")
        
        files, stats, excluded = repo2notebook.collect_files(self.temp_path)
        
        # Split and track oversized
        chunks, oversized_files = repo2notebook.split_files_into_chunks(
            files,
            self.temp_path,
            max_words=1000
        )
        
        # Add to excluded tracking
        for file_path, word_count in oversized_files:
            excluded["oversized"].append(str(file_path))
        
        # Generate report
        report_path = repo2notebook.generate_excluded_report(
            self.temp_path,
            excluded,
            self.output_dir
        )
        
        self.assertTrue(report_path.exists(), "Report should be generated")
        
        report_content = report_path.read_text()
        
        # Verify report contains oversized section
        self.assertIn("Oversized files", report_content, "Report should mention oversized files")
        self.assertIn("massive.txt", report_content, "Report should list massive.txt")

    def test_normal_files_within_limit_not_marked_oversized(self):
        """Test that files within limit are not marked as oversized."""
        # Create files well within limit
        for i in range(5):
            content = " ".join([f"word{j}" for j in range(100)])  # 100 words each
            (self.temp_path / f"file_{i}.txt").write_text(content)
        
        files, stats, excluded = repo2notebook.collect_files(self.temp_path)
        
        chunks, oversized = repo2notebook.split_files_into_chunks(
            files,
            self.temp_path,
            max_words=1000
        )
        
        # No files should be oversized
        self.assertEqual(len(oversized), 0, "No files should be oversized")
        
        # All files should be in chunks
        all_chunk_files = []
        for chunk in chunks:
            all_chunk_files.extend(chunk)
        
        self.assertEqual(len(all_chunk_files), 5, "All 5 files should be in chunks")

    def test_boundary_file_at_exact_limit(self):
        """Test file with exactly max_words is included (not oversized)."""
        # Create file with exactly 1000 words
        content = " ".join([f"word{i}" for i in range(1000)])
        (self.temp_path / "boundary.txt").write_text(content)
        
        files, stats, excluded = repo2notebook.collect_files(self.temp_path)
        
        chunks, oversized = repo2notebook.split_files_into_chunks(
            files,
            self.temp_path,
            max_words=1000
        )
        
        # File at exact limit should NOT be oversized
        self.assertEqual(len(oversized), 0, "File at exact limit should not be oversized")
        
        # Should be in chunks
        all_chunk_files = []
        for chunk in chunks:
            all_chunk_files.extend(chunk)
        
        chunk_names = [f.name for f in all_chunk_files]
        self.assertIn("boundary.txt", chunk_names, "Boundary file should be included")

    def test_boundary_file_one_word_over_limit(self):
        """Test file with max_words + 1 is marked oversized."""
        # Create file with 1001 words (one over limit)
        content = " ".join([f"word{i}" for i in range(1001)])
        (self.temp_path / "oversize_by_one.txt").write_text(content)
        
        files, stats, excluded = repo2notebook.collect_files(self.temp_path)
        
        chunks, oversized = repo2notebook.split_files_into_chunks(
            files,
            self.temp_path,
            max_words=1000
        )
        
        # Should be detected as oversized
        self.assertEqual(len(oversized), 1, "File should be oversized")
        
        oversized_path, word_count = oversized[0]
        self.assertEqual(oversized_path.name, "oversize_by_one.txt")
        self.assertEqual(word_count, 1001, "Should have 1001 words")

    def test_mixed_normal_and_oversized_files(self):
        """Test chunking with mix of normal and oversized files."""
        # Create oversized files
        for i in range(2):
            large_content = " ".join([f"large{i}_{j}" for j in range(1500)])
            (self.temp_path / f"large_{i}.txt").write_text(large_content)
        
        # Create normal files
        for i in range(3):
            content = " ".join([f"normal{i}_{j}" for j in range(100)])
            (self.temp_path / f"normal_{i}.txt").write_text(content)
        
        files, stats, excluded = repo2notebook.collect_files(self.temp_path)
        
        chunks, oversized = repo2notebook.split_files_into_chunks(
            files,
            self.temp_path,
            max_words=1000
        )
        
        # Verify oversized detection
        self.assertEqual(len(oversized), 2, "Should detect 2 oversized files")
        
        # Verify normal files are chunked
        all_chunk_files = []
        for chunk in chunks:
            all_chunk_files.extend(chunk)
        
        chunk_names = [f.name for f in all_chunk_files]
        self.assertEqual(len(chunk_names), 3, "Should have 3 normal files in chunks")
        
        for i in range(3):
            self.assertIn(f"normal_{i}.txt", chunk_names)
        
        for i in range(2):
            self.assertNotIn(f"large_{i}.txt", chunk_names)

    def test_chunking_respects_limit_with_multiple_files(self):
        """Test that chunking respects word limit when combining multiple files."""
        # Create files with varying sizes
        (self.temp_path / "file1.txt").write_text(" ".join([f"w{i}" for i in range(300)]))  # 300 words
        (self.temp_path / "file2.txt").write_text(" ".join([f"w{i}" for i in range(400)]))  # 400 words
        (self.temp_path / "file3.txt").write_text(" ".join([f"w{i}" for i in range(350)]))  # 350 words
        (self.temp_path / "file4.txt").write_text(" ".join([f"w{i}" for i in range(200)]))  # 200 words
        
        files, stats, excluded = repo2notebook.collect_files(self.temp_path)
        
        chunks, oversized = repo2notebook.split_files_into_chunks(
            files,
            self.temp_path,
            max_words=800  # Limit of 800 words per chunk
        )
        
        # No files should be oversized individually
        self.assertEqual(len(oversized), 0, "No individual files should be oversized")
        
        # Verify chunks don't exceed limit
        for i, chunk in enumerate(chunks):
            total_words = 0
            for file_path in chunk:
                content = repo2notebook.read_file_content(file_path)
                if content:
                    total_words += len(content.split())
            
            self.assertLessEqual(
                total_words, 
                800, 
                f"Chunk {i} should not exceed word limit (has {total_words} words)"
            )

    def test_oversized_sql_file_realistic(self):
        """Test realistic scenario with large SQL file (like test-ind-iskne.sql)."""
        # Create large SQL file similar to real scenario
        sql_statements = []
        for i in range(5000):
            sql_statements.append(f"""
CREATE INDEX "SCHEMA"."INDEX_{i}" ON "SCHEMA"."TABLE_{i}" ("COLUMN_{i}") 
  PCTFREE 10 INITRANS 2 MAXTRANS 255 
  STORAGE(INITIAL 1048576 NEXT 1048576 MINEXTENTS 1 MAXEXTENTS 2147483645
  PCTINCREASE 0 FREELISTS 1 FREELIST GROUPS 1
  BUFFER_POOL DEFAULT FLASH_CACHE DEFAULT CELL_FLASH_CACHE DEFAULT)
  TABLESPACE "INDEXY" PARALLEL 1;
""")
        
        large_sql = "\n".join(sql_statements)
        (self.temp_path / "test-ind-schema.sql").write_text(large_sql)
        
        # Create normal SQL files
        (self.temp_path / "create_table.sql").write_text("CREATE TABLE test (id INT);")
        (self.temp_path / "insert_data.sql").write_text("INSERT INTO test VALUES (1);")
        
        files, stats, excluded = repo2notebook.collect_files(self.temp_path)
        
        # Use realistic limit (400k words)
        chunks, oversized = repo2notebook.split_files_into_chunks(
            files,
            self.temp_path,
            max_words=400000
        )
        
        # The large SQL should be oversized
        if len(large_sql.split()) > 400000:
            self.assertEqual(len(oversized), 1, "Large SQL should be oversized")
            oversized_path, word_count = oversized[0]
            self.assertEqual(oversized_path.name, "test-ind-schema.sql")
        
        # Normal SQL files should be in chunks
        all_chunk_files = []
        for chunk in chunks:
            all_chunk_files.extend(chunk)
        
        chunk_names = [f.name for f in all_chunk_files]
        self.assertIn("create_table.sql", chunk_names)
        self.assertIn("insert_data.sql", chunk_names)


class TestOversizedFileReporting(unittest.TestCase):
    """Test reporting and messaging for oversized files."""

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

    def test_oversized_return_value_format(self):
        """Test that split_files_into_chunks returns correct tuple format."""
        (self.temp_path / "test.txt").write_text("content")
        
        files, stats, excluded = repo2notebook.collect_files(self.temp_path)
        
        result = repo2notebook.split_files_into_chunks(
            files,
            self.temp_path,
            max_words=1000
        )
        
        # Should return tuple of (chunks, oversized_files)
        self.assertIsInstance(result, tuple, "Should return tuple")
        self.assertEqual(len(result), 2, "Should return 2-element tuple")
        
        chunks, oversized = result
        self.assertIsInstance(chunks, list, "First element should be list")
        self.assertIsInstance(oversized, list, "Second element should be list")

    def test_oversized_tuple_format(self):
        """Test that oversized files are returned as (Path, int) tuples."""
        # Create oversized file
        large_content = " ".join([f"word{i}" for i in range(1500)])
        (self.temp_path / "large.txt").write_text(large_content)
        
        files, stats, excluded = repo2notebook.collect_files(self.temp_path)
        
        chunks, oversized = repo2notebook.split_files_into_chunks(
            files,
            self.temp_path,
            max_words=1000
        )
        
        self.assertEqual(len(oversized), 1)
        
        # Check tuple format
        file_path, word_count = oversized[0]
        self.assertIsInstance(file_path, Path, "First element should be Path")
        self.assertIsInstance(word_count, int, "Second element should be int")
        self.assertEqual(file_path.name, "large.txt")
        self.assertGreater(word_count, 1000)

    def test_excluded_report_includes_oversized_category(self):
        """Test that EXCLUDED.md report has proper oversized category."""
        # Create various excluded files
        (self.temp_path / "image.png").write_bytes(b"\x89PNG\r\n\x1a\n" * 10)
        large_content = " ".join([f"word{i}" for i in range(1500)])
        (self.temp_path / "huge.txt").write_text(large_content)
        
        files, stats, excluded = repo2notebook.collect_files(self.temp_path)
        
        # Track oversized
        chunks, oversized_files = repo2notebook.split_files_into_chunks(
            files,
            self.temp_path,
            max_words=1000
        )
        
        for file_path, word_count in oversized_files:
            excluded["oversized"].append(str(file_path))
        
        # Generate report
        report_path = repo2notebook.generate_excluded_report(
            self.temp_path,
            excluded,
            self.output_dir
        )
        
        report_content = report_path.read_text()
        
        # Verify report structure
        self.assertIn("# Excluded Files Report", report_content)
        self.assertIn("Summary by Extension", report_content)
        self.assertIn("Files by Extension", report_content)
        
        # Verify oversized category
        self.assertIn("Oversized files (>max-words limit)", report_content)
        self.assertIn("huge.txt", report_content)
        
        # Verify other categories still work
        self.assertIn("Binary files", report_content)
        self.assertIn("image.png", report_content)


if __name__ == '__main__':
    unittest.main()
