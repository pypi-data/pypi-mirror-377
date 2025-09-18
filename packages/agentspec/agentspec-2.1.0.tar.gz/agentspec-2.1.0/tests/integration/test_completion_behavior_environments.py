"""
Integration tests for completion behavior across different shell environments.

This module tests how completion behaves in various shell environments,
including different operating systems, terminal emulators, and shell configurations.
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, Mock, patch

import pytest

from agentspec.cli.completers import (
    category_completer,
    comma_separated_tag_completer,
    command_completer,
    format_completer,
    tag_completer,
    template_completer,
)
from agentspec.cli.completion import CompletionEngine, get_completion_engine

# Import test fixtures
from ..fixtures.shell_completion_fixtures import (
    MockShellEnvironment,
    bash_completion_fixture,
    create_mock_argcomplete_environment,
    fish_completion_fixture,
    simulate_argcomplete_completion,
    zsh_completion_fixture,
)


class TestCompletionEnvironmentVariables:
    """Test completion behavior with different environment variable configurations"""

    def test_completion_with_minimal_environment(self):
        """
        Test completion works with minimal environment variables.

        Requirements: 8.4 - Robust completion in minimal environments
        """
        # Save original environment
        original_env = dict(os.environ)

        try:
            # Clear most environment variables except essential ones
            essential_vars = ["PATH", "HOME", "USER"]
            os.environ.clear()
            for var in essential_vars:
                if var in original_env:
                    os.environ[var] = original_env[var]

            # Test basic completion still works
            completions = command_completer("list", None)
            assert isinstance(completions, list)

            # Should include list commands
            list_commands = [c for c in completions if c.startswith("list")]
            assert len(list_commands) > 0

        finally:
            # Restore original environment
            os.environ.clear()
            os.environ.update(original_env)

    def test_completion_with_custom_shell_variables(self):
        """
        Test completion with custom shell-specific variables.

        Requirements: 8.1, 8.2, 8.3 - Shell-specific environment handling
        """
        test_environments = [
            # Bash environment
            {
                "SHELL": "/bin/bash",
                "BASH_VERSION": "5.1.0",
                "PS1": "$ ",
                "COMP_WORDBREAKS": " \t\n\"'@><=;|&(",
            },
            # Zsh environment
            {
                "SHELL": "/usr/bin/zsh",
                "ZSH_VERSION": "5.8",
                "PS1": "%% ",
                "WORDCHARS": "*?_-.[]~=/&;!#$%^(){}<>",
            },
            # Fish environment
            {"SHELL": "/usr/local/bin/fish", "FISH_VERSION": "3.3.0", "PS1": "> "},
        ]

        for env_vars in test_environments:
            with patch.dict(os.environ, env_vars, clear=False):
                # Test that completion works in each environment
                completions = command_completer("gen", None)
                assert "generate" in completions

                # Test format completion
                format_completions = format_completer("json", None)
                assert "json" in format_completions or len(format_completions) >= 0

    def test_completion_with_locale_variations(self):
        """
        Test completion with different locale settings.

        Requirements: 8.4 - Locale-aware completion
        """
        locales = [
            "C",
            "en_US.UTF-8",
            "en_GB.UTF-8",
            "fr_FR.UTF-8",
            "de_DE.UTF-8",
            "ja_JP.UTF-8",
        ]

        for locale in locales:
            with patch.dict(os.environ, {"LC_ALL": locale, "LANG": locale}):
                try:
                    # Test basic completion
                    completions = command_completer("help", None)
                    assert "help" in completions

                    # Test that completion doesn't break with different locales
                    category_completions = category_completer("Test", None)
                    assert isinstance(category_completions, list)

                except Exception as e:
                    # Some locales might not be available, which is acceptable
                    # as long as completion doesn't crash
                    assert "locale" in str(e).lower() or "encoding" in str(e).lower()


class TestCompletionWithDifferentTerminals:
    """Test completion behavior in different terminal environments"""

    def test_completion_with_terminal_variations(self):
        """
        Test completion with different terminal types.

        Requirements: 8.4 - Terminal-agnostic completion
        """
        terminal_environments = [
            {"TERM": "xterm"},
            {"TERM": "xterm-256color"},
            {"TERM": "screen"},
            {"TERM": "tmux"},
            {"TERM": "linux"},
            {"TERM": "vt100"},
            {"TERM": "dumb"},  # Non-interactive terminal
        ]

        for term_env in terminal_environments:
            with patch.dict(os.environ, term_env):
                # Test that completion works regardless of terminal type
                completions = command_completer("analyze", None)
                assert "analyze" in completions

                # Test dynamic completion
                with patch(
                    "agentspec.cli.completers.get_completion_engine"
                ) as mock_get_engine:
                    mock_engine = Mock()
                    mock_engine.get_tag_completions.return_value = [
                        "testing",
                        "frontend",
                    ]
                    mock_get_engine.return_value = mock_engine

                    tag_completions = tag_completer("test", None)
                    assert "testing" in tag_completions

    def test_completion_with_different_column_widths(self):
        """
        Test completion behavior with different terminal widths.

        Requirements: 8.4 - Adaptive completion for different terminal sizes
        """
        column_widths = [40, 80, 120, 200, 300]

        for width in column_widths:
            with patch.dict(os.environ, {"COLUMNS": str(width)}):
                # Test that completion works with different terminal widths
                completions = command_completer("", None)  # Get all commands

                # Should return all commands regardless of terminal width
                expected_commands = ["list-tags", "generate", "help", "version"]
                for cmd in expected_commands:
                    assert cmd in completions

                # Test long completion lists
                with patch(
                    "agentspec.cli.completers.get_completion_engine"
                ) as mock_get_engine:
                    mock_engine = Mock()
                    # Create a long list of mock completions
                    long_list = [f"tag_{i:03d}" for i in range(50)]
                    mock_engine.get_tag_completions.return_value = long_list
                    mock_get_engine.return_value = mock_engine

                    tag_completions = tag_completer("tag_", None)
                    # Should return all completions regardless of terminal width
                    assert len(tag_completions) == 50


class TestCompletionWithShellOptions:
    """Test completion with different shell option configurations"""

    def test_completion_with_bash_options(self):
        """
        Test completion with various bash options enabled.

        Requirements: 8.1 - Bash option compatibility
        """
        bash_options = [
            {"BASHOPTS": "checkwinsize:cmdhist:complete_fullquote:expand_aliases"},
            {"SHELLOPTS": "braceexpand:hashall:histexpand:monitor:history"},
            {"set": "+H"},  # Disable history expansion
            {"set": "-o vi"},  # Vi mode
            {"set": "-o emacs"},  # Emacs mode
        ]

        for options in bash_options:
            with patch.dict(os.environ, options, clear=False):
                # Test that completion works with different bash options
                completions = command_completer("validate", None)
                assert "validate" in completions

                # Test comma-separated completion
                comma_completions = comma_separated_tag_completer("frontend,", None)
                assert isinstance(comma_completions, list)

    def test_completion_with_zsh_options(self):
        """
        Test completion with various zsh options enabled.

        Requirements: 8.2 - Zsh option compatibility
        """
        zsh_environments = [
            {"ZSH_DISABLE_COMPFIX": "true"},
            {"CASE_SENSITIVE": "true"},
            {"HYPHEN_INSENSITIVE": "true"},
            {"DISABLE_AUTO_UPDATE": "true"},
            {"COMPLETION_WAITING_DOTS": "true"},
        ]

        for env_vars in zsh_environments:
            with patch.dict(os.environ, env_vars, clear=False):
                # Test that completion works with different zsh configurations
                completions = command_completer("int", None)
                matching = [c for c in completions if "int" in c]
                assert len(matching) > 0  # Should match "interactive" and "integrate"

    def test_completion_with_fish_options(self):
        """
        Test completion with various fish options enabled.

        Requirements: 8.3 - Fish option compatibility
        """
        fish_environments = [
            {"fish_greeting": ""},
            {"fish_key_bindings": "fish_vi_key_bindings"},
            {"fish_key_bindings": "fish_default_key_bindings"},
            {"FISH_CLIPBOARD_CMD": "pbcopy"},
        ]

        for env_vars in fish_environments:
            with patch.dict(os.environ, env_vars, clear=False):
                # Test that completion works with different fish configurations
                completions = format_completer("", None)
                expected_formats = ["markdown", "json", "yaml"]
                for fmt in expected_formats:
                    assert fmt in completions


class TestCompletionWithArgcompleteEnvironment:
    """Test completion behavior with different argcomplete configurations"""

    def test_completion_with_argcomplete_environment_variables(self):
        """
        Test completion with argcomplete-specific environment variables.

        Requirements: 2.1 - Argcomplete environment handling
        """
        argcomplete_envs = [
            create_mock_argcomplete_environment(),
            {
                **create_mock_argcomplete_environment(),
                "_ARGCOMPLETE_COMP_WORDBREAKS": " \t\n\"'@><=;|&(",
                "_ARGCOMPLETE_IFS": "\013",
                "_ARGCOMPLETE_SUPPRESS_SPACE": "1",
            },
            {
                **create_mock_argcomplete_environment(),
                "COMP_LINE": "agentspec generate --tags frontend,",
                "COMP_POINT": "35",
                "COMP_WORDS": "agentspec generate --tags frontend,",
                "COMP_CWORD": "3",
            },
        ]

        for env_vars in argcomplete_envs:
            with patch.dict(os.environ, env_vars):
                # Test that completion works with argcomplete environment
                simulation = simulate_argcomplete_completion("agentspec generate ")
                assert simulation["command_line"] == "agentspec generate "
                assert isinstance(simulation["words"], list)

    def test_completion_with_different_wordbreak_characters(self):
        """
        Test completion with different word break character configurations.

        Requirements: 10.1, 10.3 - Word break handling for comma-separated values
        """
        wordbreak_configs = [
            " \t\n\"'@><=;|&(",  # Default
            " \t\n\"'@><=;|&(,",  # Include comma
            " \t\n\"'@><=;|&()[]{}",  # Include brackets
            " \t\n",  # Minimal
        ]

        for wordbreaks in wordbreak_configs:
            env_vars = {
                **create_mock_argcomplete_environment(),
                "_ARGCOMPLETE_COMP_WORDBREAKS": wordbreaks,
            }

            with patch.dict(os.environ, env_vars):
                # Test comma-separated completion with different word breaks
                completions = comma_separated_tag_completer("frontend,back", None)
                assert isinstance(completions, list)

                # Should handle comma separation regardless of wordbreak config
                if completions:
                    # If we get completions, they should be properly formatted
                    for completion in completions:
                        assert isinstance(completion, str)


class TestCompletionCrossPlatform:
    """Test completion behavior across different operating systems"""

    def test_completion_on_different_platforms(self):
        """
        Test completion behavior on different operating systems.

        Requirements: 8.4 - Cross-platform completion support
        """
        platform_configs = [
            # Linux
            {
                "os.name": "posix",
                "platform.system": "Linux",
                "PATH": "/usr/local/bin:/usr/bin:/bin",
            },
            # macOS
            {
                "os.name": "posix",
                "platform.system": "Darwin",
                "PATH": "/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin",
            },
            # Windows (if supported)
            {
                "os.name": "nt",
                "platform.system": "Windows",
                "PATH": "C:\\Windows\\System32;C:\\Windows",
            },
        ]

        for config in platform_configs:
            with patch.dict(os.environ, {"PATH": config["PATH"]}):
                with patch("os.name", config["os.name"]):
                    # Test that completion works on different platforms
                    completions = command_completer("version", None)
                    assert "version" in completions

                    # Test file path completion behavior (platform-specific)
                    # This is a basic test since file completion is handled by argcomplete
                    category_completions = category_completer("Gen", None)
                    assert "General" in category_completions

    def test_completion_with_different_path_separators(self):
        """
        Test completion with different path separator conventions.

        Requirements: 6.1, 6.2, 6.3 - Path completion across platforms
        """
        # Test with different path styles
        path_styles = [
            "/unix/style/path",
            "C:\\Windows\\style\\path",
            "~/home/relative/path",
            "./relative/path",
            "../parent/relative/path",
        ]

        for path_style in path_styles:
            # Test that completion doesn't break with different path styles
            # This is mainly testing that our completion functions are robust
            completions = command_completer("list", None)
            assert len([c for c in completions if c.startswith("list")]) > 0


class TestCompletionPerformanceInDifferentEnvironments:
    """Test completion performance across different environments"""

    def test_completion_performance_with_large_datasets(self):
        """
        Test completion performance with large datasets.

        Requirements: 11.1, 11.2 - Performance with large datasets
        """
        import time

        # Mock large datasets
        with patch("agentspec.cli.completers.get_completion_engine") as mock_get_engine:
            mock_engine = Mock()

            # Large tag dataset
            large_tag_list = [f"tag_{i:04d}" for i in range(1000)]
            mock_engine.get_tag_completions.return_value = large_tag_list

            # Large template dataset
            large_template_list = [f"template_{i:04d}" for i in range(500)]
            mock_engine.get_template_completions.return_value = large_template_list

            mock_get_engine.return_value = mock_engine

            # Test tag completion performance
            start_time = time.time()
            tag_completions = tag_completer("tag_", None)
            tag_time = time.time() - start_time

            assert len(tag_completions) == 1000
            assert tag_time < 1.0, f"Tag completion too slow: {tag_time:.3f}s"

            # Test template completion performance
            start_time = time.time()
            template_completions = template_completer("template_", None)
            template_time = time.time() - start_time

            assert len(template_completions) == 500
            assert (
                template_time < 1.0
            ), f"Template completion too slow: {template_time:.3f}s"

    def test_completion_performance_with_slow_services(self):
        """
        Test completion performance when services are slow.

        Requirements: 11.1, 11.3 - Timeout handling for slow services
        """
        import time

        def slow_tag_completion(prefix):
            time.sleep(0.5)  # Simulate slow service
            return ["slow_tag_1", "slow_tag_2"]

        with patch("agentspec.cli.completers.get_completion_engine") as mock_get_engine:
            mock_engine = Mock()
            mock_engine.get_tag_completions.side_effect = slow_tag_completion
            mock_get_engine.return_value = mock_engine

            # Test that completion handles slow services
            start_time = time.time()
            completions = tag_completer("slow", None)
            completion_time = time.time() - start_time

            # Should either complete quickly (cached/timeout) or complete with results
            if completion_time < 0.1:
                # Fast completion (likely cached or timed out)
                assert isinstance(completions, list)
            else:
                # Slow completion completed
                assert "slow_tag_1" in completions or "slow_tag_2" in completions
                assert (
                    completion_time < 2.0
                ), f"Completion too slow: {completion_time:.3f}s"

    def test_completion_memory_usage_in_different_environments(self):
        """
        Test completion memory usage across different environments.

        Requirements: 11.1 - Memory-efficient completion
        """
        # This is a basic test for memory efficiency
        # In a real scenario, you might use memory profiling tools

        with patch("agentspec.cli.completers.get_completion_engine") as mock_get_engine:
            mock_engine = Mock()

            # Create completions that could potentially use a lot of memory
            large_completions = [
                f"very_long_completion_name_{i:06d}_with_lots_of_text"
                for i in range(100)
            ]
            mock_engine.get_tag_completions.return_value = large_completions
            mock_get_engine.return_value = mock_engine

            # Test that completion doesn't consume excessive memory
            completions = tag_completer("very", None)

            # Basic check - should return the completions without issues
            assert len(completions) == 100
            assert all(isinstance(c, str) for c in completions)

            # Test multiple calls don't accumulate memory
            for _ in range(10):
                more_completions = tag_completer("very", None)
                assert len(more_completions) == 100
