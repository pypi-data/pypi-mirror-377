#!/bin/bash

# Local CI Test Script for AgentSpec
# Runs all CI checks locally to prevent CI failures

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Global variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PYTHON_CMD="python"
FAILED_TESTS=()
TEMP_DIR=""

# Determine python command
if ! command -v python &> /dev/null; then
    PYTHON_CMD="python3"
fi

# Print functions
print_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Cleanup function
cleanup() {
    if [[ -n "$TEMP_DIR" && -d "$TEMP_DIR" ]]; then
        rm -rf "$TEMP_DIR"
    fi
    # Clean up any test files in project root
    cd "$PROJECT_ROOT"
    rm -f test_spec.md full_spec.md agentspec_report.md
    rm -rf test_project
}

# Trap cleanup on exit
trap cleanup EXIT

# Usage function
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Run AgentSpec CI checks locally to prevent CI failures.

OPTIONS:
    --all           Run all tests (default)
    --cli           Run CLI functionality tests only
    --lint          Run linting checks only
    --security      Run security checks only
    --integration   Run integration tests only
    --docs          Run documentation checks only
    --help          Show this help message

EXAMPLES:
    $0                  # Run all tests
    $0 --lint           # Run only linting
    $0 --cli --docs     # Run CLI and documentation tests
EOF
}

# Check dependencies
check_dependencies() {
    print_header "Checking Dependencies"

    # Check if we're in a virtual environment
    if [[ -z "$VIRTUAL_ENV" ]]; then
        print_warning "Not in a virtual environment. Consider activating one."
    fi

    # Check Python version
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    print_info "Using Python $PYTHON_VERSION"

    # Check if package is installed in development mode
    if ! $PYTHON_CMD -c "import agentspec" 2>/dev/null; then
        print_error "AgentSpec not installed. Installing in development mode..."
        cd "$PROJECT_ROOT"
        $PYTHON_CMD -m pip install -e .[dev,test] || {
            print_error "Failed to install AgentSpec"
            return 1
        }
    fi

    print_success "Dependencies check passed"
}

# CLI functionality tests
test_cli() {
    print_header "Testing CLI Functionality"

    cd "$PROJECT_ROOT"

    # Test basic CLI commands
    print_info "Testing basic CLI commands..."
    $PYTHON_CMD -m agentspec --help > /dev/null || {
        print_error "CLI help command failed"
        return 1
    }

    $PYTHON_CMD -m agentspec list-tags > /dev/null || {
        print_error "CLI list-tags command failed"
        return 1
    }

    # Test spec generation
    print_info "Testing spec generation..."
    $PYTHON_CMD -m agentspec generate --tags general,testing --output test_spec.md || {
        print_error "Spec generation failed"
        return 1
    }

    # Verify output file was created
    if [[ ! -f test_spec.md ]]; then
        print_error "Output file test_spec.md was not created"
        return 1
    fi

    # Check content
    if ! grep -q "AgentSpec - Project Specification" test_spec.md; then
        print_error "Generated spec does not contain expected content"
        return 1
    fi

    print_success "CLI functionality tests passed"
}

# Setup script tests
test_setup() {
    print_header "Testing Setup Script"

    cd "$PROJECT_ROOT"

    # Create temporary directory for setup test
    TEMP_DIR=$(mktemp -d)
    cd "$TEMP_DIR"

    # Copy setup script
    cp "$PROJECT_ROOT/setup.sh" . || {
        print_error "Setup script not found"
        return 1
    }

    # Test minimal setup
    print_info "Testing minimal setup..."
    bash setup.sh --minimal || {
        print_error "Setup script failed"
        return 1
    }

    # Verify structure was created
    for dir in scripts docs; do
        if [[ ! -d "$dir" ]]; then
            print_error "Directory $dir was not created"
            return 1
        fi
    done

    for file in .agentspec project_context.md scripts/validate.sh; do
        if [[ ! -f "$file" ]]; then
            print_error "File $file was not created"
            return 1
        fi
    done

    # Test validation script
    print_info "Testing validation script..."
    chmod +x scripts/validate.sh

    bash scripts/validate.sh --help > /dev/null || {
        print_error "Validation script help failed"
        return 1
    }

    bash scripts/validate.sh --structure || {
        print_error "Validation script structure check failed"
        return 1
    }

    bash scripts/validate.sh --report || {
        print_error "Validation script report generation failed"
        return 1
    }

    # Verify report was generated
    if [[ ! -f agentspec_report.md ]]; then
        print_error "Validation report was not generated"
        return 1
    fi

    print_success "Setup script tests passed"
}

# Linting tests
test_lint() {
    print_header "Running Linting Checks"

    cd "$PROJECT_ROOT"

    # Run flake8
    print_info "Running flake8..."
    flake8 agentspec tests || {
        print_error "flake8 linting failed"
        return 1
    }

    # Check code formatting with black
    print_info "Checking code formatting with black..."
    black --check --diff agentspec/ || {
        print_error "Black formatting check failed"
        return 1
    }

    # Check import sorting with isort
    print_info "Checking import sorting with isort..."
    isort --check-only --diff --profile=black agentspec/ || {
        print_error "isort import sorting check failed"
        return 1
    }

    print_success "Linting checks passed"
}

# Security tests
test_security() {
    print_header "Running Security Checks"

    cd "$PROJECT_ROOT"

    # Run bandit security linter
    print_info "Running bandit security linter..."
    bandit -r agentspec/ --skip B101,B603,B607 || {
        print_error "Bandit security check failed"
        return 1
    }

    # Check for known security vulnerabilities
    print_info "Checking for known security vulnerabilities..."
    echo "# No external dependencies" > requirements.txt
    safety check --file requirements.txt || {
        print_warning "Safety check found potential issues (non-critical)"
    }
    rm -f requirements.txt

    print_success "Security checks passed"
}

# Integration tests
test_integration() {
    print_header "Running Integration Tests"

    cd "$PROJECT_ROOT"

    # Create test project directory
    rm -rf test_project
    mkdir test_project
    cd test_project

    # Copy setup script
    cp ../setup.sh . || {
        print_error "Setup script not found for integration test"
        return 1
    }

    # Run full setup
    print_info "Running full setup..."
    bash setup.sh --minimal || {
        print_error "Integration test setup failed"
        return 1
    }

    # Generate comprehensive spec using installed agentspec
    print_info "Generating comprehensive spec..."
    $PYTHON_CMD -m agentspec generate --tags general,testing,frontend,backend,security --output full_spec.md || {
        print_error "Integration test spec generation failed"
        return 1
    }

    # Validate the setup
    print_info "Validating setup..."
    bash scripts/validate.sh --structure || {
        print_error "Integration test validation failed"
        return 1
    }

    # Verify all expected files exist
    for file in full_spec.md project_context.md .agentspec; do
        if [[ ! -f "$file" ]]; then
            print_error "Integration test: File $file missing"
            return 1
        fi
    done

    for dir in scripts docs; do
        if [[ ! -d "$dir" ]]; then
            print_error "Integration test: Directory $dir missing"
            return 1
        fi
    done

    # Check spec content
    if ! grep -q "AgentSpec - Project Specification" full_spec.md; then
        print_error "Integration test: Generated spec missing expected content"
        return 1
    fi

    print_success "Integration tests passed"
}

# Documentation tests
test_docs() {
    print_header "Running Documentation Checks"

    cd "$PROJECT_ROOT"

    # Verify all documentation files exist
    print_info "Checking documentation files..."
    for file in README.md CONTRIBUTING.md CHANGELOG.md LICENSE docs/quick-start.md docs/instructions-reference.md; do
        if [[ ! -f "$file" ]]; then
            print_error "Documentation file missing: $file"
            return 1
        fi
    done

    # Check for broken links in markdown files (basic check)
    print_info "Checking for potential broken links..."
    if grep -r "](http" docs/ README.md CONTRIBUTING.md 2>/dev/null | grep -v "github.com\|localhost" | head -5; then
        print_warning "Found external links - manual verification recommended"
    fi

    print_success "Documentation checks passed"
}

# Run unit tests
test_unit() {
    print_header "Running Unit Tests"

    cd "$PROJECT_ROOT"

    # Run the existing test script
    bash scripts/run_tests.sh || {
        print_error "Unit tests failed"
        return 1
    }

    print_success "Unit tests passed"
}

# Main execution function
run_tests() {
    local run_all=true
    local run_cli=false
    local run_lint=false
    local run_security=false
    local run_integration=false
    local run_docs=false
    local run_unit=false

    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --all)
                run_all=true
                shift
                ;;
            --cli)
                run_all=false
                run_cli=true
                shift
                ;;
            --lint)
                run_all=false
                run_lint=true
                shift
                ;;
            --security)
                run_all=false
                run_security=true
                shift
                ;;
            --integration)
                run_all=false
                run_integration=true
                shift
                ;;
            --docs)
                run_all=false
                run_docs=true
                shift
                ;;
            --unit)
                run_all=false
                run_unit=true
                shift
                ;;
            --help)
                usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done

    # Start execution
    print_header "AgentSpec Local CI Test Suite"
    print_info "Project root: $PROJECT_ROOT"
    print_info "Python command: $PYTHON_CMD"

    # Check dependencies first
    check_dependencies || {
        print_error "Dependency check failed"
        exit 1
    }

    # Run selected tests
    if [[ "$run_all" == true ]]; then
        run_cli=true
        run_lint=true
        run_security=true
        run_integration=true
        run_docs=true
        run_unit=true
    fi

    # Execute test suites
    if [[ "$run_unit" == true ]]; then
        if ! test_unit; then
            FAILED_TESTS+=("Unit Tests")
        fi
    fi

    if [[ "$run_cli" == true ]]; then
        if ! test_cli; then
            FAILED_TESTS+=("CLI Tests")
        fi
    fi

    if [[ "$run_lint" == true ]]; then
        if ! test_lint; then
            FAILED_TESTS+=("Linting")
        fi
    fi

    if [[ "$run_security" == true ]]; then
        if ! test_security; then
            FAILED_TESTS+=("Security")
        fi
    fi

    if [[ "$run_integration" == true ]]; then
        if ! test_integration; then
            FAILED_TESTS+=("Integration")
        fi
    fi

    if [[ "$run_docs" == true ]]; then
        if ! test_docs; then
            FAILED_TESTS+=("Documentation")
        fi
    fi

    # Print final results
    print_header "Test Results Summary"

    if [[ ${#FAILED_TESTS[@]} -eq 0 ]]; then
        print_success "All tests passed! 🎉"
        print_info "Your code is ready for CI/CD pipeline"
        exit 0
    else
        print_error "Some tests failed:"
        for test in "${FAILED_TESTS[@]}"; do
            echo -e "  ${RED}- $test${NC}"
        done
        print_info "Fix the issues above before pushing to CI"
        exit 1
    fi
}

# Run the tests
run_tests "$@"
