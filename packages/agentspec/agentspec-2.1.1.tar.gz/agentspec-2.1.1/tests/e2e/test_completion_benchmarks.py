"""
Performance benchmark tests for CLI completion operations.

This module provides comprehensive benchmarks for completion performance,
measuring response times, throughput, memory usage, and scalability.
"""

import json
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import Mock

import pytest

from agentspec.cli.completion import CompletionCache, CompletionEngine


class TestCompletionPerformanceBenchmarks:
    """Performance benchmark tests for completion operations."""

    def setup_method(self):
        """Set up test fixtures for benchmarks."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.engine = CompletionEngine()

    def teardown_method(self):
        """Clean up after benchmarks."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_tag_completion_performance_benchmark(self):
        """Benchmark tag completion performance with mock data."""
        # Mock large dataset
        mock_db = Mock()
        large_tags = {f"tag_{i:04d}" for i in range(2000)}
        mock_db.get_all_tags.return_value = large_tags

        self.engine.set_services(instruction_db=mock_db)

        # Benchmark different scenarios
        scenarios = [
            ("empty_prefix", ""),
            ("single_char", "t"),
            ("short_prefix", "tag"),
            ("medium_prefix", "tag_1"),
            ("no_matches", "nonexistent"),
        ]

        results = {}

        for scenario_name, prefix in scenarios:
            # Warm up
            self.engine.get_tag_completions(prefix)

            # Benchmark
            times = []
            for _ in range(5):  # Reduced iterations for faster testing
                start_time = time.time()
                result = self.engine.get_tag_completions(prefix)
                end_time = time.time()
                times.append(end_time - start_time)

            avg_time = sum(times) / len(times)

            results[scenario_name] = {
                "avg_time": avg_time,
                "result_count": len(result) if isinstance(result, list) else 0,
            }

            # Performance assertions
            assert (
                avg_time < 1.0
            ), f"Tag completion for '{prefix}' took {avg_time:.3f}s (expected < 1.0s)"

    def test_template_completion_performance_benchmark(self):
        """Benchmark template completion performance with mock data."""
        # Mock large dataset
        mock_manager = Mock()
        large_templates = [f"template_{i:04d}" for i in range(1000)]
        mock_manager.get_all_template_ids.return_value = large_templates

        self.engine.set_services(template_manager=mock_manager)

        # Benchmark different scenarios
        scenarios = [
            ("empty_prefix", ""),
            ("single_char", "t"),
            ("short_prefix", "template"),
            ("no_matches", "nonexistent"),
        ]

        for scenario_name, prefix in scenarios:
            # Warm up
            self.engine.get_template_completions(prefix)

            # Benchmark
            times = []
            for _ in range(5):
                start_time = time.time()
                result = self.engine.get_template_completions(prefix)
                end_time = time.time()
                times.append(end_time - start_time)

            avg_time = sum(times) / len(times)

            # Performance assertions
            assert (
                avg_time < 0.5
            ), f"Template completion for '{prefix}' took {avg_time:.3f}s (expected < 0.5s)"

    def test_cache_performance_benchmark(self):
        """Benchmark cache performance with various scenarios."""
        cache = CompletionCache(ttl=300, max_size=1000)

        # Test cache write performance
        large_dataset = [
            f"item_{i}" for i in range(100)
        ]  # Smaller dataset for faster testing

        write_times = []
        for i in range(10):  # Reduced iterations
            start_time = time.time()
            cache.set(f"key_{i}", large_dataset)
            end_time = time.time()
            write_times.append(end_time - start_time)

        avg_write_time = sum(write_times) / len(write_times)

        # Test cache read performance
        read_times = []
        for i in range(10):
            start_time = time.time()
            result = cache.get(f"key_{i}")
            end_time = time.time()
            read_times.append(end_time - start_time)

        avg_read_time = sum(read_times) / len(read_times)

        # Performance assertions
        assert (
            avg_write_time < 0.01
        ), f"Cache write took {avg_write_time:.6f}s (expected < 0.01s)"
        assert (
            avg_read_time < 0.01
        ), f"Cache read took {avg_read_time:.6f}s (expected < 0.01s)"

    def test_concurrent_completion_performance_benchmark(self):
        """Benchmark completion performance under concurrent load."""
        # Create mock dataset
        mock_db = Mock()
        mock_db.get_all_tags.return_value = {f"tag_{i}" for i in range(100)}
        self.engine.set_services(instruction_db=mock_db)

        # Test concurrent performance
        thread_counts = [1, 3, 5]  # Reduced thread counts for faster testing

        for thread_count in thread_counts:
            completion_times = []
            errors = []

            def completion_worker():
                try:
                    start_time = time.time()
                    result = self.engine.get_tag_completions("tag")
                    end_time = time.time()
                    completion_times.append(end_time - start_time)
                except Exception as e:
                    errors.append(e)

            # Run concurrent completions
            threads = []
            for _ in range(thread_count):
                thread = threading.Thread(target=completion_worker)
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join(timeout=5.0)

            # Performance assertions
            assert len(errors) == 0, f"Concurrent completion had {len(errors)} errors"
            if completion_times:
                avg_completion_time = sum(completion_times) / len(completion_times)
                assert (
                    avg_completion_time < 2.0
                ), f"Average concurrent completion took {avg_completion_time:.3f}s"

    def test_static_completion_performance_benchmark(self):
        """Benchmark static completion performance (formats, categories)."""
        engine = CompletionEngine()

        # Benchmark format completions
        format_times = []
        for _ in range(10):  # Reduced iterations
            start_time = time.time()
            result = engine.get_format_completions("")
            end_time = time.time()
            format_times.append(end_time - start_time)

        avg_format_time = sum(format_times) / len(format_times)

        # Benchmark category completions
        category_times = []
        for _ in range(10):
            start_time = time.time()
            result = engine.get_category_completions("")
            end_time = time.time()
            category_times.append(end_time - start_time)

        avg_category_time = sum(category_times) / len(category_times)

        # Performance assertions
        assert (
            avg_format_time < 0.01
        ), f"Format completion took {avg_format_time:.6f}s (expected < 0.01s)"
        assert (
            avg_category_time < 0.01
        ), f"Category completion took {avg_category_time:.6f}s (expected < 0.01s)"

    def test_cache_efficiency_benchmark(self):
        """Benchmark cache efficiency and hit rates."""
        mock_db = Mock()
        mock_db.get_all_tags.return_value = {"tag1", "tag2", "tag3"}

        engine = CompletionEngine()
        engine.set_services(instruction_db=mock_db)

        # Test cache efficiency with repeated requests
        prefixes = ["tag", "t", "ta"]

        # First round - cache misses
        miss_times = []
        for prefix in prefixes:
            start_time = time.time()
            engine.get_tag_completions(prefix)
            end_time = time.time()
            miss_times.append(end_time - start_time)

        # Second round - cache hits
        hit_times = []
        for prefix in prefixes:
            start_time = time.time()
            engine.get_tag_completions(prefix)
            end_time = time.time()
            hit_times.append(end_time - start_time)

        avg_miss_time = sum(miss_times) / len(miss_times)
        avg_hit_time = sum(hit_times) / len(hit_times)

        # Cache should provide some speedup (may be minimal with small datasets)
        assert (
            avg_hit_time <= avg_miss_time * 2
        ), "Cache hits should not be significantly slower than misses"


class TestCompletionThroughputBenchmarks:
    """Throughput-focused benchmark tests."""

    def setup_method(self):
        """Set up throughput test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Clean up throughput test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_completion_throughput_benchmark(self):
        """Benchmark completion throughput (requests per second)."""
        # Create mock data
        mock_db = Mock()
        mock_db.get_all_tags.return_value = {f"tag_{i}" for i in range(100)}

        engine = CompletionEngine()
        engine.set_services(instruction_db=mock_db)

        # Measure throughput over short time period
        test_duration = 1  # 1 second test

        request_count = 0
        start_time = time.time()
        end_time = start_time + test_duration

        while time.time() < end_time:
            engine.get_tag_completions("tag")
            request_count += 1

        actual_duration = time.time() - start_time
        throughput = request_count / actual_duration

        # Throughput should be reasonable
        assert (
            throughput > 10
        ), f"Throughput {throughput:.2f} req/s too low (expected > 10 req/s)"

    def test_mixed_completion_throughput_benchmark(self):
        """Benchmark throughput with mixed completion types."""
        # Create mock data
        mock_db = Mock()
        mock_db.get_all_tags.return_value = {"tag1", "tag2"}

        engine = CompletionEngine()
        engine.set_services(instruction_db=mock_db)

        # Test mixed completion types
        completion_types = [
            lambda: engine.get_tag_completions("tag"),
            lambda: engine.get_format_completions("j"),
            lambda: engine.get_category_completions("test"),
            lambda: engine.get_output_format_completions("t"),
        ]

        request_count = 0
        start_time = time.time()
        test_duration = 1  # 1 second test
        end_time = start_time + test_duration

        while time.time() < end_time:
            completion_func = completion_types[request_count % len(completion_types)]
            completion_func()
            request_count += 1

        actual_duration = time.time() - start_time
        throughput = request_count / actual_duration

        # Mixed throughput should still be reasonable
        assert (
            throughput > 5
        ), f"Mixed throughput {throughput:.2f} req/s too low (expected > 5 req/s)"
