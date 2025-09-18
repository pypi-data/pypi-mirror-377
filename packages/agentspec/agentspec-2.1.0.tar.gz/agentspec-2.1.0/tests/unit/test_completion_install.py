"""
Unit tests for completion installation functionality.

Tests the CompletionInstaller class and related command handlers for installing,
showing, and checking the status of shell completion.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest

from agentspec.cli.completion_install import (
    CompletionInstaller,
    completion_status_command,
    install_completion_command,
    show_completion_command,
)


class TestCompletionInstaller:
    """Test cases for CompletionInstaller class"""

    def setup_method(self):
        """Set up test fixtures"""
        self.installer = CompletionInstaller("test-program")

    def test_init(self):
        """Test CompletionInstaller initialization"""
        installer = CompletionInstaller("my-program")
        assert installer.program_name == "my-program"
        assert installer.supported_shells == ["bash", "zsh", "fish"]

    def test_init_default_program_name(self):
        """Test CompletionInstaller with default program name"""
        installer = CompletionInstaller()
        assert installer.program_name == "agentspec"

    @patch.dict(os.environ, {"SHELL": "/bin/bash"})
    def test_detect_shell_from_env(self):
        """Test shell detection from SHELL environment variable"""
        shell = self.installer.detect_shell()
        assert shell == "bash"

    @patch.dict(os.environ, {"SHELL": "/usr/bin/zsh"})
    def test_detect_shell_zsh_from_env(self):
        """Test zsh detection from SHELL environment variable"""
        shell = self.installer.detect_shell()
        assert shell == "zsh"

    @patch.dict(os.environ, {"SHELL": "/usr/local/bin/fish"})
    def test_detect_shell_fish_from_env(self):
        """Test fish detection from SHELL environment variable"""
        shell = self.installer.detect_shell()
        assert shell == "fish"

    @patch.dict(os.environ, {"SHELL": "/bin/sh"}, clear=True)
    def test_detect_shell_unsupported(self):
        """Test detection with unsupported shell"""
        with patch("subprocess.run") as mock_run:
            with patch(
                "builtins.__import__",
                side_effect=ImportError("No module named 'psutil'"),
            ):
                # Mock subprocess calls to fail
                mock_run.side_effect = FileNotFoundError()
                shell = self.installer.detect_shell()
                assert shell is None

    @patch("agentspec.cli.completion_install.ARGCOMPLETE_AVAILABLE", True)
    def test_get_completion_script_bash(self):
        """Test getting completion script for bash"""
        shell, script = self.installer.get_completion_script("bash")
        assert shell == "bash"
        assert 'eval "$(register-python-argcomplete test-program)"' in script

    @patch("agentspec.cli.completion_install.ARGCOMPLETE_AVAILABLE", True)
    def test_get_completion_script_zsh(self):
        """Test getting completion script for zsh"""
        shell, script = self.installer.get_completion_script("zsh")
        assert shell == "zsh"
        assert "autoload -U +X bashcompinit && bashcompinit" in script
        assert 'eval "$(register-python-argcomplete test-program)"' in script

    @patch("agentspec.cli.completion_install.ARGCOMPLETE_AVAILABLE", True)
    def test_get_completion_script_fish(self):
        """Test getting completion script for fish"""
        shell, script = self.installer.get_completion_script("fish")
        assert shell == "fish"
        assert (
            "register-python-argcomplete --shell fish test-program | source" in script
        )

    @patch("agentspec.cli.completion_install.ARGCOMPLETE_AVAILABLE", False)
    def test_get_completion_script_no_argcomplete(self):
        """Test getting completion script when argcomplete is not available"""
        with pytest.raises(ValueError, match="argcomplete is not available"):
            self.installer.get_completion_script("bash")

    @patch("agentspec.cli.completion_install.ARGCOMPLETE_AVAILABLE", True)
    def test_get_completion_script_unsupported_shell(self):
        """Test getting completion script for unsupported shell"""
        with pytest.raises(ValueError, match="Unsupported shell: tcsh"):
            self.installer.get_completion_script("tcsh")

    @patch("agentspec.cli.completion_install.ARGCOMPLETE_AVAILABLE", True)
    def test_get_completion_script_auto_detect(self):
        """Test getting completion script with auto-detection"""
        with patch.object(self.installer, "detect_shell", return_value="bash"):
            shell, script = self.installer.get_completion_script()
            assert shell == "bash"
            assert "register-python-argcomplete test-program" in script

    @patch("agentspec.cli.completion_install.ARGCOMPLETE_AVAILABLE", True)
    def test_get_completion_script_auto_detect_fail(self):
        """Test getting completion script when auto-detection fails"""
        with patch.object(self.installer, "detect_shell", return_value=None):
            with pytest.raises(ValueError, match="Could not detect shell"):
                self.installer.get_completion_script()

    def test_get_shell_config_file_bash(self):
        """Test getting bash config file path"""
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir)
            bashrc = home / ".bashrc"
            bashrc.touch()

            with patch("pathlib.Path.home", return_value=home):
                config_file = self.installer.get_shell_config_file("bash")
                assert config_file == bashrc

    def test_get_shell_config_file_zsh(self):
        """Test getting zsh config file path"""
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir)
            zshrc = home / ".zshrc"
            zshrc.touch()

            with patch("pathlib.Path.home", return_value=home):
                config_file = self.installer.get_shell_config_file("zsh")
                assert config_file == zshrc

    def test_get_shell_config_file_fish(self):
        """Test getting fish config file path"""
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir)
            fish_config_dir = home / ".config" / "fish"
            fish_config_dir.mkdir(parents=True)
            fish_config = fish_config_dir / "config.fish"
            fish_config.touch()

            with patch("pathlib.Path.home", return_value=home):
                config_file = self.installer.get_shell_config_file("fish")
                assert config_file == fish_config

    def test_get_shell_config_file_no_existing(self):
        """Test getting config file path when none exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir)

            with patch("pathlib.Path.home", return_value=home):
                config_file = self.installer.get_shell_config_file("bash")
                assert config_file == home / ".bashrc"

    def test_get_shell_config_file_unsupported(self):
        """Test getting config file for unsupported shell"""
        config_file = self.installer.get_shell_config_file("tcsh")
        assert config_file is None

    def test_is_completion_installed_not_installed(self):
        """Test checking completion status when not installed"""
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir)
            bashrc = home / ".bashrc"
            bashrc.write_text("# Some other content\n")

            with patch("pathlib.Path.home", return_value=home):
                (
                    is_installed,
                    shell,
                    config_file,
                ) = self.installer.is_completion_installed("bash")
                assert not is_installed
                assert shell == "bash"
                assert config_file == str(bashrc)

    def test_is_completion_installed_already_installed(self):
        """Test checking completion status when already installed"""
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir)
            bashrc = home / ".bashrc"
            bashrc.write_text('eval "$(register-python-argcomplete test-program)"\n')

            with patch("pathlib.Path.home", return_value=home):
                (
                    is_installed,
                    shell,
                    config_file,
                ) = self.installer.is_completion_installed("bash")
                assert is_installed
                assert shell == "bash"
                assert config_file == str(bashrc)

    def test_is_completion_installed_fish_format(self):
        """Test checking completion status for fish shell format"""
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir)
            fish_config_dir = home / ".config" / "fish"
            fish_config_dir.mkdir(parents=True)
            fish_config = fish_config_dir / "config.fish"
            fish_config.write_text(
                "register-python-argcomplete --shell fish test-program | source\n"
            )

            with patch("pathlib.Path.home", return_value=home):
                (
                    is_installed,
                    shell,
                    config_file,
                ) = self.installer.is_completion_installed("fish")
                assert is_installed
                assert shell == "fish"
                assert config_file == str(fish_config)

    def test_is_completion_installed_no_config_file(self):
        """Test checking completion status when config file doesn't exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir)

            with patch("pathlib.Path.home", return_value=home):
                (
                    is_installed,
                    shell,
                    config_file,
                ) = self.installer.is_completion_installed("bash")
                assert not is_installed
                assert shell == "bash"
                assert config_file == str(home / ".bashrc")

    def test_is_completion_installed_auto_detect(self):
        """Test checking completion status with auto-detection"""
        with patch.object(self.installer, "detect_shell", return_value="bash"):
            with patch.object(
                self.installer, "get_shell_config_file", return_value=None
            ):
                (
                    is_installed,
                    shell,
                    config_file,
                ) = self.installer.is_completion_installed()
                assert not is_installed
                assert shell == "bash"
                assert config_file is None

    @patch("agentspec.cli.completion_install.ARGCOMPLETE_AVAILABLE", True)
    def test_install_completion_success(self):
        """Test successful completion installation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir)
            bashrc = home / ".bashrc"
            bashrc.write_text("# Existing content\n")

            with patch("pathlib.Path.home", return_value=home):
                success, message = self.installer.install_completion("bash")
                assert success
                assert "Completion installed for bash" in message

                # Check that completion was added to file
                content = bashrc.read_text()
                assert "register-python-argcomplete test-program" in content

    @patch("agentspec.cli.completion_install.ARGCOMPLETE_AVAILABLE", True)
    def test_install_completion_already_installed(self):
        """Test installation when completion is already installed"""
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir)
            bashrc = home / ".bashrc"
            bashrc.write_text('eval "$(register-python-argcomplete test-program)"\n')

            with patch("pathlib.Path.home", return_value=home):
                success, message = self.installer.install_completion("bash")
                assert success
                assert "already installed" in message

    @patch("agentspec.cli.completion_install.ARGCOMPLETE_AVAILABLE", True)
    def test_install_completion_force_reinstall(self):
        """Test forced reinstallation of completion"""
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir)
            bashrc = home / ".bashrc"
            bashrc.write_text('eval "$(register-python-argcomplete test-program)"\n')

            with patch("pathlib.Path.home", return_value=home):
                success, message = self.installer.install_completion("bash", force=True)
                assert success
                assert "already installed" in message

    @patch("agentspec.cli.completion_install.ARGCOMPLETE_AVAILABLE", False)
    def test_install_completion_no_argcomplete(self):
        """Test installation when argcomplete is not available"""
        success, message = self.installer.install_completion("bash")
        assert not success
        assert "argcomplete is not available" in message

    @patch("agentspec.cli.completion_install.ARGCOMPLETE_AVAILABLE", True)
    def test_install_completion_auto_detect_fail(self):
        """Test installation when shell auto-detection fails"""
        with patch.object(self.installer, "detect_shell", return_value=None):
            success, message = self.installer.install_completion()
            assert not success
            assert "Could not detect shell" in message

    @patch("agentspec.cli.completion_install.ARGCOMPLETE_AVAILABLE", True)
    def test_show_completion_script_success(self):
        """Test showing completion script successfully"""
        success, shell, script = self.installer.show_completion_script("bash")
        assert success
        assert shell == "bash"
        assert "register-python-argcomplete test-program" in script

    @patch("agentspec.cli.completion_install.ARGCOMPLETE_AVAILABLE", False)
    def test_show_completion_script_no_argcomplete(self):
        """Test showing completion script when argcomplete is not available"""
        success, shell, script = self.installer.show_completion_script("bash")
        assert not success
        assert shell == "unknown"
        assert "argcomplete is not available" in script

    def test_get_completion_status(self):
        """Test getting completion status for all shells"""
        with patch.object(self.installer, "is_completion_installed") as mock_check:
            with patch.object(self.installer, "detect_shell", return_value="bash"):
                mock_check.side_effect = [
                    (True, "bash", "/home/user/.bashrc"),
                    (False, "zsh", "/home/user/.zshrc"),
                    (False, "fish", None),
                ]

                status = self.installer.get_completion_status()

                assert len(status) == 3
                assert status["bash"]["installed"] == "Yes"
                assert status["bash"]["available"] == "Yes"
                assert status["zsh"]["installed"] == "No"
                assert status["zsh"]["available"] == "No"
                assert status["fish"]["installed"] == "No"


class TestCompletionCommands:
    """Test cases for completion command handlers"""

    @patch("agentspec.cli.completion_install.CompletionInstaller")
    def test_install_completion_command_success(self, mock_installer_class):
        """Test install completion command success"""
        mock_installer = Mock()
        mock_installer.install_completion.return_value = (
            True,
            "Installation successful",
        )
        mock_installer_class.return_value = mock_installer

        with patch("builtins.print") as mock_print:
            result = install_completion_command()
            assert result == 0
            mock_print.assert_called_once_with("✅ Installation successful")

    @patch("agentspec.cli.completion_install.CompletionInstaller")
    def test_install_completion_command_failure(self, mock_installer_class):
        """Test install completion command failure"""
        mock_installer = Mock()
        mock_installer.install_completion.return_value = (False, "Installation failed")
        mock_installer_class.return_value = mock_installer

        with patch("builtins.print") as mock_print:
            result = install_completion_command()
            assert result == 1
            mock_print.assert_called_once()

    @patch("agentspec.cli.completion_install.CompletionInstaller")
    def test_show_completion_command_success(self, mock_installer_class):
        """Test show completion command success"""
        mock_installer = Mock()
        mock_installer.show_completion_script.return_value = (
            True,
            "bash",
            "completion script",
        )
        mock_installer_class.return_value = mock_installer

        with patch("builtins.print") as mock_print:
            result = show_completion_command()
            assert result == 0
            assert mock_print.call_count >= 3  # Multiple print calls for formatting

    @patch("agentspec.cli.completion_install.CompletionInstaller")
    def test_show_completion_command_failure(self, mock_installer_class):
        """Test show completion command failure"""
        mock_installer = Mock()
        mock_installer.show_completion_script.return_value = (
            False,
            "unknown",
            "Error message",
        )
        mock_installer_class.return_value = mock_installer

        with patch("builtins.print") as mock_print:
            result = show_completion_command()
            assert result == 1
            mock_print.assert_called_once()

    @patch("agentspec.cli.completion_install.CompletionInstaller")
    def test_completion_status_command(self, mock_installer_class):
        """Test completion status command"""
        mock_installer = Mock()
        mock_installer.get_completion_status.return_value = {
            "bash": {
                "installed": "Yes",
                "config_file": "/home/user/.bashrc",
                "available": "Yes",
            },
            "zsh": {"installed": "No", "config_file": "Not found", "available": "No"},
            "fish": {"installed": "No", "config_file": "Not found", "available": "No"},
        }
        mock_installer_class.return_value = mock_installer

        with patch("builtins.print") as mock_print:
            result = completion_status_command()
            assert result == 0
            assert mock_print.call_count >= 5  # Multiple print calls for status display
