# Completion Customization Guide

AgentSpec's shell completion system can be customized to fit your workflow and preferences. This guide covers advanced configuration options and customization techniques.

## Environment Variables

You can customize completion behavior using environment variables:

### Cache Configuration

```bash
# Disable completion caching (not recommended for performance)
export AGENTSPEC_COMPLETION_CACHE=false

# Set custom cache TTL in seconds (default: 300 = 5 minutes)
export AGENTSPEC_COMPLETION_TTL=600

# Set maximum cache size (default: 100 entries)
export AGENTSPEC_COMPLETION_CACHE_SIZE=200
```

### Performance Tuning

```bash
# Set completion timeout in seconds (default: 1)
export AGENTSPEC_COMPLETION_TIMEOUT=2

# Enable/disable lazy loading of services (default: true)
export AGENTSPEC_COMPLETION_LAZY_LOAD=true

# Set debug level for completion operations
export AGENTSPEC_COMPLETION_DEBUG=true
```

### Data Source Configuration

```bash
# Use custom instruction database path
export AGENTSPEC_INSTRUCTIONS_PATH=/path/to/custom/instructions

# Use custom templates path
export AGENTSPEC_TEMPLATES_PATH=/path/to/custom/templates

# Disable dynamic completions (use static only)
export AGENTSPEC_COMPLETION_STATIC_ONLY=true
```

## Configuration File Customization

Create a `.agentspec.yaml` file in your project or home directory:

```yaml
# ~/.agentspec.yaml or ./.agentspec.yaml
agentspec:
  version: "1.0.0"

  # Completion configuration
  completion:
    # Cache settings
    cache:
      enabled: true
      ttl: 300  # 5 minutes
      max_size: 100

    # Performance settings
    performance:
      timeout: 1.0  # seconds
      lazy_load: true

    # Feature toggles
    features:
      dynamic_tags: true
      dynamic_templates: true
      file_completion: true
      descriptions: true

    # Custom completers
    custom:
      # Add custom tag completions
      extra_tags:
        - "custom-tag-1"
        - "custom-tag-2"

      # Add custom categories
      extra_categories:
        - "Custom Category"
        - "Organization Specific"
```

## Custom Completion Scripts

### Adding Custom Completers

You can extend AgentSpec's completion by creating custom completer functions:

```python
# ~/.agentspec/custom_completers.py
from typing import List
import argparse

def custom_tag_completer(prefix: str, parsed_args: argparse.Namespace, **kwargs) -> List[str]:
    """Custom tag completer with organization-specific tags"""
    custom_tags = [
        "org-frontend",
        "org-backend",
        "org-security",
        "org-testing"
    ]

    return [tag for tag in custom_tags if tag.startswith(prefix)]

def custom_template_completer(prefix: str, parsed_args: argparse.Namespace, **kwargs) -> List[str]:
    """Custom template completer with organization templates"""
    custom_templates = [
        "org-react-app",
        "org-python-service",
        "org-microservice"
    ]

    return [template for template in custom_templates if template.startswith(prefix)]
```

### Registering Custom Completers

```bash
# Set environment variable to load custom completers
export AGENTSPEC_CUSTOM_COMPLETERS=~/.agentspec/custom_completers.py
```

## Shell-Specific Customization

### Bash Customization

Add custom completion behavior to your `.bashrc`:

```bash
# ~/.bashrc

# Custom completion wrapper
_agentspec_custom() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Add custom logic here
    if [[ ${prev} == "--custom-option" ]]; then
        COMPREPLY=( $(compgen -W "custom1 custom2 custom3" -- ${cur}) )
        return 0
    fi

    # Fall back to default completion
    _agentspec_completion
}

# Override default completion
complete -F _agentspec_custom agentspec
```

### Zsh Customization

Add custom completion behavior to your `.zshrc`:

```bash
# ~/.zshrc

# Custom completion function
_agentspec_custom() {
    local context state line

    _arguments \
        '--custom-option[Custom option]:custom:(custom1 custom2 custom3)' \
        '*::agentspec command:_agentspec_default'
}

# Override default completion
compdef _agentspec_custom agentspec
```

### Fish Customization

Create custom completion file:

```fish
# ~/.config/fish/completions/agentspec_custom.fish

# Add custom completions
complete -c agentspec -l custom-option -d "Custom option" -xa "custom1 custom2 custom3"

# Conditional completions
complete -c agentspec -n "__fish_seen_subcommand_from generate" -l custom-tag -d "Custom tag" -xa "org-tag1 org-tag2"
```

## Advanced Filtering

### Context-Aware Completion

Customize completion based on project context:

```yaml
# .agentspec.yaml
agentspec:
  completion:
    context_filters:
      # Only show React templates in React projects
      templates:
        react_project:
          condition: "package.json contains react"
          templates: ["react-app", "react-component"]

      # Show Python-specific tags in Python projects
      tags:
        python_project:
          condition: "*.py files exist"
          tags: ["python", "fastapi", "django"]
```

### Project-Specific Completions

Create project-specific completion rules:

```yaml
# project/.agentspec.yaml
agentspec:
  completion:
    project_specific:
      # Custom tags for this project
      tags:
        - "project-specific-tag"
        - "team-standard"

      # Preferred templates
      templates:
        - "company-react-app"
        - "company-api-service"

      # Custom categories
      categories:
        - "Company Standards"
```

## Completion Hooks

### Pre-completion Hooks

Execute custom logic before completion:

```python
# ~/.agentspec/hooks.py
def pre_completion_hook(command: str, args: List[str]) -> None:
    """Called before completion is performed"""
    # Log completion requests
    with open("~/.agentspec/completion.log", "a") as f:
        f.write(f"Completion requested: {command} {' '.join(args)}\n")

def post_completion_hook(command: str, args: List[str], results: List[str]) -> List[str]:
    """Called after completion is performed"""
    # Filter results based on custom logic
    if command == "generate" and "--tags" in args:
        # Prioritize certain tags
        priority_tags = ["testing", "security", "performance"]
        prioritized = [r for r in results if r in priority_tags]
        others = [r for r in results if r not in priority_tags]
        return prioritized + others

    return results
```

### Enabling Hooks

```bash
# Enable completion hooks
export AGENTSPEC_COMPLETION_HOOKS=~/.agentspec/hooks.py
```

## Performance Optimization

### Caching Strategies

```yaml
# .agentspec.yaml
agentspec:
  completion:
    cache:
      # Different TTL for different completion types
      tag_ttl: 300      # 5 minutes
      template_ttl: 600  # 10 minutes
      category_ttl: -1   # Never expire

      # Preload common completions
      preload:
        - tags
        - templates
        - categories
```

### Lazy Loading Configuration

```yaml
agentspec:
  completion:
    lazy_loading:
      # Services to load on demand
      instruction_db: true
      template_manager: true

      # Completion types to compute on demand
      dynamic_completions: true

      # Timeout for service initialization
      init_timeout: 2.0
```

## Debugging Completion

### Enable Debug Logging

```bash
# Enable detailed completion logging
export AGENTSPEC_LOG_LEVEL=DEBUG
export AGENTSPEC_COMPLETION_DEBUG=true

# Test completion with debug output
agentspec generate --tags <TAB>

# View completion logs
tail -f ~/.agentspec/logs/completion.log
```

### Completion Profiling

```bash
# Enable completion profiling
export AGENTSPEC_COMPLETION_PROFILE=true

# View performance metrics
agentspec --completion-status --verbose
```

### Testing Custom Completions

```bash
# Test completion without shell integration
python -c "
from agentspec.cli.completers import tag_completer
import argparse
args = argparse.Namespace()
results = tag_completer('test', args)
print('Completions:', results)
"
```

## Integration with Development Tools

### IDE Integration

Configure your IDE to use AgentSpec completion:

```json
// VS Code settings.json
{
  "terminal.integrated.shellArgs.linux": [
    "-c",
    "source ~/.agentspec-completion.bash && exec bash"
  ]
}
```

### CI/CD Integration

Use completion in automated scripts:

```bash
#!/bin/bash
# ci/generate-specs.sh

# Enable completion in non-interactive mode
export AGENTSPEC_COMPLETION_CACHE=true
export AGENTSPEC_COMPLETION_TIMEOUT=5

# Generate specs for all templates
for template in $(agentspec list-templates --format json | jq -r '.[].id'); do
    agentspec generate --template "$template" --output "specs/${template}-spec.md"
done
```

## Troubleshooting Custom Completions

### Common Issues

1. **Custom completers not loading:**
   ```bash
   # Check if custom completer file exists and is readable
   ls -la ~/.agentspec/custom_completers.py

   # Test loading custom completers
   python -c "import sys; sys.path.append('~/.agentspec'); import custom_completers"
   ```

2. **Configuration not applied:**
   ```bash
   # Check configuration loading
   agentspec --completion-status --verbose

   # Verify configuration file syntax
   python -c "import yaml; yaml.safe_load(open('.agentspec.yaml'))"
   ```

3. **Performance issues:**
   ```bash
   # Profile completion performance
   time agentspec generate --tags <TAB>

   # Check cache status
   agentspec --completion-status
   ```

### Reset to Defaults

```bash
# Remove custom configuration
rm ~/.agentspec.yaml
rm -rf ~/.agentspec/

# Reinstall completion
agentspec --install-completion

# Clear environment variables
unset AGENTSPEC_COMPLETION_*
```

## Best Practices

### Configuration Management

1. **Use project-specific configuration** for team consistency
2. **Version control completion configuration** with your project
3. **Document custom completions** for team members
4. **Test completion changes** before deploying to team

### Performance Guidelines

1. **Keep cache TTL reasonable** (5-10 minutes for dynamic data)
2. **Use lazy loading** for better startup performance
3. **Limit custom completer complexity** to avoid delays
4. **Monitor completion performance** in team environments

### Security Considerations

1. **Validate custom completer inputs** to prevent injection
2. **Limit file system access** in custom completers
3. **Use safe defaults** for configuration options
4. **Audit custom completion scripts** regularly

This completes the completion customization guide. Use these techniques to tailor AgentSpec's completion system to your specific needs and workflow.
