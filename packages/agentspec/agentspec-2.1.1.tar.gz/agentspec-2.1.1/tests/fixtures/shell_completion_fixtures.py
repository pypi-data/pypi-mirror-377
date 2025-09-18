"""
Test fixtures for shell completion testing.

This module provides fixtures and utilities for testing shell completion
functionality across different shell environments (bash, zsh, fish).
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from unittest.mock import Mock, patch

import pytest


class ShellCompletionFixture:
    """Base fixture for shell completion testing"""

    def __init__(self, shell_name: str):
        """
        Initialize shell completion fixture.

        Args:
            shell_name: Name of the shell (bash, zsh, fish)
        """
        self.shell_name = shell_name
        self.temp_dir = None
        self.shell_rc_file = None
        self.completion_script = None

    def setup(self) -> None:
        """Set up temporary shell environment for testing"""
        self.temp_dir = tempfile.mkdtemp(prefix=f"agentspec_test_{self.shell_name}_")
        self.shell_rc_file = Path(self.temp_dir) / f".{self.shell_name}rc"
        self.completion_script = (
            Path(self.temp_dir) / f"agentspec_completion_{self.shell_name}.sh"
        )

    def teardown(self) -> None:
        """Clean up temporary shell environment"""
        if self.temp_dir and Path(self.temp_dir).exists():
            import shutil

            shutil.rmtree(self.temp_dir)

    def create_completion_script(self, content: str) -> Path:
        """
        Create a completion script file for testing.

        Args:
            content: Content of the completion script

        Returns:
            Path to the created completion script
        """
        self.completion_script.write_text(content)
        return self.completion_script

    def create_shell_rc(self, content: str) -> Path:
        """
        Create a shell RC file for testing.

        Args:
            content: Content of the shell RC file

        Returns:
            Path to the created shell RC file
        """
        self.shell_rc_file.write_text(content)
        return self.shell_rc_file

    def simulate_completion_request(
        self, command_line: str, cursor_position: Optional[int] = None
    ) -> Dict:
        """
        Simulate a completion request for testing.

        Args:
            command_line: Command line to complete
            cursor_position: Position of cursor (defaults to end of line)

        Returns:
            Dictionary with completion simulation results
        """
        if cursor_position is None:
            cursor_position = len(command_line)

        # Parse the command line to extract components
        parts = command_line.split()
        if not parts:
            return {"completions": [], "prefix": "", "command": ""}

        command = parts[0] if parts else ""
        prefix = ""

        # Determine what we're completing
        if command_line.endswith(" "):
            # Completing a new argument
            prefix = ""
        else:
            # Completing the last argument
            prefix = parts[-1] if parts else ""

        return {
            "completions": [],
            "prefix": prefix,
            "command": command,
            "command_line": command_line,
            "cursor_position": cursor_position,
            "shell": self.shell_name,
        }


class BashCompletionFixture(ShellCompletionFixture):
    """Fixture for bash completion testing"""

    def __init__(self):
        super().__init__("bash")

    def get_completion_script_template(self) -> str:
        """
        Get bash completion script template.

        Returns:
            Bash completion script template
        """
        return """#!/bin/bash
# Bash completion for agentspec

_agentspec_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Basic command completion
    if [[ ${COMP_CWORD} == 1 ]]; then
        opts="list-tags list-instructions list-templates generate interactive analyze validate integrate version help"
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
        return 0
    fi

    # Subcommand-specific completion would go here
    case "${COMP_WORDS[1]}" in
        generate)
            case "${prev}" in
                --tags)
                    # Mock tag completion
                    COMPREPLY=( $(compgen -W "testing frontend backend" -- ${cur}) )
                    ;;
                --format)
                    COMPREPLY=( $(compgen -W "markdown json yaml" -- ${cur}) )
                    ;;
                *)
                    COMPREPLY=( $(compgen -W "--tags --format --output --template" -- ${cur}) )
                    ;;
            esac
            ;;
        *)
            ;;
    esac
}

complete -F _agentspec_completion agentspec
"""

    def test_completion_activation(self) -> bool:
        """
        Test if bash completion can be activated.

        Returns:
            True if completion activation succeeds
        """
        try:
            # Create a test completion script
            script_content = self.get_completion_script_template()
            script_path = self.create_completion_script(script_content)

            # Create a test bash RC file that sources the completion
            rc_content = f"source {script_path}\n"
            rc_path = self.create_shell_rc(rc_content)

            # Test that the files were created successfully
            return script_path.exists() and rc_path.exists()

        except Exception:
            return False

    def simulate_bash_completion(self, command_line: str) -> List[str]:
        """
        Simulate bash completion for a command line.

        Args:
            command_line: Command line to complete

        Returns:
            List of completion suggestions
        """
        # Parse command line
        parts = command_line.strip().split()
        if not parts or parts[0] != "agentspec":
            return []

        # Simulate basic completion logic
        if len(parts) == 1 or (len(parts) == 2 and not command_line.endswith(" ")):
            # Completing main command
            commands = [
                "list-tags",
                "list-instructions",
                "list-templates",
                "generate",
                "interactive",
                "analyze",
                "validate",
                "integrate",
                "version",
                "help",
            ]
            prefix = parts[1] if len(parts) == 2 else ""
            return [cmd for cmd in commands if cmd.startswith(prefix)]

        elif len(parts) >= 2 and parts[1] == "generate":
            # Completing generate command options
            if command_line.endswith(" "):
                return ["--tags", "--format", "--output", "--template"]
            else:
                last_part = parts[-1]
                if last_part.startswith("--"):
                    options = ["--tags", "--format", "--output", "--template"]
                    return [opt for opt in options if opt.startswith(last_part)]

        return []


class ZshCompletionFixture(ShellCompletionFixture):
    """Fixture for zsh completion testing"""

    def __init__(self):
        super().__init__("zsh")

    def get_completion_script_template(self) -> str:
        """
        Get zsh completion script template.

        Returns:
            Zsh completion script template
        """
        return """#compdef agentspec

_agentspec() {
    local context state line
    typeset -A opt_args

    _arguments -C \
        '1: :_agentspec_commands' \
        '*::arg:->args'

    case $state in
        args)
            case $words[1] in
                generate)
                    _arguments \
                        '--tags[Comma-separated list of tags]:tags:_agentspec_tags' \
                        '--format[Output format]:format:(markdown json yaml)' \
                        '--output[Output file]:file:_files' \
                        '--template[Template ID]:template:_agentspec_templates'
                    ;;
                list-tags)
                    _arguments \
                        '--category[Filter by category]:category:_agentspec_categories' \
                        '--verbose[Show detailed information]'
                    ;;
                *)
                    ;;
            esac
            ;;
    esac
}

_agentspec_commands() {
    local commands
    commands=(
        'list-tags:List available instruction tags'
        'list-instructions:List instructions'
        'list-templates:List available templates'
        'generate:Generate a specification'
        'interactive:Run interactive wizard'
        'analyze:Analyze project context'
        'validate:Validate specification file'
        'integrate:Integrate AI best practices'
        'version:Show version information'
        'help:Show help information'
    )
    _describe 'commands' commands
}

_agentspec_tags() {
    local tags
    tags=(testing frontend backend devops)
    _describe 'tags' tags
}

_agentspec_templates() {
    local templates
    templates=(react-app python-api nodejs-api)
    _describe 'templates' templates
}

_agentspec_categories() {
    local categories
    categories=(General Testing Frontend Backend Languages DevOps Architecture)
    _describe 'categories' categories
}

_agentspec "$@"
"""

    def test_completion_activation(self) -> bool:
        """
        Test if zsh completion can be activated.

        Returns:
            True if completion activation succeeds
        """
        try:
            # Create a test completion script
            script_content = self.get_completion_script_template()
            script_path = self.create_completion_script(script_content)

            # Create a test zsh RC file that loads the completion
            rc_content = f"""
# Add completion directory to fpath
fpath=({self.temp_dir} $fpath)

# Load completion system
autoload -Uz compinit
compinit

# Source the completion script
source {script_path}
"""
            rc_path = self.create_shell_rc(rc_content)

            # Test that the files were created successfully
            return script_path.exists() and rc_path.exists()

        except Exception:
            return False

    def simulate_zsh_completion(self, command_line: str) -> List[str]:
        """
        Simulate zsh completion for a command line.

        Args:
            command_line: Command line to complete

        Returns:
            List of completion suggestions
        """
        # Parse command line
        parts = command_line.strip().split()
        if not parts or parts[0] != "agentspec":
            return []

        # Simulate zsh completion logic (similar to bash but with descriptions)
        if len(parts) == 1 or (len(parts) == 2 and not command_line.endswith(" ")):
            # Completing main command
            commands = [
                "list-tags",
                "list-instructions",
                "list-templates",
                "generate",
                "interactive",
                "analyze",
                "validate",
                "integrate",
                "version",
                "help",
            ]
            prefix = parts[1] if len(parts) == 2 else ""
            return [cmd for cmd in commands if cmd.startswith(prefix)]

        elif len(parts) >= 2 and parts[1] == "generate":
            # Completing generate command options
            if command_line.endswith(" "):
                return ["--tags", "--format", "--output", "--template"]
            else:
                last_part = parts[-1]
                if last_part.startswith("--"):
                    options = ["--tags", "--format", "--output", "--template"]
                    return [opt for opt in options if opt.startswith(last_part)]
                elif "--tags" in parts:
                    # Simulate tag completion
                    return ["testing", "frontend", "backend", "devops"]
                elif "--format" in parts:
                    # Simulate format completion
                    return ["markdown", "json", "yaml"]

        return []


class FishCompletionFixture(ShellCompletionFixture):
    """Fixture for fish completion testing"""

    def __init__(self):
        super().__init__("fish")

    def get_completion_script_template(self) -> str:
        """
        Get fish completion script template.

        Returns:
            Fish completion script template
        """
        return """# Fish completion for agentspec

# Main commands
complete -c agentspec -f -n '__fish_use_subcommand' -a 'list-tags' -d 'List available instruction tags'
complete -c agentspec -f -n '__fish_use_subcommand' -a 'list-instructions' -d 'List instructions'
complete -c agentspec -f -n '__fish_use_subcommand' -a 'list-templates' -d 'List available templates'
complete -c agentspec -f -n '__fish_use_subcommand' -a 'generate' -d 'Generate a specification'
complete -c agentspec -f -n '__fish_use_subcommand' -a 'interactive' -d 'Run interactive wizard'
complete -c agentspec -f -n '__fish_use_subcommand' -a 'analyze' -d 'Analyze project context'
complete -c agentspec -f -n '__fish_use_subcommand' -a 'validate' -d 'Validate specification file'
complete -c agentspec -f -n '__fish_use_subcommand' -a 'integrate' -d 'Integrate AI best practices'
complete -c agentspec -f -n '__fish_use_subcommand' -a 'version' -d 'Show version information'
complete -c agentspec -f -n '__fish_use_subcommand' -a 'help' -d 'Show help information'

# Generate command options
complete -c agentspec -f -n '__fish_seen_subcommand_from generate' -l tags -d 'Comma-separated list of tags'
complete -c agentspec -f -n '__fish_seen_subcommand_from generate' -l format -a 'markdown json yaml' -d 'Output format'
complete -c agentspec -f -n '__fish_seen_subcommand_from generate' -l output -F -d 'Output file'
complete -c agentspec -f -n '__fish_seen_subcommand_from generate' -l template -d 'Template ID'

# List commands options
complete -c agentspec -f -n '__fish_seen_subcommand_from list-tags' -l category -d 'Filter by category'
complete -c agentspec -f -n '__fish_seen_subcommand_from list-tags' -l verbose -d 'Show detailed information'

complete -c agentspec -f -n '__fish_seen_subcommand_from list-instructions' -l tag -d 'Filter by tag'
complete -c agentspec -f -n '__fish_seen_subcommand_from list-instructions' -l category -d 'Filter by category'
complete -c agentspec -f -n '__fish_seen_subcommand_from list-instructions' -l verbose -d 'Show detailed information'

complete -c agentspec -f -n '__fish_seen_subcommand_from list-templates' -l project-type -d 'Filter by project type'
complete -c agentspec -f -n '__fish_seen_subcommand_from list-templates' -l verbose -d 'Show detailed information'
"""

    def test_completion_activation(self) -> bool:
        """
        Test if fish completion can be activated.

        Returns:
            True if completion activation succeeds
        """
        try:
            # Create a test completion script
            script_content = self.get_completion_script_template()
            script_path = self.create_completion_script(script_content)

            # Fish completions are typically stored in specific directories
            # For testing, we just verify the script can be created
            return script_path.exists()

        except Exception:
            return False

    def simulate_fish_completion(self, command_line: str) -> List[str]:
        """
        Simulate fish completion for a command line.

        Args:
            command_line: Command line to complete

        Returns:
            List of completion suggestions
        """
        # Parse command line
        parts = command_line.strip().split()
        if not parts or parts[0] != "agentspec":
            return []

        # Simulate fish completion logic
        if len(parts) == 1 or (len(parts) == 2 and not command_line.endswith(" ")):
            # Completing main command
            commands = [
                "list-tags",
                "list-instructions",
                "list-templates",
                "generate",
                "interactive",
                "analyze",
                "validate",
                "integrate",
                "version",
                "help",
            ]
            prefix = parts[1] if len(parts) == 2 else ""
            return [cmd for cmd in commands if cmd.startswith(prefix)]

        elif len(parts) >= 2 and parts[1] == "generate":
            # Completing generate command options
            if command_line.endswith(" "):
                return ["--tags", "--format", "--output", "--template"]
            else:
                last_part = parts[-1]
                if last_part.startswith("--"):
                    options = ["--tags", "--format", "--output", "--template"]
                    return [opt for opt in options if opt.startswith(last_part)]

        return []


@pytest.fixture
def bash_completion_fixture():
    """Pytest fixture for bash completion testing"""
    fixture = BashCompletionFixture()
    fixture.setup()
    yield fixture
    fixture.teardown()


@pytest.fixture
def zsh_completion_fixture():
    """Pytest fixture for zsh completion testing"""
    fixture = ZshCompletionFixture()
    fixture.setup()
    yield fixture
    fixture.teardown()


@pytest.fixture
def fish_completion_fixture():
    """Pytest fixture for fish completion testing"""
    fixture = FishCompletionFixture()
    fixture.setup()
    yield fixture
    fixture.teardown()


@pytest.fixture
def all_shell_fixtures(
    bash_completion_fixture, zsh_completion_fixture, fish_completion_fixture
):
    """Pytest fixture providing all shell completion fixtures"""
    return {
        "bash": bash_completion_fixture,
        "zsh": zsh_completion_fixture,
        "fish": fish_completion_fixture,
    }


class MockShellEnvironment:
    """Mock shell environment for testing completion behavior"""

    def __init__(self, shell_name: str):
        """
        Initialize mock shell environment.

        Args:
            shell_name: Name of the shell to mock
        """
        self.shell_name = shell_name
        self.env_vars = {}
        self.completion_functions = {}

    def set_env_var(self, name: str, value: str) -> None:
        """Set an environment variable in the mock shell"""
        self.env_vars[name] = value

    def register_completion_function(self, command: str, function) -> None:
        """Register a completion function for a command"""
        self.completion_functions[command] = function

    def simulate_completion(self, command_line: str) -> List[str]:
        """
        Simulate completion in the mock shell environment.

        Args:
            command_line: Command line to complete

        Returns:
            List of completion suggestions
        """
        parts = command_line.split()
        if not parts:
            return []

        command = parts[0]
        if command in self.completion_functions:
            return self.completion_functions[command](command_line)

        return []


def create_mock_argcomplete_environment():
    """Create a mock argcomplete environment for testing"""
    mock_env = {
        "COMP_LINE": "",
        "COMP_POINT": "0",
        "COMP_WORDS": "",
        "COMP_CWORD": "0",
        "_ARGCOMPLETE": "1",
        "_ARGCOMPLETE_COMP_WORDBREAKS": " \t\n\"'@><=;|&(",
        "_ARGCOMPLETE_IFS": "\013",
    }
    return mock_env


def simulate_argcomplete_completion(
    command_line: str, cursor_position: Optional[int] = None
) -> Dict:
    """
    Simulate argcomplete completion process.

    Args:
        command_line: Command line to complete
        cursor_position: Cursor position (defaults to end of line)

    Returns:
        Dictionary with completion simulation results
    """
    if cursor_position is None:
        cursor_position = len(command_line)

    # Set up argcomplete environment variables
    env = create_mock_argcomplete_environment()
    env["COMP_LINE"] = command_line
    env["COMP_POINT"] = str(cursor_position)

    # Parse command line into words
    words = command_line[:cursor_position].split()
    env["COMP_WORDS"] = " ".join(words)
    env["COMP_CWORD"] = str(len(words) - 1 if words else 0)

    return {
        "env": env,
        "command_line": command_line,
        "cursor_position": cursor_position,
        "words": words,
        "current_word": words[-1] if words else "",
        "previous_word": words[-2] if len(words) > 1 else "",
    }
