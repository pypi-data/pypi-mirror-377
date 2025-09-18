"""
Completion installation utilities for AgentSpec CLI.

This module provides functionality to install, show, and check the status of
shell completion for the AgentSpec CLI using argcomplete.
"""

import os
import subprocess  # nosec B404
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

try:
    import argcomplete  # noqa: F401

    ARGCOMPLETE_AVAILABLE = True
except ImportError:
    ARGCOMPLETE_AVAILABLE = False


class CompletionInstaller:
    """Handles installation and management of shell completion for AgentSpec CLI"""

    def __init__(self, program_name: str = "agentspec") -> None:
        """
        Initialize completion installer.

        Args:
            program_name: Name of the program for completion registration
        """
        self.program_name = program_name
        self.supported_shells = ["bash", "zsh", "fish"]

    def detect_shell(self) -> Optional[str]:
        """
        Detect the current shell environment.

        Returns:
            Shell name (bash, zsh, fish) or None if not detected/supported
        """
        # Try to detect from SHELL environment variable
        shell_path = os.environ.get("SHELL", "")
        if shell_path:
            shell_name = Path(shell_path).name
            if shell_name in self.supported_shells:
                return shell_name

        # Try to detect from parent process
        try:
            # Get parent process name
            import psutil

            parent = psutil.Process().parent()
            if parent:
                parent_name = str(parent.name())
                if parent_name in self.supported_shells:
                    return parent_name
        except (ImportError, Exception):
            pass

        # Fallback: try common shell detection methods
        for shell in self.supported_shells:
            try:
                result = subprocess.run(
                    [shell, "--version"], capture_output=True, text=True, timeout=2
                )
                if result.returncode == 0:
                    return shell
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue

        return None

    def get_completion_script(self, shell: Optional[str] = None) -> Tuple[str, str]:
        """
        Get the completion script for the specified shell.

        Args:
            shell: Shell name (bash, zsh, fish). If None, auto-detect.

        Returns:
            Tuple of (shell_name, completion_script)

        Raises:
            ValueError: If shell is not supported or argcomplete is not available
        """
        if not ARGCOMPLETE_AVAILABLE:
            raise ValueError(
                "argcomplete is not available. Please install it with: pip install argcomplete"
            )

        if shell is None:
            shell = self.detect_shell()
            if shell is None:
                raise ValueError(
                    "Could not detect shell. Please specify shell explicitly."
                )

        if shell not in self.supported_shells:
            raise ValueError(
                f"Unsupported shell: {shell}. Supported shells: {', '.join(self.supported_shells)}"
            )

        # Generate completion script using argcomplete
        if shell == "bash":
            script = f'eval "$(register-python-argcomplete {self.program_name})"'
        elif shell == "zsh":
            # For zsh, we need to enable bash completion compatibility first
            script = f"""# Enable bash completion compatibility
autoload -U +X bashcompinit && bashcompinit
eval "$(register-python-argcomplete {self.program_name})" """
        elif shell == "fish":
            script = (
                f"register-python-argcomplete --shell fish {self.program_name} | source"
            )
        else:
            raise ValueError(f"Unsupported shell: {shell}")

        return shell, script

    def get_shell_config_file(self, shell: str) -> Optional[Path]:
        """
        Get the shell configuration file path for the given shell.

        Args:
            shell: Shell name (bash, zsh, fish)

        Returns:
            Path to shell config file or None if not found
        """
        home = Path.home()

        if shell == "bash":
            # Try common bash config files in order of preference
            candidates = [home / ".bashrc", home / ".bash_profile", home / ".profile"]
        elif shell == "zsh":
            candidates = [home / ".zshrc", home / ".zprofile"]
        elif shell == "fish":
            candidates = [home / ".config" / "fish" / "config.fish"]
        else:
            return None

        # Return the first existing file, or the first candidate if none exist
        for candidate in candidates:
            if candidate.exists():
                return candidate

        return candidates[0] if candidates else None

    def is_completion_installed(
        self, shell: Optional[str] = None
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Check if completion is already installed for the given shell.

        Args:
            shell: Shell name. If None, auto-detect.

        Returns:
            Tuple of (is_installed, shell_name, config_file_path)
        """
        if shell is None:
            shell = self.detect_shell()
            if shell is None:
                return False, "unknown", None

        config_file = self.get_shell_config_file(shell)
        if not config_file or not config_file.exists():
            return False, shell, str(config_file) if config_file else None

        try:
            content = config_file.read_text()
            # Check if our completion is already registered
            is_installed = (
                f"register-python-argcomplete {self.program_name}" in content
                or f"register-python-argcomplete --shell fish {self.program_name}"
                in content
            )
            return is_installed, shell, str(config_file)
        except Exception:
            return False, shell, str(config_file)

    def install_completion(
        self, shell: Optional[str] = None, force: bool = False
    ) -> Tuple[bool, str]:
        """
        Install completion for the specified shell.

        Args:
            shell: Shell name. If None, auto-detect.
            force: Force installation even if already installed

        Returns:
            Tuple of (success, message)
        """
        try:
            # Check if argcomplete is available
            if not ARGCOMPLETE_AVAILABLE:
                return (
                    False,
                    "argcomplete is not available. Please install it with: pip install argcomplete",
                )

            # Detect shell if not specified
            if shell is None:
                shell = self.detect_shell()
                if shell is None:
                    return (
                        False,
                        "Could not detect shell. Please specify shell with --shell option.",
                    )

            # Check if already installed
            (
                is_installed,
                detected_shell,
                config_file_path,
            ) = self.is_completion_installed(shell)
            if is_installed and not force:
                return (
                    True,
                    f"Completion is already installed for {detected_shell} in {config_file_path}",
                )

            # Get completion script
            shell_name, script = self.get_completion_script(shell)

            # Get config file path
            config_file = self.get_shell_config_file(shell_name)
            if not config_file:
                return False, f"Could not determine config file for {shell_name}"

            # Create config file directory if it doesn't exist
            config_file.parent.mkdir(parents=True, exist_ok=True)

            # Add completion script to config file
            completion_block = f"""
# AgentSpec CLI completion (added by agentspec --install-completion)
{script}
"""

            if config_file.exists():
                content = config_file.read_text()
                if f"register-python-argcomplete {self.program_name}" not in content:
                    # Append to existing file
                    with open(config_file, "a") as f:
                        f.write(completion_block)
                else:
                    return (
                        True,
                        f"Completion is already installed for {shell_name} in {config_file}",
                    )
            else:
                # Create new config file
                config_file.write_text(completion_block)

            return (
                True,
                f"Completion installed for {shell_name}. Restart your shell or run: source {config_file}",
            )

        except Exception as e:
            return False, f"Failed to install completion: {e}"

    def show_completion_script(
        self, shell: Optional[str] = None
    ) -> Tuple[bool, str, str]:
        """
        Show the completion script for manual installation.

        Args:
            shell: Shell name. If None, auto-detect.

        Returns:
            Tuple of (success, shell_name, script_content)
        """
        try:
            shell_name, script = self.get_completion_script(shell)
            return True, shell_name, script
        except Exception as e:
            return False, "unknown", f"Error: {e}"

    def get_completion_status(self) -> Dict[str, Dict[str, str]]:
        """
        Get completion installation status for all supported shells.

        Returns:
            Dictionary with status information for each shell
        """
        status = {}

        for shell in self.supported_shells:
            try:
                is_installed, shell_name, config_file = self.is_completion_installed(
                    shell
                )
                status[shell] = {
                    "installed": "Yes" if is_installed else "No",
                    "config_file": config_file or "Not found",
                    "available": "Yes" if self.detect_shell() == shell else "No",
                }
            except Exception as e:
                status[shell] = {
                    "installed": "Error",
                    "config_file": f"Error: {e}",
                    "available": "Unknown",
                }

        return status


def install_completion_command(shell: Optional[str] = None, force: bool = False) -> int:
    """
    Command handler for --install-completion option.

    Args:
        shell: Shell name for installation
        force: Force installation even if already installed

    Returns:
        Exit code (0 for success, 1 for error)
    """
    installer = CompletionInstaller()
    success, message = installer.install_completion(shell, force)

    if success:
        print(f"✅ {message}")
        return 0
    else:
        print(f"❌ {message}", file=sys.stderr)
        return 1


def show_completion_command(shell: Optional[str] = None) -> int:
    """
    Command handler for --show-completion option.

    Args:
        shell: Shell name to show script for

    Returns:
        Exit code (0 for success, 1 for error)
    """
    installer = CompletionInstaller()
    success, shell_name, script = installer.show_completion_script(shell)

    if success:
        print(f"# Completion script for {shell_name}")
        print(f"# Add this to your {shell_name} configuration file:")
        print()
        print(script)
        return 0
    else:
        print(f"❌ {script}", file=sys.stderr)
        return 1


def completion_status_command() -> int:
    """
    Command handler for --completion-status option.

    Returns:
        Exit code (always 0)
    """
    installer = CompletionInstaller()
    status = installer.get_completion_status()

    print("AgentSpec CLI Completion Status")
    print("=" * 40)

    for shell, info in status.items():
        print(f"\n{shell.upper()}:")
        print(f"  Installed: {info['installed']}")
        print(f"  Config file: {info['config_file']}")
        print(f"  Current shell: {info['available']}")

    print("\nTo install completion:")
    print("  agentspec --install-completion")
    print("\nTo show completion script:")
    print("  agentspec --show-completion")

    return 0
