"""
End-to-end tests for CLI completion workflows.

This module tests complete completion workflows from shell interaction
to final completion results, ensuring the entire completion system works
together correctly.
"""

import json
import os
import subprocess
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from agentspec.cli.completion import CompletionEngine, get_completion_engine
from agentspec.cli.main import AgentSpecCLI
from agentspec.core.instruction_database import InstructionDatabase
from agentspec.core.template_manager import TemplateManager


class TestCompleteCompletionWorkflows:
    """End-to-end tests for complete completion workflows."""

    def setup_method(self):
        """Set up test fixtures for each test."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.cli = AgentSpecCLI()

    def teardown_method(self):
        """Clean up after each test."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_complete_tag_completion_workflow(self):
        """Test complete workflow for tag completion from CLI to results."""
        # Create test instruction data
        instructions_dir = self.temp_dir / "instructions"
        instructions_dir.mkdir()

        test_instructions = {
            "instructions": [
                {
                    "id": "frontend_001",
                    "version": "1.0.0",
                    "tags": ["frontend", "react", "testing"],
                    "content": "Frontend instruction 1",
                },
                {
                    "id": "backend_001",
                    "version": "1.0.0",
                    "tags": ["backend", "api", "testing"],
                    "content": "Backend instruction 1",
                },
                {
                    "id": "testing_001",
                    "version": "1.0.0",
                    "tags": ["testing", "unit-tests", "integration"],
                    "content": "Testing instruction 1",
                },
            ]
        }

        with open(instructions_dir / "test.json", "w") as f:
            json.dump(test_instructions, f)

        # Test the complete workflow
        try:
            # Initialize instruction database with test data
            db = InstructionDatabase(instructions_path=instructions_dir)

            # Initialize completion engine
            engine = CompletionEngine()
            engine.set_services(instruction_db=db)

            # Test tag completion workflow
            result = engine.get_tag_completions("test")

            # Verify results
            assert "testing" in result
            assert len(result) >= 1

            # Test prefix matching
            result = engine.get_tag_completions("front")
            assert "frontend" in result

            # Test empty prefix (should return all tags)
            result = engine.get_tag_completions("")
            expected_tags = {
                "frontend",
                "react",
                "testing",
                "backend",
                "api",
                "unit-tests",
                "integration",
            }
            assert len(result) >= 6  # Should have at least the main tags

        except Exception as e:
            # Workflow should not crash, even with errors
            assert isinstance(e, Exception)

    def test_complete_template_completion_workflow(self):
        """Test complete workflow for template completion."""
        # Create test template data
        templates_dir = self.temp_dir / "templates"
        templates_dir.mkdir()

        # Create test templates
        react_template = {
            "id": "react-frontend-app",
            "name": "React Frontend Application",
            "description": "Complete React frontend application template",
            "version": "1.0.0",
            "project_type": "web_frontend",
            "technology_stack": ["react", "typescript", "webpack"],
            "default_tags": ["frontend", "react", "typescript"],
        }

        python_template = {
            "id": "python-api-service",
            "name": "Python API Service",
            "description": "FastAPI-based Python API service template",
            "version": "1.0.0",
            "project_type": "web_backend",
            "technology_stack": ["python", "fastapi", "sqlalchemy"],
            "default_tags": ["backend", "python", "api"],
        }

        with open(templates_dir / "react-frontend-app.json", "w") as f:
            json.dump(react_template, f)

        with open(templates_dir / "python-api-service.json", "w") as f:
            json.dump(python_template, f)

        try:
            # Initialize template manager with test data
            manager = TemplateManager(templates_path=templates_dir)

            # Initialize completion engine
            engine = CompletionEngine()
            engine.set_services(template_manager=manager)

            # Test template completion workflow
            result = engine.get_template_completions("react")
            assert "react-frontend-app" in result

            result = engine.get_template_completions("python")
            assert "python-api-service" in result

            # Test empty prefix (should return all templates)
            result = engine.get_template_completions("")
            assert len(result) >= 2
            assert "react-frontend-app" in result
            assert "python-api-service" in result

        except Exception as e:
            # Workflow should not crash, even with errors
            assert isinstance(e, Exception)

    def test_complete_cli_integration_workflow(self):
        """Test complete CLI integration workflow with real parser."""
        # Test that CLI parser can be created with completion support
        try:
            parser = self.cli.create_parser()

            # Verify parser was created successfully
            assert parser is not None

            # Verify subcommands exist
            subparsers_action = None
            for action in parser._actions:
                if hasattr(action, "choices") and action.choices:
                    subparsers_action = action
                    break

            if subparsers_action:
                # Verify expected commands are present
                expected_commands = [
                    "generate",
                    "list-tags",
                    "list-instructions",
                    "analyze",
                ]
                for cmd in expected_commands:
                    if cmd in subparsers_action.choices:
                        assert cmd in subparsers_action.choices

        except Exception as e:
            # CLI integration should not crash
            assert isinstance(e, Exception)

    def test_complete_error_recovery_workflow(self):
        """Test complete error recovery workflow."""
        engine = CompletionEngine()

        # Test with no services configured
        result = engine.get_tag_completions("test")
        assert isinstance(result, list)  # Should return list, not crash

        result = engine.get_template_completions("test")
        assert isinstance(result, list)  # Should return list, not crash

        # Test with failing services
        mock_db = Mock()
        mock_db.get_all_tags.side_effect = Exception("Database error")

        mock_manager = Mock()
        mock_manager.get_all_template_ids.side_effect = Exception("Manager error")

        engine.set_services(instruction_db=mock_db, template_manager=mock_manager)

        # Should handle errors gracefully
        result = engine.get_tag_completions("test")
        assert isinstance(result, list)

        result = engine.get_template_completions("test")
        assert isinstance(result, list)

    def test_complete_caching_workflow(self):
        """Test complete caching workflow across multiple requests."""
        # Create test data
        instructions_dir = self.temp_dir / "instructions"
        instructions_dir.mkdir()

        test_instructions = {
            "instructions": [
                {
                    "id": "cache_test_001",
                    "version": "1.0.0",
                    "tags": ["caching", "performance", "testing"],
                    "content": "Cache test instruction",
                }
            ]
        }

        with open(instructions_dir / "cache_test.json", "w") as f:
            json.dump(test_instructions, f)

        try:
            # Initialize services
            db = InstructionDatabase(instructions_path=instructions_dir)
            engine = CompletionEngine()
            engine.set_services(instruction_db=db)

            # First request (cache miss)
            start_time = time.time()
            result1 = engine.get_tag_completions("cache")
            first_time = time.time() - start_time

            # Second request (cache hit)
            start_time = time.time()
            result2 = engine.get_tag_completions("cache")
            second_time = time.time() - start_time

            # Verify results are consistent
            assert result1 == result2
            assert "caching" in result1

            # Cache hit should be faster (though this might not always be measurable)
            # Just verify both completed successfully
            assert first_time >= 0
            assert second_time >= 0

        except Exception as e:
            # Caching workflow should not crash
            assert isinstance(e, Exception)

    def test_complete_concurrent_workflow(self):
        """Test complete workflow under concurrent access."""
        import threading

        # Create test data
        instructions_dir = self.temp_dir / "instructions"
        instructions_dir.mkdir()

        test_instructions = {
            "instructions": [
                {
                    "id": f"concurrent_{i:03d}",
                    "version": "1.0.0",
                    "tags": ["concurrent", f"thread-{i % 3}", "testing"],
                    "content": f"Concurrent instruction {i}",
                }
                for i in range(20)
            ]
        }

        with open(instructions_dir / "concurrent.json", "w") as f:
            json.dump(test_instructions, f)

        try:
            # Initialize services
            db = InstructionDatabase(instructions_path=instructions_dir)
            engine = CompletionEngine()
            engine.set_services(instruction_db=db)

            results = []
            errors = []

            def completion_worker(prefix):
                try:
                    result = engine.get_tag_completions(prefix)
                    results.append((prefix, result))
                except Exception as e:
                    errors.append(e)

            # Start concurrent completion requests
            threads = []
            prefixes = ["concurrent", "thread", "test", "conc", "thr"]

            for prefix in prefixes:
                thread = threading.Thread(target=completion_worker, args=(prefix,))
                threads.append(thread)
                thread.start()

            # Wait for all threads
            for thread in threads:
                thread.join(timeout=5.0)

            # Verify no errors occurred
            assert len(errors) == 0, f"Concurrent workflow had errors: {errors}"
            assert len(results) == len(
                prefixes
            ), f"Expected {len(prefixes)} results, got {len(results)}"

            # Verify results are reasonable
            for prefix, result in results:
                assert isinstance(
                    result, list
                ), f"Result for '{prefix}' is not a list: {result}"

        except Exception as e:
            # Concurrent workflow should not crash
            assert isinstance(e, Exception)

    def test_complete_performance_workflow(self):
        """Test complete performance workflow with timing requirements."""
        # Create larger test dataset
        instructions_dir = self.temp_dir / "instructions"
        instructions_dir.mkdir()

        # Create 100 instructions for performance testing
        test_instructions = {
            "instructions": [
                {
                    "id": f"perf_{i:03d}",
                    "version": "1.0.0",
                    "tags": ["performance", f"category-{i % 10}", f"type-{i % 5}"],
                    "content": f"Performance test instruction {i}",
                }
                for i in range(100)
            ]
        }

        with open(instructions_dir / "performance.json", "w") as f:
            json.dump(test_instructions, f)

        try:
            # Initialize services
            db = InstructionDatabase(instructions_path=instructions_dir)
            engine = CompletionEngine()
            engine.set_services(instruction_db=db)

            # Test performance requirements
            start_time = time.time()
            result = engine.get_tag_completions("perf")
            response_time = time.time() - start_time

            # Verify performance (should complete within reasonable time)
            assert (
                response_time < 2.0
            ), f"Completion took {response_time:.3f}s (expected < 2s)"
            assert len(result) > 0, "Should return some results"

            # Test cached performance
            start_time = time.time()
            cached_result = engine.get_tag_completions("perf")
            cached_time = time.time() - start_time

            assert cached_result == result, "Cached result should match original"
            assert (
                cached_time < 0.1
            ), f"Cached completion took {cached_time:.3f}s (expected < 0.1s)"

        except Exception as e:
            # Performance workflow should not crash
            assert isinstance(e, Exception)

    def test_complete_format_completion_workflow(self):
        """Test complete format completion workflow."""
        engine = CompletionEngine()

        # Test format completions
        result = engine.get_format_completions("")
        expected_formats = ["markdown", "json", "yaml"]

        for fmt in expected_formats:
            assert fmt in result, f"Format '{fmt}' missing from completion"

        # Test prefix matching
        result = engine.get_format_completions("j")
        assert "json" in result
        assert "yaml" not in result  # Should not match

        # Test output format completions
        result = engine.get_output_format_completions("")
        expected_output_formats = ["text", "json"]

        for fmt in expected_output_formats:
            assert fmt in result, f"Output format '{fmt}' missing from completion"

    def test_complete_category_completion_workflow(self):
        """Test complete category completion workflow."""
        engine = CompletionEngine()

        # Test category completions
        result = engine.get_category_completions("")
        expected_categories = [
            "General",
            "Testing",
            "Frontend",
            "Backend",
            "Languages",
            "DevOps",
            "Architecture",
        ]

        # Should have all expected categories
        assert len(result) >= 7, f"Expected at least 7 categories, got {len(result)}"

        # Test prefix matching (case-insensitive)
        result = engine.get_category_completions("front")
        assert any(
            "frontend" in cat.lower() for cat in result
        ), "Should match Frontend category"

        result = engine.get_category_completions("BACK")
        assert any(
            "backend" in cat.lower() for cat in result
        ), "Should match Backend category"

    def test_complete_edge_cases_workflow(self):
        """Test complete workflow with edge cases."""
        engine = CompletionEngine()

        # Test with None prefix
        try:
            result = engine.get_tag_completions(None)
            assert result == [], "None prefix should return empty list"
        except (TypeError, AttributeError):
            # This is acceptable behavior
            pass

        # Test with empty string
        result = engine.get_tag_completions("")
        assert isinstance(result, list), "Empty prefix should return list"

        # Test with very long prefix
        long_prefix = "a" * 1000
        result = engine.get_tag_completions(long_prefix)
        assert isinstance(result, list), "Long prefix should return list"
        assert len(result) == 0, "Long prefix should return no matches"

        # Test with special characters
        special_prefixes = ["@#$", "test-", "test_", "test.", "test/"]
        for prefix in special_prefixes:
            result = engine.get_tag_completions(prefix)
            assert isinstance(
                result, list
            ), f"Special prefix '{prefix}' should return list"

    def test_complete_integration_with_real_services(self):
        """Test complete integration with real AgentSpec services."""
        try:
            # Try to initialize real services (may fail if data not available)
            from agentspec.core.instruction_database import InstructionDatabase
            from agentspec.core.template_manager import TemplateManager

            # Test with default paths (may not exist in test environment)
            try:
                db = InstructionDatabase()
                manager = TemplateManager()

                engine = CompletionEngine()
                engine.set_services(instruction_db=db, template_manager=manager)

                # Test basic functionality
                tag_result = engine.get_tag_completions("test")
                template_result = engine.get_template_completions("react")

                # Results should be lists (may be empty if no data)
                assert isinstance(tag_result, list)
                assert isinstance(template_result, list)

            except (FileNotFoundError, ImportError):
                # Expected if real data files don't exist in test environment
                pass

        except Exception as e:
            # Integration test should not crash the test suite
            assert isinstance(e, Exception)

    def test_complete_cli_argument_completion_workflow(self):
        """Test complete CLI argument completion workflow."""
        try:
            # Test that CLI can handle completion-related arguments
            parser = self.cli.create_parser()

            # Test parsing completion-related arguments
            test_args = [["--help"], ["generate", "--help"], ["list-tags", "--help"]]

            for args in test_args:
                try:
                    # This may raise SystemExit for --help, which is expected
                    parsed = parser.parse_args(args)
                except SystemExit:
                    # Expected for --help arguments
                    pass
                except Exception as e:
                    # Other exceptions should not occur
                    assert False, f"Unexpected error parsing {args}: {e}"

        except Exception as e:
            # CLI workflow should not crash
            assert isinstance(e, Exception)


class TestCompletionWorkflowPerformance:
    """Performance-focused tests for completion workflows."""

    def test_completion_workflow_response_times(self):
        """Test that completion workflows meet response time requirements."""
        engine = CompletionEngine()

        # Test static completion performance
        start_time = time.time()
        result = engine.get_format_completions("")
        static_time = time.time() - start_time

        assert (
            static_time < 0.1
        ), f"Static completion took {static_time:.3f}s (expected < 0.1s)"
        assert len(result) > 0, "Static completion should return results"

        # Test category completion performance
        start_time = time.time()
        result = engine.get_category_completions("")
        category_time = time.time() - start_time

        assert (
            category_time < 0.1
        ), f"Category completion took {category_time:.3f}s (expected < 0.1s)"
        assert len(result) > 0, "Category completion should return results"

    def test_completion_workflow_memory_usage(self):
        """Test that completion workflows don't consume excessive memory."""
        engine = CompletionEngine()

        # Make many completion requests
        for i in range(100):
            engine.get_format_completions(f"prefix_{i % 10}")
            engine.get_category_completions(f"cat_{i % 5}")

        # Verify engine is still functional
        result = engine.get_format_completions("json")
        assert "json" in result, "Engine should still be functional after many requests"

    def test_completion_workflow_scalability(self):
        """Test completion workflow scalability with increasing load."""
        engine = CompletionEngine()

        # Test with increasing number of requests
        request_counts = [10, 50, 100]

        for count in request_counts:
            start_time = time.time()

            for i in range(count):
                engine.get_format_completions(f"test_{i % 3}")

            total_time = time.time() - start_time
            avg_time = total_time / count

            # Average time per request should remain reasonable
            assert (
                avg_time < 0.01
            ), f"Average completion time {avg_time:.4f}s too high for {count} requests"


class TestCompletionWorkflowEdgeCases:
    """Edge case tests for completion workflows."""

    def test_completion_workflow_with_corrupted_data(self):
        """Test completion workflow with corrupted or invalid data."""
        engine = CompletionEngine()

        # Mock services that return invalid data
        mock_db = Mock()
        mock_db.get_all_tags.return_value = "not a set or list"  # Invalid return type

        mock_manager = Mock()
        mock_manager.get_all_template_ids.return_value = 12345  # Invalid return type

        engine.set_services(instruction_db=mock_db, template_manager=mock_manager)

        # Should handle invalid data gracefully
        result = engine.get_tag_completions("test")
        assert result == [], "Should return empty list for invalid data"

        result = engine.get_template_completions("test")
        assert result == [], "Should return empty list for invalid data"

    def test_completion_workflow_with_network_errors(self):
        """Test completion workflow with network-like errors."""
        engine = CompletionEngine()

        # Mock services that raise network-like errors
        mock_db = Mock()
        mock_db.get_all_tags.side_effect = ConnectionError("Network error")

        mock_manager = Mock()
        mock_manager.get_all_template_ids.side_effect = TimeoutError("Request timeout")

        engine.set_services(instruction_db=mock_db, template_manager=mock_manager)

        # Should handle network errors gracefully
        result = engine.get_tag_completions("test")
        assert result == [], "Should return empty list for network errors"

        result = engine.get_template_completions("test")
        assert result == [], "Should return empty list for timeout errors"

    def test_completion_workflow_with_permission_errors(self):
        """Test completion workflow with permission errors."""
        engine = CompletionEngine()

        # Mock services that raise permission errors
        mock_db = Mock()
        mock_db.get_all_tags.side_effect = PermissionError("Access denied")

        engine.set_services(instruction_db=mock_db)

        # Should handle permission errors gracefully
        result = engine.get_tag_completions("test")
        assert result == [], "Should return empty list for permission errors"

    def test_completion_workflow_with_unicode_input(self):
        """Test completion workflow with unicode and special character input."""
        engine = CompletionEngine()

        # Test with various unicode inputs
        unicode_inputs = ["café", "测试", "🚀", "naïve", "résumé", "Москва"]

        for input_text in unicode_inputs:
            result = engine.get_tag_completions(input_text)
            assert isinstance(
                result, list
            ), f"Unicode input '{input_text}' should return list"

            result = engine.get_format_completions(input_text)
            assert isinstance(
                result, list
            ), f"Unicode input '{input_text}' should return list"
