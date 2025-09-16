"""
Integration tests for file system operations.
"""

import json
import tempfile
import time
from pathlib import Path

import pytest

from agentspec.core.instruction_database import InstructionDatabase
from agentspec.core.template_manager import TemplateManager


class TestFileSystemIntegration:
    """Integration tests for file system operations."""

    def test_instruction_database_file_loading(self, temp_dir):
        """Test instruction database file loading integration."""
        instructions_dir = temp_dir / "instructions"
        instructions_dir.mkdir()

        # Create multiple instruction files
        general_instructions = {
            "instructions": [
                {
                    "id": "general_quality",
                    "version": "1.0.0",
                    "tags": ["general", "quality"],
                    "content": "Maintain high code quality standards throughout the project.",
                    "metadata": {
                        "category": "general",
                        "priority": 5,
                        "author": "quality_team",
                    },
                },
                {
                    "id": "code_review",
                    "version": "1.1.0",
                    "tags": ["general", "review"],
                    "content": "Implement thorough code review processes.",
                    "metadata": {"category": "general", "priority": 7},
                },
            ]
        }

        testing_instructions = {
            "instructions": [
                {
                    "id": "unit_testing",
                    "version": "2.0.0",
                    "tags": ["testing", "unit"],
                    "content": "Write comprehensive unit tests for all functions and methods.",
                    "conditions": [
                        {
                            "type": "project_type",
                            "value": "web_frontend",
                            "operator": "equals",
                        }
                    ],
                    "metadata": {"category": "testing", "priority": 9},
                }
            ]
        }

        # Save instruction files
        with open(instructions_dir / "general.json", "w") as f:
            json.dump(general_instructions, f, indent=2)

        with open(instructions_dir / "testing.json", "w") as f:
            json.dump(testing_instructions, f, indent=2)

        # Test loading
        db = InstructionDatabase(instructions_path=instructions_dir)
        instructions = db.load_instructions()

        # Verify all instructions loaded
        assert len(instructions) == 3
        assert "general_quality" in instructions
        assert "code_review" in instructions
        assert "unit_testing" in instructions

        # Verify instruction properties
        quality_inst = instructions["general_quality"]
        assert quality_inst.version == "1.0.0"
        assert "general" in quality_inst.tags
        assert quality_inst.metadata.category == "general"
        assert quality_inst.metadata.priority == 5

        # Test tag-based retrieval
        general_instructions = db.get_by_tags(["general"])
        assert len(general_instructions) == 2

        testing_instructions = db.get_by_tags(["testing"])
        assert len(testing_instructions) == 1
        assert testing_instructions[0].id == "unit_testing"

    def test_template_manager_file_loading(self, temp_dir):
        """Test template manager file loading integration."""
        templates_dir = temp_dir / "templates"
        templates_dir.mkdir()

        # Create React template
        react_template = {
            "id": "react_app",
            "name": "React Application",
            "description": "Template for React applications with modern tooling",
            "version": "1.0.0",
            "project_type": "web_frontend",
            "technology_stack": ["react", "javascript", "webpack"],
            "default_tags": ["frontend", "react", "testing"],
            "required_instructions": ["unit_testing", "code_review"],
            "optional_instructions": ["general_quality"],
            "parameters": {
                "project_name": {
                    "type": "string",
                    "default": "my-react-app",
                    "description": "Name of the React project",
                    "required": True,
                },
                "use_typescript": {
                    "type": "boolean",
                    "default": False,
                    "description": "Whether to use TypeScript",
                },
            },
            "conditions": [
                {
                    "type": "file_exists",
                    "value": "package.json",
                    "operator": "exists",
                    "weight": 0.8,
                }
            ],
            "metadata": {
                "category": "web",
                "complexity": "intermediate",
                "author": "frontend_team",
            },
        }

        # Create Vue template
        vue_template = {
            "id": "vue_app",
            "name": "Vue Application",
            "description": "Template for Vue.js applications",
            "version": "1.2.0",
            "project_type": "web_frontend",
            "technology_stack": ["vue", "javascript"],
            "default_tags": ["frontend", "vue", "testing"],
            "required_instructions": ["unit_testing"],
            "metadata": {"category": "web", "complexity": "beginner"},
        }

        # Save template files
        with open(templates_dir / "react_app.json", "w") as f:
            json.dump(react_template, f, indent=2)

        with open(templates_dir / "vue-app.json", "w") as f:
            json.dump(vue_template, f, indent=2)

        # Test loading
        manager = TemplateManager(templates_path=templates_dir)
        templates = manager.load_templates()

        # Verify templates loaded
        assert len(templates) == 2
        assert "react_app" in templates
        assert "vue_app" in templates

        # Verify template properties
        react = templates["react_app"]
        assert react.name == "React Application"
        assert react.project_type == "web_frontend"
        assert "react" in react.technology_stack
        assert len(react.parameters) == 2
        assert "project_name" in react.parameters

        # Test template retrieval by project type
        web_templates = manager.get_templates_by_project_type("web_frontend")
        assert len(web_templates) == 2

        # Test template retrieval by technology
        react_templates = manager.get_templates_by_technology("react")
        assert len(react_templates) == 1
        assert react_templates[0].id == "react_app"

    def test_cross_component_file_integration(self, temp_dir):
        """Test integration between components using file system."""
        # Setup directories
        instructions_dir = temp_dir / "instructions"
        templates_dir = temp_dir / "templates"
        contexts_dir = temp_dir / "contexts"

        instructions_dir.mkdir()
        templates_dir.mkdir()
        contexts_dir.mkdir()

        # Create instruction that will be referenced by template
        instruction_data = {
            "instructions": [
                {
                    "id": "react_testing_setup",
                    "version": "1.0.0",
                    "tags": ["react", "testing", "setup"],
                    "content": "Set up Jest and React Testing Library for comprehensive testing.",
                    "metadata": {"category": "testing", "priority": 8},
                }
            ]
        }

        with open(instructions_dir / "react-testing.json", "w") as f:
            json.dump(instruction_data, f)

        # Create template that references the instruction
        template_data = {
            "id": "react_with_testing",
            "name": "React App with Testing",
            "description": "React application template with testing setup",
            "version": "1.0.0",
            "project_type": "web_frontend",
            "technology_stack": ["react", "jest"],
            "default_tags": ["react", "testing"],
            "required_instructions": ["react_testing_setup"],
            "metadata": {"category": "web", "complexity": "intermediate"},
        }

        with open(templates_dir / "react-testing.json", "w") as f:
            json.dump(template_data, f)

        # Initialize components
        instruction_db = InstructionDatabase(instructions_path=instructions_dir)
        template_manager = TemplateManager(templates_path=templates_dir)

        # Load data
        instructions = instruction_db.load_instructions()
        templates = template_manager.load_templates()

        # Verify cross-references work
        template = templates["react_with_testing"]
        required_instruction_id = template.required_instructions[0]
        instruction = instruction_db.get_instruction(required_instruction_id)

        assert instruction is not None
        assert instruction.id == "react_testing_setup"
        assert "testing" in instruction.tags

    def test_concurrent_file_operations(self, temp_dir):
        """Test concurrent file operations integration."""
        import threading
        import time

        instructions_dir = temp_dir / "instructions"
        instructions_dir.mkdir()

        # Create base instruction file
        base_instructions = {
            "instructions": [
                {
                    "id": "base_instruction",
                    "version": "1.0.0",
                    "tags": ["base"],
                    "content": "Base instruction content",
                    "metadata": {"category": "base"},
                }
            ]
        }

        with open(instructions_dir / "base.json", "w") as f:
            json.dump(base_instructions, f)

        results = []
        errors = []

        def load_instructions(thread_id):
            try:
                db = InstructionDatabase(instructions_path=instructions_dir)
                instructions = db.load_instructions()
                results.append((thread_id, len(instructions)))
                time.sleep(0.1)  # Simulate some processing
            except Exception as e:
                errors.append((thread_id, str(e)))

        # Run multiple threads concurrently
        threads = []
        for i in range(5):
            thread = threading.Thread(target=load_instructions, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Verify results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 5

        # All threads should have loaded the same number of instructions
        instruction_counts = [count for _, count in results]
        assert all(count == 1 for count in instruction_counts)

    def test_large_file_handling(self, temp_dir):
        """Test handling of large instruction/template files."""
        instructions_dir = temp_dir / "instructions"
        instructions_dir.mkdir()

        # Create large instruction file
        large_instructions = {"instructions": []}

        for i in range(1000):  # Create 1000 instructions
            instruction = {
                "id": f"large_instruction_{i}",
                "version": "1.0.0",
                "tags": [f"tag-{i % 10}", f"category-{i % 5}"],
                "content": f"Large instruction {i} with detailed content for performance testing. "
                * 10,
                "metadata": {"category": f"category-{i % 5}", "priority": (i % 10) + 1},
            }
            large_instructions["instructions"].append(instruction)

        # Save large file
        large_file = instructions_dir / "large.json"
        with open(large_file, "w") as f:
            json.dump(large_instructions, f)

        # Verify file size
        file_size = large_file.stat().st_size
        assert file_size > 100000  # Should be > 100KB

        # Test loading large file
        start_time = time.time()
        db = InstructionDatabase(instructions_path=instructions_dir)
        instructions = db.load_instructions()
        load_time = time.time() - start_time

        # Verify all instructions loaded
        assert len(instructions) == 1000

        # Performance should be reasonable (< 5 seconds)
        assert load_time < 5.0, f"Loading took too long: {load_time:.2f}s"

        # Test querying large dataset
        start_time = time.time()
        tag_0_instructions = db.get_by_tags(["tag-0"])
        query_time = time.time() - start_time

        # Should find 100 instructions with tag-0
        assert len(tag_0_instructions) == 100

        # Query should be fast (< 1 second)
        assert query_time < 1.0, f"Query took too long: {query_time:.2f}s"

    def test_file_corruption_handling(self, temp_dir):
        """Test handling of corrupted files."""
        instructions_dir = temp_dir / "instructions"
        instructions_dir.mkdir()

        # Create valid instruction file
        valid_instructions = {
            "instructions": [
                {
                    "id": "valid_instruction",
                    "version": "1.0.0",
                    "tags": ["valid"],
                    "content": "Valid instruction content",
                    "metadata": {"category": "valid"},
                }
            ]
        }

        with open(instructions_dir / "valid.json", "w") as f:
            json.dump(valid_instructions, f)

        # Create corrupted JSON file
        with open(instructions_dir / "corrupted.json", "w") as f:
            f.write('{"instructions": [{"id": "corrupted", "invalid": json}]}')

        # Create file with missing required fields
        invalid_instructions = {
            "instructions": [
                {
                    "id": "",  # Empty ID
                    "version": "1.0.0",
                    "tags": [],  # Empty tags
                    "content": "Short",  # Too short content
                    "metadata": {"category": "invalid"},
                }
            ]
        }

        with open(instructions_dir / "invalid.json", "w") as f:
            json.dump(invalid_instructions, f)

        # Test loading with corrupted files
        db = InstructionDatabase(instructions_path=instructions_dir)
        instructions = db.load_instructions()

        # Should only load valid instructions, skip corrupted ones
        assert len(instructions) == 1
        assert "valid_instruction" in instructions

        # Verify the valid instruction loaded correctly
        valid_inst = instructions["valid_instruction"]
        assert valid_inst.id == "valid_instruction"
        assert "valid" in valid_inst.tags
