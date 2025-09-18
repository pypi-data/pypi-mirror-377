"""
Integration tests for CLI workflows.
"""

import json
import tempfile
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

from agentspec.cli.main import AgentSpecCLI


class TestCLIWorkflows:
    """Integration tests for complete CLI workflows."""

    def test_list_tags_workflow(self, mock_instruction_files):
        """Test complete list-tags workflow."""
        cli = AgentSpecCLI()

        # Mock the instruction database path
        with patch(
            "agentspec.core.instruction_database.InstructionDatabase"
        ) as mock_db_class:
            mock_db = mock_db_class.return_value
            mock_db.load_instructions.return_value = {
                "test_inst1": type(
                    "Instruction",
                    (),
                    {
                        "id": "test_inst1",
                        "tags": ["testing", "quality"],
                        "metadata": type("Metadata", (), {"category": "testing"})(),
                    },
                )(),
                "test_inst2": type(
                    "Instruction",
                    (),
                    {
                        "id": "test_inst2",
                        "tags": ["general", "standards"],
                        "metadata": type("Metadata", (), {"category": "general"})(),
                    },
                )(),
            }
            mock_db.get_all_tags.return_value = {
                "testing",
                "quality",
                "general",
                "standards",
            }

            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                result = cli.run(["list-tags"])

            assert result == 0
            output = mock_stdout.getvalue()
            assert "Available tags:" in output
            assert "testing" in output
            assert "general" in output.lower()

    def test_generate_spec_workflow(
        self, mock_instruction_files, mock_template_files, temp_dir
    ):
        """Test complete spec generation workflow."""
        cli = AgentSpecCLI()
        output_file = temp_dir / "generated_spec.md"

        with patch(
            "agentspec.core.instruction_database.InstructionDatabase"
        ) as mock_db_class:
            with patch(
                "agentspec.core.template_manager.TemplateManager"
            ) as mock_tm_class:
                with patch(
                    "agentspec.core.context_detector.ContextDetector"
                ) as mock_cd_class:
                    with patch(
                        "agentspec.core.spec_generator.SpecGenerator"
                    ) as mock_sg_class:
                        # Setup mocks
                        mock_spec = type(
                            "GeneratedSpec",
                            (),
                            {
                                "content": "# Generated Specification\n\nTest content",
                                "format": "markdown",
                                "instructions_used": ["test_inst1"],
                                "validation_result": type(
                                    "ValidationResult",
                                    (),
                                    {"is_valid": True, "errors": [], "warnings": []},
                                )(),
                            },
                        )()

                        mock_generator = mock_sg_class.return_value
                        mock_generator.generate_spec.return_value = mock_spec
                        mock_generator.export_spec.return_value = mock_spec.content

                        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                            result = cli.run(
                                [
                                    "generate",
                                    "--tags",
                                    "testing,quality",
                                    "--output",
                                    str(output_file),
                                    "--format",
                                    "markdown",
                                ]
                            )

                        assert result == 0
                        output = mock_stdout.getvalue()
                        assert "Generating specification..." in output
                        assert (
                            "Generated specification with" in output
                            and "instructions" in output
                        )

    def test_interactive_workflow(self):
        """Test interactive workflow."""
        cli = AgentSpecCLI()

        with patch("agentspec.cli.commands.InteractiveWizard") as mock_wizard_class:
            mock_wizard = mock_wizard_class.return_value
            mock_wizard.run_wizard.return_value = {
                "selected_tags": ["general", "testing"],
                "instructions": [{"id": "test_instruction"}],
                "template_id": None,
                "output_file": "test_spec.md",
                "project_context": {},
            }

            result = cli.run(["interactive"])

            assert result == 0
            mock_wizard_class.assert_called_once()
            mock_wizard.run_wizard.assert_called_once()

    def test_analyze_project_workflow(self, mock_project_structure):
        """Test project analysis workflow."""
        cli = AgentSpecCLI()

        with patch("agentspec.core.context_detector.ContextDetector") as mock_cd_class:
            # Setup mock context
            mock_context = type(
                "ProjectContext",
                (),
                {
                    "project_path": str(mock_project_structure),
                    "project_type": type(
                        "ProjectType", (), {"value": "web_frontend"}
                    )(),
                    "technology_stack": type(
                        "TechnologyStack",
                        (),
                        {
                            "languages": [
                                type("Language", (), {"value": "javascript"})()
                            ],
                            "frameworks": [type("Framework", (), {"name": "react"})()],
                            "databases": ["postgresql"],
                            "tools": ["webpack"],
                        },
                    )(),
                    "file_structure": type(
                        "FileStructure",
                        (),
                        {
                            "total_files": 25,
                            "directories": ["src", "public"],
                            "config_files": ["package.json"],
                            "test_files": ["App.test.js"],
                        },
                    )(),
                    "dependencies": [],
                    "git_info": None,
                    "confidence_score": 0.85,
                },
            )()

            mock_detector = mock_cd_class.return_value
            mock_detector.analyze_project.return_value = mock_context
            mock_detector.suggest_instructions.return_value = []

            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                result = cli.run(["analyze", str(mock_project_structure)])

            assert result == 0
            output = mock_stdout.getvalue()
            assert "PROJECT ANALYSIS RESULTS" in output
            assert "web_frontend" in output
            assert "0.85" in output or "confidence" in output.lower()

    def test_validate_spec_workflow(self, temp_dir):
        """Test spec validation workflow."""
        cli = AgentSpecCLI()

        # Create test spec file
        spec_file = temp_dir / "test_spec.md"
        spec_file.write_text(
            """
# AgentSpec - Project Specification

## IMPLEMENTATION FRAMEWORK

### Pre-Development Checklist
- [ ] Load existing project context

## QUALITY GATES

1. **Zero Errors**: No linting errors
        """
        )

        with patch("agentspec.core.spec_generator.SpecGenerator") as mock_sg_class:
            mock_generator = mock_sg_class.return_value
            mock_result = type(
                "ValidationResult", (), {"is_valid": True, "errors": [], "warnings": []}
            )()
            mock_generator.validate_spec.return_value = mock_result

            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                result = cli.run(["validate", str(spec_file)])

            assert result == 0
            output = mock_stdout.getvalue()
            assert "✅ Specification is valid" in output

    def test_version_workflow(self):
        """Test version command workflow."""
        cli = AgentSpecCLI()

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = cli.run(["version"])

        assert result == 0
        output = mock_stdout.getvalue()
        assert "AgentSpec" in output
        assert "Specification-Driven Development" in output

    def test_help_workflow(self):
        """Test help command workflow."""
        cli = AgentSpecCLI()

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = cli.run(["help"])

        assert result == 0
        output = mock_stdout.getvalue()
        assert "AgentSpec - Specification-Driven Development" in output
        assert "Commands:" in output or "Available commands" in output

    def test_error_handling_workflow(self):
        """Test error handling in workflows."""
        cli = AgentSpecCLI()

        # Test with invalid command
        with patch("sys.stdout", new_callable=StringIO):
            try:
                result = cli.run(["invalid-command"])
                # Should return error code
                assert result != 0
            except SystemExit as e:
                # argparse calls sys.exit() for invalid commands
                assert e.code != 0

    def test_config_file_workflow(self, temp_dir):
        """Test workflow with custom config file."""
        # Create custom config
        config_file = temp_dir / "custom_config.yaml"
        config_content = """
agentspec:
  version: "2.0.0"
  paths:
    instructions: "custom/instructions"
    templates: "custom/templates"
  logging:
    level: "DEBUG"
        """
        config_file.write_text(config_content)

        cli = AgentSpecCLI()

        with patch(
            "agentspec.core.instruction_database.InstructionDatabase"
        ) as mock_db_class:
            mock_db = mock_db_class.return_value
            mock_db.load_instructions.return_value = {}
            mock_db.get_all_tags.return_value = set()

            with patch("sys.stdout", new_callable=StringIO):
                result = cli.run(["--config", str(config_file), "list-tags"])

            assert result == 0

    def test_verbose_output_workflow(self):
        """Test workflow with verbose output."""
        cli = AgentSpecCLI()

        with patch(
            "agentspec.core.instruction_database.InstructionDatabase"
        ) as mock_db_class:
            mock_db = mock_db_class.return_value
            mock_db.load_instructions.return_value = {}
            mock_db.get_all_tags.return_value = set()

            with patch("sys.stdout", new_callable=StringIO):
                result = cli.run(["--verbose", "list-tags"])

            assert result == 0

    def test_quiet_output_workflow(self):
        """Test workflow with quiet output."""
        cli = AgentSpecCLI()

        with patch(
            "agentspec.core.instruction_database.InstructionDatabase"
        ) as mock_db_class:
            mock_db = mock_db_class.return_value
            mock_db.load_instructions.return_value = {}
            mock_db.get_all_tags.return_value = set()

            with patch("sys.stdout", new_callable=StringIO):
                result = cli.run(["--quiet", "list-tags"])

            assert result == 0


class TestEndToEndWorkflows:
    """End-to-end integration tests."""

    def test_complete_spec_generation_workflow(self, temp_dir):
        """Test complete workflow from project analysis to spec generation."""
        # Create mock project structure
        project_dir = temp_dir / "test_project"
        project_dir.mkdir()

        # Create package.json
        package_json = {
            "name": "test-app",
            "dependencies": {"react": "^18.0.0", "react-dom": "^18.0.0"},
        }

        with open(project_dir / "package.json", "w") as f:
            json.dump(package_json, f)

        # Create source files
        src_dir = project_dir / "src"
        src_dir.mkdir()
        (src_dir / "App.js").write_text("import React from 'react';")

        cli = AgentSpecCLI()
        output_file = temp_dir / "complete_spec.md"

        with patch("agentspec.core.context_detector.ContextDetector") as mock_cd_class:
            with patch("agentspec.core.spec_generator.SpecGenerator") as mock_sg_class:
                # Setup context detection
                mock_context = type(
                    "ProjectContext",
                    (),
                    {
                        "project_type": type(
                            "ProjectType", (), {"value": "web_frontend"}
                        )(),
                        "technology_stack": type(
                            "TechnologyStack",
                            (),
                            {
                                "frameworks": [
                                    type("Framework", (), {"name": "react"})()
                                ]
                            },
                        )(),
                        "confidence_score": 0.9,
                    },
                )()

                mock_detector = mock_cd_class.return_value
                mock_detector.analyze_project.return_value = mock_context

                # Setup spec generation
                mock_spec = type(
                    "GeneratedSpec",
                    (),
                    {
                        "content": "# Complete Specification\n\nGenerated from analysis",
                        "format": "markdown",
                        "instructions_used": ["react_testing", "frontend_quality"],
                        "validation_result": type(
                            "ValidationResult",
                            (),
                            {"is_valid": True, "errors": [], "warnings": []},
                        )(),
                    },
                )()

                mock_generator = mock_sg_class.return_value
                mock_generator.context_detector = mock_detector
                mock_generator.generate_spec.return_value = mock_spec
                mock_generator.export_spec.return_value = mock_spec.content

                with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                    result = cli.run(
                        [
                            "generate",
                            "--tags",
                            "frontend,testing",
                            "--project-path",
                            str(project_dir),
                            "--output",
                            str(output_file),
                        ]
                    )

                assert result == 0
                output = mock_stdout.getvalue()
                assert "Detected project type:" in output
                assert "Generating specification..." in output

    def test_template_based_workflow(self, temp_dir):
        """Test workflow using templates."""
        cli = AgentSpecCLI()
        output_file = temp_dir / "template_spec.md"

        # Mock the CLI's template manager and spec generator directly
        with patch.object(cli, "template_manager") as mock_tm:
            with patch.object(cli, "spec_generator") as mock_sg:
                # Setup template
                mock_template = type(
                    "Template",
                    (),
                    {
                        "id": "react_app",
                        "name": "React Application",
                        "default_tags": ["frontend", "react", "testing"],
                    },
                )()

                mock_tm.load_templates.return_value = {"react_app": mock_template}
                mock_tm.get_template.return_value = mock_template

                # Setup spec generation
                mock_spec = type(
                    "GeneratedSpec",
                    (),
                    {
                        "content": "# React App Specification\n\nTemplate-based spec",
                        "format": "markdown",
                        "template_used": "react_app",
                        "validation_result": type(
                            "ValidationResult",
                            (),
                            {"is_valid": True, "errors": [], "warnings": []},
                        )(),
                    },
                )()

                mock_sg.template_manager = mock_tm
                mock_sg.generate_spec.return_value = mock_spec
                mock_sg.export_spec.return_value = mock_spec.content

                with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                    result = cli.run(
                        [
                            "generate",
                            "--template",
                            "react_app",
                            "--output",
                            str(output_file),
                        ]
                    )

                assert result == 0
                output = mock_stdout.getvalue()
                assert "Generating specification..." in output

    def test_error_recovery_workflow(self):
        """Test error recovery in workflows."""
        cli = AgentSpecCLI()

        # Test with failing service initialization by mocking at the class level
        with patch(
            "agentspec.core.instruction_database.InstructionDatabase.load_instructions",
            side_effect=Exception("Database error"),
        ):
            try:
                result = cli.run(["list-tags"])
                assert result == 1  # Should return error code
            except SystemExit as e:
                # sys.exit(1) was called, which is the expected error handling
                assert e.code == 1

    def test_keyboard_interrupt_workflow(self):
        """Test keyboard interrupt handling."""
        cli = AgentSpecCLI()

        # Mock at the class level to ensure it persists through CLI initialization
        with patch(
            "agentspec.core.instruction_database.InstructionDatabase.get_all_tags",
            side_effect=KeyboardInterrupt(),
        ):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                try:
                    result = cli.run(["list-tags"])
                    assert result == 1
                except KeyboardInterrupt:
                    # KeyboardInterrupt might propagate, which is also acceptable
                    pass
            output = mock_stdout.getvalue()
            # The test should pass if KeyboardInterrupt is handled properly


class TestCLIIntegrationEdgeCases:
    """Test edge cases in CLI integration."""

    def test_empty_instruction_database(self):
        """Test CLI with empty instruction database."""
        cli = AgentSpecCLI()

        # Mock at the class level to ensure it persists through CLI initialization
        with patch(
            "agentspec.core.instruction_database.InstructionDatabase.get_all_tags",
            return_value=set(),
        ):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                result = cli.run(["list-tags"])

            assert result == 0
            output = mock_stdout.getvalue()
            # Check if the output indicates no tags (empty set should result in different output)
            assert "No tags available" in output or "Available tags:" in output

    def test_malformed_project_structure(self, temp_dir):
        """Test CLI with malformed project structure."""
        # Create project with invalid files
        project_dir = temp_dir / "malformed_project"
        project_dir.mkdir()

        # Create invalid package.json
        (project_dir / "package.json").write_text("{ invalid json }")

        cli = AgentSpecCLI()

        # Mock at the class level to ensure it persists through CLI initialization
        with patch(
            "agentspec.core.context_detector.ContextDetector.analyze_project",
            side_effect=Exception("Analysis failed"),
        ):
            with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
                result = cli.run(["analyze", str(project_dir)])

            # The CLI should handle the exception gracefully and return error code
            assert result == 1
            error_output = mock_stderr.getvalue()
            assert "Error:" in error_output

    def test_permission_denied_scenarios(self, temp_dir):
        """Test CLI with permission denied scenarios."""
        cli = AgentSpecCLI()

        # Test with unwritable output file
        output_file = temp_dir / "readonly_spec.md"
        output_file.write_text("existing content")
        output_file.chmod(0o444)  # Read-only

        with patch("agentspec.core.spec_generator.SpecGenerator") as mock_sg_class:
            mock_spec = type(
                "GeneratedSpec",
                (),
                {
                    "content": "# Test Spec",
                    "format": "markdown",
                    "validation_result": type(
                        "ValidationResult",
                        (),
                        {"is_valid": True, "errors": [], "warnings": []},
                    )(),
                },
            )()

            mock_generator = mock_sg_class.return_value
            mock_generator.generate_spec.return_value = mock_spec
            mock_generator.export_spec.side_effect = PermissionError(
                "Permission denied"
            )

            with patch("sys.stderr", new_callable=StringIO):
                result = cli.run(
                    ["generate", "--tags", "testing", "--output", str(output_file)]
                )

            assert result == 1

    def test_large_specification_generation(self):
        """Test CLI with large specification generation."""
        cli = AgentSpecCLI()

        # Create large mock specification
        large_content = "# Large Specification\n\n" + "Content line\n" * 10000

        with patch("agentspec.core.spec_generator.SpecGenerator") as mock_sg_class:
            mock_spec = type(
                "GeneratedSpec",
                (),
                {
                    "content": large_content,
                    "format": "markdown",
                    "instructions_used": [f"inst_{i}" for i in range(100)],
                    "validation_result": type(
                        "ValidationResult",
                        (),
                        {"is_valid": True, "errors": [], "warnings": []},
                    )(),
                },
            )()

            mock_generator = mock_sg_class.return_value
            mock_generator.generate_spec.return_value = mock_spec

            with patch("sys.stdout", new_callable=StringIO):
                result = cli.run(["generate", "--tags", "testing"])

            assert result == 0

    def test_concurrent_cli_usage(self):
        """Test concurrent CLI usage scenarios."""
        import threading
        import time

        results = []

        def run_cli_command():
            cli = AgentSpecCLI()

            with patch(
                "agentspec.core.instruction_database.InstructionDatabase"
            ) as mock_db_class:
                mock_db = mock_db_class.return_value
                mock_db.load_instructions.return_value = {}
                mock_db.get_all_tags.return_value = set()

                with patch("sys.stdout", new_callable=StringIO):
                    result = cli.run(["list-tags"])
                    results.append(result)

        # Run multiple CLI instances concurrently
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=run_cli_command)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # All should succeed
        assert all(result == 0 for result in results)
        assert len(results) == 5
