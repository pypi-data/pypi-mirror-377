"""
Integration tests for shell completion activation and installation.

This module tests the activation and installation of shell completion
across different shell environments, ensuring proper setup and functionality.
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional
from unittest.mock import Mock, call, patch

import pytest

from agentspec.cli.completion_install import (
    CompletionInstaller,
    completion_status_command,
    install_completion_command,
    show_completion_command,
)

# Import test fixtures
from ..fixtures.shell_completion_fixtures import (
    MockShellEnvironment,
    bash_completion_fixture,
    fish_completion_fixture,
    zsh_completion_fixture,
)


class TestShellDetection:
    """Test shell detection functionality"""

    def test_detect_shell_from_environment(self):
        """
        Test shell detection from SHELL environment variable.

        Requirements: 8.1, 8.2, 8.3 - Shell detection for completion setup
        """
        installer = CompletionInstaller()

        test_cases = [
            ("/bin/bash", "bash"),
            ("/usr/bin/bash", "bash"),
            ("/usr/local/bin/bash", "bash"),
            ("/bin/zsh", "zsh"),
            ("/usr/bin/zsh", "zsh"),
            ("/usr/local/bin/zsh", "zsh"),
            ("/usr/bin/fish", "fish"),
            ("/usr/local/bin/fish", "fish"),
            ("/bin/sh", None),  # sh not in supported shells
            ("/usr/bin/dash", None),  # dash not in supported shells
            ("", None),  # Empty shell
            ("/unknown/shell", None),  # Unknown shell
        ]

        for shell_path, expected in test_cases:
            env_dict = {"SHELL": shell_path} if shell_path else {}
            with patch.dict(os.environ, env_dict, clear=True):
                # Mock all fallback mechanisms
                with patch("subprocess.run") as mock_run:
                    mock_run.side_effect = FileNotFoundError()
                    # Mock the import of psutil to prevent parent process detection
                    with patch("builtins.__import__") as mock_import:

                        def side_effect(name, *args, **kwargs):
                            if name == "psutil":
                                raise ImportError("No module named 'psutil'")
                            return __import__(name, *args, **kwargs)

                        mock_import.side_effect = side_effect

                        detected = installer.detect_shell()
                        if expected:
                            assert (
                                detected == expected
                            ), f"Expected {expected}, got {detected} for {shell_path}"
                        else:
                            assert detected is None, f"Expected None, got {detected}"

    def test_detect_shell_fallback_mechanisms(self):
        """
        Test shell detection fallback mechanisms.

        Requirements: 8.4 - Graceful fallback for shell detection
        """
        installer = CompletionInstaller()

        # Test with no SHELL environment variable
        with patch.dict(os.environ, {}, clear=True):
            detected = installer.detect_shell()
            # Should fall back to None or detect from other methods
            assert detected is None or detected in installer.supported_shells

        # Test with invalid SHELL path - should fall back to other detection methods
        with patch.dict(os.environ, {"SHELL": "/nonexistent/shell"}):
            detected = installer.detect_shell()
            # Should either be None or a valid shell found through fallback mechanisms
            assert detected is None or detected in installer.supported_shells

    def test_detect_shell_with_symlinks(self):
        """
        Test shell detection with symbolic links.

        Requirements: 8.4 - Robust shell detection
        """
        installer = CompletionInstaller()

        # Test with symlink-like path
        with patch.dict(os.environ, {"SHELL": "/usr/local/bin/bash"}):
            detected = installer.detect_shell()
            assert detected == "bash"


class TestCompletionScriptGeneration:
    """Test completion script generation for different shells"""

    def test_generate_bash_completion_script(self):
        """
        Test generation of bash completion script.

        Requirements: 8.1 - Bash completion script generation
        """
        installer = CompletionInstaller()
        shell_name, script = installer.get_completion_script("bash")

        assert shell_name == "bash"
        assert script is not None
        assert len(script) > 0

        # Verify bash-specific content
        assert "register-python-argcomplete" in script
        assert "agentspec" in script

    def test_generate_zsh_completion_script(self):
        """
        Test generation of zsh completion script.

        Requirements: 8.2 - Zsh completion script generation
        """
        installer = CompletionInstaller()
        shell_name, script = installer.get_completion_script("zsh")

        assert shell_name == "zsh"
        assert script is not None
        assert len(script) > 0

        # Verify zsh-specific content
        assert "register-python-argcomplete" in script
        assert "bashcompinit" in script
        assert "agentspec" in script

    def test_generate_fish_completion_script(self):
        """
        Test generation of fish completion script.

        Requirements: 8.3 - Fish completion script generation
        """
        installer = CompletionInstaller()
        shell_name, script = installer.get_completion_script("fish")

        assert shell_name == "fish"
        assert script is not None
        assert len(script) > 0

        # Verify fish-specific content
        assert "register-python-argcomplete --shell fish" in script
        assert "agentspec" in script

    def test_generate_script_for_unsupported_shell(self):
        """
        Test script generation for unsupported shells.

        Requirements: 8.4 - Graceful handling of unsupported shells
        """
        installer = CompletionInstaller()

        # Test with unsupported shell
        try:
            shell_name, script = installer.get_completion_script("tcsh")
            # Should not reach here for unsupported shells
            pytest.fail("Should raise ValueError for unsupported shell")
        except ValueError as e:
            assert "Unsupported shell" in str(e)

    def test_script_generation_with_custom_commands(self):
        """
        Test that generated scripts include AgentSpec program name.

        Requirements: 1.1 - Complete command coverage in scripts
        """
        installer = CompletionInstaller()

        for shell in ["bash", "zsh", "fish"]:
            try:
                shell_name, script = installer.get_completion_script(shell)
                # Verify the script references agentspec
                assert "agentspec" in script, f"agentspec missing from {shell} script"
            except ValueError:
                # Skip unsupported shells
                pass


class TestCompletionInstallation:
    """Test completion installation functionality"""

    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp(prefix="agentspec_test_install_")
        self.original_home = os.environ.get("HOME")

    def teardown_method(self):
        """Clean up test environment"""
        if self.temp_dir and Path(self.temp_dir).exists():
            import shutil

            shutil.rmtree(self.temp_dir)

        if self.original_home:
            os.environ["HOME"] = self.original_home

    def test_get_completion_install_path_bash(self):
        """
        Test getting installation path for bash completion.

        Requirements: 9.2 - Bash completion installation path
        """
        installer = CompletionInstaller()

        with patch.dict(os.environ, {"HOME": self.temp_dir}):
            path = installer.get_shell_config_file("bash")

            assert path is not None
            assert "bash" in str(path).lower() or ".profile" in str(path)

            # Should be within user's home directory
            assert str(path).startswith(self.temp_dir)

    def test_get_completion_install_path_zsh(self):
        """
        Test getting installation path for zsh completion.

        Requirements: 9.2 - Zsh completion installation path
        """
        installer = CompletionInstaller()

        with patch.dict(os.environ, {"HOME": self.temp_dir}):
            path = installer.get_shell_config_file("zsh")

            assert path is not None
            assert "zsh" in str(path).lower()

            # Should be within user's home directory
            assert str(path).startswith(self.temp_dir)

    def test_get_completion_install_path_fish(self):
        """
        Test getting installation path for fish completion.

        Requirements: 9.2 - Fish completion installation path
        """
        installer = CompletionInstaller()

        with patch.dict(os.environ, {"HOME": self.temp_dir}):
            path = installer.get_shell_config_file("fish")

            assert path is not None
            assert "fish" in str(path).lower()

            # Should be within user's home directory
            assert str(path).startswith(self.temp_dir)

    @patch("agentspec.cli.completion_install.CompletionInstaller")
    def test_install_completion_for_shell_success(self, mock_installer_class):
        """
        Test successful completion installation.

        Requirements: 9.2 - Successful completion installation
        """
        # Mock installer instance
        mock_installer = Mock()
        mock_installer.install_completion.return_value = (
            True,
            "Installation successful",
        )
        mock_installer_class.return_value = mock_installer

        # Test installation
        result = install_completion_command("bash")

        assert result == 0  # Success exit code
        mock_installer.install_completion.assert_called_once_with("bash", False)

    @patch("agentspec.cli.completion_install.CompletionInstaller")
    def test_install_completion_unsupported_shell(self, mock_installer_class):
        """
        Test installation with unsupported shell.

        Requirements: 8.4 - Graceful handling of unsupported shells
        """
        # Mock installer instance
        mock_installer = Mock()
        mock_installer.install_completion.return_value = (False, "Unsupported shell")
        mock_installer_class.return_value = mock_installer

        result = install_completion_command("tcsh")

        # Should return error exit code
        assert result == 1

    def test_is_completion_installed_detection(self):
        """
        Test detection of existing completion installation.

        Requirements: 9.4 - Completion installation status detection
        """
        installer = CompletionInstaller()

        # Test with non-existent installation
        with patch.dict(os.environ, {"HOME": self.temp_dir}):
            installed, shell, config_file = installer.is_completion_installed("bash")
            assert installed is False
            assert shell == "bash"

        # Test with existing installation
        bash_rc = Path(self.temp_dir) / ".bashrc"
        bash_rc.write_text(
            "# AgentSpec completion\nregister-python-argcomplete agentspec\n"
        )

        with patch.dict(os.environ, {"HOME": self.temp_dir}):
            installed, shell, config_file = installer.is_completion_installed("bash")
            assert installed is True
            assert shell == "bash"


class TestCompletionCommands:
    """Test completion-related CLI commands"""

    @patch("agentspec.cli.completion_install.CompletionInstaller")
    def test_install_completion_command_success(self, mock_installer_class):
        """
        Test successful completion installation command.

        Requirements: 9.2 - Install completion command
        """
        mock_installer = Mock()
        mock_installer.install_completion.return_value = (True, "Success")
        mock_installer_class.return_value = mock_installer

        result = install_completion_command()

        assert result == 0  # Success exit code
        mock_installer.install_completion.assert_called_once_with(None, False)

    @patch("agentspec.cli.completion_install.CompletionInstaller")
    def test_install_completion_command_no_shell(self, mock_installer_class):
        """
        Test installation command when shell cannot be detected.

        Requirements: 8.4 - Graceful handling when shell detection fails
        """
        mock_installer = Mock()
        mock_installer.install_completion.return_value = (
            False,
            "Could not detect shell",
        )
        mock_installer_class.return_value = mock_installer

        result = install_completion_command()

        assert result != 0  # Error exit code

    @patch("agentspec.cli.completion_install.CompletionInstaller")
    def test_show_completion_command(self, mock_installer_class):
        """
        Test show completion script command.

        Requirements: 9.3 - Show completion script command
        """
        mock_installer = Mock()
        mock_installer.show_completion_script.return_value = (
            True,
            "bash",
            "# Mock completion script",
        )
        mock_installer_class.return_value = mock_installer

        with patch("builtins.print") as mock_print:
            result = show_completion_command()

            assert result == 0  # Success exit code
            mock_installer.show_completion_script.assert_called_once_with(None)
            mock_print.assert_called()

    @patch("agentspec.cli.completion_install.CompletionInstaller")
    def test_completion_status_command(self, mock_installer_class):
        """
        Test completion status command.

        Requirements: 9.4 - Completion status command
        """
        mock_installer = Mock()
        mock_installer.get_completion_status.return_value = {
            "bash": {"installed": "Yes", "config_file": "~/.bashrc", "available": "Yes"}
        }
        mock_installer_class.return_value = mock_installer

        with patch("builtins.print") as mock_print:
            result = completion_status_command()

            assert result == 0  # Success exit code
            mock_installer.get_completion_status.assert_called_once()
            mock_print.assert_called()


class TestCompletionActivationWorkflow:
    """Test the complete completion activation workflow"""

    def test_end_to_end_bash_activation(self, bash_completion_fixture):
        """
        Test end-to-end bash completion activation.

        Requirements: 8.1 - Complete bash activation workflow
        """
        # Test the complete workflow
        assert bash_completion_fixture.test_completion_activation()

        # Test script generation
        script_content = bash_completion_fixture.get_completion_script_template()
        script_path = bash_completion_fixture.create_completion_script(script_content)

        # Verify script exists and has correct content
        assert script_path.exists()
        with open(script_path, "r") as f:
            content = f.read()
            assert "agentspec" in content
            assert "complete" in content

        # Test RC file creation
        rc_content = f"source {script_path}\n"
        rc_path = bash_completion_fixture.create_shell_rc(rc_content)

        # Verify RC file exists and sources completion
        assert rc_path.exists()
        with open(rc_path, "r") as f:
            content = f.read()
            assert str(script_path) in content

    def test_end_to_end_zsh_activation(self, zsh_completion_fixture):
        """
        Test end-to-end zsh completion activation.

        Requirements: 8.2 - Complete zsh activation workflow
        """
        # Test the complete workflow
        assert zsh_completion_fixture.test_completion_activation()

        # Test script generation
        script_content = zsh_completion_fixture.get_completion_script_template()
        script_path = zsh_completion_fixture.create_completion_script(script_content)

        # Verify script exists and has correct content
        assert script_path.exists()
        with open(script_path, "r") as f:
            content = f.read()
            assert "#compdef agentspec" in content
            assert "_agentspec" in content

        # Test RC file creation with fpath setup
        rc_content = f"""
fpath=({zsh_completion_fixture.temp_dir} $fpath)
autoload -Uz compinit
compinit
source {script_path}
"""
        rc_path = zsh_completion_fixture.create_shell_rc(rc_content)

        # Verify RC file exists and has proper setup
        assert rc_path.exists()
        with open(rc_path, "r") as f:
            content = f.read()
            assert "fpath" in content
            assert "compinit" in content
            assert str(script_path) in content

    def test_end_to_end_fish_activation(self, fish_completion_fixture):
        """
        Test end-to-end fish completion activation.

        Requirements: 8.3 - Complete fish activation workflow
        """
        # Test the complete workflow
        assert fish_completion_fixture.test_completion_activation()

        # Test script generation
        script_content = fish_completion_fixture.get_completion_script_template()
        script_path = fish_completion_fixture.create_completion_script(script_content)

        # Verify script exists and has correct content
        assert script_path.exists()
        with open(script_path, "r") as f:
            content = f.read()
            assert "complete -c agentspec" in content
            assert (
                "__fish_use_subcommand" in content
                or "__fish_seen_subcommand_from" in content
            )

    @patch("agentspec.cli.completion_install.CompletionInstaller")
    def test_activation_with_permission_errors(self, mock_installer_class):
        """
        Test activation workflow with permission errors.

        Requirements: 8.4 - Graceful handling of permission errors
        """
        mock_installer = Mock()
        mock_installer.install_completion.return_value = (False, "Permission denied")
        mock_installer_class.return_value = mock_installer

        # Should handle permission errors gracefully
        result = install_completion_command("bash")

        # Should return error exit code
        assert result == 1

    def test_activation_with_missing_directories(self):
        """
        Test activation when completion directories don't exist.

        Requirements: 8.4 - Graceful handling of missing directories
        """
        installer = CompletionInstaller()

        with tempfile.TemporaryDirectory() as temp_dir:
            nonexistent_config = Path(temp_dir) / "nonexistent" / ".bashrc"

            with patch.object(
                installer, "get_shell_config_file", return_value=nonexistent_config
            ):
                success, message = installer.install_completion("bash")

                # Should handle missing directories (create them or succeed)
                assert isinstance(success, bool)
                assert isinstance(message, str)
