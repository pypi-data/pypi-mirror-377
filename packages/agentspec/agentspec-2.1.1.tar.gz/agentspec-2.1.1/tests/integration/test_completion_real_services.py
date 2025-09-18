"""
Integration tests for completion with real AgentSpec services.

This module tests completion functionality with real InstructionDatabase
and TemplateManager instances, ensuring proper integration and data handling.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from agentspec.cli.completion import CompletionEngine, get_completion_engine
from agentspec.core.instruction_database import InstructionDatabase
from agentspec.core.template_manager import TemplateManager


class TestCompletionWithRealInstructionDatabase:
    """Integration tests with real InstructionDatabase."""

    def setup_method(self):
        """Set up test fixtures with real instruction data."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.instructions_dir = self.temp_dir / "instructions"
        self.instructions_dir.mkdir()

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_realistic_instruction_data(self):
        """Create realistic instruction data for testing."""
        # Core instructions
        core_instructions = {
            "instructions": [
                {
                    "id": "core_001",
                    "version": "1.0.0",
                    "tags": ["core", "fundamentals", "best-practices"],
                    "content": "Establish clear project structure and coding standards.",
                    "metadata": {
                        "category": "General",
                        "priority": 10,
                        "author": "AgentSpec Team",
                    },
                },
                {
                    "id": "core_002",
                    "version": "1.0.0",
                    "tags": ["core", "documentation", "maintainability"],
                    "content": "Write comprehensive documentation for all public APIs.",
                    "metadata": {"category": "General", "priority": 8},
                },
            ]
        }

        # Frontend instructions
        frontend_instructions = {
            "instructions": [
                {
                    "id": "frontend_001",
                    "version": "1.0.0",
                    "tags": ["frontend", "react", "components", "typescript"],
                    "content": "Create reusable React components with TypeScript interfaces.",
                    "conditions": [
                        {"type": "technology", "value": "react", "operator": "equals"}
                    ],
                    "metadata": {"category": "Frontend", "priority": 9},
                },
                {
                    "id": "frontend_002",
                    "version": "1.0.0",
                    "tags": ["frontend", "css", "responsive", "accessibility"],
                    "content": "Implement responsive design with accessibility considerations.",
                    "metadata": {"category": "Frontend", "priority": 7},
                },
            ]
        }

        # Testing instructions
        testing_instructions = {
            "instructions": [
                {
                    "id": "testing_001",
                    "version": "1.0.0",
                    "tags": ["testing", "unit-tests", "jest", "coverage"],
                    "content": "Write comprehensive unit tests with high coverage.",
                    "metadata": {"category": "Testing", "priority": 9},
                },
                {
                    "id": "testing_002",
                    "version": "1.0.0",
                    "tags": ["testing", "integration", "e2e", "automation"],
                    "content": "Implement integration and end-to-end test automation.",
                    "metadata": {"category": "Testing", "priority": 8},
                },
            ]
        }

        # Save instruction files
        with open(self.instructions_dir / "core.json", "w") as f:
            json.dump(core_instructions, f, indent=2)

        with open(self.instructions_dir / "frontend.json", "w") as f:
            json.dump(frontend_instructions, f, indent=2)

        with open(self.instructions_dir / "testing.json", "w") as f:
            json.dump(testing_instructions, f, indent=2)

    def test_tag_completion_with_real_database(self):
        """Test tag completion with real InstructionDatabase."""
        self.create_realistic_instruction_data()

        # Initialize real database
        db = InstructionDatabase(instructions_path=self.instructions_dir)
        engine = CompletionEngine()
        engine.set_services(instruction_db=db)

        # Test tag completion
        result = engine.get_tag_completions("test")
        assert "testing" in result, "Should find 'testing' tag"

        result = engine.get_tag_completions("front")
        assert "frontend" in result, "Should find 'frontend' tag"

        result = engine.get_tag_completions("core")
        assert "core" in result, "Should find 'core' tag"

        # Test empty prefix returns all tags
        result = engine.get_tag_completions("")
        expected_tags = {
            "core",
            "fundamentals",
            "best-practices",
            "documentation",
            "maintainability",
            "frontend",
            "react",
            "components",
            "typescript",
            "css",
            "responsive",
            "accessibility",
            "testing",
            "unit-tests",
            "jest",
            "coverage",
            "integration",
            "e2e",
            "automation",
        }

        for tag in expected_tags:
            assert tag in result, f"Expected tag '{tag}' not found in results"

    def test_instruction_completion_with_real_database(self):
        """Test instruction ID completion with real InstructionDatabase."""
        self.create_realistic_instruction_data()

        db = InstructionDatabase(instructions_path=self.instructions_dir)
        engine = CompletionEngine()
        engine.set_services(instruction_db=db)

        # Test instruction ID completion
        result = engine.get_instruction_completions("core")
        assert "core_001" in result, "Should find 'core_001' instruction"
        assert "core_002" in result, "Should find 'core_002' instruction"

        result = engine.get_instruction_completions("frontend")
        assert "frontend_001" in result, "Should find 'frontend_001' instruction"
        assert "frontend_002" in result, "Should find 'frontend_002' instruction"

        result = engine.get_instruction_completions("testing")
        assert "testing_001" in result, "Should find 'testing_001' instruction"
        assert "testing_002" in result, "Should find 'testing_002' instruction"

        # Test empty prefix returns all instruction IDs
        result = engine.get_instruction_completions("")
        expected_ids = {
            "core_001",
            "core_002",
            "frontend_001",
            "frontend_002",
            "testing_001",
            "testing_002",
        }

        for instruction_id in expected_ids:
            assert (
                instruction_id in result
            ), f"Expected instruction ID '{instruction_id}' not found"

    def test_database_error_handling_integration(self):
        """Test error handling with real database scenarios."""
        # Test with empty instructions directory
        empty_dir = self.temp_dir / "empty"
        empty_dir.mkdir()

        db = InstructionDatabase(instructions_path=empty_dir)
        engine = CompletionEngine()
        engine.set_services(instruction_db=db)

        # Should handle empty database gracefully
        result = engine.get_tag_completions("test")
        assert result == [], "Empty database should return empty results"

        # Test with corrupted instruction file
        corrupted_dir = self.temp_dir / "corrupted"
        corrupted_dir.mkdir()

        with open(corrupted_dir / "corrupted.json", "w") as f:
            f.write("invalid json content {")

        db = InstructionDatabase(instructions_path=corrupted_dir)
        engine = CompletionEngine()
        engine.set_services(instruction_db=db)

        # Should handle corrupted data gracefully
        result = engine.get_tag_completions("test")
        assert isinstance(result, list), "Should return list even with corrupted data"

    def test_database_performance_integration(self):
        """Test performance with real database operations."""
        self.create_realistic_instruction_data()

        db = InstructionDatabase(instructions_path=self.instructions_dir)
        engine = CompletionEngine()
        engine.set_services(instruction_db=db)

        import time

        # Test multiple completion requests
        start_time = time.time()
        for _ in range(10):
            engine.get_tag_completions("test")
            engine.get_instruction_completions("core")

        total_time = time.time() - start_time
        avg_time = total_time / 20  # 20 total requests

        # Should complete quickly with caching
        assert avg_time < 0.1, f"Average completion time {avg_time:.3f}s too slow"

    def test_database_caching_integration(self):
        """Test caching behavior with real database."""
        self.create_realistic_instruction_data()

        db = InstructionDatabase(instructions_path=self.instructions_dir)
        engine = CompletionEngine()
        engine.set_services(instruction_db=db)

        # First request (cache miss)
        result1 = engine.get_tag_completions("test")

        # Second request (cache hit)
        result2 = engine.get_tag_completions("test")

        # Results should be identical
        assert result1 == result2, "Cached results should match original"
        assert "testing" in result1, "Should find expected tags"


class TestCompletionWithRealTemplateManager:
    """Integration tests with real TemplateManager."""

    def setup_method(self):
        """Set up test fixtures with real template data."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.templates_dir = self.temp_dir / "templates"
        self.templates_dir.mkdir()

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_realistic_template_data(self):
        """Create realistic template data for testing."""
        # React frontend template
        react_template = {
            "id": "react-frontend-app",
            "name": "React Frontend Application",
            "description": "Complete React frontend application with TypeScript and modern tooling",
            "version": "2.1.0",
            "project_type": "web_frontend",
            "technology_stack": ["react", "typescript", "webpack", "jest", "eslint"],
            "default_tags": [
                "frontend",
                "react",
                "typescript",
                "testing",
                "build-tools",
            ],
            "required_instructions": ["frontend_001", "testing_001", "core_001"],
            "optional_instructions": ["frontend_002", "testing_002"],
            "parameters": {
                "app_name": {
                    "type": "string",
                    "default": "my-react-app",
                    "description": "Name of the React application",
                },
                "use_router": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include React Router for navigation",
                },
            },
            "metadata": {
                "category": "Frontend",
                "complexity": "intermediate",
                "maintenance": "active",
            },
        }

        # Python API template
        python_template = {
            "id": "python-fastapi-service",
            "name": "Python FastAPI Service",
            "description": "RESTful API service built with FastAPI and SQLAlchemy",
            "version": "1.5.0",
            "project_type": "web_backend",
            "technology_stack": [
                "python",
                "fastapi",
                "sqlalchemy",
                "pydantic",
                "pytest",
            ],
            "default_tags": ["backend", "python", "api", "database", "testing"],
            "required_instructions": ["backend_001", "testing_001", "core_001"],
            "parameters": {
                "service_name": {
                    "type": "string",
                    "default": "my-api-service",
                    "description": "Name of the API service",
                },
                "database_type": {
                    "type": "string",
                    "default": "postgresql",
                    "description": "Database type (postgresql, mysql, sqlite)",
                },
            },
            "metadata": {
                "category": "Backend",
                "complexity": "intermediate",
                "maintenance": "active",
            },
        }

        # Node.js API template
        nodejs_template = {
            "id": "nodejs-express-api",
            "name": "Node.js Express API",
            "description": "Express.js API with TypeScript and MongoDB",
            "version": "1.3.0",
            "project_type": "web_backend",
            "technology_stack": ["nodejs", "express", "typescript", "mongodb", "jest"],
            "default_tags": ["backend", "nodejs", "api", "mongodb", "typescript"],
            "required_instructions": ["backend_001", "testing_001"],
            "metadata": {
                "category": "Backend",
                "complexity": "beginner",
                "maintenance": "active",
            },
        }

        # Save template files
        with open(self.templates_dir / "react-frontend-app.json", "w") as f:
            json.dump(react_template, f, indent=2)

        with open(self.templates_dir / "python-fastapi-service.json", "w") as f:
            json.dump(python_template, f, indent=2)

        with open(self.templates_dir / "nodejs-express-api.json", "w") as f:
            json.dump(nodejs_template, f, indent=2)

    def test_template_completion_with_real_manager(self):
        """Test template completion with real TemplateManager."""
        self.create_realistic_template_data()

        # Initialize real template manager
        manager = TemplateManager(templates_path=self.templates_dir)
        engine = CompletionEngine()
        engine.set_services(template_manager=manager)

        # Test template ID completion
        result = engine.get_template_completions("react")
        assert "react-frontend-app" in result, "Should find React template"

        result = engine.get_template_completions("python")
        assert "python-fastapi-service" in result, "Should find Python template"

        result = engine.get_template_completions("nodejs")
        assert "nodejs-express-api" in result, "Should find Node.js template"

        # Test empty prefix returns all templates
        result = engine.get_template_completions("")
        expected_templates = {
            "react-frontend-app",
            "python-fastapi-service",
            "nodejs-express-api",
        }

        for template_id in expected_templates:
            assert template_id in result, f"Expected template '{template_id}' not found"

    def test_project_type_completion_with_real_manager(self):
        """Test project type completion with real TemplateManager."""
        self.create_realistic_template_data()

        manager = TemplateManager(templates_path=self.templates_dir)
        engine = CompletionEngine()
        engine.set_services(template_manager=manager)

        # Test project type completion
        result = engine.get_project_type_completions("web")
        assert "web_frontend" in result, "Should find web_frontend project type"
        assert "web_backend" in result, "Should find web_backend project type"

        result = engine.get_project_type_completions("web_front")
        assert "web_frontend" in result, "Should match web_frontend specifically"

        # Test empty prefix returns all project types
        result = engine.get_project_type_completions("")
        expected_types = {"web_frontend", "web_backend"}

        for project_type in expected_types:
            assert (
                project_type in result
            ), f"Expected project type '{project_type}' not found"

    def test_template_manager_error_handling_integration(self):
        """Test error handling with real template manager scenarios."""
        # Test with empty templates directory
        empty_dir = self.temp_dir / "empty"
        empty_dir.mkdir()

        manager = TemplateManager(templates_path=empty_dir)
        engine = CompletionEngine()
        engine.set_services(template_manager=manager)

        # Should handle empty template directory gracefully
        result = engine.get_template_completions("test")
        assert result == [], "Empty template directory should return empty results"

        # Test with corrupted template file
        corrupted_dir = self.temp_dir / "corrupted"
        corrupted_dir.mkdir()

        with open(corrupted_dir / "corrupted.json", "w") as f:
            f.write("invalid json content {")

        manager = TemplateManager(templates_path=corrupted_dir)
        engine = CompletionEngine()
        engine.set_services(template_manager=manager)

        # Should handle corrupted data gracefully
        result = engine.get_template_completions("test")
        assert isinstance(result, list), "Should return list even with corrupted data"

    def test_template_manager_performance_integration(self):
        """Test performance with real template manager operations."""
        self.create_realistic_template_data()

        manager = TemplateManager(templates_path=self.templates_dir)
        engine = CompletionEngine()
        engine.set_services(template_manager=manager)

        import time

        # Test multiple completion requests
        start_time = time.time()
        for _ in range(10):
            engine.get_template_completions("react")
            engine.get_project_type_completions("web")

        total_time = time.time() - start_time
        avg_time = total_time / 20  # 20 total requests

        # Should complete quickly with caching
        assert avg_time < 0.1, f"Average completion time {avg_time:.3f}s too slow"


class TestCompletionWithBothRealServices:
    """Integration tests with both real InstructionDatabase and TemplateManager."""

    def setup_method(self):
        """Set up test fixtures with both services."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.instructions_dir = self.temp_dir / "instructions"
        self.templates_dir = self.temp_dir / "templates"
        self.instructions_dir.mkdir()
        self.templates_dir.mkdir()

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_complete_test_data(self):
        """Create complete test data for both services."""
        # Create instruction data
        instructions = {
            "instructions": [
                {
                    "id": "integration_001",
                    "version": "1.0.0",
                    "tags": ["integration", "testing", "real-services"],
                    "content": "Integration test instruction",
                    "metadata": {"category": "Testing"},
                }
            ]
        }

        with open(self.instructions_dir / "integration.json", "w") as f:
            json.dump(instructions, f)

        # Create template data
        template = {
            "id": "integration-test-template",
            "name": "Integration Test Template",
            "description": "Template for integration testing",
            "version": "1.0.0",
            "project_type": "web_frontend",
            "technology_stack": ["testing"],
            "default_tags": ["integration", "testing"],
            "metadata": {"category": "Testing"},
        }

        with open(self.templates_dir / "integration-test-template.json", "w") as f:
            json.dump(template, f)

    def test_complete_integration_with_both_services(self):
        """Test complete integration with both real services."""
        self.create_complete_test_data()

        # Initialize both services
        db = InstructionDatabase(instructions_path=self.instructions_dir)
        manager = TemplateManager(templates_path=self.templates_dir)

        engine = CompletionEngine()
        engine.set_services(instruction_db=db, template_manager=manager)

        # Test tag completion
        result = engine.get_tag_completions("integration")
        assert "integration" in result, "Should find integration tag"

        # Test template completion
        result = engine.get_template_completions("integration")
        assert "integration-test-template" in result, "Should find integration template"

        # Test instruction completion
        result = engine.get_instruction_completions("integration")
        assert "integration_001" in result, "Should find integration instruction"

        # Test project type completion
        result = engine.get_project_type_completions("web")
        assert "web_frontend" in result, "Should find web_frontend project type"

    def test_cross_service_consistency(self):
        """Test consistency between services."""
        self.create_complete_test_data()

        db = InstructionDatabase(instructions_path=self.instructions_dir)
        manager = TemplateManager(templates_path=self.templates_dir)

        engine = CompletionEngine()
        engine.set_services(instruction_db=db, template_manager=manager)

        # Both services should work independently
        tag_result = engine.get_tag_completions("")
        template_result = engine.get_template_completions("")

        assert isinstance(tag_result, list), "Tag completion should return list"
        assert isinstance(
            template_result, list
        ), "Template completion should return list"

        # Results should be consistent across calls
        tag_result2 = engine.get_tag_completions("")
        template_result2 = engine.get_template_completions("")

        assert tag_result == tag_result2, "Tag results should be consistent"
        assert (
            template_result == template_result2
        ), "Template results should be consistent"

    def test_service_isolation(self):
        """Test that services are properly isolated."""
        self.create_complete_test_data()

        # Test with only instruction database
        db = InstructionDatabase(instructions_path=self.instructions_dir)
        engine1 = CompletionEngine()
        engine1.set_services(instruction_db=db)

        tag_result = engine1.get_tag_completions("integration")
        template_result = engine1.get_template_completions("integration")

        assert "integration" in tag_result, "Should find tags with instruction DB"
        assert (
            template_result == []
        ), "Should not find templates without template manager"

        # Test with only template manager
        manager = TemplateManager(templates_path=self.templates_dir)
        engine2 = CompletionEngine()
        engine2.set_services(template_manager=manager)

        tag_result = engine2.get_tag_completions("integration")
        template_result = engine2.get_template_completions("integration")

        assert tag_result == [], "Should not find tags without instruction DB"
        assert (
            "integration-test-template" in template_result
        ), "Should find templates with template manager"

    def test_concurrent_access_with_real_services(self):
        """Test concurrent access to real services."""
        self.create_complete_test_data()

        db = InstructionDatabase(instructions_path=self.instructions_dir)
        manager = TemplateManager(templates_path=self.templates_dir)

        engine = CompletionEngine()
        engine.set_services(instruction_db=db, template_manager=manager)

        import threading

        results = []
        errors = []

        def completion_worker():
            try:
                tag_result = engine.get_tag_completions("integration")
                template_result = engine.get_template_completions("integration")
                results.append((tag_result, template_result))
            except Exception as e:
                errors.append(e)

        # Start concurrent workers
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=completion_worker)
            threads.append(thread)
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join(timeout=5.0)

        # Verify results
        assert len(errors) == 0, f"Concurrent access had errors: {errors}"
        assert len(results) == 5, f"Expected 5 results, got {len(results)}"

        # All results should be identical
        first_result = results[0]
        for result in results[1:]:
            assert result == first_result, "Concurrent results should be identical"


class TestCompletionWithDefaultServices:
    """Integration tests attempting to use default AgentSpec services."""

    def test_completion_with_default_instruction_database(self):
        """Test completion with default InstructionDatabase if available."""
        try:
            # Try to initialize default instruction database
            db = InstructionDatabase()
            engine = CompletionEngine()
            engine.set_services(instruction_db=db)

            # Test basic functionality
            result = engine.get_tag_completions("test")
            assert isinstance(result, list), "Should return list even if empty"

            result = engine.get_instruction_completions("core")
            assert isinstance(result, list), "Should return list even if empty"

        except (FileNotFoundError, ImportError, Exception):
            # Expected if default data files don't exist
            pytest.skip("Default instruction database not available")

    def test_completion_with_default_template_manager(self):
        """Test completion with default TemplateManager if available."""
        try:
            # Try to initialize default template manager
            manager = TemplateManager()
            engine = CompletionEngine()
            engine.set_services(template_manager=manager)

            # Test basic functionality
            result = engine.get_template_completions("react")
            assert isinstance(result, list), "Should return list even if empty"

            result = engine.get_project_type_completions("web")
            assert isinstance(result, list), "Should return list even if empty"

        except (FileNotFoundError, ImportError, Exception):
            # Expected if default data files don't exist
            pytest.skip("Default template manager not available")

    def test_completion_engine_singleton_with_real_services(self):
        """Test completion engine singleton behavior with real services."""
        # Get singleton instance
        engine1 = get_completion_engine()
        engine2 = get_completion_engine()

        # Should be the same instance
        assert engine1 is engine2, "Should return singleton instance"

        # Test that singleton works with service configuration
        temp_dir = Path(tempfile.mkdtemp())
        try:
            instructions_dir = temp_dir / "instructions"
            instructions_dir.mkdir()

            test_data = {
                "instructions": [
                    {
                        "id": "singleton_test",
                        "version": "1.0.0",
                        "tags": ["singleton", "test"],
                        "content": "Singleton test instruction",
                        "metadata": {
                            "category": "testing",
                            "description": "Test instruction for singleton behavior",
                            "priority": 1,
                        },
                    }
                ]
            }

            with open(instructions_dir / "singleton.json", "w") as f:
                json.dump(test_data, f)

            db = InstructionDatabase(instructions_path=instructions_dir)

            # Verify the database loads the tags correctly
            all_tags = db.get_all_tags()
            assert (
                "singleton" in all_tags
            ), f"Database should contain 'singleton' tag, got: {all_tags}"

            engine1.set_services(instruction_db=db)

            # Both references should work
            result1 = engine1.get_tag_completions("singleton")
            result2 = engine2.get_tag_completions("singleton")

            assert result1 == result2, "Singleton should maintain state"
            assert (
                "singleton" in result1
            ), f"Should find singleton tag in result: {result1}"

        finally:
            import shutil

            shutil.rmtree(temp_dir, ignore_errors=True)
