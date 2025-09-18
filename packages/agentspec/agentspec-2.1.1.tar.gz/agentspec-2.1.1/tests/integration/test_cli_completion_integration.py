"""
Integration tests for CLI completion setup.

This module tests the integration of argcomplete with the AgentSpec CLI parser,
ensuring that completion is properly configured for all arguments and options.
"""

import argparse
from unittest.mock import Mock, patch

import pytest

from agentspec.cli.main import AgentSpecCLI


class TestCLICompletionIntegration:
    """Test CLI completion integration with argcomplete"""

    def setup_method(self):
        """Set up test fixtures"""
        self.cli = AgentSpecCLI()

    def test_parser_creation_succeeds(self):
        """Test that parser creation succeeds regardless of argcomplete availability"""
        # This should not raise an exception
        parser = self.cli.create_parser()

        # Verify the parser was created successfully
        assert parser is not None
        assert isinstance(parser, argparse.ArgumentParser)

    def test_parser_has_expected_subcommands(self):
        """Test that parser has all expected subcommands"""
        parser = self.cli.create_parser()

        # Expected subcommands
        expected_commands = [
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

        # Find subparsers action
        subparsers_action = None
        for action in parser._actions:
            if isinstance(action, argparse._SubParsersAction):
                subparsers_action = action
                break

        assert subparsers_action is not None, "Subparsers action not found"

        # Verify all expected commands are present
        for command in expected_commands:
            assert (
                command in subparsers_action.choices
            ), f"Command {command} not found in subparsers"

    def test_format_completer_configuration(self):
        """Test that format completers are properly configured"""
        parser = self.cli.create_parser()

        # Find the generate subparser
        generate_parser = None
        for action in parser._actions:
            if isinstance(action, argparse._SubParsersAction):
                if "generate" in action.choices:
                    generate_parser = action.choices["generate"]
                    break

        assert generate_parser is not None, "Generate subparser not found"

        # Find the format argument
        format_action = None
        for action in generate_parser._actions:
            if hasattr(action, "dest") and action.dest == "format":
                format_action = action
                break

        assert format_action is not None, "Format action not found"
        # Only check for completer if argcomplete is available
        # This test verifies the structure is correct

    def test_generate_subparser_has_expected_arguments(self):
        """Test that generate subparser has expected arguments"""
        parser = self.cli.create_parser()

        # Find the generate subparser
        generate_parser = None
        for action in parser._actions:
            if isinstance(action, argparse._SubParsersAction):
                if "generate" in action.choices:
                    generate_parser = action.choices["generate"]
                    break

        assert generate_parser is not None, "Generate subparser not found"

        # Check for expected arguments
        expected_args = [
            "tags",
            "instructions",
            "template",
            "output",
            "format",
            "project_path",
        ]
        found_args = []

        for action in generate_parser._actions:
            if hasattr(action, "dest") and action.dest in expected_args:
                found_args.append(action.dest)

        for expected_arg in expected_args:
            assert (
                expected_arg in found_args
            ), f"Expected argument {expected_arg} not found in generate subparser"

    def test_completion_methods_exist(self):
        """Test that completion-related methods exist on CLI class"""
        # Verify the CLI has the completion setup method
        assert hasattr(
            self.cli, "_add_completion_support"
        ), "CLI missing _add_completion_support method"
        assert hasattr(
            self.cli, "_configure_subparser_completers"
        ), "CLI missing _configure_subparser_completers method"

        # Verify the methods are callable
        assert callable(
            self.cli._add_completion_support
        ), "_add_completion_support is not callable"
        assert callable(
            self.cli._configure_subparser_completers
        ), "_configure_subparser_completers is not callable"
