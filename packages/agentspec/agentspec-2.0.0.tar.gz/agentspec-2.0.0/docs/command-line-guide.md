# Command Line Guide

Complete reference for all AgentSpec CLI commands.

## Installation and Setup

```bash
# Install AgentSpec
pip install agentspec

# Verify installation
agentspec --version
```

## Global Options

These options work with all commands:

```bash
agentspec [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS]
```

**Global Options:**
- `--config FILE` - Use custom configuration file
- `--verbose` - Enable verbose output
- `--quiet` - Suppress non-error output
- `--version` - Show version information
- `--help` - Show help information

## Commands Overview

AgentSpec provides 10 commands:

| Command | Purpose | Example |
|---------|---------|---------|
| `generate` | Generate specifications | `agentspec generate --template react_app` |
| `list-templates` | Show available templates | `agentspec list-templates` |
| `list-instructions` | Show available instructions | `agentspec list-instructions --tag testing` |
| `list-tags` | Show available tags | `agentspec list-tags` |
| `analyze` | Analyze project structure | `agentspec analyze ./my-project` |
| `integrate` | Integrate AI best practices | `agentspec integrate .` |
| `interactive` | Run interactive wizard | `agentspec interactive` |
| `validate` | Validate specification files | `agentspec validate spec.md` |
| `version` | Show version information | `agentspec version` |
| `help` | Show help for commands | `agentspec help generate` |

## Command Details

### `generate` - Generate Specifications

The most important command - generates instruction specifications for your projects.

#### Basic Usage

```bash
# Generate from template (recommended)
agentspec generate --template react-frontend --output instructions.md

# Generate from tags
agentspec generate --tags frontend,testing,security --output instructions.md

# Generate from project analysis
agentspec generate --project-path . --tags auto --output instructions.md
```

#### All Options

```bash
agentspec generate [OPTIONS]
```

**Options:**
- `--template TEMPLATE_ID` - Use specific template
- `--tags TAG1,TAG2,...` - Comma-separated list of tags
- `--instructions ID1,ID2,...` - Specific instruction IDs
- `--project-path PATH` - Project path for context detection
- `--output FILE` - Output file path
- `--format FORMAT` - Output format (markdown, json, yaml)
- `--language LANG` - Language code (default: en)
- `--no-metadata` - Exclude metadata section

#### Examples

```bash
# React frontend with TypeScript
agentspec generate --template react_app --output react-spec.md

# Python API with security focus
agentspec generate --template python-api --output api-spec.md

# Custom instruction selection
agentspec generate --tags testing,performance,accessibility --output custom-spec.md

# Auto-detect project needs
agentspec generate --project-path ./my-project --tags auto --output project-spec.md

# JSON output for programmatic use
agentspec generate --template react-frontend --format json --output spec.json
```

### `list-templates` - Show Available Templates

View all 15 available templates with descriptions.

#### Basic Usage

```bash
# List all templates
agentspec list-templates

# Verbose output with full descriptions
agentspec list-templates --verbose

# Filter by project type
agentspec list-templates --project-type web_frontend
```

#### Options

- `--project-type TYPE` - Filter by project type
- `--verbose` - Show detailed information

#### Example Output

```
All templates (15 total):
========================

## TECHNOLOGY

React Frontend (ID: react-frontend)
  Version: 1.0.0
  Description: Modern React applications with TypeScript
  Technologies: react, typescript, webpack

Python API (ID: python-api)
  Version: 1.0.0
  Description: Python REST APIs using FastAPI
  Technologies: python, fastapi, postgresql
```

### `list-instructions` - Show Available Instructions

Browse the 107 available instructions.

#### Basic Usage

```bash
# List all instructions
agentspec list-instructions

# Filter by tag
agentspec list-instructions --tag testing

# Filter by category
agentspec list-instructions --category frontend

# Verbose output
agentspec list-instructions --verbose
```

#### Options

- `--tag TAG` - Filter by specific tag
- `--category CATEGORY` - Filter by category
- `--verbose` - Show detailed information

### `list-tags` - Show Available Tags

View all instruction tags organized by category.

#### Basic Usage

```bash
# List all tags
agentspec list-tags

# Filter by category
agentspec list-tags --category testing

# Verbose output with instruction counts
agentspec list-tags --verbose
```

#### Options

- `--category CATEGORY` - Filter by category
- `--verbose` - Show detailed information

### `analyze` - Analyze Project Structure

Analyze existing projects to understand their technology stack and get instruction recommendations.

#### Basic Usage

```bash
# Analyze current directory
agentspec analyze .

# Analyze specific project
agentspec analyze /path/to/project

# Save analysis to file
agentspec analyze . --output analysis.json

# Skip instruction suggestions
agentspec analyze . --no-suggestions
```

#### Options

- `PROJECT_PATH` - Path to project directory (required)
- `--output FILE` - Save analysis results to file
- `--no-suggestions` - Don't suggest instructions

#### Example Output

```
PROJECT ANALYSIS RESULTS
========================

Project Type: web_frontend
Confidence Score: 0.92

Technology Stack:
  Languages: javascript, typescript
  Frameworks: react (0.9), webpack (0.8)
  Tools: jest, eslint

INSTRUCTION SUGGESTIONS
======================

Top 5 suggested instructions:

1. react_component_architecture (confidence: 0.95)
   Tags: react, components, architecture

2. typescript_configuration (confidence: 0.88)
   Tags: typescript, type-safety
```

### `integrate` - Integrate AI Best Practices

Analyze projects for AI development integration opportunities.

#### Basic Usage

```bash
# Analyze current directory
agentspec integrate .

# Analyze only (don't create files)
agentspec integrate . --analyze-only

# JSON output
agentspec integrate . --analyze-only --output-format json
```

#### Options

- `PROJECT_PATH` - Path to project directory (default: current directory)
- `--analyze-only` - Only analyze, don't create integration files
- `--output-format FORMAT` - Output format (text, json)

### `interactive` - Interactive Wizard

Guided specification generation with questions and recommendations.

#### Basic Usage

```bash
agentspec interactive
```

This will guide you through:
1. Project type selection
2. Technology stack detection
3. Template recommendations
4. Custom instruction selection
5. Specification generation

### `validate` - Validate Specification Files

Validate generated specification files for correctness.

#### Basic Usage

```bash
# Validate a specification file
agentspec validate my-spec.md

# Validate with verbose output
agentspec validate my-spec.md --verbose
```

### `version` - Show Version Information

Display AgentSpec version and system information.

```bash
agentspec version
```

### `help` - Show Help Information

Get help for specific commands.

```bash
# General help
agentspec help

# Help for specific command
agentspec help generate
agentspec help analyze
```

## Common Workflows

### New Project Workflow

```bash
# 1. Choose template
agentspec list-templates

# 2. Generate instructions
agentspec generate --template react-frontend --output instructions.md

# 3. Start development with instructions
```

### Existing Project Workflow

```bash
# 1. Analyze project
agentspec analyze . --output analysis.json

# 2. Generate project-specific instructions
agentspec generate --project-path . --tags auto --output instructions.md

# 3. Integrate into development process
```

### Team Standardization Workflow

```bash
# 1. Generate team standards
agentspec generate --template enterprise-web-application --output team-standards.md

# 2. Customize for organization
# Edit team-standards.md as needed

# 3. Share with team
git add team-standards.md
git commit -m "Add team development standards"
```

### AI Integration Workflow

```bash
# 1. Analyze for AI opportunities
agentspec integrate . --analyze-only

# 2. Generate AI-focused instructions
agentspec generate --template ai-assisted-development --output ai-instructions.md

# 3. Implement AI best practices
```

## Configuration

### Configuration File

Create `.agentspec.yaml` in your project root:

```yaml
agentspec:
  version: "1.0.0"

  # Paths
  paths:
    instructions: "custom/instructions"
    templates: "custom/templates"
    output: "specs"

  # Output preferences
  output:
    format: "markdown"
    include_metadata: true
    language: "en"
```

### Environment Variables

- `AGENTSPEC_CONFIG` - Path to configuration file
- `AGENTSPEC_LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)

## Troubleshooting

### Common Issues

**Command not found:**
```bash
# Ensure AgentSpec is installed
pip install agentspec

# Check if it's in PATH
which agentspec
```

**No templates found:**
```bash
# Verify installation
agentspec list-templates

# Reinstall if needed
pip uninstall agentspec
pip install agentspec
```

**Project analysis fails:**
```bash
# Check project path
ls -la /path/to/project

# Use verbose mode for details
agentspec analyze . --verbose
```

### Getting Help

```bash
# Built-in help
agentspec --help
agentspec COMMAND --help

# Verbose output for debugging
agentspec --verbose COMMAND

# Version information
agentspec --version
```

### Debug Mode

For detailed troubleshooting:

```bash
# Enable debug logging
AGENTSPEC_LOG_LEVEL=DEBUG agentspec generate --template react-frontend
```

## Advanced Usage

### Scripting with AgentSpec

```bash
#!/bin/bash

# Generate specifications for multiple project types
for template in react-frontend python-api mobile-app; do
    agentspec generate --template $template --output "${template}-spec.md"
done

# Analyze multiple projects
for project in project1 project2 project3; do
    agentspec analyze "$project" --output "${project}-analysis.json"
done
```

### Integration with CI/CD

```yaml
# GitHub Actions example
- name: Generate AgentSpec
  run: |
    pip install agentspec
    agentspec generate --project-path . --tags auto --output project-spec.md

- name: Validate specification
  run: agentspec validate project-spec.md
```

This completes the command line reference. Use this guide to master all AgentSpec CLI capabilities!
