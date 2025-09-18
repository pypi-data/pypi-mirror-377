"""
Unit tests for CLI command handlers.
"""

import json
from io import StringIO
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest

from agentspec.cli.commands import (
    CommandError,
    analyze_project_command,
    generate_spec_command,
    help_command,
    integrate_command,
    interactive_command,
    list_instructions_command,
    list_tags_command,
    list_templates_command,
    validate_spec_command,
    version_command,
)
from agentspec.core.spec_generator import GeneratedSpec, ValidationResult
from tests.conftest import create_test_instruction, create_test_template


class TestListTagsCommand:
    """Test cases for list_tags_command."""

    def test_list_tags_success(self, instruction_database):
        """Test successful tag listing."""
        instruction_database.load_instructions()

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = list_tags_command(instruction_database)

        assert result == 0
        output = mock_stdout.getvalue()
        assert "Available tags:" in output
        assert "testing" in output
        assert "general" in output

    def test_list_tags_with_category(self, instruction_database):
        """Test tag listing with category filter."""
        instruction_database.load_instructions()

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = list_tags_command(instruction_database, category="Testing")

        assert result == 0
        output = mock_stdout.getvalue()
        assert "Testing:" in output

    def test_list_tags_invalid_category(self, instruction_database):
        """Test tag listing with invalid category."""
        instruction_database.load_instructions()

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = list_tags_command(instruction_database, category="InvalidCategory")

        assert result == 1
        output = mock_stdout.getvalue()
        assert "Unknown category" in output

    def test_list_tags_verbose(self, instruction_database):
        """Test verbose tag listing."""
        instruction_database.load_instructions()

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = list_tags_command(instruction_database, verbose=True)

        assert result == 0
        output = mock_stdout.getvalue()
        assert "e.g.," in output  # Should show sample instructions

    def test_list_tags_no_instructions(self):
        """Test tag listing with no instructions."""
        empty_db = Mock()
        empty_db.load_instructions.return_value = {}

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = list_tags_command(empty_db)

        assert result == 0
        output = mock_stdout.getvalue()
        assert "No instructions found" in output

    def test_list_tags_exception(self):
        """Test tag listing with exception."""
        failing_db = Mock()
        failing_db.load_instructions.side_effect = Exception("Database error")

        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            result = list_tags_command(failing_db)

        assert result == 1
        error_output = mock_stderr.getvalue()
        assert "Error:" in error_output


class TestListInstructionsCommand:
    """Test cases for list_instructions_command."""

    def test_list_instructions_all(self, instruction_database):
        """Test listing all instructions."""
        instruction_database.load_instructions()

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = list_instructions_command(instruction_database)

        assert result == 0
        output = mock_stdout.getvalue()
        assert "All instructions" in output
        assert "general_quality" in output
        assert "unit_testing" in output

    def test_list_instructions_by_tag(self, instruction_database):
        """Test listing instructions by tag."""
        instruction_database.load_instructions()

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = list_instructions_command(instruction_database, tag="testing")

        assert result == 0
        output = mock_stdout.getvalue()
        assert "Instructions for tag 'testing'" in output
        assert "unit_testing" in output

    def test_list_instructions_by_category(self, instruction_database):
        """Test listing instructions by category."""
        instruction_database.load_instructions()

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = list_instructions_command(instruction_database, category="testing")

        assert result == 0
        output = mock_stdout.getvalue()
        assert "Instructions for category 'testing'" in output

    def test_list_instructions_verbose(self, instruction_database):
        """Test verbose instruction listing."""
        instruction_database.load_instructions()

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = list_instructions_command(instruction_database, verbose=True)

        assert result == 0
        output = mock_stdout.getvalue()
        # Should show full content in verbose mode
        assert len(output) > 300  # Verbose output should be longer

    def test_list_instructions_no_matches(self, instruction_database):
        """Test listing instructions with no matches."""
        instruction_database.load_instructions()

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = list_instructions_command(instruction_database, tag="nonexistent")

        assert result == 0
        output = mock_stdout.getvalue()
        assert "No instructions found for tag: nonexistent" in output


class TestListTemplatesCommand:
    """Test cases for list_templates_command."""

    def test_list_templates_all(self, template_manager):
        """Test listing all templates."""
        template_manager.load_templates()

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = list_templates_command(template_manager)

        assert result == 0
        output = mock_stdout.getvalue()
        assert "All templates" in output
        assert "React Application" in output

    def test_list_templates_by_project_type(self, template_manager):
        """Test listing templates by project type."""
        template_manager.load_templates()

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = list_templates_command(
                template_manager, project_type="web_frontend"
            )

        assert result == 0
        output = mock_stdout.getvalue()
        assert "Templates for project type 'web_frontend'" in output

    def test_list_templates_verbose(self, template_manager):
        """Test verbose template listing."""
        template_manager.load_templates()

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = list_templates_command(template_manager, verbose=True)

        assert result == 0
        output = mock_stdout.getvalue()
        assert "Default tags:" in output
        assert "Required instructions:" in output

    def test_list_templates_no_templates(self):
        """Test listing with no templates."""
        empty_manager = Mock()
        empty_manager.load_templates.return_value = {}

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = list_templates_command(empty_manager)

        assert result == 0
        output = mock_stdout.getvalue()
        assert "No templates found" in output

    def test_list_templates_invalid_project_type(self):
        """Test listing with invalid project type."""
        mock_template_manager = Mock()
        mock_template_manager.get_templates_by_project_type.return_value = []
        mock_template_manager.get_all_project_types.return_value = {
            "web_frontend",
            "mobile_app",
        }

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = list_templates_command(
                mock_template_manager, project_type="invalid"
            )

        assert result == 0
        output = mock_stdout.getvalue()
        assert "No templates found for project type: invalid" in output
        assert "Available project types:" in output


class TestGenerateSpecCommand:
    """Test cases for generate_spec_command."""

    def test_generate_spec_with_tags(self):
        """Test spec generation with tags."""
        mock_spec_generator = Mock()
        mock_spec = GeneratedSpec(
            content="# Test Specification\n\nGenerated content",
            format="markdown",
            instructions_used=["test_instruction"],
        )
        mock_spec.validation_result = ValidationResult(True, [], [])

        mock_spec_generator.generate_spec.return_value = mock_spec

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = generate_spec_command(
                mock_spec_generator, tags=["testing", "quality"]
            )

        assert result == 0
        output = mock_stdout.getvalue()
        assert "Generating specification..." in output
        assert "Generated specification with 1 instructions" in output
        assert "# Test Specification" in output

    def test_generate_spec_with_output_file(self, temp_dir):
        """Test spec generation with output file."""
        mock_spec_generator = Mock()
        mock_spec = GeneratedSpec(content="# Test Specification", format="markdown")
        mock_spec.validation_result = ValidationResult(True, [], [])

        mock_spec_generator.generate_spec.return_value = mock_spec
        mock_spec_generator.export_spec.return_value = mock_spec.content

        output_file = temp_dir / "test_spec.md"

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = generate_spec_command(
                mock_spec_generator, tags=["testing"], output_file=str(output_file)
            )

        assert result == 0
        output = mock_stdout.getvalue()
        assert f"Specification saved to: {output_file}" in output
        mock_spec_generator.export_spec.assert_called_once_with(
            mock_spec, str(output_file)
        )

    def test_generate_spec_with_project_context(self, sample_project_context):
        """Test spec generation with project context."""
        mock_spec_generator = Mock()
        mock_spec = GeneratedSpec(content="# Test Spec", format="markdown")
        mock_spec.validation_result = ValidationResult(True, [], [])

        mock_spec_generator.context_detector.analyze_project.return_value = (
            sample_project_context
        )
        mock_spec_generator.generate_spec.return_value = mock_spec

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = generate_spec_command(
                mock_spec_generator, tags=["testing"], project_path="/test/project"
            )

        assert result == 0
        output = mock_stdout.getvalue()
        assert "Detected project type:" in output
        assert "Detected technologies:" in output

    def test_generate_spec_validation_errors(self):
        """Test spec generation with validation errors."""
        mock_spec_generator = Mock()
        mock_spec = GeneratedSpec(content="# Test Spec", format="markdown")
        mock_spec.validation_result = ValidationResult(
            False, ["Missing required section"], ["Template parameter not used"]
        )

        mock_spec_generator.generate_spec.return_value = mock_spec

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = generate_spec_command(mock_spec_generator, tags=["testing"])

        assert result == 0  # Should still succeed but show warnings
        output = mock_stdout.getvalue()
        assert "Specification validation warnings:" in output
        assert "Missing required section" in output
        assert "Specification warnings:" in output
        assert "Template parameter not used" in output

    def test_generate_spec_no_parameters(self, spec_generator):
        """Test spec generation with no parameters."""
        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            result = generate_spec_command(spec_generator)

        assert result == 1
        error_output = mock_stderr.getvalue()
        assert "Must specify tags, instructions, or template" in error_output

    def test_generate_spec_exception(self):
        """Test spec generation with exception."""
        mock_spec_generator = Mock()
        mock_spec_generator.generate_spec.side_effect = Exception("Generation failed")

        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            result = generate_spec_command(mock_spec_generator, tags=["testing"])

        assert result == 1
        error_output = mock_stderr.getvalue()
        assert "Error:" in error_output


class TestInteractiveCommand:
    """Test cases for interactive_command."""

    @patch("agentspec.cli.commands.InteractiveWizard")
    def test_interactive_command_success(self, mock_wizard_class, spec_generator):
        """Test successful interactive command."""
        mock_wizard = Mock()
        mock_wizard.run_wizard.return_value = {
            "selected_tags": ["general", "testing"],
            "instructions": [{"id": "test_instruction"}],
            "template_id": None,
            "output_file": "test_spec.md",
            "project_context": {},
        }
        mock_wizard_class.return_value = mock_wizard

        result = interactive_command(spec_generator)

        assert result == 0
        mock_wizard_class.assert_called_once()
        mock_wizard.run_wizard.assert_called_once()

    @patch("agentspec.cli.commands.InteractiveWizard")
    def test_interactive_command_keyboard_interrupt(
        self, mock_wizard_class, spec_generator
    ):
        """Test interactive command with keyboard interrupt."""
        mock_wizard = Mock()
        mock_wizard.run_wizard.side_effect = KeyboardInterrupt()
        mock_wizard_class.return_value = mock_wizard

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = interactive_command(spec_generator)

        assert result == 1
        output = mock_stdout.getvalue()
        assert "Operation cancelled by user" in output

    @patch("agentspec.cli.commands.InteractiveWizard")
    def test_interactive_command_exception(self, mock_wizard_class, spec_generator):
        """Test interactive command with exception."""
        mock_wizard = Mock()
        mock_wizard.run_wizard.side_effect = Exception("Wizard failed")
        mock_wizard_class.return_value = mock_wizard

        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            result = interactive_command(spec_generator)

        assert result == 1
        error_output = mock_stderr.getvalue()
        assert "Error:" in error_output


class TestAnalyzeProjectCommand:
    """Test cases for analyze_project_command."""

    def test_analyze_project_success(self, sample_project_context):
        """Test successful project analysis."""
        mock_context_detector = Mock()
        mock_context_detector.analyze_project.return_value = sample_project_context
        mock_context_detector.suggest_instructions.return_value = [
            Mock(
                instruction_id="test_inst",
                confidence=0.8,
                tags=["test"],
                reasons=["Test reason"],
            )
        ]

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = analyze_project_command(
                mock_context_detector, project_path="/test/project"
            )

        assert result == 0
        output = mock_stdout.getvalue()
        assert "PROJECT ANALYSIS RESULTS" in output
        assert "Project Type:" in output
        assert "Technology Stack:" in output
        assert "INSTRUCTION SUGGESTIONS" in output

    def test_analyze_project_with_output_file(
        self, context_detector, sample_project_context, temp_dir
    ):
        """Test project analysis with output file."""
        with patch.object(
            context_detector, "analyze_project", return_value=sample_project_context
        ), patch.object(context_detector, "suggest_instructions", return_value=[]):
            output_file = temp_dir / "analysis.json"

            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                result = analyze_project_command(
                    context_detector,
                    project_path="/test/project",
                    output_file=str(output_file),
                )

            assert result == 0
            output = mock_stdout.getvalue()
            assert f"Analysis results saved to: {output_file}" in output

            # Verify JSON file was created
            assert output_file.exists()
            with open(output_file) as f:
                data = json.load(f)
            assert "project_type" in data
            assert "confidence_score" in data

    def test_analyze_project_no_suggestions(
        self, context_detector, sample_project_context
    ):
        """Test project analysis without suggestions."""
        with patch.object(
            context_detector, "analyze_project", return_value=sample_project_context
        ):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                result = analyze_project_command(
                    context_detector,
                    project_path="/test/project",
                    suggest_instructions=False,
                )

            assert result == 0
            output = mock_stdout.getvalue()
            assert "PROJECT ANALYSIS RESULTS" in output
            assert "INSTRUCTION SUGGESTIONS" not in output

    def test_analyze_project_exception(self, context_detector):
        """Test project analysis with exception."""
        with patch.object(
            context_detector,
            "analyze_project",
            side_effect=Exception("Analysis failed"),
        ):
            with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
                result = analyze_project_command(
                    context_detector, project_path="/test/project"
                )

        assert result == 1
        error_output = mock_stderr.getvalue()
        assert "Error:" in error_output


class TestValidateSpecCommand:
    """Test cases for validate_spec_command."""

    def test_validate_spec_success(self, spec_generator, temp_dir):
        """Test successful spec validation."""
        spec_file = temp_dir / "test_spec.md"
        spec_file.write_text("# Test Specification\n\nValid content")

        mock_result = ValidationResult(True, [], [])
        with patch.object(spec_generator, "validate_spec", return_value=mock_result):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                result = validate_spec_command(spec_generator, str(spec_file))

            assert result == 0
            output = mock_stdout.getvalue()
            assert "✅ Specification is valid" in output

    def test_validate_spec_with_errors(self, spec_generator, temp_dir):
        """Test spec validation with errors."""
        spec_file = temp_dir / "test_spec.md"
        spec_file.write_text("Invalid spec")

        mock_result = ValidationResult(
            False, ["Missing required section"], ["Warning message"]
        )
        with patch.object(spec_generator, "validate_spec", return_value=mock_result):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                result = validate_spec_command(spec_generator, str(spec_file))

            assert result == 1
            output = mock_stdout.getvalue()
            assert "❌ Specification validation failed:" in output
            assert "Missing required section" in output
            assert "⚠️  Warnings:" in output
            assert "Warning message" in output

    def test_validate_spec_file_not_found(self, spec_generator):
        """Test spec validation with nonexistent file."""
        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            result = validate_spec_command(spec_generator, "/nonexistent/file.md")

        assert result == 1
        error_output = mock_stderr.getvalue()
        assert "Specification file not found" in error_output

    def test_validate_spec_exception(self, spec_generator, temp_dir):
        """Test spec validation with exception."""
        spec_file = temp_dir / "test_spec.md"
        spec_file.write_text("# Test Spec")

        with patch.object(
            spec_generator, "validate_spec", side_effect=Exception("Validation failed")
        ):
            with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
                result = validate_spec_command(spec_generator, str(spec_file))

            assert result == 1
            error_output = mock_stderr.getvalue()
            assert "Error:" in error_output


class TestVersionCommand:
    """Test cases for version_command."""

    def test_version_command_success(self):
        """Test successful version command."""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = version_command()

        assert result == 0
        output = mock_stdout.getvalue()
        assert "AgentSpec" in output
        assert "Specification-Driven Development" in output

    @patch("importlib.metadata.version")
    def test_version_command_with_package_version(self, mock_version):
        """Test version command with package metadata."""
        mock_version.return_value = "2.1.0"

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = version_command()

        assert result == 0
        output = mock_stdout.getvalue()
        assert "AgentSpec 2.1.0" in output

    def test_version_command_exception(self):
        """Test version command with exception."""
        with patch(
            "importlib.metadata.version", side_effect=Exception("Version error")
        ):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                result = version_command()

        assert result == 0  # Should still succeed with default version
        output = mock_stdout.getvalue()
        assert "AgentSpec" in output


class TestHelpCommand:
    """Test cases for help_command."""

    def test_help_command_general(self):
        """Test general help command."""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = help_command()

        assert result == 0
        output = mock_stdout.getvalue()
        assert "AgentSpec - Specification-Driven Development" in output
        assert "Commands:" in output
        assert "list-tags" in output
        assert "generate" in output

    def test_help_command_specific(self):
        """Test help for specific command."""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = help_command("generate")

        assert result == 0
        output = mock_stdout.getvalue()
        assert "Generate a specification" in output
        assert "--tags" in output
        assert "--output" in output

    def test_help_command_unknown(self):
        """Test help for unknown command."""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = help_command("unknown")

        assert result == 0
        output = mock_stdout.getvalue()
        assert "No help available for command: unknown" in output


class TestIntegrateCommand:
    """Test cases for integrate_command."""

    def test_integrate_command_analyze_only(self, temp_dir):
        """Test integrate command with analyze-only flag."""
        # Create a mock project directory
        project_dir = temp_dir / "test_project"
        project_dir.mkdir()
        (project_dir / "package.json").write_text('{"name": "test"}')

        # Create mock services
        mock_instruction_db = Mock()
        mock_template_manager = Mock()
        mock_context_detector = Mock()

        # Mock the integrator
        with patch(
            "agentspec.cli.commands.AIBestPracticesIntegrator"
        ) as mock_integrator_class:
            mock_integrator = Mock()
            mock_integrator.analyze_project.return_value = {
                "project_type": "web_application",
                "technologies": ["react", "typescript"],
                "has_ai_tools": False,
                "security_level": "basic",
                "integration_priority": "medium",
                "recommended_ai_instructions": ["human_in_the_loop_architect"],
                "recommended_templates": ["ai-prompt-engineering"],
            }
            mock_integrator_class.return_value = mock_integrator

            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                result = integrate_command(
                    mock_instruction_db,
                    mock_template_manager,
                    mock_context_detector,
                    project_path=str(project_dir),
                    analyze_only=True,
                    output_format="text",
                )

            assert result == 0
            output = mock_stdout.getvalue()
            assert "Project Analysis Results" in output
            assert "web_application" in output
            assert "human_in_the_loop_architect" in output

    def test_integrate_command_full_integration(self, temp_dir):
        """Test integrate command with full integration."""
        # Create a mock project directory
        project_dir = temp_dir / "test_project"
        project_dir.mkdir()
        (project_dir / "package.json").write_text('{"name": "test"}')

        # Create mock services
        mock_instruction_db = Mock()
        mock_template_manager = Mock()
        mock_context_detector = Mock()

        # Mock the integrator
        with patch(
            "agentspec.cli.commands.AIBestPracticesIntegrator"
        ) as mock_integrator_class:
            mock_integrator = Mock()
            mock_integrator.analyze_project.return_value = {
                "project_type": "web_application",
                "technologies": ["react"],
                "has_ai_tools": True,
                "security_level": "intermediate",
                "integration_priority": "high",
                "recommended_ai_instructions": ["human_in_the_loop_architect"],
                "recommended_templates": ["ai-comprehensive-framework"],
            }
            mock_integrator.generate_integration_plan.return_value = {
                "phases": [{"name": "Foundation", "duration": "1 week"}],
                "estimated_duration": "2 weeks",
            }
            mock_integrator_class.return_value = mock_integrator

            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                result = integrate_command(
                    mock_instruction_db,
                    mock_template_manager,
                    mock_context_detector,
                    project_path=str(project_dir),
                    analyze_only=False,
                    output_format="text",
                )

            assert result == 0
            output = mock_stdout.getvalue()
            assert "AI Best Practices Integration Complete!" in output
            assert "agentspec generate --template ai-comprehensive-framework" in output

            # Verify integration files were created
            mock_integrator.create_integration_files.assert_called_once()

    def test_integrate_command_json_output(self, temp_dir):
        """Test integrate command with JSON output format."""
        # Create a mock project directory
        project_dir = temp_dir / "test_project"
        project_dir.mkdir()

        # Create mock services
        mock_instruction_db = Mock()
        mock_template_manager = Mock()
        mock_context_detector = Mock()

        analysis_data = {
            "project_type": "web_application",
            "technologies": ["react"],
            "has_ai_tools": False,
            "security_level": "basic",
            "integration_priority": "low",
            "recommended_ai_instructions": ["human_in_the_loop_architect"],
            "recommended_templates": ["ai-prompt-engineering"],
        }

        # Mock the integrator
        with patch(
            "agentspec.cli.commands.AIBestPracticesIntegrator"
        ) as mock_integrator_class:
            mock_integrator = Mock()
            mock_integrator.analyze_project.return_value = analysis_data
            mock_integrator_class.return_value = mock_integrator

            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                result = integrate_command(
                    mock_instruction_db,
                    mock_template_manager,
                    mock_context_detector,
                    project_path=str(project_dir),
                    analyze_only=True,
                    output_format="json",
                )

            assert result == 0
            output = mock_stdout.getvalue()

            # Should contain JSON output
            import json

            json_output = json.loads(output.strip())
            assert json_output["project_type"] == "web_application"
            assert (
                "human_in_the_loop_architect"
                in json_output["recommended_ai_instructions"]
            )

    def test_integrate_command_nonexistent_project(self):
        """Test integrate command with nonexistent project path."""
        mock_instruction_db = Mock()
        mock_template_manager = Mock()
        mock_context_detector = Mock()

        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            result = integrate_command(
                mock_instruction_db,
                mock_template_manager,
                mock_context_detector,
                project_path="/nonexistent/path",
                analyze_only=True,
            )

        assert result == 1
        error_output = mock_stderr.getvalue()
        assert "Project path does not exist" in error_output

    def test_integrate_command_exception(self, temp_dir):
        """Test integrate command with exception during analysis."""
        # Create a mock project directory
        project_dir = temp_dir / "test_project"
        project_dir.mkdir()

        # Create mock services
        mock_instruction_db = Mock()
        mock_template_manager = Mock()
        mock_context_detector = Mock()

        # Mock the integrator to raise an exception
        with patch(
            "agentspec.cli.commands.AIBestPracticesIntegrator"
        ) as mock_integrator_class:
            mock_integrator = Mock()
            mock_integrator.analyze_project.side_effect = Exception("Analysis failed")
            mock_integrator_class.return_value = mock_integrator

            with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
                result = integrate_command(
                    mock_instruction_db,
                    mock_template_manager,
                    mock_context_detector,
                    project_path=str(project_dir),
                    analyze_only=True,
                )

            assert result == 1
            error_output = mock_stderr.getvalue()
            assert "Error:" in error_output


class TestCommandError:
    """Test cases for CommandError exception."""

    def test_command_error_creation(self):
        """Test creating CommandError."""
        error = CommandError("Test error message")

        assert str(error) == "Test error message"
        assert isinstance(error, Exception)
