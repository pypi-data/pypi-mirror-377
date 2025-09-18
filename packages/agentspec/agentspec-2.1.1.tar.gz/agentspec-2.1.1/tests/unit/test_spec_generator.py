"""
Unit tests for SpecGenerator class.
"""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from agentspec.core.context_detector import ProjectContext, ProjectType
from agentspec.core.instruction_database import Instruction, InstructionMetadata
from agentspec.core.spec_generator import GeneratedSpec, SpecConfig, SpecGenerator
from tests.conftest import assert_validation_result, create_test_instruction


class TestSpecGenerator:
    """Test cases for SpecGenerator class."""

    def test_init_with_dependencies(
        self, instruction_database, template_manager, context_detector
    ):
        """Test initialization with provided dependencies."""
        generator = SpecGenerator(
            instruction_db=instruction_database,
            template_manager=template_manager,
            context_detector=context_detector,
        )

        assert generator.instruction_db == instruction_database
        assert generator.template_manager == template_manager
        assert generator.context_detector == context_detector

    def test_init_with_defaults(self):
        """Test initialization with default dependencies."""
        generator = SpecGenerator()

        assert generator.instruction_db is not None
        assert generator.template_manager is not None
        assert generator.context_detector is not None

    def test_generate_spec_with_tags(self, spec_generator):
        """Test specification generation with tags."""
        config = SpecConfig(
            selected_tags=["testing", "quality"], output_format="markdown"
        )

        spec = spec_generator.generate_spec(config)

        assert isinstance(spec, GeneratedSpec)
        assert spec.content
        assert spec.format == "markdown"
        assert len(spec.instructions_used) > 0
        assert spec.generation_timestamp is not None

    def test_generate_spec_with_instructions(self, spec_generator):
        """Test specification generation with specific instructions."""
        # Load instructions first to get valid IDs
        spec_generator.instruction_db.load_instructions()
        instructions = spec_generator.instruction_db._instructions
        instruction_ids = list(instructions.keys())[:2]  # Take first 2

        config = SpecConfig(
            selected_instructions=instruction_ids, output_format="markdown"
        )

        spec = spec_generator.generate_spec(config)

        assert isinstance(spec, GeneratedSpec)
        assert spec.content
        # Should include selected instructions plus always-include instructions
        assert len(spec.instructions_used) >= len(instruction_ids)
        assert all(inst_id in spec.instructions_used for inst_id in instruction_ids)

    def test_generate_spec_with_template(self, spec_generator):
        """Test specification generation with template."""
        # Load templates first
        spec_generator.template_manager.load_templates()
        templates = spec_generator.template_manager._templates

        if templates:
            template_id = list(templates.keys())[0]

            config = SpecConfig(template_id=template_id, output_format="markdown")

            spec = spec_generator.generate_spec(config)

            assert isinstance(spec, GeneratedSpec)
            assert spec.content
            assert spec.template_used == template_id

    def test_generate_spec_with_project_context(
        self, spec_generator, sample_project_context
    ):
        """Test specification generation with project context."""
        config = SpecConfig(
            selected_tags=["frontend", "testing"],
            project_context=sample_project_context,
            output_format="markdown",
        )

        spec = spec_generator.generate_spec(config)

        assert isinstance(spec, GeneratedSpec)
        assert spec.content
        assert (
            spec.metadata["project_context"]
            == sample_project_context.project_type.value
        )

    def test_generate_spec_json_format(self, spec_generator):
        """Test specification generation in JSON format."""
        config = SpecConfig(selected_tags=["testing"], output_format="json")

        spec = spec_generator.generate_spec(config)

        assert spec.format == "json"
        assert spec.content.startswith("{")
        assert spec.content.endswith("}")

        # Should be valid JSON
        import json

        parsed = json.loads(spec.content)
        assert "metadata" in parsed
        assert "instructions" in parsed

    def test_generate_spec_yaml_format(self, spec_generator):
        """Test specification generation in YAML format."""
        config = SpecConfig(selected_tags=["testing"], output_format="yaml")

        try:
            spec = spec_generator.generate_spec(config)

            assert spec.format == "yaml"
            assert "metadata:" in spec.content
            assert "instructions:" in spec.content
        except ImportError:
            # PyYAML not available, should raise ImportError
            pytest.skip("PyYAML not available for YAML format testing")

    def test_generate_spec_invalid_config(self, spec_generator):
        """Test specification generation with invalid config."""
        config = SpecConfig()  # No tags, instructions, or template

        with pytest.raises(ValueError, match="Must specify"):
            spec_generator.generate_spec(config)

    def test_apply_template(
        self, spec_generator, sample_template, sample_project_context
    ):
        """Test applying template to create config."""
        config = spec_generator.apply_template(sample_template, sample_project_context)

        assert isinstance(config, SpecConfig)
        assert config.template_id == sample_template.id
        assert set(config.selected_tags) >= set(sample_template.default_tags)
        assert set(config.selected_instructions) >= set(
            sample_template.required_instructions
        )

    def test_validate_spec_valid(self, spec_generator):
        """Test validation of valid specification."""
        spec = GeneratedSpec(
            content="""# AgentSpec

## IMPLEMENTATION FRAMEWORK

### Pre-Development Checklist
- [ ] Load existing project context

## QUALITY GATES

1. **Zero Errors**: No linting errors
            """,
            format="markdown",
            instructions_used=["test_instruction"],
        )

        result = spec_generator.validate_spec(spec)

        assert_validation_result(result, should_be_valid=True, expected_warnings=1)

    def test_validate_spec_missing_sections(self, spec_generator):
        """Test validation of spec missing required sections."""
        spec = GeneratedSpec(
            content="This is a short spec without required sections.", format="markdown"
        )

        result = spec_generator.validate_spec(spec)

        assert_validation_result(result, should_be_valid=False, expected_errors=4)
        # Should have errors for missing sections and short content

    def test_validate_spec_invalid_json(self, spec_generator):
        """Test validation of invalid JSON spec."""
        spec = GeneratedSpec(content="{ invalid json }", format="json")

        result = spec_generator.validate_spec(spec)

        assert_validation_result(result, should_be_valid=False, expected_errors=5)
        assert any("Invalid JSON format" in error for error in result.errors)

    def test_export_spec_to_file(self, spec_generator, temp_dir):
        """Test exporting specification to file."""
        spec = GeneratedSpec(
            content="# Test Specification\n\nThis is a test spec.", format="markdown"
        )

        output_file = temp_dir / "test_spec.md"
        content = spec_generator.export_spec(spec, str(output_file))

        assert output_file.exists()
        assert output_file.read_text() == spec.content
        assert content == spec.content

    def test_export_spec_return_content(self, spec_generator):
        """Test exporting specification without file."""
        spec = GeneratedSpec(
            content="# Test Specification\n\nThis is a test spec.", format="markdown"
        )

        content = spec_generator.export_spec(spec)

        assert content == spec.content

    def test_get_instructions_for_config(self, spec_generator):
        """Test getting instructions based on config."""
        # Load instructions first
        spec_generator.instruction_db.load_instructions()

        config = SpecConfig(
            selected_tags=["testing"],
            selected_instructions=["general_quality"],
            excluded_instructions=[],
        )

        instructions = spec_generator._get_instructions_for_config(config)

        assert len(instructions) > 0
        instruction_ids = [inst.id for inst in instructions]
        assert "general_quality" in instruction_ids

    def test_filter_instructions_by_context(
        self, spec_generator, sample_project_context
    ):
        """Test filtering instructions by project context."""
        # Create instruction with condition
        instruction = create_test_instruction("conditional_inst")
        instruction.conditions = [
            Mock(type="project_type", value="web_frontend", operator="equals")
        ]

        # Mock the condition evaluation
        with patch.object(
            spec_generator, "_evaluate_instruction_condition", return_value=True
        ):
            filtered = spec_generator._filter_instructions_by_context(
                [instruction], sample_project_context
            )

        assert len(filtered) == 1
        assert filtered[0].id == "conditional_inst"

    def test_evaluate_instruction_condition_project_type(
        self, spec_generator, sample_project_context
    ):
        """Test evaluating project type condition."""
        condition = Mock(type="project_type", value="web_frontend", operator="equals")

        result = spec_generator._evaluate_instruction_condition(
            condition, sample_project_context
        )

        assert result is True

        # Test with different project type
        condition.value = "mobile_app"
        result = spec_generator._evaluate_instruction_condition(
            condition, sample_project_context
        )

        assert result is False

    def test_evaluate_instruction_condition_technology(
        self, spec_generator, sample_project_context
    ):
        """Test evaluating technology condition."""
        condition = Mock(type="technology", value="react", operator="equals")

        result = spec_generator._evaluate_instruction_condition(
            condition, sample_project_context
        )

        assert result is True

        # Test with non-existent technology
        condition.value = "vue"
        result = spec_generator._evaluate_instruction_condition(
            condition, sample_project_context
        )

        assert result is False

    def test_apply_parameter_substitution(self, spec_generator):
        """Test parameter substitution in instructions."""
        instruction = create_test_instruction(
            content="Use {project_name} for the project and {language} for development."
        )

        config = SpecConfig(
            template_parameters={"project_name": "MyApp", "language": "JavaScript"}
        )

        substituted = spec_generator._apply_parameter_substitution(
            [instruction], config
        )

        assert len(substituted) == 1
        assert "MyApp" in substituted[0].content
        assert "JavaScript" in substituted[0].content

    def test_generate_markdown_spec(self, spec_generator):
        """Test generating markdown specification."""
        instructions = [
            create_test_instruction("inst1", ["testing"], "First instruction"),
            create_test_instruction("inst2", ["quality"], "Second instruction"),
        ]

        config = SpecConfig(
            selected_tags=["testing", "quality"], output_format="markdown"
        )

        content = spec_generator._generate_markdown_spec(instructions, config)

        assert "# AgentSpec" in content
        assert "First instruction" in content
        assert "Second instruction" in content
        assert "## IMPLEMENTATION FRAMEWORK" in content
        assert "## QUALITY GATES" in content

    def test_generate_json_spec(self, spec_generator):
        """Test generating JSON specification."""
        instructions = [
            create_test_instruction("inst1", ["testing"], "First instruction")
        ]

        config = SpecConfig(selected_tags=["testing"], output_format="json")

        content = spec_generator._generate_json_spec(instructions, config)

        # Should be valid JSON
        import json

        parsed = json.loads(content)

        assert "metadata" in parsed
        assert "instructions" in parsed
        assert len(parsed["instructions"]) == 1
        assert parsed["instructions"][0]["id"] == "inst1"

    def test_get_implementation_framework(self, spec_generator):
        """Test getting implementation framework section."""
        framework = spec_generator._get_implementation_framework()

        assert isinstance(framework, list)
        assert any("IMPLEMENTATION FRAMEWORK" in line for line in framework)
        assert any("Pre-Development Checklist" in line for line in framework)
        assert any("QUALITY GATES" in line for line in framework)

    def test_get_metadata_section(self, spec_generator, sample_project_context):
        """Test getting metadata section."""
        instructions = [create_test_instruction("inst1")]

        config = SpecConfig(
            selected_tags=["testing"],
            template_id="test_template",
            project_context=sample_project_context,
            include_metadata=True,
        )

        metadata = spec_generator._get_metadata_section(instructions, config)

        assert isinstance(metadata, list)
        assert any("SPECIFICATION METADATA" in line for line in metadata)
        assert any("Generation Date" in line for line in metadata)
        assert any("Instructions Used" in line for line in metadata)

    def test_always_include_instructions(self, spec_generator):
        """Test that always-include instructions are automatically included."""
        # Mock the config manager to return our spec workflow instructions
        with patch.object(
            spec_generator.config_manager,
            "get",
            return_value=[
                "plan_and_reflect",
                "use_tools_dont_guess",
                "persist_until_complete",
                "context_management",
                "quality_standards",
                "incremental_development",
                "continuous_validation_loop",
                "avoid_vibe_coding",
                "ai_code_understanding_requirement",
                "ai_code_generation_rules",
                "ai_error_handling_patterns",
            ],
        ):
            # Create a config with no selected tags or instructions
            config = SpecConfig()

            # Get instructions - should include the always-include ones
            instructions = spec_generator._get_instructions_for_config(config)

            instruction_ids = [inst.id for inst in instructions]

            # Verify that our spec workflow instructions are included
            expected_instructions = [
                "plan_and_reflect",
                "use_tools_dont_guess",
                "persist_until_complete",
                "context_management",
                "incremental_development",
                "continuous_validation_loop",
                "avoid_vibe_coding",
            ]
            for inst_id in expected_instructions:
                assert (
                    inst_id in instruction_ids
                ), f"Missing always-include instruction: {inst_id}"

    def test_always_include_not_excluded(self, spec_generator):
        """Test that always-include instructions cannot be excluded."""
        # Mock the config manager to return our spec workflow instructions
        with patch.object(
            spec_generator.config_manager,
            "get",
            return_value=["plan_and_reflect", "use_tools_dont_guess"],
        ):
            # Create a config that tries to exclude an always-include instruction
            config = SpecConfig(
                excluded_instructions=["plan_and_reflect", "some_other_instruction"]
            )

            # Get instructions - always-include should still be present
            instructions = spec_generator._get_instructions_for_config(config)

            instruction_ids = [inst.id for inst in instructions]

            # Verify that the always-include instruction is still present despite being in excluded list
            assert "plan_and_reflect" in instruction_ids


class TestSpecConfig:
    """Test cases for SpecConfig dataclass."""

    def test_spec_config_creation(self):
        """Test creating SpecConfig with default values."""
        config = SpecConfig()

        assert config.selected_tags == []
        assert config.selected_instructions == []
        assert config.excluded_instructions == []
        assert config.template_id is None
        assert config.template_parameters == {}
        assert config.project_context is None
        assert config.output_format == "markdown"
        assert config.include_metadata is True
        assert config.language == "en"
        assert config.custom_sections == {}

    def test_spec_config_with_values(self, sample_project_context):
        """Test creating SpecConfig with specific values."""
        config = SpecConfig(
            selected_tags=["testing", "quality"],
            selected_instructions=["inst1", "inst2"],
            excluded_instructions=["inst3"],
            template_id="test_template",
            template_parameters={"param1": "value1"},
            project_context=sample_project_context,
            output_format="json",
            include_metadata=False,
            language="es",
            custom_sections={"Custom": "Content"},
        )

        assert config.selected_tags == ["testing", "quality"]
        assert config.selected_instructions == ["inst1", "inst2"]
        assert config.excluded_instructions == ["inst3"]
        assert config.template_id == "test_template"
        assert config.template_parameters == {"param1": "value1"}
        assert config.project_context == sample_project_context
        assert config.output_format == "json"
        assert config.include_metadata is False
        assert config.language == "es"
        assert config.custom_sections == {"Custom": "Content"}


class TestGeneratedSpec:
    """Test cases for GeneratedSpec dataclass."""

    def test_generated_spec_creation(self):
        """Test creating GeneratedSpec with default values."""
        spec = GeneratedSpec(content="# Test Spec", format="markdown")

        assert spec.content == "# Test Spec"
        assert spec.format == "markdown"
        assert spec.metadata == {}
        assert spec.instructions_used == []
        assert spec.template_used is None
        assert isinstance(spec.generation_timestamp, datetime)
        assert spec.validation_result is None

    def test_generated_spec_with_values(self):
        """Test creating GeneratedSpec with specific values."""
        timestamp = datetime.now()

        spec = GeneratedSpec(
            content="# Test Spec",
            format="json",
            metadata={"key": "value"},
            instructions_used=["inst1", "inst2"],
            template_used="test_template",
            generation_timestamp=timestamp,
        )

        assert spec.content == "# Test Spec"
        assert spec.format == "json"
        assert spec.metadata == {"key": "value"}
        assert spec.instructions_used == ["inst1", "inst2"]
        assert spec.template_used == "test_template"
        assert spec.generation_timestamp == timestamp
