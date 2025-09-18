"""
Unit tests for CLI completers.

Tests the static completion functions in agentspec.cli.completers module
for functionality, error handling, and requirement compliance.
"""

from unittest.mock import Mock, patch

import pytest

from agentspec.cli.completers import (
    comma_separated_instruction_completer,
    command_completer,
    format_completer,
    instruction_completer,
    output_format_completer,
    project_type_completer,
    template_completer,
)


class TestCommandCompleter:
    """Test cases for command_completer function"""

    def test_command_completion_all_commands(self):
        """Test completion returns all commands for empty prefix"""
        result = command_completer("", None)

        expected_commands = [
            "analyze",
            "generate",
            "help",
            "integrate",
            "interactive",
            "list-instructions",
            "list-tags",
            "list-templates",
            "validate",
            "version",
        ]

        assert result == expected_commands
        assert len(result) == 10

    def test_command_completion_with_prefix(self):
        """Test completion with various prefixes"""
        # Test "li" prefix - should match list-* commands
        result = command_completer("li", None)
        expected = ["list-instructions", "list-tags", "list-templates"]
        assert result == expected

        # Test "gen" prefix - should match generate
        result = command_completer("gen", None)
        assert result == ["generate"]

        # Test "v" prefix - should match version and validate
        result = command_completer("v", None)
        expected = ["validate", "version"]
        assert result == expected

    def test_command_completion_exact_match(self):
        """Test completion with exact command names"""
        result = command_completer("generate", None)
        assert result == ["generate"]

        result = command_completer("interactive", None)
        assert result == ["interactive"]

    def test_command_completion_no_matches(self):
        """Test completion with prefix that matches no commands"""
        result = command_completer("xyz", None)
        assert result == []

        result = command_completer("invalid", None)
        assert result == []

    def test_command_completion_case_sensitive(self):
        """Test that completion is case sensitive"""
        result = command_completer("GEN", None)
        assert result == []

        result = command_completer("Generate", None)
        assert result == []

    def test_command_completion_partial_matches(self):
        """Test completion with partial matches"""
        # Test "a" prefix - should match analyze
        result = command_completer("a", None)
        assert result == ["analyze"]

        # Test "h" prefix - should match help
        result = command_completer("h", None)
        assert result == ["help"]

        # Test "i" prefix - should match integrate and interactive
        result = command_completer("i", None)
        expected = ["integrate", "interactive"]  # Alphabetical order
        assert result == expected

    def test_command_completion_with_parsed_args(self):
        """Test that parsed_args parameter doesn't affect completion"""
        mock_args = Mock()
        mock_args.verbose = True

        result = command_completer("gen", mock_args)
        assert result == ["generate"]

    def test_command_completion_with_kwargs(self):
        """Test that additional kwargs don't affect completion"""
        result = command_completer("gen", None, extra_arg="value", another_arg=123)
        assert result == ["generate"]


class TestFormatCompleter:
    """Test cases for format_completer function"""

    @patch("agentspec.cli.completers.get_completion_engine")
    @patch("agentspec.cli.completers.safe_get_completions")
    def test_format_completer_calls_engine(self, mock_safe_get, mock_get_engine):
        """Test that format_completer calls the completion engine correctly"""
        mock_engine = Mock()
        mock_get_engine.return_value = mock_engine
        mock_safe_get.return_value = ["json", "yaml"]

        result = format_completer("j", None)

        # Verify engine was retrieved
        mock_get_engine.assert_called_once()

        # Verify safe_get_completions was called with correct arguments
        mock_safe_get.assert_called_once_with(mock_engine.get_format_completions, "j")

        assert result == ["json", "yaml"]

    @patch("agentspec.cli.completers.get_completion_engine")
    def test_format_completer_with_real_engine(self, mock_get_engine):
        """Test format_completer with a real completion engine"""
        from agentspec.cli.completion import CompletionEngine

        mock_engine = CompletionEngine()
        mock_get_engine.return_value = mock_engine

        # Test empty prefix
        result = format_completer("", None)
        expected = ["markdown", "json", "yaml"]
        assert result == expected

        # Test "j" prefix
        result = format_completer("j", None)
        assert result == ["json"]

        # Test "m" prefix
        result = format_completer("m", None)
        assert result == ["markdown"]

        # Test "y" prefix
        result = format_completer("y", None)
        assert result == ["yaml"]

    @patch("agentspec.cli.completers.get_completion_engine")
    @patch("agentspec.cli.completers.safe_get_completions")
    def test_format_completer_error_handling(self, mock_safe_get, mock_get_engine):
        """Test format_completer error handling through safe_get_completions"""
        mock_engine = Mock()
        mock_get_engine.return_value = mock_engine
        mock_safe_get.return_value = []  # Empty result on error

        result = format_completer("test", None)

        assert result == []
        mock_safe_get.assert_called_once()

    def test_format_completer_with_parsed_args(self):
        """Test that parsed_args parameter doesn't affect completion"""
        with patch("agentspec.cli.completers.get_completion_engine") as mock_get_engine:
            from agentspec.cli.completion import CompletionEngine

            mock_engine = CompletionEngine()
            mock_get_engine.return_value = mock_engine

            mock_args = Mock()
            mock_args.verbose = True

            result = format_completer("j", mock_args)
            assert result == ["json"]

    def test_format_completer_with_kwargs(self):
        """Test that additional kwargs don't affect completion"""
        with patch("agentspec.cli.completers.get_completion_engine") as mock_get_engine:
            from agentspec.cli.completion import CompletionEngine

            mock_engine = CompletionEngine()
            mock_get_engine.return_value = mock_engine

            result = format_completer("j", None, extra_arg="value")
            assert result == ["json"]


class TestOutputFormatCompleter:
    """Test cases for output_format_completer function"""

    @patch("agentspec.cli.completers.get_completion_engine")
    @patch("agentspec.cli.completers.safe_get_completions")
    def test_output_format_completer_calls_engine(self, mock_safe_get, mock_get_engine):
        """Test that output_format_completer calls the completion engine correctly"""
        mock_engine = Mock()
        mock_get_engine.return_value = mock_engine
        mock_safe_get.return_value = ["text", "json"]

        result = output_format_completer("t", None)

        # Verify engine was retrieved
        mock_get_engine.assert_called_once()

        # Verify safe_get_completions was called with correct arguments
        mock_safe_get.assert_called_once_with(
            mock_engine.get_output_format_completions, "t"
        )

        assert result == ["text", "json"]

    @patch("agentspec.cli.completers.get_completion_engine")
    def test_output_format_completer_with_real_engine(self, mock_get_engine):
        """Test output_format_completer with a real completion engine"""
        from agentspec.cli.completion import CompletionEngine

        mock_engine = CompletionEngine()
        mock_get_engine.return_value = mock_engine

        # Test empty prefix
        result = output_format_completer("", None)
        expected = ["text", "json"]
        assert result == expected

        # Test "t" prefix
        result = output_format_completer("t", None)
        assert result == ["text"]

        # Test "j" prefix
        result = output_format_completer("j", None)
        assert result == ["json"]

    @patch("agentspec.cli.completers.get_completion_engine")
    @patch("agentspec.cli.completers.safe_get_completions")
    def test_output_format_completer_error_handling(
        self, mock_safe_get, mock_get_engine
    ):
        """Test output_format_completer error handling through safe_get_completions"""
        mock_engine = Mock()
        mock_get_engine.return_value = mock_engine
        mock_safe_get.return_value = []  # Empty result on error

        result = output_format_completer("test", None)

        assert result == []
        mock_safe_get.assert_called_once()

    def test_output_format_completer_no_matches(self):
        """Test output_format_completer with prefix that matches nothing"""
        with patch("agentspec.cli.completers.get_completion_engine") as mock_get_engine:
            from agentspec.cli.completion import CompletionEngine

            mock_engine = CompletionEngine()
            mock_get_engine.return_value = mock_engine

            result = output_format_completer("xyz", None)
            assert result == []

    def test_output_format_completer_with_parsed_args(self):
        """Test that parsed_args parameter doesn't affect completion"""
        with patch("agentspec.cli.completers.get_completion_engine") as mock_get_engine:
            from agentspec.cli.completion import CompletionEngine

            mock_engine = CompletionEngine()
            mock_get_engine.return_value = mock_engine

            mock_args = Mock()
            mock_args.analyze_only = True

            result = output_format_completer("j", mock_args)
            assert result == ["json"]

    def test_output_format_completer_with_kwargs(self):
        """Test that additional kwargs don't affect completion"""
        with patch("agentspec.cli.completers.get_completion_engine") as mock_get_engine:
            from agentspec.cli.completion import CompletionEngine

            mock_engine = CompletionEngine()
            mock_get_engine.return_value = mock_engine

            result = output_format_completer("j", None, extra_arg="value")
            assert result == ["json"]


class TestCompletersIntegration:
    """Integration tests for completers"""

    def test_all_completers_return_lists(self):
        """Test that all completers return lists"""
        with patch("agentspec.cli.completers.get_completion_engine") as mock_get_engine:
            from agentspec.cli.completion import CompletionEngine

            mock_engine = CompletionEngine()
            mock_get_engine.return_value = mock_engine

            # Test command_completer
            result = command_completer("", None)
            assert isinstance(result, list)

            # Test format_completer
            result = format_completer("", None)
            assert isinstance(result, list)

            # Test output_format_completer
            result = output_format_completer("", None)
            assert isinstance(result, list)

    def test_completers_handle_none_prefix(self):
        """Test that completers handle None prefix gracefully"""
        with patch("agentspec.cli.completers.get_completion_engine") as mock_get_engine:
            from agentspec.cli.completion import CompletionEngine

            mock_engine = CompletionEngine()
            mock_get_engine.return_value = mock_engine

            # command_completer should handle None prefix
            try:
                result = command_completer(None, None)
                # Should either work or raise TypeError, but not crash unexpectedly
                assert isinstance(result, list) or result is None
            except TypeError:
                # This is acceptable behavior for None prefix
                pass

    def test_completers_performance(self):
        """Test that completers perform reasonably fast"""
        import time

        with patch("agentspec.cli.completers.get_completion_engine") as mock_get_engine:
            from agentspec.cli.completion import CompletionEngine

            mock_engine = CompletionEngine()
            mock_get_engine.return_value = mock_engine

            # Test command_completer performance
            start_time = time.time()
            for _ in range(100):
                command_completer("gen", None)
            command_time = time.time() - start_time

            # Should complete 100 calls in less than 100ms
            assert command_time < 0.1

            # Test format_completer performance
            start_time = time.time()
            for _ in range(100):
                format_completer("j", None)
            format_time = time.time() - start_time

            # Should complete 100 calls in less than 100ms
            assert format_time < 0.1


class TestCompletersRequirementCompliance:
    """Test cases to verify requirement compliance"""

    def test_requirement_1_1_command_completion(self):
        """Test Requirement 1.1: Command completion for all available commands"""
        # Test that all expected commands are available
        result = command_completer("", None)

        expected_commands = [
            "analyze",
            "generate",
            "help",
            "integrate",
            "interactive",
            "list-instructions",
            "list-tags",
            "list-templates",
            "validate",
            "version",
        ]

        for cmd in expected_commands:
            assert cmd in result, f"Command '{cmd}' missing from completion"

    def test_requirement_1_2_li_prefix_completion(self):
        """Test Requirement 1.2: 'li' prefix should complete to list-* commands"""
        result = command_completer("li", None)

        expected = ["list-instructions", "list-tags", "list-templates"]
        assert result == expected

    def test_requirement_1_3_gen_prefix_completion(self):
        """Test Requirement 1.3: 'gen' prefix should complete to 'generate'"""
        result = command_completer("gen", None)
        assert result == ["generate"]

    def test_requirement_1_4_invalid_prefix_no_completions(self):
        """Test Requirement 1.4: Invalid prefix should provide no completions"""
        result = command_completer("invalid_command", None)
        assert result == []

    def test_requirement_7_1_format_completion(self):
        """Test Requirement 7.1: Format completion shows available formats"""
        with patch("agentspec.cli.completers.get_completion_engine") as mock_get_engine:
            from agentspec.cli.completion import CompletionEngine

            mock_engine = CompletionEngine()
            mock_get_engine.return_value = mock_engine

            result = format_completer("", None)

            expected_formats = ["markdown", "json", "yaml"]
            for fmt in expected_formats:
                assert fmt in result, f"Format '{fmt}' missing from completion"

    def test_requirement_7_2_j_prefix_json_completion(self):
        """Test Requirement 7.2: 'j' prefix should complete to 'json'"""
        with patch("agentspec.cli.completers.get_completion_engine") as mock_get_engine:
            from agentspec.cli.completion import CompletionEngine

            mock_engine = CompletionEngine()
            mock_get_engine.return_value = mock_engine

            result = format_completer("j", None)
            assert result == ["json"]

    def test_requirement_7_3_output_format_completion(self):
        """Test Requirement 7.3: Output format completion shows integration formats"""
        with patch("agentspec.cli.completers.get_completion_engine") as mock_get_engine:
            from agentspec.cli.completion import CompletionEngine

            mock_engine = CompletionEngine()
            mock_get_engine.return_value = mock_engine

            result = output_format_completer("", None)

            expected_formats = ["text", "json"]
            for fmt in expected_formats:
                assert fmt in result, f"Output format '{fmt}' missing from completion"


class TestTemplateCompleter:
    """Test cases for template_completer function"""

    @patch("agentspec.cli.completers.get_completion_engine")
    @patch("agentspec.cli.completers.safe_get_completions")
    def test_template_completer_calls_engine(self, mock_safe_get, mock_get_engine):
        """Test that template_completer calls the completion engine correctly"""
        mock_engine = Mock()
        mock_get_engine.return_value = mock_engine
        mock_safe_get.return_value = ["react-app", "react-component"]

        result = template_completer("react", None)

        # Verify engine was retrieved
        mock_get_engine.assert_called_once()

        # Verify safe_get_completions was called with correct arguments
        mock_safe_get.assert_called_once_with(
            mock_engine.get_template_completions, "react"
        )

        assert result == ["react-app", "react-component"]

    @patch("agentspec.cli.completers.get_completion_engine")
    @patch("agentspec.cli.completers.safe_get_completions")
    def test_template_completer_error_handling(self, mock_safe_get, mock_get_engine):
        """Test template_completer error handling through safe_get_completions"""
        mock_engine = Mock()
        mock_get_engine.return_value = mock_engine
        mock_safe_get.return_value = []  # Empty result on error

        result = template_completer("test", None)

        assert result == []
        mock_safe_get.assert_called_once()

    def test_template_completer_with_parsed_args(self):
        """Test that parsed_args parameter doesn't affect completion"""
        with patch(
            "agentspec.cli.completers.get_completion_engine"
        ) as mock_get_engine, patch(
            "agentspec.cli.completers.safe_get_completions"
        ) as mock_safe_get:
            mock_engine = Mock()
            mock_get_engine.return_value = mock_engine
            mock_safe_get.return_value = ["react-app"]

            mock_args = Mock()
            mock_args.verbose = True

            result = template_completer("react", mock_args)
            assert result == ["react-app"]

    def test_template_completer_with_kwargs(self):
        """Test that additional kwargs don't affect completion"""
        with patch(
            "agentspec.cli.completers.get_completion_engine"
        ) as mock_get_engine, patch(
            "agentspec.cli.completers.safe_get_completions"
        ) as mock_safe_get:
            mock_engine = Mock()
            mock_get_engine.return_value = mock_engine
            mock_safe_get.return_value = ["react-app"]

            result = template_completer("react", None, extra_arg="value")
            assert result == ["react-app"]

    def test_requirement_4_1_template_completion(self):
        """Test Requirement 4.1: Template ID completion displays available templates"""
        with patch(
            "agentspec.cli.completers.get_completion_engine"
        ) as mock_get_engine, patch(
            "agentspec.cli.completers.safe_get_completions"
        ) as mock_safe_get:
            mock_engine = Mock()
            mock_get_engine.return_value = mock_engine
            mock_safe_get.return_value = ["react-app", "python-api", "nodejs-api"]

            result = template_completer("", None)

            expected_templates = ["react-app", "python-api", "nodejs-api"]
            assert result == expected_templates

    def test_requirement_4_2_react_prefix_completion(self):
        """Test Requirement 4.2: 'react' prefix should complete to react templates"""
        with patch(
            "agentspec.cli.completers.get_completion_engine"
        ) as mock_get_engine, patch(
            "agentspec.cli.completers.safe_get_completions"
        ) as mock_safe_get:
            mock_engine = Mock()
            mock_get_engine.return_value = mock_engine
            mock_safe_get.return_value = ["react-app", "react-component"]

            result = template_completer("react", None)
            assert result == ["react-app", "react-component"]

    def test_requirement_4_4_graceful_degradation(self):
        """Test Requirement 4.4: Graceful degradation when template manager unavailable"""
        with patch(
            "agentspec.cli.completers.get_completion_engine"
        ) as mock_get_engine, patch(
            "agentspec.cli.completers.safe_get_completions"
        ) as mock_safe_get:
            mock_engine = Mock()
            mock_get_engine.return_value = mock_engine
            mock_safe_get.return_value = []  # Simulates manager unavailable

            result = template_completer("react", None)
            assert result == []


class TestProjectTypeCompleter:
    """Test cases for project_type_completer function"""

    @patch("agentspec.cli.completers.get_completion_engine")
    @patch("agentspec.cli.completers.safe_get_completions")
    def test_project_type_completer_calls_engine(self, mock_safe_get, mock_get_engine):
        """Test that project_type_completer calls the completion engine correctly"""
        mock_engine = Mock()
        mock_get_engine.return_value = mock_engine
        mock_safe_get.return_value = ["web-application", "web-component"]

        result = project_type_completer("web", None)

        # Verify engine was retrieved
        mock_get_engine.assert_called_once()

        # Verify safe_get_completions was called with correct arguments
        mock_safe_get.assert_called_once_with(
            mock_engine.get_project_type_completions, "web"
        )

        assert result == ["web-application", "web-component"]

    @patch("agentspec.cli.completers.get_completion_engine")
    @patch("agentspec.cli.completers.safe_get_completions")
    def test_project_type_completer_error_handling(
        self, mock_safe_get, mock_get_engine
    ):
        """Test project_type_completer error handling through safe_get_completions"""
        mock_engine = Mock()
        mock_get_engine.return_value = mock_engine
        mock_safe_get.return_value = []  # Empty result on error

        result = project_type_completer("test", None)

        assert result == []
        mock_safe_get.assert_called_once()

    def test_project_type_completer_with_parsed_args(self):
        """Test that parsed_args parameter doesn't affect completion"""
        with patch(
            "agentspec.cli.completers.get_completion_engine"
        ) as mock_get_engine, patch(
            "agentspec.cli.completers.safe_get_completions"
        ) as mock_safe_get:
            mock_engine = Mock()
            mock_get_engine.return_value = mock_engine
            mock_safe_get.return_value = ["web-application"]

            mock_args = Mock()
            mock_args.verbose = True

            result = project_type_completer("web", mock_args)
            assert result == ["web-application"]

    def test_project_type_completer_with_kwargs(self):
        """Test that additional kwargs don't affect completion"""
        with patch(
            "agentspec.cli.completers.get_completion_engine"
        ) as mock_get_engine, patch(
            "agentspec.cli.completers.safe_get_completions"
        ) as mock_safe_get:
            mock_engine = Mock()
            mock_get_engine.return_value = mock_engine
            mock_safe_get.return_value = ["web-application"]

            result = project_type_completer("web", None, extra_arg="value")
            assert result == ["web-application"]

    def test_requirement_4_1_project_type_completion(self):
        """Test Requirement 4.1: Project type completion displays available types"""
        with patch(
            "agentspec.cli.completers.get_completion_engine"
        ) as mock_get_engine, patch(
            "agentspec.cli.completers.safe_get_completions"
        ) as mock_safe_get:
            mock_engine = Mock()
            mock_get_engine.return_value = mock_engine
            mock_safe_get.return_value = [
                "web-application",
                "mobile-app",
                "api-service",
            ]

            result = project_type_completer("", None)

            expected_types = ["web-application", "mobile-app", "api-service"]
            assert result == expected_types

    def test_requirement_4_4_graceful_degradation(self):
        """Test Requirement 4.4: Graceful degradation when template manager unavailable"""
        with patch(
            "agentspec.cli.completers.get_completion_engine"
        ) as mock_get_engine, patch(
            "agentspec.cli.completers.safe_get_completions"
        ) as mock_safe_get:
            mock_engine = Mock()
            mock_get_engine.return_value = mock_engine
            mock_safe_get.return_value = []  # Simulates manager unavailable

            result = project_type_completer("web", None)
            assert result == []


class TestInstructionCompleter:
    """Test cases for instruction_completer function"""

    @patch("agentspec.cli.completers.get_completion_engine")
    @patch("agentspec.cli.completers.safe_get_completions")
    def test_instruction_completer_calls_engine(self, mock_safe_get, mock_get_engine):
        """Test that instruction_completer calls the completion engine correctly"""
        mock_engine = Mock()
        mock_get_engine.return_value = mock_engine
        mock_safe_get.return_value = ["core_001", "core_002"]

        result = instruction_completer("core", None)

        # Verify engine was retrieved
        mock_get_engine.assert_called_once()

        # Verify safe_get_completions was called with correct arguments
        mock_safe_get.assert_called_once_with(
            mock_engine.get_instruction_completions, "core"
        )

        assert result == ["core_001", "core_002"]

    @patch("agentspec.cli.completers.get_completion_engine")
    @patch("agentspec.cli.completers.safe_get_completions")
    def test_instruction_completer_error_handling(self, mock_safe_get, mock_get_engine):
        """Test instruction_completer error handling through safe_get_completions"""
        mock_engine = Mock()
        mock_get_engine.return_value = mock_engine
        mock_safe_get.return_value = []  # Empty result on error

        result = instruction_completer("test", None)

        assert result == []
        mock_safe_get.assert_called_once()

    def test_instruction_completer_with_parsed_args(self):
        """Test that parsed_args parameter doesn't affect completion"""
        with patch(
            "agentspec.cli.completers.get_completion_engine"
        ) as mock_get_engine, patch(
            "agentspec.cli.completers.safe_get_completions"
        ) as mock_safe_get:
            mock_engine = Mock()
            mock_get_engine.return_value = mock_engine
            mock_safe_get.return_value = ["core_001"]

            mock_args = Mock()
            mock_args.verbose = True

            result = instruction_completer("core", mock_args)
            assert result == ["core_001"]

    def test_instruction_completer_with_kwargs(self):
        """Test that additional kwargs don't affect completion"""
        with patch(
            "agentspec.cli.completers.get_completion_engine"
        ) as mock_get_engine, patch(
            "agentspec.cli.completers.safe_get_completions"
        ) as mock_safe_get:
            mock_engine = Mock()
            mock_get_engine.return_value = mock_engine
            mock_safe_get.return_value = ["core_001"]

            result = instruction_completer("core", None, extra_arg="value")
            assert result == ["core_001"]

    def test_requirement_10_2_instruction_completion(self):
        """Test Requirement 10.2: Instruction ID completion displays available instructions"""
        with patch(
            "agentspec.cli.completers.get_completion_engine"
        ) as mock_get_engine, patch(
            "agentspec.cli.completers.safe_get_completions"
        ) as mock_safe_get:
            mock_engine = Mock()
            mock_get_engine.return_value = mock_engine
            mock_safe_get.return_value = ["core_001", "frontend_001", "testing_001"]

            result = instruction_completer("", None)

            expected_instructions = ["core_001", "frontend_001", "testing_001"]
            assert result == expected_instructions

    def test_requirement_10_2_core_prefix_completion(self):
        """Test Requirement 10.2: 'core' prefix should complete to core instructions"""
        with patch(
            "agentspec.cli.completers.get_completion_engine"
        ) as mock_get_engine, patch(
            "agentspec.cli.completers.safe_get_completions"
        ) as mock_safe_get:
            mock_engine = Mock()
            mock_get_engine.return_value = mock_engine
            mock_safe_get.return_value = ["core_001", "core_002"]

            result = instruction_completer("core", None)
            assert result == ["core_001", "core_002"]

    def test_requirement_10_4_graceful_degradation(self):
        """Test Requirement 10.4: Graceful degradation when instruction database unavailable"""
        with patch(
            "agentspec.cli.completers.get_completion_engine"
        ) as mock_get_engine, patch(
            "agentspec.cli.completers.safe_get_completions"
        ) as mock_safe_get:
            mock_engine = Mock()
            mock_get_engine.return_value = mock_engine
            mock_safe_get.return_value = []  # Simulates database unavailable

            result = instruction_completer("core", None)
            assert result == []


class TestCommaSeparatedInstructionCompleter:
    """Test cases for comma_separated_instruction_completer function"""

    @patch("agentspec.cli.completers.get_completion_engine")
    @patch("agentspec.cli.completers.safe_get_completions")
    def test_comma_separated_instruction_completer_single_instruction(
        self, mock_safe_get, mock_get_engine
    ):
        """Test comma-separated instruction completion with single instruction"""
        mock_engine = Mock()
        mock_get_engine.return_value = mock_engine
        mock_safe_get.return_value = ["core_001", "core_002"]

        result = comma_separated_instruction_completer("core", None)

        # Verify safe_get_completions was called with correct arguments
        mock_safe_get.assert_called_once_with(
            mock_engine.get_instruction_completions, "core"
        )

        assert result == ["core_001", "core_002"]

    @patch("agentspec.cli.completers.get_completion_engine")
    @patch("agentspec.cli.completers.safe_get_completions")
    def test_comma_separated_instruction_completer_multiple_instructions(
        self, mock_safe_get, mock_get_engine
    ):
        """Test comma-separated instruction completion with multiple existing instructions"""
        mock_engine = Mock()
        mock_get_engine.return_value = mock_engine
        mock_safe_get.return_value = ["core_001", "core_002", "core_003"]

        # Test with existing instructions
        result = comma_separated_instruction_completer(
            "core_001,frontend_001,core", None
        )

        # Should filter out already selected core_001
        expected = ["core_001,frontend_001,core_002", "core_001,frontend_001,core_003"]
        assert result == expected

    @patch("agentspec.cli.completers.get_completion_engine")
    @patch("agentspec.cli.completers.safe_get_completions")
    def test_comma_separated_instruction_completer_filters_existing(
        self, mock_safe_get, mock_get_engine
    ):
        """Test that comma-separated completion filters out already selected instructions"""
        mock_engine = Mock()
        mock_get_engine.return_value = mock_engine
        mock_safe_get.return_value = ["core_001", "core_002", "core_003"]

        # Test with core_001 already selected
        result = comma_separated_instruction_completer("core_001,core", None)

        # Should not suggest core_001 again
        expected = ["core_001,core_002", "core_001,core_003"]
        assert result == expected

    @patch("agentspec.cli.completers.get_completion_engine")
    @patch("agentspec.cli.completers.safe_get_completions")
    def test_comma_separated_instruction_completer_with_spaces(
        self, mock_safe_get, mock_get_engine
    ):
        """Test comma-separated completion handles spaces correctly"""
        mock_engine = Mock()
        mock_get_engine.return_value = mock_engine
        mock_safe_get.return_value = ["core_001", "core_002"]

        # Test with spaces around commas - spaces are normalized in output
        result = comma_separated_instruction_completer("frontend_001, core", None)

        # Should normalize spaces (consistent with tag completer behavior)
        expected = ["frontend_001,core_001", "frontend_001,core_002"]
        assert result == expected

    @patch("agentspec.cli.completers.get_completion_engine")
    @patch("agentspec.cli.completers.safe_get_completions")
    def test_comma_separated_instruction_completer_empty_current(
        self, mock_safe_get, mock_get_engine
    ):
        """Test comma-separated completion with empty current instruction"""
        mock_engine = Mock()
        mock_get_engine.return_value = mock_engine
        mock_safe_get.return_value = ["core_001", "frontend_001", "testing_001"]

        # Test with trailing comma and empty current instruction
        result = comma_separated_instruction_completer("core_001,", None)

        # Should suggest all available instructions except already selected
        expected = ["core_001,frontend_001", "core_001,testing_001"]
        assert result == expected

    @patch("agentspec.cli.completers.get_completion_engine")
    @patch("agentspec.cli.completers.safe_get_completions")
    def test_comma_separated_instruction_completer_error_handling(
        self, mock_safe_get, mock_get_engine
    ):
        """Test comma-separated instruction completion error handling"""
        mock_engine = Mock()
        mock_get_engine.return_value = mock_engine
        mock_safe_get.return_value = []  # Empty result on error

        result = comma_separated_instruction_completer("core_001,test", None)

        assert result == []
        mock_safe_get.assert_called_once()

    def test_comma_separated_instruction_completer_with_parsed_args(self):
        """Test that parsed_args parameter doesn't affect completion"""
        with patch(
            "agentspec.cli.completers.get_completion_engine"
        ) as mock_get_engine, patch(
            "agentspec.cli.completers.safe_get_completions"
        ) as mock_safe_get:
            mock_engine = Mock()
            mock_get_engine.return_value = mock_engine
            mock_safe_get.return_value = ["core_001"]

            mock_args = Mock()
            mock_args.verbose = True

            result = comma_separated_instruction_completer("core", mock_args)
            assert result == ["core_001"]

    def test_comma_separated_instruction_completer_with_kwargs(self):
        """Test that additional kwargs don't affect completion"""
        with patch(
            "agentspec.cli.completers.get_completion_engine"
        ) as mock_get_engine, patch(
            "agentspec.cli.completers.safe_get_completions"
        ) as mock_safe_get:
            mock_engine = Mock()
            mock_get_engine.return_value = mock_engine
            mock_safe_get.return_value = ["core_001"]

            result = comma_separated_instruction_completer(
                "core", None, extra_arg="value"
            )
            assert result == ["core_001"]

    def test_requirement_10_2_comma_separated_instruction_completion(self):
        """Test Requirement 10.2: Comma-separated instruction completion for multi-instruction lists"""
        with patch(
            "agentspec.cli.completers.get_completion_engine"
        ) as mock_get_engine, patch(
            "agentspec.cli.completers.safe_get_completions"
        ) as mock_safe_get:
            mock_engine = Mock()
            mock_get_engine.return_value = mock_engine
            mock_safe_get.return_value = ["frontend_001", "frontend_002"]

            result = comma_separated_instruction_completer("core_001,frontend", None)

            expected = ["core_001,frontend_001", "core_001,frontend_002"]
            assert result == expected

    def test_requirement_10_3_no_duplicate_suggestions(self):
        """Test Requirement 10.3: Don't suggest already-selected instruction IDs"""
        with patch(
            "agentspec.cli.completers.get_completion_engine"
        ) as mock_get_engine, patch(
            "agentspec.cli.completers.safe_get_completions"
        ) as mock_safe_get:
            mock_engine = Mock()
            mock_get_engine.return_value = mock_engine
            mock_safe_get.return_value = ["core_001", "core_002", "core_003"]

            # core_001 is already selected, should not be suggested again
            result = comma_separated_instruction_completer("core_001,core", None)

            # Should only suggest core_002 and core_003
            expected = ["core_001,core_002", "core_001,core_003"]
            assert result == expected

    def test_requirement_10_4_graceful_degradation(self):
        """Test Requirement 10.4: Graceful degradation when instruction database unavailable"""
        with patch(
            "agentspec.cli.completers.get_completion_engine"
        ) as mock_get_engine, patch(
            "agentspec.cli.completers.safe_get_completions"
        ) as mock_safe_get:
            mock_engine = Mock()
            mock_get_engine.return_value = mock_engine
            mock_safe_get.return_value = []  # Simulates database unavailable

            result = comma_separated_instruction_completer("core_001,test", None)
            assert result == []
