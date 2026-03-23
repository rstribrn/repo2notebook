#!/usr/bin/env bash
"""
Test runner for repo2notebook regression tests.
Runs unit tests and integration tests with reporting.
"""

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  repo2notebook Regression Test Suite${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
python3 --version || {
    echo -e "${RED}ERROR: Python 3 is required${NC}"
    exit 1
}
echo ""

# Function to run test suite
run_test_suite() {
    local test_type=$1
    local test_path=$2
    
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}Running ${test_type} tests...${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    if python3 -m pytest "${test_path}" -v --tb=short 2>/dev/null; then
        echo -e "${GREEN}✓ ${test_type} tests PASSED${NC}"
        return 0
    elif python3 -m unittest discover -s "${test_path}" -p "test_*.py" -v; then
        echo -e "${GREEN}✓ ${test_type} tests PASSED${NC}"
        return 0
    else
        echo -e "${RED}✗ ${test_type} tests FAILED${NC}"
        return 1
    fi
}

# Change to project root
cd "${PROJECT_ROOT}"

# Track results
UNIT_RESULT=0
INTEGRATION_RESULT=0

# Run unit tests
if [ -d "tests/unit" ]; then
    run_test_suite "Unit" "tests/unit" || UNIT_RESULT=1
else
    echo -e "${YELLOW}Warning: tests/unit directory not found${NC}"
fi

echo ""

# Run integration tests
if [ -d "tests/integration" ]; then
    run_test_suite "Integration" "tests/integration" || INTEGRATION_RESULT=1
else
    echo -e "${YELLOW}Warning: tests/integration directory not found${NC}"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Test Summary${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"

if [ $UNIT_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ Unit tests: PASSED${NC}"
else
    echo -e "${RED}✗ Unit tests: FAILED${NC}"
fi

if [ $INTEGRATION_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ Integration tests: PASSED${NC}"
else
    echo -e "${RED}✗ Integration tests: FAILED${NC}"
fi

echo ""

# Overall result
if [ $UNIT_RESULT -eq 0 ] && [ $INTEGRATION_RESULT -eq 0 ]; then
    echo -e "${GREEN}════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  ALL TESTS PASSED ✓${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════${NC}"
    exit 0
else
    echo -e "${RED}════════════════════════════════════════════════════${NC}"
    echo -e "${RED}  SOME TESTS FAILED ✗${NC}"
    echo -e "${RED}════════════════════════════════════════════════════${NC}"
    exit 1
fi
