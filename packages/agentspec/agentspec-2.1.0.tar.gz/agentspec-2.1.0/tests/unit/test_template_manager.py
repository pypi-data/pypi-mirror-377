"""
Unit tests for TemplateManager class.
"""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from agentspec.core.template_manager import (
    Template,
    TemplateCondition,
    TemplateManager,
    TemplateMetadata,
    TemplateParameter,
    TemplateRecommendation,
    ValidationResult,
)
from tests.conftest import assert_validation_result, create_test_template


class TestTemplateManager:
    """Test cases for TemplateManager class."""

    def test_init_with_default_paths(self):
        """Test initialization with default paths."""
        manager = TemplateManager()
        assert manager.templates_path is not None
        assert manager.schema_path is not None
        assert manager._templates == {}
        assert not manager._loaded

    def test_init_with_custom_paths(self, temp_dir):
        """Test initialization with custom paths."""
        templates_path = temp_dir / "templates"
        schema_path = temp_dir / "schema.json"

        manager = TemplateManager(
            templates_path=templates_path, schema_path=schema_path
        )

        assert manager.templates_path == templates_path
        assert manager.schema_path == schema_path

    def test_load_templates_success(self, template_manager):
        """Test successful template loading."""
        templates = template_manager.load_templates()

        assert len(templates) > 0
        assert "react_app" in templates

        # Verify template properties
        react_template = templates["react_app"]
        assert react_template.id == "react_app"
        assert react_template.name == "React Application"
        assert react_template.project_type == "web_frontend"
        assert "react" in react_template.technology_stack

    def test_load_templates_empty_directory(self, temp_dir):
        """Test loading from empty directory."""
        empty_dir = temp_dir / "empty"
        empty_dir.mkdir()

        manager = TemplateManager(templates_path=empty_dir)
        templates = manager.load_templates()

        assert len(templates) == 0

    def test_load_templates_nonexistent_directory(self, temp_dir):
        """Test loading from nonexistent directory."""
        nonexistent_dir = temp_dir / "nonexistent"

        manager = TemplateManager(templates_path=nonexistent_dir)
        templates = manager.load_templates()

        # Should create directory and return empty dict
        assert len(templates) == 0
        assert nonexistent_dir.exists()

    def test_get_template_exists(self, template_manager):
        """Test getting existing template."""
        template_manager.load_templates()

        template = template_manager.get_template("react_app")

        assert template is not None
        assert template.id == "react_app"
        assert template.name == "React Application"

    def test_get_template_not_exists(self, template_manager):
        """Test getting nonexistent template."""
        template_manager.load_templates()

        template = template_manager.get_template("nonexistent")

        assert template is None

    def test_validate_template_valid(self, sample_template):
        """Test validation of valid template."""
        manager = TemplateManager()
        result = manager.validate_template(sample_template)

        assert_validation_result(result, should_be_valid=True)

    def test_validate_template_missing_id(self):
        """Test validation of template with missing ID."""
        template = create_test_template(template_id="")

        manager = TemplateManager()
        result = manager.validate_template(template)

        assert_validation_result(result, should_be_valid=False, expected_errors=2)
        assert any("ID cannot be empty" in error for error in result.errors)

    def test_validate_template_missing_name(self):
        """Test validation of template with missing name."""
        template = create_test_template()
        template.name = ""

        manager = TemplateManager()
        result = manager.validate_template(template)

        assert_validation_result(result, should_be_valid=False, expected_errors=2)
        assert any("name cannot be empty" in error for error in result.errors)

    def test_validate_template_short_description(self):
        """Test validation of template with short description."""
        template = create_test_template()
        template.description = "short"

        manager = TemplateManager()
        result = manager.validate_template(template)

        assert_validation_result(result, should_be_valid=False, expected_errors=2)
        assert any("at least 10 characters" in error for error in result.errors)

    def test_validate_template_no_default_tags(self):
        """Test validation of template with no default tags."""
        template = create_test_template()
        template.default_tags = []

        manager = TemplateManager()
        result = manager.validate_template(template)

        assert_validation_result(result, should_be_valid=False, expected_errors=1)
        assert "at least one default tag" in result.errors[0]

    def test_validate_template_invalid_version(self):
        """Test validation of template with invalid version."""
        template = create_test_template()
        template.version = "invalid"

        manager = TemplateManager()
        result = manager.validate_template(template)

        assert_validation_result(result, should_be_valid=False, expected_errors=2)
        # Check for version-related error message
        assert any("version" in error.lower() for error in result.errors)

    def test_get_recommended_templates_project_type_match(self, template_manager):
        """Test template recommendation with project type match."""
        template_manager.load_templates()

        project_context = {
            "project_type": "web_frontend",
            "technology_stack": ["react", "javascript"],
            "files": ["package.json"],
        }

        recommendations = template_manager.get_recommended_templates(project_context)

        assert len(recommendations) > 0
        assert recommendations[0].template.id == "react_app"
        assert (
            recommendations[0].confidence_score > 0.4
        )  # Should have decent confidence

    def test_get_recommended_templates_no_match(self, template_manager):
        """Test template recommendation with no matches."""
        template_manager.load_templates()

        project_context = {
            "project_type": "unknown",
            "technology_stack": [],
            "files": [],
        }

        recommendations = template_manager.get_recommended_templates(project_context)

        # May have low-confidence recommendations or none
        assert isinstance(recommendations, list)

    def test_get_templates_by_project_type(self, template_manager):
        """Test getting templates by project type."""
        template_manager.load_templates()

        templates = template_manager.get_templates_by_project_type("web_frontend")

        assert len(templates) == 1
        assert templates[0].id == "react_app"

    def test_get_templates_by_technology(self, template_manager):
        """Test getting templates by technology."""
        template_manager.load_templates()

        templates = template_manager.get_templates_by_technology("react")

        assert len(templates) == 1
        assert templates[0].id == "react_app"

    def test_get_all_project_types(self, template_manager):
        """Test getting all project types."""
        template_manager.load_templates()

        project_types = template_manager.get_all_project_types()

        assert isinstance(project_types, set)
        assert "web_frontend" in project_types

    def test_get_all_technologies(self, template_manager):
        """Test getting all technologies."""
        template_manager.load_templates()

        technologies = template_manager.get_all_technologies()

        assert isinstance(technologies, set)
        assert "react" in technologies
        assert "javascript" in technologies

    def test_reload(self, template_manager):
        """Test reloading templates."""
        # Load initially
        templates1 = template_manager.load_templates()
        assert len(templates1) == 1

        # Reload
        template_manager.reload()
        templates2 = template_manager.load_templates()

        assert len(templates2) == 1
        assert template_manager._loaded

    def test_create_template(self, temp_dir):
        """Test creating a new template."""
        templates_dir = temp_dir / "templates"
        templates_dir.mkdir()

        manager = TemplateManager(templates_path=templates_dir)

        new_template = create_test_template("new_template", "cli-tool")
        new_template.name = "New CLI Template"
        new_template.description = "A new template for CLI tools"

        template_id = manager.create_template(new_template)

        assert template_id == "new_template"
        assert (templates_dir / "new_template.json").exists()

        # Verify template was added to loaded templates
        assert "new_template" in manager._templates

    def test_create_template_duplicate_id(self, template_manager):
        """Test creating template with duplicate ID."""
        template_manager.load_templates()

        duplicate_template = create_test_template("react_app")
        duplicate_template.name = "Duplicate Template"
        duplicate_template.description = "This should fail due to duplicate ID"

        with pytest.raises(ValueError, match="already exists"):
            template_manager.create_template(duplicate_template)

    def test_create_template_invalid(self, temp_dir):
        """Test creating invalid template."""
        templates_dir = temp_dir / "templates"
        templates_dir.mkdir()

        manager = TemplateManager(templates_path=templates_dir)

        invalid_template = create_test_template("")  # Empty ID

        with pytest.raises(ValueError, match="Invalid template"):
            manager.create_template(invalid_template)


class TestTemplateParameter:
    """Test cases for TemplateParameter dataclass."""

    def test_parameter_creation(self):
        """Test creating a template parameter."""
        param = TemplateParameter(
            name="project_name",
            type="string",
            default="my-project",
            description="Name of the project",
            required=True,
            options=["option1", "option2"],
        )

        assert param.name == "project_name"
        assert param.type == "string"
        assert param.default == "my-project"
        assert param.description == "Name of the project"
        assert param.required is True
        assert param.options == ["option1", "option2"]


class TestTemplateCondition:
    """Test cases for TemplateCondition dataclass."""

    def test_condition_creation(self):
        """Test creating a template condition."""
        condition = TemplateCondition(
            type="file_exists", value="package.json", operator="exists", weight=0.8
        )

        assert condition.type == "file_exists"
        assert condition.value == "package.json"
        assert condition.operator == "exists"
        assert condition.weight == 0.8


class TestTemplateRecommendation:
    """Test cases for TemplateRecommendation dataclass."""

    def test_recommendation_creation(self, sample_template):
        """Test creating a template recommendation."""
        recommendation = TemplateRecommendation(
            template=sample_template,
            confidence_score=0.85,
            matching_conditions=["file_exists:package.json"],
            reasons=["React project detected", "Package.json found"],
        )

        assert recommendation.template == sample_template
        assert recommendation.confidence_score == 0.85
        assert len(recommendation.matching_conditions) == 1
        assert len(recommendation.reasons) == 2


class TestTemplateMetadata:
    """Test cases for TemplateMetadata dataclass."""

    def test_metadata_creation(self):
        """Test creating template metadata."""
        metadata = TemplateMetadata(
            category="web",
            complexity="intermediate",
            author="test_author",
            tags=["react", "frontend"],
        )

        assert metadata.category == "web"
        assert metadata.complexity == "intermediate"
        assert metadata.author == "test_author"
        assert metadata.tags == ["react", "frontend"]


class TestTemplateInheritance:
    """Test cases for template inheritance functionality."""

    def test_template_inheritance_merge_mode(self, temp_dir):
        """Test template inheritance with merge mode."""
        templates_dir = temp_dir / "templates"
        templates_dir.mkdir()

        # Create parent template
        parent_template = {
            "id": "base_web",
            "name": "Base Web Template",
            "description": "Base template for web applications",
            "version": "1.0.0",
            "project_type": "web_frontend",
            "technology_stack": ["javascript"],
            "default_tags": ["web", "frontend"],
            "required_instructions": ["base_instruction"],
            "metadata": {"category": "web"},
        }

        # Create child template with inheritance
        child_template = {
            "id": "react_child",
            "name": "React Child Template",
            "description": "Child template for React applications",
            "version": "1.0.0",
            "project_type": "web_frontend",
            "technology_stack": ["react"],
            "default_tags": ["react"],
            "required_instructions": ["react_instruction"],
            "inheritance": {"parent": "base_web", "override_mode": "merge"},
            "metadata": {"category": "web"},
        }

        # Save templates
        with open(templates_dir / "base-web.json", "w") as f:
            json.dump(parent_template, f)

        with open(templates_dir / "react-child.json", "w") as f:
            json.dump(child_template, f)

        # Load templates and check inheritance
        manager = TemplateManager(templates_path=templates_dir)
        templates = manager.load_templates()

        child = templates["react_child"]

        # Should have merged tags and instructions
        assert "web" in child.default_tags
        assert "frontend" in child.default_tags
        assert "react" in child.default_tags
        assert "base_instruction" in child.required_instructions
        assert "react_instruction" in child.required_instructions
        assert "javascript" in child.technology_stack
        assert "react" in child.technology_stack

    def test_calculate_template_score(self, template_manager):
        """Test template scoring calculation."""
        template_manager.load_templates()
        template = template_manager.get_template("react_app")

        project_context = {
            "project_type": "web_frontend",
            "technology_stack": ["react", "javascript"],
            "files": ["package.json"],
            "dependencies": ["react", "react-dom"],
        }

        (
            score,
            matching_conditions,
            reasons,
        ) = template_manager._calculate_template_score(template, project_context)

        assert score > 0.4  # Should have decent score
        assert len(reasons) > 0
        assert isinstance(matching_conditions, list)

    def test_evaluate_condition_file_exists(self, template_manager):
        """Test condition evaluation for file existence."""
        condition = TemplateCondition(
            type="file_exists", value="package.json", operator="exists"
        )

        project_context = {"files": ["package.json", "src/App.js"]}

        result = template_manager._evaluate_condition(condition, project_context)
        assert result is True

        # Test with non-existent file
        condition.value = "nonexistent.json"
        result = template_manager._evaluate_condition(condition, project_context)
        assert result is False

    def test_evaluate_condition_dependency_exists(self, template_manager):
        """Test condition evaluation for dependency existence."""
        condition = TemplateCondition(
            type="dependency_exists", value="react", operator="exists"
        )

        project_context = {"dependencies": ["react", "react-dom", "jest"]}

        result = template_manager._evaluate_condition(condition, project_context)
        assert result is True

        # Test with non-existent dependency
        condition.value = "nonexistent"
        result = template_manager._evaluate_condition(condition, project_context)
        assert result is False

    def test_evaluate_condition_technology_detected(self, template_manager):
        """Test condition evaluation for technology detection."""
        condition = TemplateCondition(
            type="technology_detected", value="react", operator="equals"
        )

        project_context = {
            "technology_stack": ["React", "JavaScript"]  # Case insensitive
        }

        result = template_manager._evaluate_condition(condition, project_context)
        assert result is True

        # Test with non-detected technology
        condition.value = "vue"
        result = template_manager._evaluate_condition(condition, project_context)
        assert result is False
