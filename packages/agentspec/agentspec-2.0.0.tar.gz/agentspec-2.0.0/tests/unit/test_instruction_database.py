"""
Unit tests for InstructionDatabase class.
"""

import json
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest

from agentspec.core.instruction import (
    Condition,
    Conflict,
    Instruction,
    InstructionMetadata,
    Parameter,
    ValidationResult,
    VersionInfo,
)
from agentspec.core.instruction_database import InstructionDatabase
from tests.conftest import assert_validation_result, create_test_instruction


class TestInstructionDatabase:
    """Test cases for InstructionDatabase class."""

    def test_init_with_default_paths(self):
        """Test initialization with default paths."""
        db = InstructionDatabase()
        assert db.instructions_path is not None
        assert db.schema_path is not None
        assert db._instructions == {}
        assert not db._loaded

    def test_init_with_custom_paths(self, temp_dir):
        """Test initialization with custom paths."""
        instructions_path = temp_dir / "instructions"
        schema_path = temp_dir / "schema.json"

        db = InstructionDatabase(
            instructions_path=instructions_path, schema_path=schema_path
        )

        assert db.instructions_path == instructions_path
        assert db.schema_path == schema_path

    def test_load_instructions_success(self, instruction_database):
        """Test successful instruction loading."""
        instructions = instruction_database.load_instructions()

        assert len(instructions) > 0
        assert "general_quality" in instructions
        assert "unit_testing" in instructions

        # Verify instruction properties
        general_inst = instructions["general_quality"]
        assert general_inst.id == "general_quality"
        assert general_inst.version == "1.0.0"
        assert "general" in general_inst.tags
        assert general_inst.metadata.category == "general"

    def test_load_instructions_empty_directory(self, temp_dir):
        """Test loading from empty directory."""
        empty_dir = temp_dir / "empty"
        empty_dir.mkdir()

        db = InstructionDatabase(instructions_path=empty_dir)
        instructions = db.load_instructions()

        assert len(instructions) == 0

    def test_load_instructions_nonexistent_directory(self, temp_dir):
        """Test loading from nonexistent directory."""
        nonexistent_dir = temp_dir / "nonexistent"

        db = InstructionDatabase(instructions_path=nonexistent_dir)

        with pytest.raises(FileNotFoundError):
            db.load_instructions()

    def test_load_instructions_invalid_json(self, temp_dir):
        """Test loading with invalid JSON file."""
        instructions_dir = temp_dir / "instructions"
        instructions_dir.mkdir()

        # Create invalid JSON file
        with open(instructions_dir / "invalid.json", "w") as f:
            f.write("{ invalid json }")

        db = InstructionDatabase(instructions_path=instructions_dir)
        instructions = db.load_instructions()

        # Should continue loading despite invalid file
        assert len(instructions) == 0

    def test_get_by_tags_single_tag(self, instruction_database):
        """Test getting instructions by single tag."""
        instruction_database.load_instructions()

        testing_instructions = instruction_database.get_by_tags(["testing"])

        assert len(testing_instructions) == 3
        instruction_ids = [inst.id for inst in testing_instructions]
        assert "unit_testing" in instruction_ids
        assert "no_error_policy" in instruction_ids
        assert "continuous_validation_loop" in instruction_ids

    def test_get_by_tags_multiple_tags(self, instruction_database):
        """Test getting instructions by multiple tags."""
        instruction_database.load_instructions()

        instructions = instruction_database.get_by_tags(["general", "testing"])

        # Should return instructions that match any of the tags
        assert len(instructions) == 4
        instruction_ids = [inst.id for inst in instructions]
        assert "general_quality" in instruction_ids
        assert "unit_testing" in instruction_ids
        assert "no_error_policy" in instruction_ids
        assert "continuous_validation_loop" in instruction_ids

    def test_get_by_tags_no_matches(self, instruction_database):
        """Test getting instructions with no matching tags."""
        instruction_database.load_instructions()

        instructions = instruction_database.get_by_tags(["nonexistent"])

        assert len(instructions) == 0

    def test_get_by_tags_empty_list(self, instruction_database):
        """Test getting instructions with empty tag list."""
        instruction_database.load_instructions()

        instructions = instruction_database.get_by_tags([])

        # Should return all instructions
        assert len(instructions) == 13

    def test_validate_instruction_valid(self, sample_instruction):
        """Test validation of valid instruction."""
        db = InstructionDatabase()
        result = db.validate_instruction(sample_instruction)

        assert_validation_result(result, should_be_valid=True, expected_warnings=2)

    def test_validate_instruction_missing_id(self):
        """Test validation of instruction with missing ID."""
        instruction = create_test_instruction(instruction_id="")

        db = InstructionDatabase()
        result = db.validate_instruction(instruction)

        assert_validation_result(
            result, should_be_valid=False, expected_errors=2, expected_warnings=2
        )
        assert any("ID cannot be empty" in error for error in result.errors)

    def test_validate_instruction_short_content(self):
        """Test validation of instruction with short content."""
        instruction = create_test_instruction(content="short")

        db = InstructionDatabase()
        result = db.validate_instruction(instruction)

        assert_validation_result(
            result, should_be_valid=False, expected_errors=2, expected_warnings=2
        )
        assert any("at least 10 characters" in error for error in result.errors)

    def test_validate_instruction_no_tags(self):
        """Test validation of instruction with no tags."""
        instruction = create_test_instruction(tags=[])

        db = InstructionDatabase()
        result = db.validate_instruction(instruction)

        assert_validation_result(
            result, should_be_valid=False, expected_errors=2, expected_warnings=2
        )
        assert any("at least one tag" in error for error in result.errors)

    def test_validate_instruction_invalid_version(self):
        """Test validation of instruction with invalid version."""
        instruction = create_test_instruction()
        instruction.version = "invalid"

        db = InstructionDatabase()
        result = db.validate_instruction(instruction)

        assert_validation_result(
            result, should_be_valid=False, expected_errors=2, expected_warnings=2
        )
        assert any("semantic versioning format" in error for error in result.errors)

    def test_get_instruction_metadata(self, instruction_database):
        """Test getting instruction metadata."""
        instruction_database.load_instructions()

        metadata = instruction_database.get_instruction_metadata("general_quality")

        assert metadata is not None
        assert metadata.category == "general"
        assert metadata.priority == 5

    def test_get_instruction_metadata_not_found(self, instruction_database):
        """Test getting metadata for nonexistent instruction."""
        instruction_database.load_instructions()

        metadata = instruction_database.get_instruction_metadata("nonexistent")

        assert metadata is None

    def test_get_instruction(self, instruction_database):
        """Test getting specific instruction."""
        instruction_database.load_instructions()

        instruction = instruction_database.get_instruction("unit_testing")

        assert instruction is not None
        assert instruction.id == "unit_testing"
        assert "testing" in instruction.tags

    def test_get_instruction_not_found(self, instruction_database):
        """Test getting nonexistent instruction."""
        instruction_database.load_instructions()

        instruction = instruction_database.get_instruction("nonexistent")

        assert instruction is None

    def test_get_all_tags(self, instruction_database):
        """Test getting all unique tags."""
        instruction_database.load_instructions()

        tags = instruction_database.get_all_tags()

        assert isinstance(tags, set)
        assert "general" in tags
        assert "testing" in tags
        assert "quality" in tags
        assert "unit" in tags

    def test_get_instructions_by_category(self, instruction_database):
        """Test getting instructions by category."""
        instruction_database.load_instructions()

        testing_instructions = instruction_database.get_instructions_by_category(
            "testing"
        )

        assert len(testing_instructions) == 1
        assert testing_instructions[0].id == "unit_testing"

    def test_reload(self, instruction_database):
        """Test reloading instructions."""
        # Load initially
        instructions1 = instruction_database.load_instructions()
        assert len(instructions1) == 13

        # Reload
        instruction_database.reload()
        instructions2 = instruction_database.load_instructions()

        assert len(instructions2) == 13
        assert instruction_database._loaded

    def test_detect_conflicts_no_conflicts(self, instruction_database):
        """Test conflict detection with no conflicts."""
        instruction_database.load_instructions()
        instructions = list(instruction_database._instructions.values())

        conflicts = instruction_database.detect_conflicts(instructions)

        assert len(conflicts) == 0

    def test_detect_conflicts_duplicate_tags(self):
        """Test conflict detection with duplicate tag sets."""
        inst1 = create_test_instruction("inst1", ["tag1", "tag2"])
        inst2 = create_test_instruction("inst2", ["tag1", "tag2"])

        db = InstructionDatabase()
        conflicts = db.detect_conflicts([inst1, inst2])

        assert len(conflicts) > 0
        assert any(c.conflict_type == "duplicate_tags" for c in conflicts)

    def test_resolve_dependencies_no_dependencies(self):
        """Test dependency resolution with no dependencies."""
        inst1 = create_test_instruction("inst1")
        inst2 = create_test_instruction("inst2")

        db = InstructionDatabase()
        db._instructions = {"inst1": inst1, "inst2": inst2}
        db._loaded = True

        ordered_ids = db.resolve_dependencies(["inst1", "inst2"])

        assert len(ordered_ids) == 2
        assert "inst1" in ordered_ids
        assert "inst2" in ordered_ids

    def test_resolve_dependencies_with_dependencies(self):
        """Test dependency resolution with dependencies."""
        inst1 = create_test_instruction("inst1")
        inst2 = create_test_instruction("inst2")
        inst2.dependencies = ["inst1"]  # inst2 depends on inst1

        db = InstructionDatabase()
        db._instructions = {"inst1": inst1, "inst2": inst2}
        db._loaded = True

        ordered_ids = db.resolve_dependencies(["inst1", "inst2"])

        assert len(ordered_ids) == 2
        assert ordered_ids.index("inst1") < ordered_ids.index("inst2")


class TestVersionInfo:
    """Test cases for VersionInfo class."""

    def test_from_string_valid(self):
        """Test parsing valid version string."""
        version = VersionInfo.from_string("1.2.3")

        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3

    def test_from_string_invalid_format(self):
        """Test parsing invalid version string."""
        with pytest.raises(ValueError):
            VersionInfo.from_string("1.2")

        with pytest.raises(ValueError):
            VersionInfo.from_string("1.2.3.4")

        with pytest.raises(ValueError):
            VersionInfo.from_string("a.b.c")

    def test_string_representation(self):
        """Test string representation of version."""
        version = VersionInfo(1, 2, 3)

        assert str(version) == "1.2.3"

    def test_comparison_operators(self):
        """Test version comparison operators."""
        v1 = VersionInfo(1, 0, 0)
        v2 = VersionInfo(1, 1, 0)
        v3 = VersionInfo(2, 0, 0)

        assert v1 < v2
        assert v2 < v3
        assert v1 <= v2
        assert v2 <= v3
        assert v3 > v2
        assert v2 > v1
        assert v3 >= v2
        assert v2 >= v1
        assert v1 == VersionInfo(1, 0, 0)


class TestCondition:
    """Test cases for Condition dataclass."""

    def test_condition_creation(self):
        """Test creating a condition."""
        condition = Condition(
            type="project_type", value="web_frontend", operator="equals"
        )

        assert condition.type == "project_type"
        assert condition.value == "web_frontend"
        assert condition.operator == "equals"


class TestParameter:
    """Test cases for Parameter dataclass."""

    def test_parameter_creation(self):
        """Test creating a parameter."""
        parameter = Parameter(
            name="test_param",
            type="string",
            default="default_value",
            description="Test parameter",
            required=True,
        )

        assert parameter.name == "test_param"
        assert parameter.type == "string"
        assert parameter.default == "default_value"
        assert parameter.description == "Test parameter"
        assert parameter.required is True


class TestValidationResult:
    """Test cases for ValidationResult dataclass."""

    def test_validation_result_valid(self):
        """Test creating valid validation result."""
        result = ValidationResult(
            is_valid=True, errors=[], warnings=["Warning message"]
        )

        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 1

    def test_validation_result_invalid(self):
        """Test creating invalid validation result."""
        result = ValidationResult(is_valid=False, errors=["Error message"], warnings=[])

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert len(result.warnings) == 0


class TestConflict:
    """Test cases for Conflict dataclass."""

    def test_conflict_creation(self):
        """Test creating a conflict."""
        conflict = Conflict(
            instruction1_id="inst1",
            instruction2_id="inst2",
            conflict_type="duplicate_tags",
            description="Instructions have identical tags",
            severity="medium",
        )

        assert conflict.instruction1_id == "inst1"
        assert conflict.instruction2_id == "inst2"
        assert conflict.conflict_type == "duplicate_tags"
        assert conflict.description == "Instructions have identical tags"
        assert conflict.severity == "medium"
