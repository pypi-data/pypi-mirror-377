# Shell Completion Setup Guide

AgentSpec provides intelligent command-line completion for bash, zsh, and fish shells. This guide covers installation and setup for each supported shell.

## Quick Setup (Recommended)

The easiest way to enable completion is using the built-in installation command:

```bash
# Install completion for your current shell
agentspec --install-completion

# Restart your shell or source your profile
# Bash: source ~/.bashrc
# Zsh: source ~/.zshrc
# Fish: No action needed (auto-reloads)
```

## Manual Setup by Shell

### Bash Completion

#### Option 1: Automatic Installation

```bash
# Install completion
agentspec --install-completion

# Reload bash configuration
source ~/.bashrc
```

#### Option 2: Manual Installation

```bash
# Generate completion script
agentspec --show-completion > ~/.agentspec-completion.bash

# Add to your ~/.bashrc
echo 'source ~/.agentspec-completion.bash' >> ~/.bashrc

# Reload configuration
source ~/.bashrc
```

#### Option 3: System-wide Installation (requires sudo)

```bash
# Generate completion script for all users
sudo agentspec --show-completion > /etc/bash_completion.d/agentspec

# Completion will be available for all users on next login
```

### Zsh Completion

#### Option 1: Automatic Installation

```bash
# Install completion
agentspec --install-completion

# Reload zsh configuration
source ~/.zshrc
```

#### Option 2: Manual Installation

```bash
# Create completion directory if it doesn't exist
mkdir -p ~/.zsh/completions

# Generate completion script
agentspec --show-completion > ~/.zsh/completions/_agentspec

# Add to your ~/.zshrc (if not already present)
echo 'fpath=(~/.zsh/completions $fpath)' >> ~/.zshrc
echo 'autoload -U compinit && compinit' >> ~/.zshrc

# Reload configuration
source ~/.zshrc
```

#### Option 3: Oh My Zsh Integration

```bash
# Create completion file in Oh My Zsh custom directory
agentspec --show-completion > ~/.oh-my-zsh/custom/plugins/agentspec/_agentspec

# Add agentspec to plugins in ~/.zshrc
# plugins=(git agentspec other-plugins)

# Reload configuration
source ~/.zshrc
```

### Fish Completion

#### Option 1: Automatic Installation

```bash
# Install completion
agentspec --install-completion

# Fish automatically reloads completions
```

#### Option 2: Manual Installation

```bash
# Create completion directory if it doesn't exist
mkdir -p ~/.config/fish/completions

# Generate completion script
agentspec --show-completion > ~/.config/fish/completions/agentspec.fish

# Fish automatically loads the completion
```

## Verification

After installation, verify that completion is working:

```bash
# Test basic command completion
agentspec <TAB>
# Should show: analyze, generate, help, integrate, interactive, list-instructions, list-tags, list-templates, validate, version

# Test option completion
agentspec generate --<TAB>
# Should show: --format, --instructions, --language, --no-metadata, --output, --project-path, --tags, --template

# Test dynamic completion
agentspec generate --tags <TAB>
# Should show available tags: accessibility, api, backend, core, frontend, testing, etc.
```

## Troubleshooting

### Completion Not Working

**Check installation status:**
```bash
agentspec --completion-status
```

**Common issues and solutions:**

1. **Shell not supported:**
   - AgentSpec supports bash, zsh, and fish
   - Check your shell: `echo $SHELL`

2. **Completion script not loaded:**
   ```bash
   # Bash
   source ~/.bashrc

   # Zsh
   source ~/.zshrc

   # Fish (automatic reload)
   ```

3. **Permission issues:**
   ```bash
   # Check file permissions
   ls -la ~/.agentspec-completion.*

   # Fix permissions if needed
   chmod +x ~/.agentspec-completion.*
   ```

4. **Path issues:**
   ```bash
   # Ensure agentspec is in PATH
   which agentspec

   # If not found, reinstall
   pip install --force-reinstall agentspec
   ```

### Slow Completion

If completion feels slow, it might be due to:

1. **First-time data loading:** Initial completion may take up to 1 second while loading instruction database
2. **Large project analysis:** File path completion in large directories may be slower

**Performance tips:**
- Completion results are cached for 5 minutes
- Use specific prefixes to narrow results
- Consider using `--no-metadata` flag for faster generation

### Debugging Completion

Enable debug logging to troubleshoot completion issues:

```bash
# Set debug level
export AGENTSPEC_LOG_LEVEL=DEBUG

# Test completion with verbose output
agentspec generate --tags <TAB>

# Check logs
tail -f ~/.agentspec/logs/agentspec.log
```

## Advanced Configuration

### Custom Completion Behavior

You can customize completion behavior by setting environment variables:

```bash
# Disable caching (not recommended)
export AGENTSPEC_COMPLETION_CACHE=false

# Set custom cache TTL (in seconds)
export AGENTSPEC_COMPLETION_TTL=600

# Set completion timeout (in seconds)
export AGENTSPEC_COMPLETION_TIMEOUT=2
```

### Integration with Other Tools

#### Bash-it Integration

```bash
# Add to ~/.bash_it/custom/completion.bash
source ~/.agentspec-completion.bash
```

#### Prezto Integration

```bash
# Add to ~/.zpreztorc
zstyle ':prezto:module:completion' external-completions ~/.zsh/completions
```

## Shell-Specific Features

### Bash Features

- **Command completion:** Full command and subcommand completion
- **Option completion:** All command-line options with descriptions
- **File path completion:** Intelligent file and directory completion
- **Value completion:** Dynamic completion for tags, templates, and formats

### Zsh Features

- **Enhanced descriptions:** Rich descriptions for commands and options
- **Fuzzy matching:** Partial string matching for faster completion
- **Menu completion:** Navigate completions with arrow keys
- **Correction suggestions:** Suggests corrections for typos

### Fish Features

- **Real-time completion:** Completions appear as you type
- **Syntax highlighting:** Commands and options are highlighted
- **History-based suggestions:** Suggests based on command history
- **Automatic paging:** Long completion lists are automatically paged

## Uninstalling Completion

To remove AgentSpec completion:

### Bash
```bash
# Remove completion script
rm ~/.agentspec-completion.bash

# Remove from ~/.bashrc
sed -i '/agentspec-completion/d' ~/.bashrc

# Reload configuration
source ~/.bashrc
```

### Zsh
```bash
# Remove completion script
rm ~/.zsh/completions/_agentspec

# Remove from ~/.zshrc (if added manually)
sed -i '/agentspec/d' ~/.zshrc

# Reload configuration
source ~/.zshrc
```

### Fish
```bash
# Remove completion script
rm ~/.config/fish/completions/agentspec.fish

# Fish automatically reloads
```

## Getting Help

If you encounter issues with shell completion:

1. **Check the troubleshooting section above**
2. **Run completion status check:** `agentspec --completion-status`
3. **Enable debug logging:** `export AGENTSPEC_LOG_LEVEL=DEBUG`
4. **Report issues:** [GitHub Issues](https://github.com/keyurgolani/AgentSpec/issues)

For shell-specific questions, include:
- Your shell and version: `$SHELL --version`
- Operating system: `uname -a`
- AgentSpec version: `agentspec --version`
- Completion status: `agentspec --completion-status`
