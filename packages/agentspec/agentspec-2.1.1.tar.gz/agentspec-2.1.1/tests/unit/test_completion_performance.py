"""
Performance tests for CLI completion system.

This module tests the performance characteristics of the completion engine,
including response times, caching effectiveness, and timeout handling.
"""

import threading
import time
from unittest.mock import Mock, patch

import pytest

from agentspec.cli.completion import (
    COMPLETION_TIMEOUT,
    MAX_CACHE_SIZE,
    CompletionCache,
    CompletionEngine,
    safe_get_completions,
    with_timeout,
)


class TestCompletionPerformance:
    """Performance tests for completion engine."""

    def test_cache_performance_with_large_dataset(self):
        """Test cache performance with large number of entries."""
        cache = CompletionCache(ttl=300, max_size=1000)

        # Add many entries to test performance
        start_time = time.time()
        for i in range(500):
            cache.set(f"key_{i}", [f"value_{i}_{j}" for j in range(10)])

        set_time = time.time() - start_time
        assert (
            set_time < 1.0
        ), f"Setting 500 cache entries took {set_time:.3f}s (expected < 1s)"

        # Test retrieval performance
        start_time = time.time()
        hits = 0
        for i in range(500):
            result = cache.get(f"key_{i}")
            if result is not None:
                hits += 1

        get_time = time.time() - start_time
        assert (
            get_time < 0.5
        ), f"Getting 500 cache entries took {get_time:.3f}s (expected < 0.5s)"
        assert hits == 500, f"Expected 500 cache hits, got {hits}"

    def test_cache_size_limit_enforcement(self):
        """Test that cache enforces size limits and performs cleanup."""
        cache = CompletionCache(ttl=300, max_size=10)

        # Add more entries than the limit
        for i in range(15):
            cache.set(f"key_{i}", [f"value_{i}"])

        stats = cache.get_stats()
        assert (
            stats["total_entries"] <= 10
        ), f"Cache exceeded size limit: {stats['total_entries']} entries"
        assert (
            stats["utilization"] <= 1.0
        ), f"Cache utilization exceeded 100%: {stats['utilization']}"

    def test_cache_cleanup_performance(self):
        """Test that cache cleanup operations are fast."""
        cache = CompletionCache(ttl=0.1, max_size=100)  # Very short TTL for testing

        # Add entries that will expire quickly
        for i in range(50):
            cache.set(f"key_{i}", [f"value_{i}"])

        # Wait for entries to expire
        time.sleep(0.2)

        # Trigger cleanup by adding new entry
        start_time = time.time()
        cache.set("new_key", ["new_value"])
        cleanup_time = time.time() - start_time

        assert (
            cleanup_time < 0.1
        ), f"Cache cleanup took {cleanup_time:.3f}s (expected < 0.1s)"

    def test_completion_engine_response_time(self):
        """Test that completion engine responds within acceptable time limits."""
        engine = CompletionEngine()

        # Mock services to return predictable data quickly
        mock_db = Mock()
        mock_db.get_all_tags.return_value = {f"tag_{i}" for i in range(100)}
        mock_manager = Mock()
        mock_manager.get_all_template_ids.return_value = [
            f"template_{i}" for i in range(50)
        ]

        engine.set_services(instruction_db=mock_db, template_manager=mock_manager)

        # Test tag completion performance
        start_time = time.time()
        result = engine.get_tag_completions("tag_")
        response_time = time.time() - start_time

        assert (
            response_time < 0.2
        ), f"Tag completion took {response_time:.3f}s (expected < 0.2s)"
        assert len(result) == 100, f"Expected 100 tag completions, got {len(result)}"

        # Test template completion performance
        start_time = time.time()
        result = engine.get_template_completions("template_")
        response_time = time.time() - start_time

        assert (
            response_time < 0.2
        ), f"Template completion took {response_time:.3f}s (expected < 0.2s)"
        assert len(result) == 50, f"Expected 50 template completions, got {len(result)}"

    def test_cached_completion_performance(self):
        """Test that cached completions are significantly faster."""
        engine = CompletionEngine()

        # Mock services
        mock_db = Mock()
        mock_db.get_all_tags.return_value = {f"tag_{i}" for i in range(1000)}
        engine.set_services(instruction_db=mock_db)

        # First call (cache miss)
        start_time = time.time()
        result1 = engine.get_tag_completions("tag_1")
        first_call_time = time.time() - start_time

        # Second call (cache hit)
        start_time = time.time()
        result2 = engine.get_tag_completions("tag_1")
        second_call_time = time.time() - start_time

        assert result1 == result2, "Cached result should match original result"
        assert (
            second_call_time < first_call_time / 2
        ), f"Cached call ({second_call_time:.3f}s) should be much faster than first call ({first_call_time:.3f}s)"
        assert (
            second_call_time < 0.01
        ), f"Cached completion took {second_call_time:.3f}s (expected < 0.01s)"

    def test_timeout_decorator_functionality(self):
        """Test that timeout decorator properly handles slow functions."""

        @with_timeout(0.1)  # 100ms timeout
        def slow_function():
            time.sleep(0.2)  # Sleep longer than timeout
            return ["result"]

        @with_timeout(0.1)
        def fast_function():
            return ["result"]

        # Test timeout case
        start_time = time.time()
        result = slow_function()
        elapsed = time.time() - start_time

        assert result == [], "Timed out function should return empty list"
        assert elapsed < 0.15, f"Timeout took {elapsed:.3f}s (expected < 0.15s)"

        # Test normal case
        start_time = time.time()
        result = fast_function()
        elapsed = time.time() - start_time

        assert result == ["result"], "Fast function should return normal result"
        assert elapsed < 0.05, f"Fast function took {elapsed:.3f}s (expected < 0.05s)"

    def test_timeout_decorator_with_exception(self):
        """Test that timeout decorator handles exceptions properly."""

        @with_timeout(0.1)
        def failing_function():
            raise ValueError("Test error")

        result = failing_function()
        assert result == [], "Function with exception should return empty list"

    def test_concurrent_completion_requests(self):
        """Test performance under concurrent completion requests."""
        engine = CompletionEngine()

        # Mock services
        mock_db = Mock()
        mock_db.get_all_tags.return_value = {f"tag_{i}" for i in range(100)}
        engine.set_services(instruction_db=mock_db)

        results = []
        errors = []

        def completion_worker(prefix):
            try:
                start_time = time.time()
                result = engine.get_tag_completions(f"tag_{prefix}")
                response_time = time.time() - start_time
                results.append((prefix, len(result), response_time))
            except Exception as e:
                errors.append(e)

        # Start multiple concurrent completion requests
        threads = []
        for i in range(10):
            thread = threading.Thread(target=completion_worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=2.0)

        assert len(errors) == 0, f"Concurrent completions had errors: {errors}"
        assert len(results) == 10, f"Expected 10 results, got {len(results)}"

        # Check that all responses were reasonably fast
        max_response_time = max(result[2] for result in results)
        assert (
            max_response_time < 1.0
        ), f"Slowest concurrent completion took {max_response_time:.3f}s (expected < 1s)"

    def test_performance_stats_tracking(self):
        """Test that performance statistics are properly tracked."""
        # Create a fresh engine instance to avoid shared state
        engine = CompletionEngine()

        # Mock services
        mock_db = Mock()
        mock_db.get_all_tags.return_value = {"tag1", "tag2", "tag3"}
        engine.set_services(instruction_db=mock_db)

        # Reset stats to ensure clean state
        engine.reset_performance_stats()

        # Verify initial stats are zero
        initial_stats = engine.get_performance_stats()
        assert (
            initial_stats["total_completions"] == 0
        ), f"Expected 0 initial completions, got {initial_stats['total_completions']}"

        # Make some completion requests
        engine.get_tag_completions("tag")  # Cache miss
        engine.get_tag_completions("tag")  # Cache hit
        engine.get_tag_completions("other")  # Cache miss

        stats = engine.get_performance_stats()

        assert (
            stats["total_completions"] == 3
        ), f"Expected 3 total completions, got {stats['total_completions']}"
        assert (
            stats["cache_hits"] == 1
        ), f"Expected 1 cache hit, got {stats['cache_hits']}"
        assert (
            stats["cache_misses"] == 2
        ), f"Expected 2 cache misses, got {stats['cache_misses']}"
        assert (
            stats["avg_response_time"] > 0
        ), f"Average response time should be > 0, got {stats['avg_response_time']}"
        assert (
            "cache_stats" in stats
        ), "Performance stats should include cache statistics"

    def test_safe_get_completions_performance(self):
        """Test performance of safe completion wrapper."""

        def fast_completer():
            return ["result1", "result2"]

        def slow_completer():
            time.sleep(0.1)
            return ["slow_result"]

        def failing_completer():
            raise ValueError("Test error")

        # Test fast completer
        start_time = time.time()
        result = safe_get_completions(fast_completer)
        fast_time = time.time() - start_time

        assert result == ["result1", "result2"], "Fast completer should return results"
        assert (
            fast_time < 0.05
        ), f"Fast completer took {fast_time:.3f}s (expected < 0.05s)"

        # Test slow completer
        start_time = time.time()
        result = safe_get_completions(slow_completer)
        slow_time = time.time() - start_time

        assert result == ["slow_result"], "Slow completer should return results"
        assert (
            slow_time >= 0.1
        ), f"Slow completer took {slow_time:.3f}s (expected >= 0.1s)"

        # Test failing completer
        start_time = time.time()
        result = safe_get_completions(failing_completer)
        fail_time = time.time() - start_time

        assert result == [], "Failing completer should return empty list"
        assert (
            fail_time < 0.05
        ), f"Failing completer took {fail_time:.3f}s (expected < 0.05s)"

    @pytest.mark.slow
    def test_large_dataset_completion_performance(self):
        """Test completion performance with large datasets."""
        engine = CompletionEngine()

        # Create large mock datasets
        large_tags = {f"tag_{i:04d}" for i in range(10000)}
        large_templates = [f"template_{i:04d}" for i in range(5000)]

        mock_db = Mock()
        mock_db.get_all_tags.return_value = large_tags
        mock_manager = Mock()
        mock_manager.get_all_template_ids.return_value = large_templates

        engine.set_services(instruction_db=mock_db, template_manager=mock_manager)

        # Test tag completion with large dataset
        start_time = time.time()
        result = engine.get_tag_completions("tag_1")
        response_time = time.time() - start_time

        assert (
            len(result) == 1000
        ), f"Expected 1000 matching tags (tag_1000-tag_1999), got {len(result)}"
        assert (
            response_time < 1.0
        ), f"Large dataset tag completion took {response_time:.3f}s (expected < 1s)"

        # Test template completion with large dataset
        start_time = time.time()
        result = engine.get_template_completions("template_1")
        response_time = time.time() - start_time

        assert (
            len(result) == 1000
        ), f"Expected 1000 matching templates, got {len(result)}"
        assert (
            response_time < 1.0
        ), f"Large dataset template completion took {response_time:.3f}s (expected < 1s)"

    def test_memory_usage_under_load(self):
        """Test that completion engine doesn't consume excessive memory."""
        engine = CompletionEngine()

        # Mock services with moderate datasets
        mock_db = Mock()
        mock_db.get_all_tags.return_value = {f"tag_{i}" for i in range(1000)}
        engine.set_services(instruction_db=mock_db)

        # Make many completion requests to fill cache
        for i in range(200):
            engine.get_tag_completions(f"tag_{i % 50}")  # Some cache hits, some misses

        # Check cache statistics
        stats = engine.get_performance_stats()
        cache_stats = stats["cache_stats"]

        assert (
            cache_stats["total_entries"] <= MAX_CACHE_SIZE
        ), f"Cache exceeded size limit: {cache_stats['total_entries']}"
        assert (
            cache_stats["utilization"] <= 1.0
        ), f"Cache utilization exceeded 100%: {cache_stats['utilization']}"

        # Verify cache is working efficiently
        assert (
            stats["cache_hits"] > 0
        ), "Should have some cache hits with repeated requests"
        assert (
            stats["cache_hits"] + stats["cache_misses"] == stats["total_completions"]
        ), "Cache hits + misses should equal total completions"
