#!/bin/bash
# Unit test for will_be_excluded() function in repo2notebook-wrapper.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Find repo root (go up from tests/unit/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
WRAPPER_SCRIPT="$REPO_ROOT/repo2notebook-wrapper.sh"

# Change to repo root so paths work correctly
cd "$REPO_ROOT"

# Load constants first (before sourcing wrapper)
if [ -f "$REPO_ROOT/generate_constants.py" ] && command -v python3 &> /dev/null; then
    eval "$(python3 "$REPO_ROOT/generate_constants.py" 2>/dev/null)"
fi

# Now extract and source only the will_be_excluded function
# We need to avoid running the whole script
eval "$(sed -n '/^will_be_excluded()/,/^}/p' "$WRAPPER_SCRIPT")"

# Test helper
assert_excluded() {
    local file="$1"
    local repo_dir="${2:-/test/repo}"
    local description="$3"
    
    TESTS_RUN=$((TESTS_RUN + 1))
    
    if will_be_excluded "$file" "$repo_dir"; then
        echo -e "${GREEN}✓${NC} PASS: $description"
        echo "       File: $file"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}✗${NC} FAIL: $description"
        echo "       File: $file"
        echo -e "${YELLOW}       Expected: EXCLUDED, Got: NOT EXCLUDED${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

assert_not_excluded() {
    local file="$1"
    local repo_dir="${2:-/test/repo}"
    local description="$3"
    
    TESTS_RUN=$((TESTS_RUN + 1))
    
    if ! will_be_excluded "$file" "$repo_dir"; then
        echo -e "${GREEN}✓${NC} PASS: $description"
        echo "       File: $file"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}✗${NC} FAIL: $description"
        echo "       File: $file"
        echo -e "${YELLOW}       Expected: NOT EXCLUDED, Got: EXCLUDED${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Print test header
echo "=========================================="
echo "Testing will_be_excluded() function"
echo "=========================================="
echo

# Test binary extensions
echo "--- Binary Extensions ---"
assert_excluded "/test/repo/file.tgz" "/test/repo" ".tgz files should be excluded"
assert_excluded "/test/repo/install/charts/chart.tgz" "/test/repo" ".tgz in subdirectory should be excluded"
assert_excluded "/test/repo/image.png" "/test/repo" ".png files should be excluded"
assert_excluded "/test/repo/archive.zip" "/test/repo" ".zip files should be excluded"
assert_excluded "/test/repo/data.pyc" "/test/repo" ".pyc files should be excluded"
echo

# Test ignored directories
echo "--- Ignored Directories ---"
assert_excluded "/test/repo/__pycache__/module.pyc" "/test/repo" "Files in __pycache__ should be excluded"
assert_excluded "/test/repo/src/__pycache__/test.pyc" "/test/repo" "Files in nested __pycache__ should be excluded"
assert_excluded "/test/repo/target/classes/Main.class" "/test/repo" "Files in target/ should be excluded"
assert_excluded "/test/repo/main/IsknContainerRoot/target/checkout/file.txt" "/test/repo" "Files in nested target/ should be excluded"
assert_excluded "/test/repo/_repo2notebook/output.md" "/test/repo" "Files in _repo2notebook/ should be excluded"
assert_excluded "/test/repo/.git/config" "/test/repo" "Files in .git/ should be excluded"
assert_excluded "/test/repo/node_modules/package/index.js" "/test/repo" "Files in node_modules/ should be excluded"
assert_excluded "/test/repo/build/output.jar" "/test/repo" "Files in build/ should be excluded"
echo

# Test excluded file names
echo "--- Excluded File Names ---"
assert_excluded "/test/repo/.DS_Store" "/test/repo" ".DS_Store should be excluded"
assert_excluded "/test/repo/subdir/.DS_Store" "/test/repo" ".DS_Store in subdirectory should be excluded"
assert_excluded "/test/repo/.env" "/test/repo" ".env should be excluded"
echo

# Test excluded patterns
echo "--- Excluded Patterns ---"
assert_excluded "/test/repo/package-lock.json" "/test/repo" "package-lock.json should be excluded"
assert_excluded "/test/repo/yarn.lock" "/test/repo" "yarn.lock should be excluded"
assert_excluded "/test/repo/file.log" "/test/repo" "*.log files should be excluded"
assert_excluded "/test/repo/test_something.py" "/test/repo" "test_*.py should be excluded"
assert_excluded "/test/repo/file.min.js" "/test/repo" "*.min.js should be excluded"
echo

# Test files that should NOT be excluded
echo "--- Files That Should NOT Be Excluded ---"
assert_not_excluded "/test/repo/README.md" "/test/repo" "README.md should not be excluded"
assert_not_excluded "/test/repo/src/main.py" "/test/repo" "Python source files should not be excluded"
assert_not_excluded "/test/repo/config.yaml" "/test/repo" "YAML files should not be excluded"
assert_not_excluded "/test/repo/install/script.sh" "/test/repo" "Shell scripts should not be excluded"
assert_not_excluded "/test/repo/docs/guide.md" "/test/repo" "Documentation should not be excluded"
echo

# Test problematic real-world cases
echo "--- Real-World Problem Cases ---"
assert_excluded "/test/repo/install/K8SInstall/ISKNIK8S/ISKNIHelmCharts/charts/iskni/charts/monitoring/charts/kube-prometheus-11.3.10.tgz" "/test/repo" "Deep nested .tgz should be excluded"
assert_excluded "/test/repo/main/IsknContainerRoot/target/checkout/install/file.properties" "/test/repo" "Files in target/checkout should be excluded"
echo

# Print summary
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo "Total tests run:    $TESTS_RUN"
echo -e "Tests passed:       ${GREEN}$TESTS_PASSED${NC}"
if [ $TESTS_FAILED -gt 0 ]; then
    echo -e "Tests failed:       ${RED}$TESTS_FAILED${NC}"
else
    echo -e "Tests failed:       ${GREEN}$TESTS_FAILED${NC}"
fi
echo "=========================================="
echo

if [ $TESTS_FAILED -gt 0 ]; then
    echo -e "${RED}❌ Some tests failed!${NC}"
    exit 1
else
    echo -e "${GREEN}✅ All tests passed!${NC}"
    exit 0
fi
