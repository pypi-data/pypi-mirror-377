# Contributing to AgentSpec

We welcome contributions to AgentSpec! This guide will help you get started.

## Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/keyurgolani/agentspec.git
   cd agentspec
   ```
3. Install in development mode:
   ```bash
   pip install -e ".[dev]"
   ```
4. Generate a development spec:
   ```bash
   agentspec generate --tags general,testing,python --output dev_spec.md
   ```

## Code Standards

- Follow the project's AgentSpec guidelines in `project_spec.md`
- Write tests before implementation (TDD)
- Update documentation for any public API changes
- Ensure all validation checks pass before submitting PR

## Adding New Instructions

To add new instructions to the database:

1. **Identify the practice**: What specific development practice does this address?
2. **Define clear tags**: Use existing tags when possible, create new ones sparingly
3. **Write actionable instruction**: Specific, measurable guidance that an AI can follow
4. **Test with sample projects**: Ensure the instruction improves development outcomes

### Instruction Format

```python
"instruction_key": {
    "tags": ["tag1", "tag2", "tag3"],
    "instruction": "Clear, actionable instruction text that an AI agent can follow."
}
```

### Tag Guidelines

| Category | Purpose | Examples |
|----------|---------|----------|
| **Technology** | Language/framework specific | `javascript`, `react`, `python`, `docker` |
| **Practice** | Development methodologies | `tdd`, `testing`, `security`, `performance` |
| **Phase** | Development lifecycle | `design`, `implementation`, `deployment` |
| **Scope** | Application area | `frontend`, `backend`, `database`, `api` |
| **Quality** | Code quality aspects | `linting`, `standards`, `documentation` |

## Pull Request Process

1. Create feature branch from main:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Implement changes following AgentSpec guidelines:
   - Update project context after each step
   - Run tests frequently: `pytest`

3. Ensure all checks pass:
   ```bash
   # Run tests
   pytest

   # Run type checking
   mypy agentspec/

   # Run linting
   flake8 agentspec/ tests/

   # Test CLI functionality
   agentspec list-tags
   agentspec generate --tags general,testing --output test_spec.md
   ```

4. Update documentation:
   - Update README.md if adding new features
   - Add examples to docs/ if applicable
   - Update project_context.md with lessons learned

5. Submit PR with:
   - Clear description of changes
   - Test results and validation output
   - Screenshots/examples if applicable
   - Reference to any related issues

## Issue Reporting

When reporting issues:

1. Use provided issue templates
2. Include system information and test results:
   ```bash
   agentspec --version
   python --version
   ```
3. Provide minimal reproduction steps
4. Tag issues with relevant AgentSpec categories
5. Include environment information (OS, Python version, etc.)

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_agentspec.py -v

# Run with coverage
python -m pytest tests/ --cov=agentspec --cov-report=html
```

### Writing Tests

- Write tests for all new functionality
- Use descriptive test names
- Include both positive and negative test cases
- Test edge cases and error conditions

Example test structure:
```python
def test_generate_spec_with_valid_tags():
    """Test spec generation with valid tags produces expected output."""
    from agentspec.core.spec_generator import SpecGenerator, SpecConfig

    # Arrange
    spec_generator = SpecGenerator()
    config = SpecConfig(selected_tags=["general", "testing"])

    # Act
    result = spec_generator.generate_spec(config)

    # Assert
    assert "CORE WORKFLOW INSTRUCTIONS" in result.content
    assert "TESTING" in result.content
```

## Documentation

### Writing Documentation

- Use clear, concise language
- Include code examples where helpful
- Follow existing documentation style
- Update table of contents if adding new sections

### Documentation Structure

```
docs/
├── getting-started.md      # Quick start guide
├── specifications.md       # Spec reference
├── validation.md          # Validation framework
└── best-practices.md      # Best practices guide
```

## Release Process

1. Update version in `pyproject.toml` and `agentspec/__init__.py`
2. Update CHANGELOG.md with new features/fixes
3. Create release PR
4. Tag release after merge
5. Update GitHub release notes

## Community Guidelines

- Be respectful and inclusive
- Help newcomers get started
- Share knowledge and best practices
- Provide constructive feedback
- Follow the code of conduct

## Getting Help

- Check existing documentation first
- Search existing issues
- Join discussions in GitHub Discussions
- Ask questions in issues with "question" label

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- GitHub releases
- Project documentation
- Community showcases

Thank you for contributing to AgentSpec! 🚀
