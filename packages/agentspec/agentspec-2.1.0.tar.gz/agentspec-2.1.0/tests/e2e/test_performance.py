"""
Performance and benchmarking tests for AgentSpec.
"""

import json
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from agentspec.core.context_detector import ContextDetector
from agentspec.core.instruction_database import InstructionDatabase
from agentspec.core.spec_generator import SpecConfig, SpecGenerator
from agentspec.core.template_manager import TemplateManager


@pytest.mark.slow
@pytest.mark.timeout(300)  # 5 minute timeout for performance tests
class TestPerformance:
    """Performance tests for AgentSpec components."""

    @pytest.mark.timeout(120)  # 2 minute timeout
    def test_large_instruction_database_performance(self, temp_dir):
        """Test performance with large instruction database."""
        instructions_dir = temp_dir / "instructions"
        instructions_dir.mkdir()

        # Create large instruction dataset
        categories = ["frontend", "backend", "testing", "security", "performance"]
        instructions_per_category = 200

        for category in categories:
            category_instructions = {"instructions": []}

            for i in range(instructions_per_category):
                instruction = {
                    "id": f"{category}_instruction_{i}",
                    "version": "1.0.0",
                    "tags": [category, f"subcategory-{i % 10}", f"tag-{i % 5}"],
                    "content": f"Detailed instruction content for {category} instruction {i}. "
                    * 20,
                    "conditions": (
                        [
                            {
                                "type": "project_type",
                                "value": (
                                    "web_frontend" if i % 2 == 0 else "web_backend"
                                ),
                                "operator": "equals",
                            }
                        ]
                        if i % 3 == 0
                        else None
                    ),
                    "parameters": (
                        [
                            {
                                "name": f"param_{i}",
                                "type": "string",
                                "default": f"default_value_{i}",
                                "description": f"Parameter {i} description",
                            }
                        ]
                        if i % 4 == 0
                        else None
                    ),
                    "dependencies": (
                        [f"{category}_instruction_{i-1}"]
                        if i > 0 and i % 5 == 0
                        else None
                    ),
                    "metadata": {
                        "category": category,
                        "priority": (i % 10) + 1,
                        "author": f"author_{i % 3}",
                        "created_at": "2023-01-01T00:00:00Z",
                        "updated_at": "2023-06-01T00:00:00Z",
                    },
                }
                category_instructions["instructions"].append(instruction)

            # Save category file
            with open(instructions_dir / f"{category}.json", "w") as f:
                json.dump(category_instructions, f)

        # Test loading performance
        start_time = time.time()
        db = InstructionDatabase(instructions_path=instructions_dir)
        instructions = db.load_instructions()
        load_time = time.time() - start_time

        # Verify all instructions loaded
        expected_count = len(categories) * instructions_per_category
        assert len(instructions) == expected_count

        # Performance benchmark: should load 1000 instructions in < 5 seconds
        assert (
            load_time < 5.0
        ), f"Loading {expected_count} instructions took {load_time:.2f}s (expected < 5s)"

        # Test query performance
        start_time = time.time()
        frontend_instructions = db.get_by_tags(["frontend"])
        query_time = time.time() - start_time

        # Should find all frontend instructions
        assert len(frontend_instructions) == instructions_per_category

        # Query should be fast (< 1 second)
        assert query_time < 1.0, f"Query took {query_time:.2f}s (expected < 1s)"

        # Test complex query performance
        start_time = time.time()
        multi_tag_instructions = db.get_by_tags(["frontend", "testing", "security"])
        complex_query_time = time.time() - start_time

        # Should find instructions from multiple categories
        assert len(multi_tag_instructions) == instructions_per_category * 3

        # Complex query should still be fast (< 2 seconds)
        assert (
            complex_query_time < 2.0
        ), f"Complex query took {complex_query_time:.2f}s (expected < 2s)"

        # Test conflict detection performance
        start_time = time.time()
        conflicts = db.detect_conflicts()
        conflict_time = time.time() - start_time

        # Conflict detection should complete in reasonable time (< 10 seconds)
        assert (
            conflict_time < 10.0
        ), f"Conflict detection took {conflict_time:.2f}s (expected < 10s)"

    @pytest.mark.timeout(120)  # 2 minute timeout
    def test_large_template_database_performance(self, temp_dir):
        """Test performance with large template database."""
        templates_dir = temp_dir / "templates"
        templates_dir.mkdir()

        # Create large template dataset
        project_types = [
            "web_frontend",
            "web_backend",
            "mobile-app",
            "desktop-app",
            "cli-tool",
        ]
        templates_per_type = 50

        for project_type in project_types:
            for i in range(templates_per_type):
                template = {
                    "id": f"{project_type}_template_{i}",
                    "name": f"{project_type.title()} Template {i}",
                    "description": f"Template {i} for {project_type} projects with comprehensive setup.",
                    "version": f"1.{i}.0",
                    "project_type": project_type,
                    "technology_stack": [f"tech_{j}" for j in range(i % 5 + 1)],
                    "default_tags": [
                        project_type,
                        f"template_{i}",
                        f"category-{i % 3}",
                    ],
                    "required_instructions": [
                        f"instruction_{j}" for j in range(i % 10 + 1)
                    ],
                    "optional_instructions": [f"optional_{j}" for j in range(i % 5)],
                    "parameters": {
                        f"param_{j}": {
                            "type": "string",
                            "default": f"default_{j}",
                            "description": f"Parameter {j} description",
                        }
                        for j in range(i % 8 + 1)
                    },
                    "conditions": [
                        {
                            "type": "file_exists",
                            "value": f"config_{j}.json",
                            "operator": "exists",
                            "weight": 0.8 - (j * 0.1),
                        }
                        for j in range(i % 3 + 1)
                    ],
                    "metadata": {
                        "category": project_type,
                        "complexity": ["beginner", "intermediate", "advanced"][i % 3],
                        "author": f"author-{i % 5}",
                        "created_at": "2023-01-01T00:00:00Z",
                        "tags": [f"meta-tag-{j}" for j in range(i % 4)],
                    },
                }

                # Save individual template file
                with open(
                    templates_dir / f"{project_type}_template_{i}.json", "w"
                ) as f:
                    json.dump(template, f)

        # Test loading performance
        start_time = time.time()
        manager = TemplateManager(templates_path=templates_dir)
        templates = manager.load_templates()
        load_time = time.time() - start_time

        # Verify all templates loaded
        expected_count = len(project_types) * templates_per_type
        assert len(templates) == expected_count

        # Performance benchmark: should load 250 templates in < 3 seconds
        assert (
            load_time < 3.0
        ), f"Loading {expected_count} templates took {load_time:.2f}s (expected < 3s)"

        # Test query performance
        start_time = time.time()
        web_templates = manager.get_templates_by_project_type("web_frontend")
        query_time = time.time() - start_time

        # Should find all web frontend templates
        assert len(web_templates) == templates_per_type

        # Query should be fast (< 0.5 seconds)
        assert (
            query_time < 0.5
        ), f"Template query took {query_time:.2f}s (expected < 0.5s)"

        # Test recommendation performance
        project_context = {
            "project_type": "web_frontend",
            "technology_stack": ["tech_1", "tech_2"],
            "files": ["config_1.json", "package.json"],
            "dependencies": ["react", "typescript"],
        }

        start_time = time.time()
        recommendations = manager.get_recommended_templates(project_context)
        recommendation_time = time.time() - start_time

        # Should get recommendations
        assert len(recommendations) > 0

        # Recommendation should be fast (< 2 seconds)
        assert (
            recommendation_time < 2.0
        ), f"Template recommendation took {recommendation_time:.2f}s (expected < 2s)"

    @pytest.mark.timeout(180)  # 3 minute timeout
    def test_project_analysis_performance(self, temp_dir):
        """Test performance of project analysis with large projects."""
        # Create large project structure
        project_dir = temp_dir / "large_project"
        project_dir.mkdir()

        # Create deep directory structure
        current_dir = project_dir
        for depth in range(10):  # 10 levels deep
            current_dir = current_dir / f"level_{depth}"
            current_dir.mkdir()

            # Create files at each level
            for i in range(20):  # 20 files per level
                file_extensions = [
                    ".js",
                    ".ts",
                    ".jsx",
                    ".tsx",
                    ".py",
                    ".java",
                    ".go",
                    ".rs",
                ]
                ext = file_extensions[i % len(file_extensions)]

                (current_dir / f"file_{i}{ext}").write_text(
                    f"""
// File {i} at depth {depth}
function example_{i}() {{
    console.log("Example function {i} at depth {depth}");
    return "result_{i}";
}}

class Example_{i} {{
    constructor() {{
        this.value = {i};
        this.depth = {depth};
    }}

    method_{i}() {{
        return this.value * this.depth;
    }}
}}

export default Example_{i};
                """
                )

        # Create package.json with many dependencies
        package_json = {
            "name": "large-project",
            "version": "1.0.0",
            "dependencies": {f"package_{i}": f"^{i % 5 + 1}.0.0" for i in range(100)},
            "devDependencies": {
                f"dev_package_{i}": f"^{i % 3 + 1}.0.0" for i in range(50)
            },
        }

        with open(project_dir / "package.json", "w") as f:
            json.dump(package_json, f, indent=2)

        # Create other config files
        config_files = [
            ("tsconfig.json", {"compilerOptions": {"target": "es5"}}),
            ("webpack.config.js", "module.exports = {};"),
            (".eslintrc.json", {"extends": ["eslint:recommended"]}),
            ("jest.config.js", "module.exports = {};"),
            ("babel.config.js", "module.exports = {};"),
        ]

        for filename, content in config_files:
            if isinstance(content, dict):
                with open(project_dir / filename, "w") as f:
                    json.dump(content, f)
            else:
                (project_dir / filename).write_text(content)

        # Test analysis performance
        detector = ContextDetector()

        start_time = time.time()
        context = detector.analyze_project(str(project_dir))
        analysis_time = time.time() - start_time

        # Verify analysis results (handle macOS path resolution)
        assert context.project_path.endswith("large_project")
        assert context.project_type.value != "unknown"
        assert len(context.technology_stack.languages) > 0
        assert context.file_structure.total_files > 200  # Should detect many files

        # Performance benchmark: should analyze large project in < 15 seconds
        assert (
            analysis_time < 15.0
        ), f"Project analysis took {analysis_time:.2f}s (expected < 15s)"

        # Test suggestion performance
        start_time = time.time()
        suggestions = detector.suggest_instructions(context)
        suggestion_time = time.time() - start_time

        # Should get suggestions
        assert len(suggestions) > 0

        # Suggestion should be fast (< 5 seconds)
        assert (
            suggestion_time < 5.0
        ), f"Instruction suggestion took {suggestion_time:.2f}s (expected < 5s)"

    def test_spec_generation_performance(self, temp_dir):
        """Test performance of specification generation with large datasets."""
        # Setup large instruction database
        instructions_dir = temp_dir / "instructions"
        instructions_dir.mkdir()

        # Create 500 instructions
        large_instructions = {"instructions": []}
        for i in range(500):
            instruction = {
                "id": f"perf_instruction_{i}",
                "version": "1.0.0",
                "tags": [f"tag-{i % 20}", f"category-{i % 10}", f"type-{i % 5}"],
                "content": f"Performance test instruction {i} with detailed content. "
                * 15,
                "metadata": {
                    "category": f"category-{i % 10}",
                    "priority": (i % 10) + 1,
                },
            }
            large_instructions["instructions"].append(instruction)

        with open(instructions_dir / "performance.json", "w") as f:
            json.dump(large_instructions, f)

        # Setup components
        instruction_db = InstructionDatabase(instructions_path=instructions_dir)
        spec_generator = SpecGenerator(instruction_db=instruction_db)

        # Test spec generation performance with many tags
        many_tags = [f"tag-{i}" for i in range(20)]  # All tag categories

        start_time = time.time()
        config = SpecConfig(selected_tags=many_tags)
        spec = spec_generator.generate_spec(config)
        generation_time = time.time() - start_time

        # Verify spec generation
        assert spec.content
        assert len(spec.instructions_used) > 100  # Should include many instructions

        # Performance benchmark: should generate spec in < 10 seconds
        assert (
            generation_time < 10.0
        ), f"Spec generation took {generation_time:.2f}s (expected < 10s)"

        # Test different output formats
        formats = ["markdown", "json"]

        for output_format in formats:
            start_time = time.time()
            config = SpecConfig(
                selected_tags=many_tags[:10], output_format=output_format
            )
            spec = spec_generator.generate_spec(config)
            format_time = time.time() - start_time

            # Each format should be fast (< 5 seconds)
            assert (
                format_time < 5.0
            ), f"{output_format} generation took {format_time:.2f}s (expected < 5s)"

            # Verify format-specific content
            if output_format == "json":
                # Should be valid JSON
                json.loads(spec.content)
            else:
                # Should contain markdown headers
                assert "# AgentSpec" in spec.content

    def test_concurrent_operations_performance(self, temp_dir):
        """Test performance under concurrent operations."""
        import concurrent.futures
        import threading

        # Setup test data
        instructions_dir = temp_dir / "instructions"
        instructions_dir.mkdir()

        # Create moderate-sized instruction set
        instructions_data = {"instructions": []}
        for i in range(100):
            instruction = {
                "id": f"concurrent_instruction_{i}",
                "version": "1.0.0",
                "tags": [f"tag-{i % 10}", "concurrent"],
                "content": f"Concurrent test instruction {i}.",
                "metadata": {"category": f"category-{i % 5}"},
            }
            instructions_data["instructions"].append(instruction)

        with open(instructions_dir / "concurrent.json", "w") as f:
            json.dump(instructions_data, f)

        # Test concurrent loading
        def load_instructions():
            db = InstructionDatabase(instructions_path=instructions_dir)
            return db.load_instructions()

        start_time = time.time()

        # Run 10 concurrent loading operations
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(load_instructions) for _ in range(10)]
            results = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]

        concurrent_time = time.time() - start_time

        # All operations should succeed
        assert len(results) == 10
        assert all(len(result) == 100 for result in results)

        # Concurrent operations should complete in reasonable time (< 20 seconds)
        assert (
            concurrent_time < 20.0
        ), f"Concurrent operations took {concurrent_time:.2f}s (expected < 20s)"

        # Test concurrent spec generation
        def generate_spec(tags):
            db = InstructionDatabase(instructions_path=instructions_dir)
            generator = SpecGenerator(instruction_db=db)
            config = SpecConfig(selected_tags=tags)
            return generator.generate_spec(config)

        tag_sets = [[f"tag_{i}"] for i in range(5)]

        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(generate_spec, tags) for tags in tag_sets]
            specs = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]

        concurrent_gen_time = time.time() - start_time

        # All spec generations should succeed
        assert len(specs) == 5
        assert all(spec.content for spec in specs)

        # Concurrent spec generation should be efficient (< 15 seconds)
        assert (
            concurrent_gen_time < 15.0
        ), f"Concurrent spec generation took {concurrent_gen_time:.2f}s (expected < 15s)"

    @pytest.mark.timeout(180)  # 3 minute timeout
    def test_memory_usage_performance(self, temp_dir):
        """Test memory usage with large datasets."""
        import os

        import psutil

        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Create very large instruction database
        instructions_dir = temp_dir / "instructions"
        instructions_dir.mkdir()

        # Create 1000 instructions with large content
        large_instructions = {"instructions": []}
        for i in range(1000):
            instruction = {
                "id": f"memory_instruction_{i}",
                "version": "1.0.0",
                "tags": [f"tag-{i % 50}", f"category-{i % 20}"],
                "content": f"Large instruction content {i}. " * 100,  # Large content
                "metadata": {
                    "category": f"category-{i % 20}",
                    "priority": (i % 10) + 1,
                    "description": f"Detailed description for instruction {i}. " * 20,
                },
            }
            large_instructions["instructions"].append(instruction)

        with open(instructions_dir / "memory_test.json", "w") as f:
            json.dump(large_instructions, f)

        # Load instructions and measure memory
        db = InstructionDatabase(instructions_path=instructions_dir)
        instructions = db.load_instructions()

        after_load_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = after_load_memory - initial_memory

        # Verify instructions loaded
        assert len(instructions) == 1000

        # Memory usage should be reasonable (< 500MB increase)
        assert (
            memory_increase < 500
        ), f"Memory usage increased by {memory_increase:.1f}MB (expected < 500MB)"

        # Perform operations and check memory doesn't grow excessively
        for _ in range(10):
            # Multiple queries shouldn't significantly increase memory
            db.get_by_tags([f"tag_{i}" for i in range(10)])

        after_queries_memory = process.memory_info().rss / 1024 / 1024  # MB
        query_memory_increase = after_queries_memory - after_load_memory

        # Memory shouldn't grow much from queries (< 50MB)
        assert (
            query_memory_increase < 50
        ), f"Query memory increased by {query_memory_increase:.1f}MB (expected < 50MB)"
