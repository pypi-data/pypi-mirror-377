# Local Development Guide

This guide covers setting up AgentSpec for local development, contributing to the project, and extending AgentSpec with custom instructions and templates.

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- A code editor (VS Code recommended)

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/keyurgolani/AgentSpec.git
cd AgentSpec

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Verify installation
agentspec --version
```

### Development Dependencies

The `[dev]` extra includes:
- `pytest` - Testing framework
- `pytest-cov` - Test coverage
- `black` - Code formatting
- `flake8` - Linting
- `mypy` - Type checking
- `pre-commit` - Git hooks

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=agentspec --cov-report=html

# Run specific test file
pytest tests/test_cli.py

# Run tests with verbose output
pytest -v
```

### Code Quality

```bash
# Format code
black agentspec/ tests/

# Check linting
flake8 agentspec/ tests/

# Type checking
mypy agentspec/

# Run all quality checks
make check-all  # If Makefile exists
```

## Project Structure

```
AgentSpec/
├── agentspec/                  # Main package
│   ├── __init__.py
│   ├── __main__.py            # CLI entry point
│   ├── cli/                   # Command line interface
│   │   ├── main.py           # Main CLI logic
│   │   ├── commands.py       # Command implementations
│   │   └── interactive.py    # Interactive wizard
│   ├── core/                 # Core functionality
│   │   ├── spec_generator.py # Specification generation
│   │   ├── template_manager.py # Template management
│   │   ├── instruction_database.py # Instruction handling
│   │   ├── context_detector.py # Project analysis
│   │   └── ai_integrator.py  # AI best practices
│   ├── data/                 # Data files
│   │   ├── instructions/     # Instruction JSON files
│   │   ├── templates/        # Template JSON files
│   │   └── schemas/          # JSON schemas
│   ├── utils/                # Utility functions
│   └── config/               # Configuration files
├── tests/                    # Test files
├── docs/                     # Documentation
├── examples/                 # Example projects
├── scripts/                  # Development scripts
├── pyproject.toml           # Project configuration
└── README.md
```

## Adding New Instructions

### 1. Create Instruction File

Instructions are stored in `agentspec/data/instructions/` as JSON files organized by category.

Create a new file or add to existing category:

```json
// agentspec/data/instructions/my-category.json
{
  "instructions": {
    "my_new_instruction": {
      "id": "my_new_instruction",
      "version": "1.0.0",
      "tags": ["general", "quality", "my-tag"],
      "content": "Clear, actionable instruction that AI can follow. Be specific about what to do, how to do it, and what success looks like.",
      "conditions": [
        {
          "type": "file_exists",
          "value": "package.json",
          "operator": "exists",
          "weight": 0.8
        }
      ],
      "parameters": {
        "framework": {
          "type": "string",
          "default": "react",
          "options": ["react", "vue", "angular"]
        }
      },
      "dependencies": ["core_workflow"],
      "metadata": {
        "category": "my-category",
        "priority": 7,
        "author": "Your Name",
        "created_at": "2024-12-15T00:00:00Z",
        "updated_at": "2024-12-15T00:00:00Z"
      }
    }
  }
}
```

### 2. Instruction Schema

Each instruction must follow this schema:

- **id**: Unique identifier (snake_case)
- **version**: Semantic version
- **tags**: Array of category tags
- **content**: The actual instruction text
- **conditions**: When this instruction applies (optional)
- **parameters**: Configurable options (optional)
- **dependencies**: Other instructions this depends on (optional)
- **metadata**: Additional information

### 3. Writing Good Instructions

**Be Specific:**
```json
// Bad
"content": "Write good code"

// Good
"content": "Implement comprehensive error handling with try-catch blocks, proper error messages, and graceful degradation. Log errors with appropriate severity levels and provide user-friendly error messages."
```

**Include Examples:**
```json
"content": "Use TypeScript strict mode with proper type definitions. Example: interface User { id: number; name: string; email: string; } Never use 'any' types."
```

**Define Success Criteria:**
```json
"content": "Implement input validation that sanitizes all user input, validates data types, and returns clear error messages. Success criteria: All inputs validated, no XSS vulnerabilities, proper error responses."
```

### 4. Test Your Instructions

```bash
# Test instruction loading
python -c "from agentspec.core.instruction_database import InstructionDatabase; db = InstructionDatabase(); print(len(db.load_instructions()))"

# Test specific instruction
agentspec list-instructions --tag my-tag

# Generate spec with your instruction
agentspec generate --tags my-tag --output test-spec.md
```

## Adding New Templates

### 1. Create Template File

Templates are stored in `agentspec/data/templates/` organized by category:

```json
// agentspec/data/templates/technology/my-framework.json
{
  "id": "my-framework",
  "name": "My Framework Application",
  "description": "Template for applications using My Framework",
  "version": "1.0.0",
  "project_type": "web-app",
  "technology_stack": [
    "my-framework",
    "typescript",
    "javascript"
  ],
  "default_tags": [
    "frontend",
    "my-framework",
    "typescript",
    "testing"
  ],
  "required_instructions": [
    "component_architecture",
    "typescript_configuration",
    "testing_setup"
  ],
  "optional_instructions": [
    "state_management",
    "routing_setup",
    "api_integration"
  ],
  "excluded_instructions": [
    "backend_setup",
    "database_configuration"
  ],
  "parameters": {
    "ui_library": {
      "type": "string",
      "default": "none",
      "description": "UI component library to use",
      "required": false,
      "options": ["none", "material-ui", "ant-design"]
    }
  },
  "conditions": [
    {
      "type": "dependency_exists",
      "value": "my-framework",
      "operator": "exists",
      "weight": 0.9
    }
  ],
  "metadata": {
    "category": "frontend",
    "complexity": "intermediate",
    "author": "Your Name",
    "created_at": "2024-12-15T00:00:00Z",
    "updated_at": "2024-12-15T00:00:00Z",
    "tags": ["frontend", "framework", "modern"]
  }
}
```

### 2. Template Categories

Organize templates into these directories:

- `technology/` - Specific frameworks/languages
- `domain/` - Business domains (e-commerce, fintech, etc.)
- `architecture/` - System architectures (microservices, etc.)
- `methodology/` - Development approaches (AI-assisted, security-focused)

### 3. Test Your Template

```bash
# List templates to verify it's loaded
agentspec list-templates

# Test template generation
agentspec generate --template my-framework --output test-template.md

# Test with project analysis
mkdir test-project
cd test-project
# Create some files that match your template conditions
agentspec analyze . --output analysis.json
```

## Extending Core Functionality

### 1. Adding New CLI Commands

Add commands in `agentspec/cli/commands.py`:

```python
def my_new_command(
    spec_generator: SpecGenerator,
    my_param: str,
    verbose: bool = False,
) -> int:
    """
    My new command description.

    Args:
        spec_generator: SpecGenerator instance
        my_param: Description of parameter
        verbose: Show detailed output

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        # Implementation here
        print(f"Running my command with {my_param}")
        return 0
    except Exception as e:
        logger.error(f"Error in my command: {e}")
        print(f"Error: {e}", file=sys.stderr)
        return 1
```

Add to CLI parser in `agentspec/cli/main.py`:

```python
# In create_parser method
my_parser = subparsers.add_parser(
    "my-command", help="Description of my command"
)
my_parser.add_argument(
    "my_param", help="Description of parameter"
)
my_parser.add_argument(
    "--verbose", action="store_true", help="Verbose output"
)

# In run method
elif parsed_args.command == "my-command":
    return my_new_command(
        self.spec_generator,
        my_param=parsed_args.my_param,
        verbose=parsed_args.verbose,
    )
```

### 2. Adding New Analysis Features

Extend `agentspec/core/context_detector.py`:

```python
def detect_my_technology(self, project_path: Path) -> bool:
    """Detect if project uses my technology."""
    config_file = project_path / "my-config.json"
    return config_file.exists()

def analyze_my_patterns(self, project_path: Path) -> Dict[str, Any]:
    """Analyze project for my specific patterns."""
    patterns = {}
    # Analysis logic here
    return patterns
```

### 3. Adding New Validation Rules

Extend validation in `agentspec/utils/validation.py`:

```python
def validate_my_requirement(spec: GeneratedSpec) -> List[str]:
    """Validate my specific requirement."""
    errors = []

    # Validation logic here
    if not some_condition:
        errors.append("My requirement not met")

    return errors
```

## Testing

### 1. Writing Tests

Create test files in `tests/` directory:

```python
# tests/test_my_feature.py
import pytest
from agentspec.core.my_module import MyClass

def test_my_function():
    """Test my function works correctly."""
    result = my_function("input")
    assert result == "expected_output"

def test_my_function_error():
    """Test my function handles errors."""
    with pytest.raises(ValueError):
        my_function("invalid_input")

@pytest.fixture
def my_fixture():
    """Fixture for testing."""
    return MyClass()

def test_with_fixture(my_fixture):
    """Test using fixture."""
    assert my_fixture.method() == "expected"
```

### 2. Test Categories

Use pytest markers to categorize tests:

```python
@pytest.mark.unit
def test_unit_functionality():
    """Unit test."""
    pass

@pytest.mark.integration
def test_integration():
    """Integration test."""
    pass

@pytest.mark.slow
def test_slow_operation():
    """Slow test."""
    pass
```

Run specific test categories:

```bash
# Run only unit tests
pytest -m unit

# Run all except slow tests
pytest -m "not slow"

# Run integration tests
pytest -m integration
```

### 3. Test Configuration

Configure pytest in `pytest.ini`:

```ini
[tool:pytest]
minversion = 7.0
addopts = -ra -q --strict-markers --cov=agentspec
testpaths = tests
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
```

## Documentation

### 1. Updating Documentation

Documentation is in Markdown format in the `docs/` directory:

- Keep documentation up-to-date with code changes
- Use clear, beginner-friendly language
- Include practical examples
- Test all code examples

### 2. Documentation Structure

```
docs/
├── README.md                 # Documentation index
├── what-is-agentspec.md     # Introduction for beginners
├── quick-start.md           # 5-minute getting started
├── your-first-project.md    # Complete tutorial
├── core-concepts.md         # Deep dive into concepts
├── command-line-guide.md    # CLI reference
├── working-with-templates.md # Template usage guide
├── instructions-reference.md # All instructions
├── templates-reference.md   # All templates
├── api-reference.md         # Python API docs
├── ai-practices.md          # AI collaboration guide
└── local-development.md     # This file
```

### 3. Writing Good Documentation

**Be Beginner-Friendly:**
- Explain concepts before diving into details
- Use simple language
- Include "why" not just "how"

**Include Examples:**
- Show real command examples
- Include expected output
- Provide complete, working examples

**Keep It Current:**
- Update docs when changing code
- Test all examples
- Fix broken links

## Contributing Workflow

### 1. Development Process

```bash
# 1. Create feature branch
git checkout -b feature/my-new-feature

# 2. Make changes
# Edit code, add tests, update docs

# 3. Run quality checks
black agentspec/ tests/
flake8 agentspec/ tests/
mypy agentspec/
pytest

# 4. Commit changes
git add .
git commit -m "Add my new feature"

# 5. Push and create PR
git push origin feature/my-new-feature
# Create pull request on GitHub
```

### 2. Pre-commit Hooks

Set up pre-commit hooks to ensure code quality:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

### 3. Code Review Checklist

Before submitting a PR, ensure:

- [ ] All tests pass
- [ ] Code is formatted with Black
- [ ] No linting errors
- [ ] Type checking passes
- [ ] Documentation is updated
- [ ] Examples are tested
- [ ] Commit messages are clear

## Debugging

### 1. Debug Mode

Enable debug logging:

```bash
# Set environment variable
export AGENTSPEC_LOG_LEVEL=DEBUG

# Or use CLI flag
agentspec --verbose generate --template react_app
```

### 2. Common Issues

**Import Errors:**
```bash
# Ensure package is installed in development mode
pip install -e .
```

**Test Failures:**
```bash
# Run specific test with verbose output
pytest -v tests/test_specific.py::test_function

# Run with debugging
pytest --pdb tests/test_specific.py
```

**Template/Instruction Not Loading:**
```bash
# Check file syntax
python -m json.tool agentspec/data/templates/my-template.json

# Test loading
python -c "from agentspec.core.template_manager import TemplateManager; tm = TemplateManager(); print(tm.load_templates())"
```

## Release Process

### 1. Version Management

Update version in `pyproject.toml` and `agentspec/__init__.py`:

```toml
# pyproject.toml
[project]
version = "2.1.0"
```

```python
# agentspec/__init__.py
__version__ = "2.1.0"
```

### 2. Release Checklist

- [ ] All tests pass
- [ ] Documentation is updated
- [ ] Version numbers are updated
- [ ] CHANGELOG.md is updated
- [ ] Examples are tested
- [ ] Performance is acceptable

### 3. Building and Publishing

```bash
# Build package
python -m build

# Check package
twine check dist/*

# Upload to PyPI (maintainers only)
twine upload dist/*
```

## Getting Help

### 1. Development Questions

- Check existing issues on GitHub
- Look at test files for examples
- Read the source code
- Ask in GitHub Discussions

### 2. Debugging Resources

- Use `pytest --pdb` for interactive debugging
- Add print statements or logging
- Use VS Code debugger
- Check the test suite for examples

### 3. Contributing Guidelines

See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed contribution guidelines.

---

**Happy coding!** AgentSpec is designed to be extensible and welcoming to contributors of all skill levels.
