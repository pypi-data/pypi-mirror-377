"""
Integration tests for template loading and inheritance.
"""

import json
from pathlib import Path

import pytest

from agentspec.core.instruction_database import InstructionDatabase
from agentspec.core.spec_generator import SpecConfig, SpecGenerator
from agentspec.core.template_manager import TemplateManager


class TestTemplateLoadingIntegration:
    """Integration tests for template loading and processing."""

    def test_template_inheritance_chain(self, temp_dir):
        """Test complex template inheritance chains."""
        templates_dir = temp_dir / "templates"
        templates_dir.mkdir()

        # Create base template
        base_template = {
            "id": "base_web",
            "name": "Base Web Template",
            "description": "Base template for all web applications",
            "version": "1.0.0",
            "project_type": "web_frontend",
            "technology_stack": ["html", "css", "javascript"],
            "default_tags": ["web", "frontend", "quality"],
            "required_instructions": ["html_validation", "css_best_practices"],
            "optional_instructions": ["accessibility_guidelines"],
            "parameters": {
                "project_name": {
                    "type": "string",
                    "default": "web-app",
                    "description": "Name of the web project",
                },
                "include_analytics": {
                    "type": "boolean",
                    "default": False,
                    "description": "Include analytics tracking",
                },
            },
            "metadata": {"category": "web", "complexity": "beginner"},
        }

        # Create framework-specific template that inherits from base
        framework_template = {
            "id": "spa_framework",
            "name": "SPA Framework Template",
            "description": "Template for Single Page Applications",
            "version": "1.0.0",
            "project_type": "web_frontend",
            "technology_stack": ["spa", "routing"],
            "default_tags": ["spa", "routing"],
            "required_instructions": ["spa_routing", "state_management"],
            "parameters": {
                "router_library": {
                    "type": "string",
                    "default": "react-router",
                    "description": "Routing library to use",
                }
            },
            "inheritance": {"parent": "base_web", "override_mode": "merge"},
            "metadata": {"category": "web", "complexity": "intermediate"},
        }

        # Create React-specific template that inherits from SPA framework
        react_template = {
            "id": "react_spa",
            "name": "React SPA Template",
            "description": "Template for React Single Page Applications",
            "version": "1.0.0",
            "project_type": "web_frontend",
            "technology_stack": ["react", "jsx"],
            "default_tags": ["react", "jsx"],
            "required_instructions": ["react_components", "jsx_best_practices"],
            "parameters": {
                "use_hooks": {
                    "type": "boolean",
                    "default": True,
                    "description": "Use React Hooks",
                },
                "state_library": {
                    "type": "string",
                    "default": "redux",
                    "description": "State management library",
                    "options": ["redux", "zustand", "context"],
                },
            },
            "inheritance": {"parent": "spa_framework", "override_mode": "merge"},
            "metadata": {"category": "web", "complexity": "intermediate"},
        }

        # Save templates
        with open(templates_dir / "base-web.json", "w") as f:
            json.dump(base_template, f, indent=2)

        with open(templates_dir / "spa-framework.json", "w") as f:
            json.dump(framework_template, f, indent=2)

        with open(templates_dir / "react-spa.json", "w") as f:
            json.dump(react_template, f, indent=2)

        # Load templates and test inheritance
        manager = TemplateManager(templates_path=templates_dir)
        templates = manager.load_templates()

        # Verify all templates loaded
        assert len(templates) == 3

        # Test React template inheritance
        react = templates["react_spa"]

        # Should have merged technology stack
        expected_tech = {"html", "css", "javascript", "spa", "routing", "react", "jsx"}
        assert set(react.technology_stack) == expected_tech

        # Should have merged tags
        expected_tags = {"web", "frontend", "quality", "spa", "routing", "react", "jsx"}
        assert set(react.default_tags) == expected_tags

        # Should have merged required instructions
        expected_instructions = {
            "html_validation",
            "css_best_practices",
            "spa_routing",
            "state_management",
            "react_components",
            "jsx_best_practices",
        }
        assert set(react.required_instructions) == expected_instructions

        # Should have merged parameters
        assert "project_name" in react.parameters  # From base
        assert "include_analytics" in react.parameters  # From base
        assert "router_library" in react.parameters  # From SPA framework
        assert "use_hooks" in react.parameters  # From React
        assert "state_library" in react.parameters  # From React

        # Verify parameter defaults
        assert react.parameters["project_name"].default == "web-app"
        assert react.parameters["use_hooks"].default is True

    def test_template_override_modes(self, temp_dir):
        """Test different template inheritance override modes."""
        templates_dir = temp_dir / "templates"
        templates_dir.mkdir()

        # Create parent template
        parent_template = {
            "id": "parent_template",
            "name": "Parent Template",
            "description": "Parent template for testing override modes",
            "version": "1.0.0",
            "project_type": "web_frontend",
            "technology_stack": ["html", "css"],
            "default_tags": ["parent", "base"],
            "required_instructions": ["parent_instruction"],
            "metadata": {"category": "web"},
        }

        # Create child template with merge mode
        merge_child = {
            "id": "merge_child",
            "name": "Merge Child Template",
            "description": "Child template using merge mode",
            "version": "1.0.0",
            "project_type": "web_frontend",
            "technology_stack": ["javascript"],
            "default_tags": ["child", "merge"],
            "required_instructions": ["child_instruction"],
            "inheritance": {"parent": "parent_template", "override_mode": "merge"},
            "metadata": {"category": "web"},
        }

        # Create child template with extend mode
        extend_child = {
            "id": "extend_child",
            "name": "Extend Child Template",
            "description": "Child template using extend mode",
            "version": "1.0.0",
            "project_type": "web_frontend",
            "technology_stack": ["typescript"],
            "default_tags": ["child", "extend"],
            "required_instructions": ["child_instruction"],
            "inheritance": {"parent": "parent_template", "override_mode": "extend"},
            "metadata": {"category": "web"},
        }

        # Create child template with replace mode
        replace_child = {
            "id": "replace_child",
            "name": "Replace Child Template",
            "description": "Child template using replace mode",
            "version": "1.0.0",
            "project_type": "web_frontend",
            "technology_stack": ["python"],
            "default_tags": ["child", "replace"],
            "required_instructions": ["child_instruction"],
            "inheritance": {"parent": "parent_template", "override_mode": "replace"},
            "metadata": {"category": "web"},
        }

        # Save templates
        templates_data = [
            (parent_template, "parent.json"),
            (merge_child, "merge-child.json"),
            (extend_child, "extend-child.json"),
            (replace_child, "replace-child.json"),
        ]

        for template_data, filename in templates_data:
            with open(templates_dir / filename, "w") as f:
                json.dump(template_data, f, indent=2)

        # Load and test
        manager = TemplateManager(templates_path=templates_dir)
        templates = manager.load_templates()

        # Test merge mode
        merge_template = templates["merge_child"]
        assert set(merge_template.technology_stack) == {"html", "css", "javascript"}
        assert set(merge_template.default_tags) == {"parent", "base", "child", "merge"}
        assert set(merge_template.required_instructions) == {
            "parent_instruction",
            "child_instruction",
        }

        # Test extend mode
        extend_template = templates["extend_child"]
        assert set(extend_template.technology_stack) == {"html", "css", "typescript"}
        assert set(extend_template.default_tags) == {
            "child",
            "extend",
            "parent",
            "base",
        }
        assert set(extend_template.required_instructions) == {
            "child_instruction",
            "parent_instruction",
        }

        # Test replace mode (should only have child values)
        replace_template = templates["replace_child"]
        assert replace_template.technology_stack == ["python"]
        assert replace_template.default_tags == ["child", "replace"]
        assert replace_template.required_instructions == ["child_instruction"]

    def test_template_parameter_inheritance(self, temp_dir):
        """Test parameter inheritance in templates."""
        templates_dir = temp_dir / "templates"
        templates_dir.mkdir()

        # Create parent with parameters
        parent_template = {
            "id": "param_parent",
            "name": "Parameter Parent",
            "description": "Parent template with parameters",
            "version": "1.0.0",
            "project_type": "web_frontend",
            "technology_stack": ["base"],
            "default_tags": ["parent"],
            "parameters": {
                "app_name": {
                    "type": "string",
                    "default": "my-app",
                    "description": "Application name",
                    "required": True,
                },
                "version": {
                    "type": "string",
                    "default": "1.0.0",
                    "description": "Application version",
                },
                "author": {
                    "type": "string",
                    "default": "developer",
                    "description": "Application author",
                },
            },
            "metadata": {"category": "web"},
        }

        # Create child that overrides some parameters
        child_template = {
            "id": "param_child",
            "name": "Parameter Child",
            "description": "Child template with parameter overrides",
            "version": "1.0.0",
            "project_type": "web_frontend",
            "technology_stack": ["child"],
            "default_tags": ["child"],
            "parameters": {
                "app_name": {
                    "type": "string",
                    "default": "child-app",  # Override default
                    "description": "Child application name",
                    "required": True,
                },
                "framework": {
                    "type": "string",
                    "default": "react",
                    "description": "Framework to use",
                    "options": ["react", "vue", "angular"],
                },
            },
            "inheritance": {"parent": "param_parent", "override_mode": "merge"},
            "metadata": {"category": "web"},
        }

        # Save templates
        with open(templates_dir / "param-parent.json", "w") as f:
            json.dump(parent_template, f, indent=2)

        with open(templates_dir / "param-child.json", "w") as f:
            json.dump(child_template, f, indent=2)

        # Load and test
        manager = TemplateManager(templates_path=templates_dir)
        templates = manager.load_templates()

        child = templates["param_child"]

        # Should have all parameters
        assert len(child.parameters) == 4
        assert "app_name" in child.parameters
        assert "version" in child.parameters
        assert "author" in child.parameters
        assert "framework" in child.parameters

        # Child should override parent parameter
        assert child.parameters["app_name"].default == "child-app"
        assert child.parameters["app_name"].description == "Child application name"

        # Parent parameters should be preserved
        assert child.parameters["version"].default == "1.0.0"
        assert child.parameters["author"].default == "developer"

        # Child-specific parameter should exist
        assert child.parameters["framework"].default == "react"
        assert child.parameters["framework"].options == ["react", "vue", "angular"]

    def test_template_condition_inheritance(self, temp_dir):
        """Test condition inheritance in templates."""
        templates_dir = temp_dir / "templates"
        templates_dir.mkdir()

        # Create parent with conditions
        parent_template = {
            "id": "condition_parent",
            "name": "Condition Parent",
            "description": "Parent template with conditions",
            "version": "1.0.0",
            "project_type": "web_frontend",
            "technology_stack": ["base"],
            "default_tags": ["parent"],
            "conditions": [
                {
                    "type": "file_exists",
                    "value": "package.json",
                    "operator": "exists",
                    "weight": 0.8,
                },
                {
                    "type": "project_structure",
                    "value": "src",
                    "operator": "exists",
                    "weight": 0.6,
                },
            ],
            "metadata": {"category": "web"},
        }

        # Create child with additional conditions
        child_template = {
            "id": "condition_child",
            "name": "Condition Child",
            "description": "Child template with additional conditions",
            "version": "1.0.0",
            "project_type": "web_frontend",
            "technology_stack": ["child"],
            "default_tags": ["child"],
            "conditions": [
                {
                    "type": "dependency_exists",
                    "value": "react",
                    "operator": "exists",
                    "weight": 0.9,
                },
                {
                    "type": "file_exists",
                    "value": "tsconfig.json",
                    "operator": "exists",
                    "weight": 0.7,
                },
            ],
            "inheritance": {"parent": "condition_parent", "override_mode": "merge"},
            "metadata": {"category": "web"},
        }

        # Save templates
        with open(templates_dir / "condition-parent.json", "w") as f:
            json.dump(parent_template, f, indent=2)

        with open(templates_dir / "condition-child.json", "w") as f:
            json.dump(child_template, f, indent=2)

        # Load and test
        manager = TemplateManager(templates_path=templates_dir)
        templates = manager.load_templates()

        child = templates["condition_child"]

        # Should have all conditions (parent + child)
        assert len(child.conditions) == 4

        # Verify condition types
        condition_types = [cond.type for cond in child.conditions]
        assert "file_exists" in condition_types
        assert "project_structure" in condition_types
        assert "dependency_exists" in condition_types

        # Verify specific conditions
        package_json_conditions = [
            cond
            for cond in child.conditions
            if cond.type == "file_exists" and cond.value == "package.json"
        ]
        assert len(package_json_conditions) == 1
        assert package_json_conditions[0].weight == 0.8

        react_conditions = [
            cond
            for cond in child.conditions
            if cond.type == "dependency_exists" and cond.value == "react"
        ]
        assert len(react_conditions) == 1
        assert react_conditions[0].weight == 0.9

    def test_template_with_spec_generator_integration(self, temp_dir):
        """Test template integration with spec generator."""
        # Setup directories
        templates_dir = temp_dir / "templates"
        instructions_dir = temp_dir / "instructions"
        templates_dir.mkdir()
        instructions_dir.mkdir()

        # Create instructions that will be used by template
        instructions_data = {
            "instructions": [
                {
                    "id": "react_setup",
                    "version": "1.0.0",
                    "tags": ["react", "setup"],
                    "content": "Set up React application with {project_name} and {framework_version}.",
                    "parameters": [
                        {
                            "name": "project_name",
                            "type": "string",
                            "default": "react-app",
                        },
                        {
                            "name": "framework_version",
                            "type": "string",
                            "default": "18.0.0",
                        },
                    ],
                    "metadata": {"category": "setup"},
                },
                {
                    "id": "testing_setup",
                    "version": "1.0.0",
                    "tags": ["testing", "jest"],
                    "content": "Configure Jest and React Testing Library for {project_name}.",
                    "parameters": [
                        {
                            "name": "project_name",
                            "type": "string",
                            "default": "react-app",
                        }
                    ],
                    "metadata": {"category": "testing"},
                },
            ]
        }

        with open(instructions_dir / "react-instructions.json", "w") as f:
            json.dump(instructions_data, f, indent=2)

        # Create template that uses these instructions
        template_data = {
            "id": "full_react_app",
            "name": "Full React Application",
            "description": "Complete React application template with testing",
            "version": "1.0.0",
            "project_type": "web_frontend",
            "technology_stack": ["react", "jest"],
            "default_tags": ["react", "testing"],
            "required_instructions": ["react_setup", "testing_setup"],
            "parameters": {
                "project_name": {
                    "type": "string",
                    "default": "my-react-app",
                    "description": "Name of the React project",
                    "required": True,
                },
                "framework_version": {
                    "type": "string",
                    "default": "18.2.0",
                    "description": "React version to use",
                },
            },
            "metadata": {"category": "web", "complexity": "intermediate"},
        }

        with open(templates_dir / "full-react-frontend.json", "w") as f:
            json.dump(template_data, f, indent=2)

        # Initialize components
        instruction_db = InstructionDatabase(instructions_path=instructions_dir)
        template_manager = TemplateManager(templates_path=templates_dir)
        spec_generator = SpecGenerator(
            instruction_db=instruction_db, template_manager=template_manager
        )

        # Generate spec using template
        config = SpecConfig(
            template_id="full_react_app",
            template_parameters={
                "project_name": "AwesomeReactApp",
                "framework_version": "18.2.0",
            },
        )

        spec = spec_generator.generate_spec(config)

        # Verify spec generation
        assert spec.content
        assert spec.template_used == "full_react_app"
        assert len(spec.instructions_used) == 2
        assert "react_setup" in spec.instructions_used
        assert "testing_setup" in spec.instructions_used

        # Verify parameter substitution
        assert "AwesomeReactApp" in spec.content
        assert "18.2.0" in spec.content

        # Verify spec structure
        assert "# AgentSpec" in spec.content
        assert "## IMPLEMENTATION FRAMEWORK" in spec.content
        assert "## QUALITY GATES" in spec.content
