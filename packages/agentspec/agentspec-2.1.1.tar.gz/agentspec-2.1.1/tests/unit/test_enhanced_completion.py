"""
Tests for enhanced completion functionality with descriptions and grouping.

This module tests the new enhanced completion features that provide
contextual help, descriptions, and better organization of completion results.
"""

from unittest.mock import Mock, patch

import pytest

from agentspec.cli.completers import (
    category_completer,
    command_completer,
    format_completer,
    output_format_completer,
)
from agentspec.cli.completion import (
    CompletionEngine,
    CompletionItem,
    CompletionResult,
    get_completion_engine,
)


class TestEnhancedCompletionStructures:
    """Test the enhanced completion data structures"""

    def test_completion_item_creation(self):
        """Test CompletionItem creation and properties"""
        item = CompletionItem(
            value="test-tag",
            description="Test tag for testing purposes",
            category="Testing",
            priority=8,
        )

        assert item.value == "test-tag"
        assert item.description == "Test tag for testing purposes"
        assert item.category == "Testing"
        assert item.priority == 8
        assert str(item) == "test-tag"

    def test_completion_item_defaults(self):
        """Test CompletionItem with default values"""
        item = CompletionItem(value="simple-tag")

        assert item.value == "simple-tag"
        assert item.description is None
        assert item.category is None
        assert item.priority == 0

    def test_completion_result_creation(self):
        """Test CompletionResult creation and methods"""
        items = [
            CompletionItem("tag1", "First tag", "Testing", 10),
            CompletionItem("tag2", "Second tag", "Frontend", 5),
            CompletionItem("tag3", "Third tag", "Testing", 8),
        ]

        result = CompletionResult(items=items)

        assert len(result.items) == 3
        assert result.to_string_list() == ["tag1", "tag2", "tag3"]

    def test_completion_result_sorting(self):
        """Test CompletionResult sorting by priority and name"""
        items = [
            CompletionItem("zebra", "Z tag", "General", 5),
            CompletionItem("alpha", "A tag", "General", 10),
            CompletionItem("beta", "B tag", "General", 10),
        ]

        result = CompletionResult(items=items)
        sorted_items = result.get_sorted_items()

        # Should be sorted by priority (desc) then name (asc)
        assert sorted_items[0].value == "alpha"  # priority 10, name alpha
        assert sorted_items[1].value == "beta"  # priority 10, name beta
        assert sorted_items[2].value == "zebra"  # priority 5, name zebra


class TestEnhancedCompletionEngine:
    """Test enhanced completion engine functionality"""

    def test_enhanced_tag_completions(self):
        """Test enhanced tag completions with descriptions"""
        engine = CompletionEngine()
        mock_db = Mock()
        mock_db.get_all_tags.return_value = {"testing", "frontend", "test-driven"}
        mock_db.load_instructions.return_value = {}

        engine.set_services(instruction_db=mock_db)

        result = engine.get_tag_completions_enhanced("test")

        assert isinstance(result, CompletionResult)
        assert len(result.items) == 2  # testing, test-driven

        # Check that items have descriptions and categories
        for item in result.items:
            assert isinstance(item, CompletionItem)
            assert item.description is not None
            assert item.category is not None
            assert item.priority >= 0

    def test_enhanced_template_completions(self):
        """Test enhanced template completions with descriptions"""
        engine = CompletionEngine()
        mock_manager = Mock()

        # Mock template objects
        mock_template1 = Mock()
        mock_template1.description = "React web application template"
        mock_template1.project_type = "web-app"

        mock_template2 = Mock()
        mock_template2.description = "React component template"
        mock_template2.project_type = "component"

        mock_manager.load_templates.return_value = None
        mock_manager._templates = {
            "react-app": mock_template1,
            "react-component": mock_template2,
        }

        engine.set_services(template_manager=mock_manager)

        result = engine.get_template_completions_enhanced("react")

        assert isinstance(result, CompletionResult)
        assert len(result.items) == 2

        # Check that items have descriptions from templates
        for item in result.items:
            assert isinstance(item, CompletionItem)
            assert item.description is not None
            assert "React" in item.description
            assert item.category is not None

    def test_enhanced_category_completions(self):
        """Test enhanced category completions with descriptions"""
        engine = CompletionEngine()

        result = engine.get_category_completions_enhanced("test")

        assert isinstance(result, CompletionResult)
        assert len(result.items) == 1  # Only "Testing" matches "test"

        item = result.items[0]
        assert item.value == "Testing"
        assert "testing" in item.description.lower()
        assert item.category == "Categories"
        assert item.priority > 0

    def test_enhanced_format_completions(self):
        """Test enhanced format completions with descriptions"""
        engine = CompletionEngine()

        result = engine.get_format_completions_enhanced("j")

        assert isinstance(result, CompletionResult)
        assert len(result.items) == 1  # Only "json" matches "j"

        item = result.items[0]
        assert item.value == "json"
        assert "JSON" in item.description
        assert item.category == "Output Formats"
        assert item.priority > 0

    def test_backward_compatibility(self):
        """Test that legacy methods still work"""
        engine = CompletionEngine()
        mock_db = Mock()
        mock_db.get_all_tags.return_value = {"testing", "frontend"}
        mock_db.load_instructions.return_value = {}

        engine.set_services(instruction_db=mock_db)

        # Legacy method should return list of strings
        result = engine.get_tag_completions("test")

        assert isinstance(result, list)
        assert all(isinstance(item, str) for item in result)
        assert "testing" in result


class TestEnhancedCompleters:
    """Test enhanced static completers with descriptions"""

    def test_enhanced_command_completer(self):
        """Test command completer with prioritization"""
        result = command_completer("gen", None)

        assert isinstance(result, list)
        assert "generate" in result

        # Test that generate appears before other commands due to priority
        all_commands = command_completer("", None)
        assert "generate" in all_commands
        assert "interactive" in all_commands

    def test_enhanced_format_completer(self):
        """Test format completer with prioritization"""
        result = format_completer("", None)

        assert isinstance(result, list)
        assert "markdown" in result
        assert "json" in result
        assert "yaml" in result

        # Test prefix filtering
        json_result = format_completer("j", None)
        assert json_result == ["json"]

    def test_enhanced_category_completer(self):
        """Test category completer with case-insensitive matching"""
        result = category_completer("test", None)

        assert isinstance(result, list)
        assert "Testing" in result

        # Test case-insensitive matching
        result_lower = category_completer("testing", None)
        assert "Testing" in result_lower

    def test_enhanced_output_format_completer(self):
        """Test output format completer with descriptions"""
        result = output_format_completer("", None)

        assert isinstance(result, list)
        assert "text" in result
        assert "json" in result

        # Test prefix filtering
        text_result = output_format_completer("t", None)
        assert text_result == ["text"]


class TestCompletionGrouping:
    """Test completion result grouping functionality"""

    def test_group_items_by_category(self):
        """Test grouping completion items by category"""
        engine = CompletionEngine()

        items = [
            CompletionItem("react", "React framework", "Frontend", 8),
            CompletionItem("testing", "Testing guidelines", "Testing", 9),
            CompletionItem("vue", "Vue framework", "Frontend", 7),
            CompletionItem("python", "Python language", "Languages", 6),
        ]

        grouped = engine._group_items_by_category(items)

        assert "Frontend" in grouped
        assert "Testing" in grouped
        assert "Languages" in grouped

        assert len(grouped["Frontend"]) == 2
        assert len(grouped["Testing"]) == 1
        assert len(grouped["Languages"]) == 1

        # Check that items within categories are sorted by priority
        frontend_items = grouped["Frontend"]
        assert frontend_items[0].value == "react"  # Higher priority
        assert frontend_items[1].value == "vue"  # Lower priority

    def test_completion_result_with_grouping(self):
        """Test CompletionResult with grouped items"""
        items = [
            CompletionItem("tag1", "First tag", "Testing", 10),
            CompletionItem("tag2", "Second tag", "Frontend", 5),
        ]

        result = CompletionResult(items=items)
        result.grouped_items = {"Testing": [items[0]], "Frontend": [items[1]]}

        assert result.grouped_items is not None
        assert "Testing" in result.grouped_items
        assert "Frontend" in result.grouped_items
        assert len(result.grouped_items["Testing"]) == 1
        assert len(result.grouped_items["Frontend"]) == 1


class TestCompletionMetadata:
    """Test completion metadata generation"""

    def test_tag_metadata_generation(self):
        """Test tag metadata generation with instruction analysis"""
        engine = CompletionEngine()

        # Mock instruction database with sample instructions
        mock_instruction = Mock()
        mock_instruction.tags = ["testing", "unit-testing"]
        mock_instruction.metadata = Mock()
        mock_instruction.metadata.category = "Testing"

        mock_db = Mock()
        mock_db.load_instructions.return_value = {"inst1": mock_instruction}

        tags = ["testing", "unknown-tag"]
        metadata = engine._get_tag_metadata(mock_db, tags)

        assert "testing" in metadata
        assert "unknown-tag" in metadata

        # Testing tag should have proper metadata
        testing_meta = metadata["testing"]
        assert testing_meta["category"] == "Testing"
        assert testing_meta["priority"] > 0
        assert "testing" in testing_meta["description"].lower()

    def test_template_priority_calculation(self):
        """Test template priority calculation"""
        engine = CompletionEngine()

        # Mock template with beginner complexity
        mock_template = Mock()
        mock_template.metadata = Mock()
        mock_template.metadata.complexity = "beginner"
        mock_template.project_type = "web-app"
        mock_template.technology_stack = ["react", "typescript"]

        priority = engine._get_template_priority(mock_template)

        assert (
            priority > 5
        )  # Should be higher than default due to beginner + popular tech

    def test_template_priority_fallback(self):
        """Test template priority calculation with missing attributes"""
        engine = CompletionEngine()

        # Mock template with minimal attributes
        mock_template = Mock()
        mock_template.project_type = "unknown"

        # Remove metadata attribute to test fallback
        if hasattr(mock_template, "metadata"):
            delattr(mock_template, "metadata")

        priority = engine._get_template_priority(mock_template)

        assert priority >= 5  # Should have at least default priority
        assert priority <= 10  # Should not exceed maximum


class TestCompletionErrorHandling:
    """Test error handling in enhanced completion features"""

    def test_enhanced_completion_with_service_failure(self):
        """Test enhanced completions when services fail"""
        engine = CompletionEngine()

        # Don't set any services - should gracefully degrade
        result = engine.get_tag_completions_enhanced("nonexistent")

        assert isinstance(result, CompletionResult)
        # Should return empty result for non-matching prefix, not crash
        assert len(result.items) == 0

        # But should still provide predefined completions for matching prefixes
        test_result = engine.get_tag_completions_enhanced("test")
        assert isinstance(test_result, CompletionResult)
        # Should find "testing" from predefined categories even without services

    def test_enhanced_completion_with_invalid_data(self):
        """Test enhanced completions with invalid data types"""
        engine = CompletionEngine()
        mock_db = Mock()
        mock_db.get_all_tags.return_value = {"valid_tag", 123, None}  # Mixed types
        mock_db.load_instructions.return_value = {}

        engine.set_services(instruction_db=mock_db)

        result = engine.get_tag_completions_enhanced("valid")

        assert isinstance(result, CompletionResult)
        # Should filter out invalid types and only return valid string tags
        assert len(result.items) == 1
        assert result.items[0].value == "valid_tag"

    def test_metadata_generation_error_handling(self):
        """Test metadata generation with error conditions"""
        engine = CompletionEngine()

        # Test with tags that might cause string processing errors
        problematic_tags = [None, 123, "", "normal-tag"]

        # This should not crash even with problematic input
        try:
            metadata = engine._get_tag_metadata(Mock(), problematic_tags)
            # Should only have metadata for valid string tags
            assert "normal-tag" in metadata
            assert None not in metadata
            assert 123 not in metadata
            assert "" not in metadata or metadata[""] is not None
        except Exception as e:
            pytest.fail(f"Metadata generation should handle errors gracefully: {e}")
