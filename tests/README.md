# Regression Testing

This directory contains the regression test suite for repo2notebook.

## Test Organization

### Unit Tests (`tests/unit/`)
Tests for individual features in isolation:

- **`test_binary_detection.py`** - Binary file detection
  - Image extensions (.png, .jpg, .gif, etc.)
  - Archive extensions (.zip, .tar, .gz, etc.)
  - Executable extensions (.exe, .dll, .so, etc.)
  - Java keystores (.jks, .p12, .pfx, etc.)
  - Oracle Fusion Middleware (.fmb, .rdf, .pll, etc.)
  - Content-based detection (>30% non-text bytes)
  - Text file validation

- **`test_exclude_patterns.py`** - Exclusion pattern matching
  - Exact filename matches
  - Wildcard patterns (`*.log`)
  - Directory patterns (`node_modules/`)
  - Recursive wildcards (`**/*.spec.js`)
  - Default exclude patterns
  - Multiple pattern combinations
  - Case sensitivity

- **`test_excluded_report.py`** - EXCLUDED.md report generation
  - Report file creation
  - Organization by file extension
  - Exclusion reason display
  - Alphabetical sorting
  - Summary statistics
  - Empty exclusions handling
  - Files without extensions

### Integration Tests (`tests/integration/`)
Tests for complex feature combinations:

- **`test_complex_scenarios.py`** - Real-world scenarios
  - **Multiple exclusion methods** - All 4 exclusion tiers working together:
    - `.repo2notebookignore` (highest priority)
    - Custom CLI excludes
    - Default patterns
    - `.gitignore`
    - Binary detection
  
  - **Large repository processing** - Complex project with:
    - Multiple file types
    - Nested directories
    - Binary files
    - Sensitive files
    - Build artifacts
    - EXCLUDED.md report generation
  
  - **Enterprise Java project** - Real-world Java setup:
    - Source code inclusion
    - Java keystores exclusion
    - Oracle Forms/Reports exclusion
    - Build artifacts exclusion
    - Configuration files handling
  
  - **Wrapper script integration** - Bash wrapper testing
  
  - **Stress test** - 100+ files of mixed types

## Running Tests

### Run All Tests
```bash
cd tests
./run_tests.sh
```

### Run Specific Test Suite
```bash
# Unit tests only
python3 -m unittest discover -s tests/unit -p "test_*.py" -v

# Integration tests only
python3 -m unittest discover -s tests/integration -p "test_*.py" -v
```

### Run Individual Test File
```bash
# Binary detection tests
python3 tests/unit/test_binary_detection.py

# Exclude pattern tests
python3 tests/unit/test_exclude_patterns.py

# Excluded report tests
python3 tests/unit/test_excluded_report.py

# Complex scenario tests
python3 tests/integration/test_complex_scenarios.py
```

### Run Specific Test Case
```bash
# Run single test method
python3 -m unittest tests.unit.test_binary_detection.TestBinaryDetection.test_image_extensions

# Run single test class
python3 -m unittest tests.unit.test_binary_detection.TestBinaryDetection
```

## Test Coverage

### Unit Tests Coverage
- ✅ Binary file detection (70+ types)
- ✅ Java keystores detection
- ✅ Oracle Fusion Middleware detection
- ✅ Exclude pattern matching
- ✅ Wildcard patterns
- ✅ Directory patterns
- ✅ .repo2notebookignore parsing
- ✅ EXCLUDED.md generation
- ✅ Report organization
- ✅ Statistics tracking

### Integration Tests Coverage
- ✅ All exclusion methods together
- ✅ Priority handling (.repo2notebookignore > custom > default > .gitignore)
- ✅ Large repository processing
- ✅ Report generation with complex exclusions
- ✅ Enterprise Java projects
- ✅ Stress testing (100+ files)
- ✅ Wrapper script integration

## Requirements

- Python 3.7+
- No external dependencies (uses standard library only)

## Test Structure

Each test file follows this pattern:
1. **setUp()** - Create temporary test environment
2. **Test methods** - Individual test cases
3. **Assertions** - Verify expected behavior
4. **tearDown()** - Clean up temporary files

## Adding New Tests

When adding new features:
1. Add unit tests to `tests/unit/` for the specific feature
2. Add integration tests to `tests/integration/` for feature combinations
3. Update this README with test descriptions
4. Run full test suite to ensure no regressions

## Test Output

The test runner provides:
- Colored output (green = pass, red = fail)
- Verbose test names
- Failure details with tracebacks
- Summary statistics

Example output:
```
═══════════════════════════════════════════════════════
  repo2notebook Regression Test Suite
═══════════════════════════════════════════════════════

Checking Python version...
Python 3.11.0

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Running Unit tests...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
test_image_extensions ... ok
test_java_keystore_extensions ... ok
...
✓ Unit tests PASSED

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Running Integration tests...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
test_multiple_exclusion_methods_together ... ok
test_enterprise_java_project ... ok
...
✓ Integration tests PASSED

═══════════════════════════════════════════════════════
  Test Summary
═══════════════════════════════════════════════════════
✓ Unit tests: PASSED
✓ Integration tests: PASSED

════════════════════════════════════════════════════
  ALL TESTS PASSED ✓
════════════════════════════════════════════════════
```

## Continuous Integration

To integrate with CI/CD:
```bash
# In CI script
cd /path/to/repo2notebook
./tests/run_tests.sh || exit 1
```

## Test Fixtures

The `tests/fixtures/` directory can be used for:
- Sample repositories
- Test configuration files
- Expected output examples
- Binary test files

Currently, fixtures are created dynamically in tests using `tempfile` for isolation.
