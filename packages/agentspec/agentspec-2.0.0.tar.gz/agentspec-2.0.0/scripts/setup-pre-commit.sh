#!/bin/bash
# Setup pre-commit hooks for AgentSpec development

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if pre-commit is installed
check_pre_commit() {
    if ! command -v pre-commit &> /dev/null; then
        log_error "pre-commit is not installed. Please install it first:"
        echo "  pip install pre-commit"
        echo "  # or"
        echo "  pip install -e .[dev]"
        exit 1
    fi
    log_success "pre-commit is installed"
}

# Install pre-commit hooks
install_hooks() {
    log_info "Installing pre-commit hooks..."

    if pre-commit install; then
        log_success "Pre-commit hooks installed successfully"
    else
        log_error "Failed to install pre-commit hooks"
        exit 1
    fi
}

# Run pre-commit on all files to test
test_hooks() {
    log_info "Testing pre-commit hooks on all files..."

    if pre-commit run --all-files; then
        log_success "All pre-commit hooks passed"
    else
        log_warning "Some pre-commit hooks failed. This is normal for the first run."
        log_info "The hooks have been installed and will run on future commits."
    fi
}

# Main function
main() {
    echo -e "${BLUE}🔧 Setting up pre-commit hooks for AgentSpec${NC}\n"

    check_pre_commit
    install_hooks
    test_hooks

    echo -e "\n${GREEN}✅ Pre-commit hooks setup completed!${NC}\n"

    echo -e "${BLUE}What happens now:${NC}"
    echo "• Pre-commit hooks will run automatically before each commit"
    echo "• They will check code formatting, linting, and run tests"
    echo "• If any hook fails, the commit will be blocked"
    echo "• You can run hooks manually with: pre-commit run --all-files"
    echo "• To skip hooks (not recommended): git commit --no-verify"

    echo -e "\n${BLUE}Configured hooks:${NC}"
    echo "• Code formatting (black, isort)"
    echo "• Linting (flake8, mypy)"
    echo "• Security checks (bandit)"
    echo "• Test execution (pytest)"
    echo "• AgentSpec validation"
    echo "• File checks (trailing whitespace, large files, etc.)"
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        echo "AgentSpec Pre-commit Setup Script"
        echo ""
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "This script sets up pre-commit hooks for AgentSpec development."
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --test-only    Only test existing hooks, don't install"
        echo ""
        exit 0
        ;;
    --test-only)
        log_info "Testing existing pre-commit hooks..."
        check_pre_commit
        test_hooks
        exit 0
        ;;
    "")
        main
        ;;
    *)
        echo "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac
