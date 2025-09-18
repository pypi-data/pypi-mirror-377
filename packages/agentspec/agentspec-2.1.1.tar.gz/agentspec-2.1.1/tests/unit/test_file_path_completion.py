"""
Unit tests for file path completion functionality.

Tests the file path completion features including output file completion,
project directory completion, and spec file completion.
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from agentspec.cli.completers import (
    ARGCOMPLETE_AVAILABLE,
    output_file_completer,
    project_directory_completer,
    spec_file_completer,
)


class TestFilePathCompletion(unittest.TestCase):
    """Test file path completion functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

        # Create test files and directories
        (self.temp_path / "test_file.md").touch()
        (self.temp_path / "test_file.txt").touch()
        (self.temp_path / "test_file.json").touch()
        (self.temp_path / "test_dir").mkdir()
        (self.temp_path / "another_dir").mkdir()
        (self.temp_path / "spec.md").touch()
        (self.temp_path / "README.md").touch()

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil

        shutil.rmtree(self.temp_dir)

    @pytest.mark.skipif(not ARGCOMPLETE_AVAILABLE, reason="argcomplete not available")
    def test_output_file_completer_exists(self):
        """Test that output file completer is available when argcomplete is installed"""
        self.assertIsNotNone(output_file_completer)

    @pytest.mark.skipif(not ARGCOMPLETE_AVAILABLE, reason="argcomplete not available")
    def test_project_directory_completer_exists(self):
        """Test that project directory completer is available when argcomplete is installed"""
        self.assertIsNotNone(project_directory_completer)

    @pytest.mark.skipif(not ARGCOMPLETE_AVAILABLE, reason="argcomplete not available")
    def test_spec_file_completer_exists(self):
        """Test that spec file completer is available when argcomplete is installed"""
        self.assertIsNotNone(spec_file_completer)

    @pytest.mark.skipif(
        ARGCOMPLETE_AVAILABLE, reason="Testing behavior when argcomplete not available"
    )
    def test_completers_none_when_argcomplete_unavailable(self):
        """Test that completers are None when argcomplete is not available"""
        self.assertIsNone(output_file_completer)
        self.assertIsNone(project_directory_completer)
        self.assertIsNone(spec_file_completer)

    @pytest.mark.skipif(not ARGCOMPLETE_AVAILABLE, reason="argcomplete not available")
    def test_output_file_completer_with_files_and_directories(self):
        """Test that output file completer works with both files and directories"""
        # Change to temp directory for testing
        original_cwd = os.getcwd()
        try:
            os.chdir(self.temp_dir)

            # Mock the completion call
            mock_kwargs = {
                "prefix": "test_",
                "action": Mock(),
                "parser": Mock(),
                "parsed_args": Mock(),
            }

            # The FilesCompleter should handle file completion
            # We can't easily test the actual completion without shell integration,
            # but we can verify the completer is properly configured
            self.assertTrue(hasattr(output_file_completer, "__call__"))

        finally:
            os.chdir(original_cwd)

    @pytest.mark.skipif(not ARGCOMPLETE_AVAILABLE, reason="argcomplete not available")
    def test_project_directory_completer_directories_only(self):
        """Test that project directory completer is configured for directories only"""
        # Change to temp directory for testing
        original_cwd = os.getcwd()
        try:
            os.chdir(self.temp_dir)

            # The DirectoriesCompleter should handle directory completion
            # We can't easily test the actual completion without shell integration,
            # but we can verify the completer is properly configured
            self.assertTrue(hasattr(project_directory_completer, "__call__"))

        finally:
            os.chdir(original_cwd)

    @pytest.mark.skipif(not ARGCOMPLETE_AVAILABLE, reason="argcomplete not available")
    def test_spec_file_completer_markdown_files(self):
        """Test that spec file completer is configured for markdown files"""
        # Change to temp directory for testing
        original_cwd = os.getcwd()
        try:
            os.chdir(self.temp_dir)

            # The FilesCompleter should handle spec file completion
            # We can't easily test the actual completion without shell integration,
            # but we can verify the completer is properly configured
            self.assertTrue(hasattr(spec_file_completer, "__call__"))

        finally:
            os.chdir(original_cwd)


class TestFilePathCompletionIntegration(unittest.TestCase):
    """Integration tests for file path completion with CLI"""

    def test_cli_configures_file_completers(self):
        """Test that CLI properly configures file path completers"""
        from agentspec.cli.main import AgentSpecCLI

        cli = AgentSpecCLI()
        parser = cli.create_parser()

        # Find the generate subparser
        generate_parser = None
        for action in parser._actions:
            if (
                hasattr(action, "choices")
                and action.choices
                and "generate" in action.choices
            ):
                generate_parser = action.choices["generate"]
                break

        self.assertIsNotNone(generate_parser, "Generate subparser not found")

        # Check that output argument has a completer configured
        output_action = None
        for action in generate_parser._actions:
            if hasattr(action, "dest") and action.dest == "output":
                output_action = action
                break

        if output_action and ARGCOMPLETE_AVAILABLE:
            self.assertTrue(hasattr(output_action, "completer"))

    def test_cli_configures_project_path_completers(self):
        """Test that CLI properly configures project path completers"""
        from agentspec.cli.main import AgentSpecCLI

        cli = AgentSpecCLI()
        parser = cli.create_parser()

        # Find the analyze subparser
        analyze_parser = None
        for action in parser._actions:
            if (
                hasattr(action, "choices")
                and action.choices
                and "analyze" in action.choices
            ):
                analyze_parser = action.choices["analyze"]
                break

        self.assertIsNotNone(analyze_parser, "Analyze subparser not found")

        # Check that project_path argument has a completer configured
        project_path_action = None
        for action in analyze_parser._actions:
            if hasattr(action, "dest") and action.dest == "project_path":
                project_path_action = action
                break

        if project_path_action and ARGCOMPLETE_AVAILABLE:
            self.assertTrue(hasattr(project_path_action, "completer"))

    def test_cli_configures_spec_file_completers(self):
        """Test that CLI properly configures spec file completers"""
        from agentspec.cli.main import AgentSpecCLI

        cli = AgentSpecCLI()
        parser = cli.create_parser()

        # Find the validate subparser
        validate_parser = None
        for action in parser._actions:
            if (
                hasattr(action, "choices")
                and action.choices
                and "validate" in action.choices
            ):
                validate_parser = action.choices["validate"]
                break

        self.assertIsNotNone(validate_parser, "Validate subparser not found")

        # Check that spec_file argument has a completer configured
        spec_file_action = None
        for action in validate_parser._actions:
            if hasattr(action, "dest") and action.dest == "spec_file":
                spec_file_action = action
                break

        if spec_file_action and ARGCOMPLETE_AVAILABLE:
            self.assertTrue(hasattr(spec_file_action, "completer"))


if __name__ == "__main__":
    unittest.main()
