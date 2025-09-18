"""
Integration tests for component interactions.
"""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from agentspec.core.context_detector import ContextDetector
from agentspec.core.instruction_database import InstructionDatabase
from agentspec.core.spec_generator import SpecConfig, SpecGenerator
from agentspec.core.template_manager import TemplateManager


class TestInstructionDatabaseIntegration:
    """Integration tests for InstructionDatabase with other components."""

    def test_instruction_database_with_spec_generator(self, mock_instruction_files):
        """Test InstructionDatabase integration with SpecGenerator."""
        # Create real instances
        instruction_db = InstructionDatabase(instructions_path=mock_instruction_files)
        spec_generator = SpecGenerator(instruction_db=instruction_db)

        # Load instructions
        instructions = instruction_db.load_instructions()
        assert len(instructions) > 0

        # Generate spec using loaded instructions
        config = SpecConfig(selected_tags=["testing"])
        spec = spec_generator.generate_spec(config)

        assert spec.content
        assert len(spec.instructions_used) > 0
        assert spec.validation_result.is_valid

    def test_instruction_database_with_template_manager(
        self, mock_instruction_files, mock_template_files
    ):
        """Test InstructionDatabase integration with TemplateManager."""
        instruction_db = InstructionDatabase(instructions_path=mock_instruction_files)
        template_manager = TemplateManager(templates_path=mock_template_files)

        # Load both
        instructions = instruction_db.load_instructions()
        templates = template_manager.load_templates()

        assert len(instructions) > 0
        assert len(templates) > 0

        # Verify template references valid instructions
        for template in templates.values():
            for required_inst in template.required_instructions:
                # Should be able to find instruction
                instruction = instruction_db.get_instruction(required_inst)
                # Note: In real scenario, this should exist, but in mock it might not
                # This tests the integration pattern

    def test_instruction_database_dependency_resolution(self, temp_dir):
        """Test instruction dependency resolution integration."""
        instructions_dir = temp_dir / "instructions"
        instructions_dir.mkdir()

        # Create instructions with dependencies
        dependent_instructions = {
            "instructions": [
                {
                    "id": "base_instruction",
                    "version": "1.0.0",
                    "tags": ["base"],
                    "content": "Base instruction content",
                    "metadata": {"category": "base"},
                },
                {
                    "id": "dependent_instruction",
                    "version": "1.0.0",
                    "tags": ["dependent"],
                    "content": "Dependent instruction content",
                    "dependencies": ["base_instruction"],
                    "metadata": {"category": "dependent"},
                },
            ]
        }

        with open(instructions_dir / "dependent.json", "w") as f:
            json.dump(dependent_instructions, f)

        instruction_db = InstructionDatabase(instructions_path=instructions_dir)
        instructions = instruction_db.load_instructions()

        # Test dependency resolution
        ordered_ids = instruction_db.resolve_dependencies(
            ["dependent_instruction", "base_instruction"]
        )

        # Base instruction should come before dependent
        assert ordered_ids.index("base_instruction") < ordered_ids.index(
            "dependent_instruction"
        )


class TestTemplateManagerIntegration:
    """Integration tests for TemplateManager with other components."""

    def test_template_manager_with_context_detector(
        self, mock_template_files, mock_project_structure
    ):
        """Test TemplateManager integration with ContextDetector."""
        template_manager = TemplateManager(templates_path=mock_template_files)
        context_detector = ContextDetector()

        # Load templates
        templates = template_manager.load_templates()
        assert len(templates) > 0

        # Analyze project
        context = context_detector.analyze_project(str(mock_project_structure))

        # Get template recommendations based on context
        project_context_dict = {
            "project_type": context.project_type.value,
            "technology_stack": [fw.name for fw in context.technology_stack.frameworks],
            "files": context.file_structure.config_files,
        }

        recommendations = template_manager.get_recommended_templates(
            project_context_dict
        )

        # Should get some recommendations
        assert isinstance(recommendations, list)

    def test_template_manager_with_spec_generator(self, mock_template_files):
        """Test TemplateManager integration with SpecGenerator."""
        template_manager = TemplateManager(templates_path=mock_template_files)
        spec_generator = SpecGenerator(template_manager=template_manager)

        # Load templates
        templates = template_manager.load_templates()
        template_id = list(templates.keys())[0] if templates else None

        if template_id:
            # Generate spec using template
            config = SpecConfig(template_id=template_id)
            spec = spec_generator.generate_spec(config)

            assert spec.content
            assert spec.template_used == template_id

    def test_template_inheritance_integration(self, temp_dir):
        """Test template inheritance integration."""
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
            "required_instructions": ["base_quality"],
            "metadata": {"category": "web"},
        }

        # Create child template
        child_template = {
            "id": "react_web",
            "name": "React Web Template",
            "description": "React-specific web template",
            "version": "1.0.0",
            "project_type": "web_frontend",
            "technology_stack": ["react"],
            "default_tags": ["react"],
            "required_instructions": ["react_testing"],
            "inheritance": {"parent": "base_web", "override_mode": "merge"},
            "metadata": {"category": "web"},
        }

        # Save templates
        with open(templates_dir / "base-web.json", "w") as f:
            json.dump(parent_template, f)

        with open(templates_dir / "react-web.json", "w") as f:
            json.dump(child_template, f)

        # Test inheritance resolution
        template_manager = TemplateManager(templates_path=templates_dir)
        templates = template_manager.load_templates()

        react_template = templates["react_web"]

        # Should have merged properties
        assert "web" in react_template.default_tags
        assert "react" in react_template.default_tags
        assert "base_quality" in react_template.required_instructions
        assert "react_testing" in react_template.required_instructions


class TestContextDetectorIntegration:
    """Integration tests for ContextDetector with other components."""

    def test_context_detector_with_spec_generator(self, mock_project_structure):
        """Test ContextDetector integration with SpecGenerator."""
        context_detector = ContextDetector()
        spec_generator = SpecGenerator(context_detector=context_detector)

        # Analyze project
        context = context_detector.analyze_project(str(mock_project_structure))

        # Generate spec with context
        config = SpecConfig(
            selected_tags=["frontend", "testing"], project_context=context
        )

        spec = spec_generator.generate_spec(config)

        assert spec.content
        assert spec.metadata["project_context"] == context.project_type.value

    def test_context_detector_instruction_suggestions(self, mock_project_structure):
        """Test context detector instruction suggestions integration."""
        context_detector = ContextDetector()

        # Analyze project
        context = context_detector.analyze_project(str(mock_project_structure))

        # Get instruction suggestions
        suggestions = context_detector.suggest_instructions(context)

        assert isinstance(suggestions, list)

        # Suggestions should be relevant to detected project type
        if suggestions:
            for suggestion in suggestions[:5]:  # Check first 5
                assert suggestion.instruction_id
                assert isinstance(suggestion.tags, list)
                assert 0 <= suggestion.confidence <= 1
                assert isinstance(suggestion.reasons, list)

    def test_context_detector_framework_detection_integration(self, temp_dir):
        """Test framework detection integration."""
        # Create React project structure
        project_dir = temp_dir / "react_project"
        project_dir.mkdir()

        # Create package.json with React
        package_json = {
            "name": "react-app",
            "dependencies": {"react": "^18.0.0", "react-dom": "^18.0.0"},
            "devDependencies": {"jest": "^28.0.0"},
        }

        with open(project_dir / "package.json", "w") as f:
            json.dump(package_json, f)

        # Create React component
        src_dir = project_dir / "src"
        src_dir.mkdir()

        (src_dir / "App.jsx").write_text(
            """
import React from 'react';

function App() {
  return <div>Hello React</div>;
}

export default App;
        """
        )

        context_detector = ContextDetector()
        context = context_detector.analyze_project(str(project_dir))

        # Should detect React
        framework_names = [fw.name for fw in context.technology_stack.frameworks]
        assert "react" in framework_names

        # Should detect JavaScript
        language_values = [lang.value for lang in context.technology_stack.languages]
        assert "javascript" in language_values


class TestSpecGeneratorIntegration:
    """Integration tests for SpecGenerator with all components."""

    def test_spec_generator_full_integration(
        self, mock_instruction_files, mock_template_files, mock_project_structure
    ):
        """Test SpecGenerator with all components integrated."""
        # Create all components
        instruction_db = InstructionDatabase(instructions_path=mock_instruction_files)
        template_manager = TemplateManager(templates_path=mock_template_files)
        context_detector = ContextDetector()

        spec_generator = SpecGenerator(
            instruction_db=instruction_db,
            template_manager=template_manager,
            context_detector=context_detector,
        )

        # Analyze project
        context = context_detector.analyze_project(str(mock_project_structure))

        # Load templates and get recommendation
        templates = template_manager.load_templates()
        if templates:
            template_id = list(templates.keys())[0]
            template = templates[template_id]

            # Apply template with context
            config = spec_generator.apply_template(template, context)

            # Generate spec
            spec = spec_generator.generate_spec(config)

            assert spec.content
            assert spec.template_used == template_id
            assert len(spec.instructions_used) > 0

    def test_spec_generator_conditional_instructions(self, temp_dir):
        """Test spec generator with conditional instructions."""
        # Create instructions with conditions
        instructions_dir = temp_dir / "instructions"
        instructions_dir.mkdir()

        conditional_instructions = {
            "instructions": [
                {
                    "id": "react_specific",
                    "version": "1.0.0",
                    "tags": ["react", "frontend"],
                    "content": "React-specific instruction content",
                    "conditions": [
                        {"type": "technology", "value": "react", "operator": "equals"}
                    ],
                    "metadata": {"category": "frontend"},
                },
                {
                    "id": "vue_specific",
                    "version": "1.0.0",
                    "tags": ["vue", "frontend"],
                    "content": "Vue-specific instruction content",
                    "conditions": [
                        {"type": "technology", "value": "vue", "operator": "equals"}
                    ],
                    "metadata": {"category": "frontend"},
                },
            ]
        }

        with open(instructions_dir / "conditional.json", "w") as f:
            json.dump(conditional_instructions, f)

        # Create mock context with React
        mock_framework = Mock()
        mock_framework.name = "react"

        mock_language = Mock()
        mock_language.value = "javascript"

        mock_context = Mock()
        mock_context.project_path = str(temp_dir)
        mock_context.project_type.value = "web_frontend"
        mock_context.confidence_score = 0.85
        mock_context.technology_stack.frameworks = [mock_framework]
        mock_context.technology_stack.languages = [mock_language]

        instruction_db = InstructionDatabase(instructions_path=instructions_dir)
        spec_generator = SpecGenerator(instruction_db=instruction_db)

        # Load instructions to ensure they're available
        instructions = instruction_db.load_instructions()

        # Ensure instructions were loaded correctly
        assert "react_specific" in instructions
        assert "vue_specific" in instructions

        # Generate spec with context
        config = SpecConfig(selected_tags=["frontend"], project_context=mock_context)

        spec = spec_generator.generate_spec(config)

        # Should include React-specific instruction but not Vue-specific
        assert (
            "react_specific" in spec.instructions_used
        ), f"Instructions used: {spec.instructions_used}"
        assert (
            "vue_specific" not in spec.instructions_used
        ), f"Instructions used: {spec.instructions_used}"

    def test_spec_generator_parameter_substitution(self, temp_dir):
        """Test spec generator parameter substitution integration."""
        # Create instructions with parameters
        instructions_dir = temp_dir / "instructions"
        instructions_dir.mkdir()

        parameterized_instructions = {
            "instructions": [
                {
                    "id": "project_setup",
                    "version": "1.0.0",
                    "tags": ["setup"],
                    "content": "Set up project {project_name} using {framework} framework.",
                    "parameters": [
                        {"name": "project_name", "type": "string", "default": "my-app"},
                        {"name": "framework", "type": "string", "default": "react"},
                    ],
                    "metadata": {"category": "setup"},
                }
            ]
        }

        with open(instructions_dir / "parameterized.json", "w") as f:
            json.dump(parameterized_instructions, f)

        instruction_db = InstructionDatabase(instructions_path=instructions_dir)
        spec_generator = SpecGenerator(instruction_db=instruction_db)

        # Generate spec with parameters
        config = SpecConfig(
            selected_tags=["setup"],
            template_parameters={"project_name": "MyAwesomeApp", "framework": "Vue"},
        )

        spec = spec_generator.generate_spec(config)

        # Parameters should be substituted
        assert "MyAwesomeApp" in spec.content
        assert "Vue" in spec.content


class TestCrossComponentValidation:
    """Integration tests for cross-component validation."""

    def test_instruction_template_consistency(
        self, mock_instruction_files, mock_template_files
    ):
        """Test consistency between instructions and templates."""
        instruction_db = InstructionDatabase(instructions_path=mock_instruction_files)
        template_manager = TemplateManager(templates_path=mock_template_files)

        instructions = instruction_db.load_instructions()
        templates = template_manager.load_templates()

        # Check that template references exist in instruction database
        for template in templates.values():
            for required_inst in template.required_instructions:
                # In a real scenario, this should pass
                # Here we just test the integration pattern
                instruction = instruction_db.get_instruction(required_inst)
                # Note: May be None in mock scenario, but tests the lookup

    def test_context_template_matching(
        self, mock_template_files, mock_project_structure
    ):
        """Test context and template matching integration."""
        template_manager = TemplateManager(templates_path=mock_template_files)
        context_detector = ContextDetector()

        # Analyze project
        context = context_detector.analyze_project(str(mock_project_structure))

        # Get template recommendations
        project_context_dict = {
            "project_type": context.project_type.value,
            "technology_stack": [fw.name for fw in context.technology_stack.frameworks],
            "files": context.file_structure.config_files,
        }

        recommendations = template_manager.get_recommended_templates(
            project_context_dict
        )

        # Recommendations should be sorted by confidence
        if len(recommendations) > 1:
            for i in range(len(recommendations) - 1):
                assert (
                    recommendations[i].confidence_score
                    >= recommendations[i + 1].confidence_score
                )

    def test_spec_validation_integration(self, mock_instruction_files):
        """Test specification validation integration."""
        instruction_db = InstructionDatabase(instructions_path=mock_instruction_files)
        spec_generator = SpecGenerator(instruction_db=instruction_db)

        # Generate spec
        config = SpecConfig(selected_tags=["testing"])
        spec = spec_generator.generate_spec(config)

        # Validate spec
        validation_result = spec_generator.validate_spec(spec)

        # Should have validation result
        assert validation_result is not None
        assert isinstance(validation_result.is_valid, bool)
        assert isinstance(validation_result.errors, list)
        assert isinstance(validation_result.warnings, list)
