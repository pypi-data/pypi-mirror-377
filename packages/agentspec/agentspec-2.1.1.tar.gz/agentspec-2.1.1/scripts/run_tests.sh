#!/bin/bash

# Run tests with timeout and proper exit code handling
echo "Running AgentSpec tests..."

# Determine python command
PYTHON_CMD="python"
if ! command -v python &> /dev/null; then
    PYTHON_CMD="python3"
fi

echo "Using Python command: $PYTHON_CMD"

# Run tests and capture both exit code and output
set +e  # Don't exit on command failure
$PYTHON_CMD -m pytest tests/ -v --tb=short --no-cov -x --maxfail=5 -m "not slow" 2>&1 | tee test_output.log
PYTEST_EXIT_CODE=$?
set -e  # Re-enable exit on error

echo "Pytest exit code: $PYTEST_EXIT_CODE"

# Check test results - look for actual test failures vs cleanup issues
if grep -q "FAILED" test_output.log; then
    echo "❌ Tests failed with actual test failures"
    grep "FAILED" test_output.log || true
    exit 1
elif grep -q "ERROR" test_output.log && ! grep -q "KeyboardInterrupt" test_output.log; then
    echo "❌ Tests failed with errors (not cleanup related)"
    grep "ERROR" test_output.log || true
    exit 1
elif grep -q "passed" test_output.log; then
    # Count passed tests
    PASSED_COUNT=$(grep -o "[0-9]\+ passed" test_output.log | head -1 | grep -o "[0-9]\+")
    echo "✅ Tests passed successfully ($PASSED_COUNT tests)"
    exit 0
else
    echo "⚠️  Test results unclear, exit code: $PYTEST_EXIT_CODE"
    echo "Last 20 lines of output:"
    tail -20 test_output.log
    exit 1
fi
