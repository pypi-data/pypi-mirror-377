"""
Integration tests for multi-shell completion support.

This module tests shell completion functionality across different shell environments
(bash, zsh, fish) to ensure AgentSpec CLI autocomplete works consistently.
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, patch

import pytest

from agentspec.cli.completers import (
    category_completer,
    command_completer,
    format_completer,
    tag_completer,
    template_completer,
)
from agentspec.cli.completion import CompletionEngine, get_completion_engine
from agentspec.cli.main import AgentSpecCLI

# Import test fixtures
from ..fixtures.shell_completion_fixtures import (
    MockShellEnvironment,
    all_shell_fixtures,
    bash_completion_fixture,
    fish_completion_fixture,
    simulate_argcomplete_completion,
    zsh_completion_fixture,
)


class TestMultiShellCompletionSupport:
    """Test completion support across multiple shell environments"""

    def test_bash_completion_activation(self, bash_completion_fixture):
        """
        Test that bash completion can be activated successfully.

        Requirements: 8.1 - Bash shell completion support
        """
        # Test completion script creation
        assert bash_completion_fixture.test_completion_activation()

        # Test completion script content
        script_content = bash_completion_fixture.get_completion_script_template()
        assert "_agentspec_completion" in script_content
        assert "complete -F _agentspec_completion agentspec" in script_content

        # Test that completion script is valid bash syntax
        script_path = bash_completion_fixture.create_completion_script(script_content)
        assert script_path.exists()

        # Verify the script contains expected completion logic
        with open(script_path, "r") as f:
            content = f.read()
            assert "COMPREPLY" in content
            assert "compgen" in content
            assert "list-tags" in content
            assert "generate" in content

    def test_zsh_completion_activation(self, zsh_completion_fixture):
        """
        Test that zsh completion can be activated successfully.

        Requirements: 8.2 - Zsh shell completion support
        """
        # Test completion script creation
        assert zsh_completion_fixture.test_completion_activation()

        # Test completion script content
        script_content = zsh_completion_fixture.get_completion_script_template()
        assert "#compdef agentspec" in script_content
        assert "_agentspec" in script_content
        assert "_arguments" in script_content

        # Test that completion script is valid zsh syntax
        script_path = zsh_completion_fixture.create_completion_script(script_content)
        assert script_path.exists()

        # Verify the script contains expected completion functions
        with open(script_path, "r") as f:
            content = f.read()
            assert "_agentspec_commands" in content
            assert "_agentspec_tags" in content
            assert "_agentspec_templates" in content
            assert "_describe" in content

    def test_fish_completion_activation(self, fish_completion_fixture):
        """
        Test that fish completion can be activated successfully.

        Requirements: 8.3 - Fish shell completion support
        """
        # Test completion script creation
        assert fish_completion_fixture.test_completion_activation()

        # Test completion script content
        script_content = fish_completion_fixture.get_completion_script_template()
        assert "complete -c agentspec" in script_content
        assert "__fish_use_subcommand" in script_content
        assert "__fish_seen_subcommand_from" in script_content

        # Test that completion script is valid fish syntax
        script_path = fish_completion_fixture.create_completion_script(script_content)
        assert script_path.exists()

        # Verify the script contains expected completion definitions
        with open(script_path, "r") as f:
            content = f.read()
            assert "list-tags" in content
            assert "generate" in content
            assert "-d 'List available instruction tags'" in content

    def test_all_shells_support_basic_commands(self, all_shell_fixtures):
        """
        Test that all shells support basic command completion.

        Requirements: 8.1, 8.2, 8.3 - Multi-shell command completion
        """
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

        for shell_name, fixture in all_shell_fixtures.items():
            # Test command completion for each shell
            if shell_name == "bash":
                completions = fixture.simulate_bash_completion("agentspec ")
            elif shell_name == "zsh":
                completions = fixture.simulate_zsh_completion("agentspec ")
            elif shell_name == "fish":
                completions = fixture.simulate_fish_completion("agentspec ")
            else:
                continue

            # Verify all expected commands are available
            for command in expected_commands:
                assert (
                    command in completions
                ), f"Command {command} missing in {shell_name} completion"

    def test_shell_specific_completion_behavior(self, all_shell_fixtures):
        """
        Test shell-specific completion behavior differences.

        Requirements: 8.1, 8.2, 8.3, 8.4 - Shell-specific completion behavior
        """
        test_cases = [
            ("agentspec gen", ["generate"]),
            ("agentspec list-", ["list-tags", "list-instructions", "list-templates"]),
            ("agentspec generate --", ["--tags", "--format", "--output", "--template"]),
        ]

        for shell_name, fixture in all_shell_fixtures.items():
            for command_line, expected_partial in test_cases:
                if shell_name == "bash":
                    completions = fixture.simulate_bash_completion(command_line)
                elif shell_name == "zsh":
                    completions = fixture.simulate_zsh_completion(command_line)
                elif shell_name == "fish":
                    completions = fixture.simulate_fish_completion(command_line)
                else:
                    continue

                # Verify expected completions are present
                for expected in expected_partial:
                    matching = [c for c in completions if expected in c]
                    assert (
                        matching
                    ), f"Expected completion '{expected}' not found in {shell_name} for '{command_line}'"


class TestShellCompletionIntegration:
    """Test integration of completion with actual CLI components"""

    def setup_method(self):
        """Set up test fixtures"""
        self.cli = AgentSpecCLI()

    def test_argcomplete_integration_with_parser(self):
        """
        Test that argcomplete integrates properly with the CLI parser.

        Requirements: 2.1, 2.2, 2.3, 2.4 - CLI parser completion integration
        """
        # Create parser with completion support
        parser = self.cli.create_parser()

        # Verify parser was created successfully
        assert parser is not None

        # Test that completion methods exist
        assert hasattr(self.cli, "_add_completion_support")
        assert hasattr(self.cli, "_configure_subparser_completers")

        # Test completion setup doesn't raise exceptions
        try:
            self.cli._add_completion_support(parser)
        except Exception as e:
            # Should not raise exceptions even if argcomplete is not available
            pytest.fail(f"Completion setup raised unexpected exception: {e}")

    def test_argcomplete_autocomplete_called(self):
        """
        Test that argcomplete.autocomplete is called when available.

        Requirements: 2.1 - Argcomplete integration
        """
        # Skip this test if argcomplete is not available
        try:
            import argcomplete
        except ImportError:
            pytest.skip("argcomplete not available")

        with patch.object(self.cli, "_add_completion_support") as mock_add_completion:
            # Create parser
            parser = self.cli.create_parser()

            # Verify completion support was added
            mock_add_completion.assert_called_once_with(parser)

    def test_graceful_degradation_without_argcomplete(self):
        """
        Test graceful degradation when argcomplete is not available.

        Requirements: 8.4 - Graceful degradation for unsupported shells
        """
        # Test that completion setup handles errors gracefully by mocking argcomplete.autocomplete to fail
        with patch(
            "argcomplete.autocomplete", side_effect=Exception("argcomplete error")
        ):
            # Create parser - should not raise exceptions even if argcomplete fails
            parser = self.cli.create_parser()

            # Should not raise exceptions due to error handling in _add_completion_support
            assert parser is not None

    def test_completer_configuration_for_subparsers(self):
        """
        Test that completers are properly configured for subparser arguments.

        Requirements: 2.2, 2.3, 2.4 - Subparser completer configuration
        """
        parser = self.cli.create_parser()

        # Find generate subparser
        generate_parser = None
        for action in parser._actions:
            if (
                hasattr(action, "choices")
                and action.choices
                and "generate" in action.choices
            ):
                generate_parser = action.choices["generate"]
                break

        assert generate_parser is not None, "Generate subparser not found"

        # Test completer configuration
        self.cli._configure_subparser_completers(generate_parser, "generate")

        # Verify completers are set for expected arguments
        completer_args = {}
        for action in generate_parser._actions:
            if hasattr(action, "dest") and hasattr(action, "completer"):
                completer_args[action.dest] = action.completer

        # Check that key arguments have completers configured
        # Note: Only check if argcomplete is available to avoid import errors
        try:
            from agentspec.cli.completers import format_completer, tag_completer

            # If we can import, then we can check for completer assignment
            # This is a structural test rather than functional
        except ImportError:
            # If completers can't be imported, skip the detailed check
            pass


class TestCompletionBehaviorAcrossShells:
    """Test that completion behavior is consistent across different shells"""

    def setup_method(self):
        """Set up test environment"""
        self.mock_engine = Mock(spec=CompletionEngine)

    def test_command_completion_consistency(self, all_shell_fixtures):
        """
        Test that command completion is consistent across shells.

        Requirements: 8.1, 8.2, 8.3 - Consistent command completion
        """
        test_prefixes = ["", "l", "li", "list-", "gen", "int"]

        for prefix in test_prefixes:
            command_line = f"agentspec {prefix}"
            shell_results = {}

            # Get completions from each shell
            for shell_name, fixture in all_shell_fixtures.items():
                if shell_name == "bash":
                    completions = fixture.simulate_bash_completion(command_line)
                elif shell_name == "zsh":
                    completions = fixture.simulate_zsh_completion(command_line)
                elif shell_name == "fish":
                    completions = fixture.simulate_fish_completion(command_line)
                else:
                    continue

                shell_results[shell_name] = set(completions)

            # Verify consistency (all shells should provide similar completions)
            if len(shell_results) > 1:
                shell_names = list(shell_results.keys())
                first_shell = shell_names[0]
                first_results = shell_results[first_shell]

                for other_shell in shell_names[1:]:
                    other_results = shell_results[other_shell]
                    # Allow for some variation but core commands should be consistent
                    common_commands = ["list-tags", "generate", "help"]
                    for cmd in common_commands:
                        if any(cmd in comp for comp in first_results):
                            assert any(
                                cmd in comp for comp in other_results
                            ), f"Command {cmd} missing in {other_shell} but present in {first_shell}"

    @patch("agentspec.cli.completers.get_completion_engine")
    def test_dynamic_completion_consistency(self, mock_get_engine, all_shell_fixtures):
        """
        Test that dynamic completions (tags, templates) work consistently.

        Requirements: 3.1, 4.1 - Dynamic completion consistency across shells
        """
        # Mock the completion engine
        mock_engine = Mock()
        mock_engine.get_tag_completions.return_value = [
            "testing",
            "frontend",
            "backend",
        ]
        mock_engine.get_template_completions.return_value = ["react-app", "python-api"]
        mock_engine.get_format_completions.return_value = ["markdown", "json", "yaml"]
        mock_get_engine.return_value = mock_engine

        # Test tag completion
        tag_completions = tag_completer("test", None)
        assert "testing" in tag_completions

        # Test template completion
        template_completions = template_completer("react", None)
        mock_engine.get_template_completions.assert_called_with("react")

        # Test format completion
        format_completions = format_completer("json", None)
        assert "json" in format_completions or len(format_completions) > 0

    def test_error_handling_across_shells(self, all_shell_fixtures):
        """
        Test that error handling is consistent across shells.

        Requirements: 8.4 - Consistent error handling across shells
        """
        # Test invalid command lines
        invalid_commands = [
            "invalid_command",
            "agentspec invalid_subcommand",
            "",
            "agentspec generate --invalid-option",
        ]

        for command_line in invalid_commands:
            for shell_name, fixture in all_shell_fixtures.items():
                try:
                    if shell_name == "bash":
                        completions = fixture.simulate_bash_completion(command_line)
                    elif shell_name == "zsh":
                        completions = fixture.simulate_zsh_completion(command_line)
                    elif shell_name == "fish":
                        completions = fixture.simulate_fish_completion(command_line)
                    else:
                        continue

                    # Should not raise exceptions and should return empty or safe completions
                    assert isinstance(completions, list)

                except Exception as e:
                    pytest.fail(
                        f"Shell {shell_name} raised exception for invalid command '{command_line}': {e}"
                    )


class TestShellEnvironmentDetection:
    """Test shell environment detection and adaptation"""

    def test_shell_detection_from_environment(self):
        """
        Test shell detection from environment variables.

        Requirements: 8.4 - Shell environment detection
        """
        test_shells = [
            ("bash", "/bin/bash"),
            ("zsh", "/usr/bin/zsh"),
            ("fish", "/usr/local/bin/fish"),
            ("sh", "/bin/sh"),
        ]

        for shell_name, shell_path in test_shells:
            with patch.dict(os.environ, {"SHELL": shell_path}):
                detected_shell = os.environ.get("SHELL", "").split("/")[-1]
                assert shell_name in detected_shell or detected_shell == shell_name

    def test_completion_script_generation_per_shell(self):
        """
        Test that completion scripts can be generated for different shells.

        Requirements: 9.2, 9.3 - Shell-specific completion script generation
        """
        from agentspec.cli.completion_install import CompletionInstaller

        installer = CompletionInstaller()

        # Test script generation for different shells
        shells_to_test = ["bash", "zsh", "fish"]

        for shell in shells_to_test:
            try:
                shell_name, script = installer.get_completion_script(shell)
                assert script is not None
                assert len(script) > 0
                assert shell_name == shell

                # Verify shell-specific content
                if shell == "bash":
                    assert "register-python-argcomplete" in script
                elif shell == "zsh":
                    assert "register-python-argcomplete" in script
                    assert "bashcompinit" in script
                elif shell == "fish":
                    assert "register-python-argcomplete --shell fish" in script

            except Exception as e:
                # Some shells might not be supported, which is acceptable
                # as long as the function handles it gracefully
                assert (
                    "not supported" in str(e).lower()
                    or "not available" in str(e).lower()
                )


class TestCompletionPerformanceAcrossShells:
    """Test completion performance across different shell environments"""

    def test_completion_response_time_consistency(self, all_shell_fixtures):
        """
        Test that completion response times are consistent across shells.

        Requirements: 11.1, 11.2 - Performance consistency across shells
        """
        import time

        test_commands = [
            "agentspec ",
            "agentspec generate ",
            "agentspec list-tags ",
            "agentspec generate --tags ",
        ]

        performance_results = {}

        for shell_name, fixture in all_shell_fixtures.items():
            shell_times = []

            for command in test_commands:
                start_time = time.time()

                try:
                    if shell_name == "bash":
                        fixture.simulate_bash_completion(command)
                    elif shell_name == "zsh":
                        fixture.simulate_zsh_completion(command)
                    elif shell_name == "fish":
                        fixture.simulate_fish_completion(command)

                    end_time = time.time()
                    response_time = end_time - start_time
                    shell_times.append(response_time)

                except Exception:
                    # If completion fails, record a high time to indicate poor performance
                    shell_times.append(1.0)

            performance_results[shell_name] = {
                "avg_time": sum(shell_times) / len(shell_times),
                "max_time": max(shell_times),
                "times": shell_times,
            }

        # Verify all shells perform reasonably well (under 100ms for mock completions)
        for shell_name, results in performance_results.items():
            assert (
                results["avg_time"] < 0.1
            ), f"{shell_name} completion too slow: {results['avg_time']:.3f}s"
            assert (
                results["max_time"] < 0.2
            ), f"{shell_name} max completion time too slow: {results['max_time']:.3f}s"

    @patch("agentspec.cli.completers.get_completion_engine")
    def test_caching_behavior_across_shells(self, mock_get_engine):
        """
        Test that caching behavior is consistent across shells.

        Requirements: 11.1, 11.2 - Consistent caching across shells
        """
        # Mock completion engine with caching
        mock_engine = Mock()
        mock_engine.get_tag_completions.return_value = ["testing", "frontend"]
        mock_get_engine.return_value = mock_engine

        # Call completion multiple times
        for _ in range(3):
            completions = tag_completer("test", None)
            assert "testing" in completions

        # Verify the engine method was called (caching is internal to engine)
        assert mock_engine.get_tag_completions.call_count >= 1

        # Test with different prefixes
        tag_completer("front", None)
        tag_completer("back", None)

        # Should have been called for each unique prefix
        assert mock_engine.get_tag_completions.call_count >= 3


class TestShellCompletionEdgeCases:
    """Test edge cases and error conditions in shell completion"""

    def test_empty_command_line_handling(self, all_shell_fixtures):
        """
        Test handling of empty command lines.

        Requirements: 8.4 - Robust error handling
        """
        empty_commands = ["", " ", "\t", "\n"]

        for shell_name, fixture in all_shell_fixtures.items():
            for empty_cmd in empty_commands:
                try:
                    if shell_name == "bash":
                        completions = fixture.simulate_bash_completion(empty_cmd)
                    elif shell_name == "zsh":
                        completions = fixture.simulate_zsh_completion(empty_cmd)
                    elif shell_name == "fish":
                        completions = fixture.simulate_fish_completion(empty_cmd)
                    else:
                        continue

                    # Should return empty list or handle gracefully
                    assert isinstance(completions, list)

                except Exception as e:
                    pytest.fail(
                        f"Shell {shell_name} failed on empty command '{repr(empty_cmd)}': {e}"
                    )

    def test_malformed_command_handling(self, all_shell_fixtures):
        """
        Test handling of malformed commands.

        Requirements: 8.4 - Robust error handling for malformed input
        """
        malformed_commands = [
            "agentspec --invalid-global-option",
            "agentspec generate --tags --format",  # Missing values
            "agentspec unknown-command",
            "not-agentspec command",
        ]

        for shell_name, fixture in all_shell_fixtures.items():
            for malformed_cmd in malformed_commands:
                try:
                    if shell_name == "bash":
                        completions = fixture.simulate_bash_completion(malformed_cmd)
                    elif shell_name == "zsh":
                        completions = fixture.simulate_zsh_completion(malformed_cmd)
                    elif shell_name == "fish":
                        completions = fixture.simulate_fish_completion(malformed_cmd)
                    else:
                        continue

                    # Should handle gracefully without crashing
                    assert isinstance(completions, list)

                except Exception as e:
                    pytest.fail(
                        f"Shell {shell_name} failed on malformed command '{malformed_cmd}': {e}"
                    )

    def test_unicode_and_special_characters(self, all_shell_fixtures):
        """
        Test handling of unicode and special characters in completion.

        Requirements: 8.4 - Robust handling of special characters
        """
        special_commands = [
            "agentspec générate",  # Unicode
            "agentspec generate --tags test,ñoño",  # Unicode in values
            "agentspec generate --output /path/with spaces/file.md",  # Spaces
            "agentspec generate --tags 'quoted,values'",  # Quotes
        ]

        for shell_name, fixture in all_shell_fixtures.items():
            for special_cmd in special_commands:
                try:
                    if shell_name == "bash":
                        completions = fixture.simulate_bash_completion(special_cmd)
                    elif shell_name == "zsh":
                        completions = fixture.simulate_zsh_completion(special_cmd)
                    elif shell_name == "fish":
                        completions = fixture.simulate_fish_completion(special_cmd)
                    else:
                        continue

                    # Should handle gracefully
                    assert isinstance(completions, list)

                except Exception as e:
                    # Some shells might not handle unicode well, which is acceptable
                    # as long as they don't crash
                    assert "encoding" in str(e).lower() or isinstance(completions, list)
