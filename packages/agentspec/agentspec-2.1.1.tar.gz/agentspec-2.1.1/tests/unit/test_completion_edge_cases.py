"""
Comprehensive edge case and error condition tests for CLI completion.

This module tests all possible edge cases, error conditions, and boundary
scenarios for the completion system to ensure robust error handling.
"""

import json
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from agentspec.cli.completion import (
    COMPLETION_TIMEOUT,
    MAX_CACHE_SIZE,
    CompletionCache,
    CompletionEngine,
    get_completion_engine,
    reset_completion_engine,
    safe_get_completions,
    with_timeout,
)


class TestCompletionEngineEdgeCases:
    """Edge case tests for CompletionEngine."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = CompletionEngine()

    def test_completion_with_none_prefix(self):
        """Test completion with None prefix."""
        # Tag completion with None
        result = self.engine.get_tag_completions(None)
        assert result == [], "None prefix should return empty list"

        # Template completion with None
        result = self.engine.get_template_completions(None)
        assert result == [], "None prefix should return empty list"

        # Instruction completion with None
        result = self.engine.get_instruction_completions(None)
        assert result == [], "None prefix should return empty list"

    def test_completion_with_non_string_prefix(self):
        """Test completion with non-string prefix types."""
        non_string_inputs = [123, 12.34, [], {}, True, False, object()]

        for input_val in non_string_inputs:
            # Should handle gracefully without crashing
            result = self.engine.get_tag_completions(input_val)
            assert (
                result == []
            ), f"Non-string input {type(input_val)} should return empty list"

            result = self.engine.get_template_completions(input_val)
            assert (
                result == []
            ), f"Non-string input {type(input_val)} should return empty list"

            result = self.engine.get_instruction_completions(input_val)
            assert (
                result == []
            ), f"Non-string input {type(input_val)} should return empty list"

    def test_completion_with_extremely_long_prefix(self):
        """Test completion with extremely long prefix."""
        # Create very long prefix (10KB)
        long_prefix = "a" * 10000

        result = self.engine.get_tag_completions(long_prefix)
        assert isinstance(result, list), "Long prefix should return list"
        assert len(result) == 0, "Long prefix should return no matches"

        result = self.engine.get_template_completions(long_prefix)
        assert isinstance(result, list), "Long prefix should return list"
        assert len(result) == 0, "Long prefix should return no matches"

    def test_completion_with_special_characters(self):
        """Test completion with special characters and unicode."""
        special_inputs = [
            "@#$%^&*()",
            "test-with-dashes",
            "test_with_underscores",
            "test.with.dots",
            "test/with/slashes",
            "test\\with\\backslashes",
            "test with spaces",
            "test\twith\ttabs",
            "test\nwith\nnewlines",
            "café",
            "naïve",
            "résumé",
            "测试",
            "🚀🎉💻",
            "Москва",
            "العربية",
        ]

        for special_input in special_inputs:
            # Should handle all special characters gracefully
            result = self.engine.get_tag_completions(special_input)
            assert isinstance(
                result, list
            ), f"Special input '{special_input}' should return list"

            result = self.engine.get_format_completions(special_input)
            assert isinstance(
                result, list
            ), f"Special input '{special_input}' should return list"

    def test_completion_with_empty_string(self):
        """Test completion with empty string prefix."""
        # Empty string should return all available options
        result = self.engine.get_format_completions("")
        assert len(result) > 0, "Empty prefix should return all formats"

        result = self.engine.get_category_completions("")
        assert len(result) > 0, "Empty prefix should return all categories"

        result = self.engine.get_output_format_completions("")
        assert len(result) > 0, "Empty prefix should return all output formats"

    def test_completion_with_whitespace_only_prefix(self):
        """Test completion with whitespace-only prefix."""
        whitespace_inputs = [
            " ",
            "  ",
            "\t",
            "\n",
            "\r",
            " \t\n\r ",
        ]

        for whitespace in whitespace_inputs:
            result = self.engine.get_tag_completions(whitespace)
            assert isinstance(
                result, list
            ), f"Whitespace input '{repr(whitespace)}' should return list"

            result = self.engine.get_format_completions(whitespace)
            assert isinstance(
                result, list
            ), f"Whitespace input '{repr(whitespace)}' should return list"

    def test_completion_with_case_variations(self):
        """Test completion with various case combinations."""
        case_inputs = [
            "TEST",
            "Test",
            "tEST",
            "TeSt",
            "test",
            "JSON",
            "Json",
            "json",
            "jSoN",
        ]

        for case_input in case_inputs:
            result = self.engine.get_format_completions(case_input)
            assert isinstance(
                result, list
            ), f"Case input '{case_input}' should return list"

            # Format completion should be case-sensitive for exact matches
            if case_input.lower() == "json":
                assert (
                    "json" in result or len(result) == 0
                ), "Should find json format or return empty"

    def test_service_initialization_edge_cases(self):
        """Test edge cases in service initialization."""
        # Test setting None services
        self.engine.set_services(instruction_db=None, template_manager=None)

        result = self.engine.get_tag_completions("test")
        assert result == [], "None services should return empty results"

        # Test setting services multiple times
        mock_db1 = Mock()
        mock_db1.get_all_tags.return_value = {"tag1", "tag2"}

        mock_db2 = Mock()
        mock_db2.get_all_tags.return_value = {"tag3", "tag4"}

        self.engine.set_services(instruction_db=mock_db1)
        result1 = self.engine.get_tag_completions("")

        self.engine.set_services(instruction_db=mock_db2)
        result2 = self.engine.get_tag_completions("")

        # Should use the latest service
        assert set(result1) != set(result2), "Should use different services"

    def test_concurrent_service_access(self):
        """Test concurrent access to services."""
        mock_db = Mock()
        mock_db.get_all_tags.return_value = {"concurrent", "test"}

        self.engine.set_services(instruction_db=mock_db)

        results = []
        errors = []

        def completion_worker():
            try:
                for _ in range(10):
                    result = self.engine.get_tag_completions("test")
                    results.append(result)
            except Exception as e:
                errors.append(e)

        # Start multiple concurrent workers
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=completion_worker)
            threads.append(thread)
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join(timeout=5.0)

        # Should handle concurrent access without errors
        assert len(errors) == 0, f"Concurrent access had errors: {errors}"
        assert len(results) == 50, f"Expected 50 results, got {len(results)}"


class TestCompletionCacheEdgeCases:
    """Edge case tests for CompletionCache."""

    def test_cache_with_none_key(self):
        """Test cache operations with None key."""
        cache = CompletionCache()

        # Setting with None key should handle gracefully
        cache.set(None, ["data"])
        result = cache.get(None)

        # Behavior may vary, but should not crash
        assert result is None or isinstance(result, list)

    def test_cache_with_non_string_key(self):
        """Test cache operations with non-string keys."""
        cache = CompletionCache()

        non_string_keys = [123, 12.34, [], {}, True, object()]

        for key in non_string_keys:
            # Should handle gracefully without crashing
            cache.set(key, ["data"])
            result = cache.get(key)

            # May or may not work, but should not crash
            assert result is None or isinstance(result, list)

    def test_cache_with_none_data(self):
        """Test cache operations with None data."""
        cache = CompletionCache()

        cache.set("test_key", None)
        result = cache.get("test_key")

        # Should handle None data gracefully
        assert result is None or isinstance(result, list)

    def test_cache_with_non_list_data(self):
        """Test cache operations with non-list data."""
        cache = CompletionCache()

        non_list_data = ["string_data", 123, {"key": "value"}, True, object()]

        for data in non_list_data:
            cache.set("test_key", data)
            result = cache.get("test_key")

            # Should handle gracefully
            assert result is None or isinstance(result, list)

    def test_cache_with_zero_ttl(self):
        """Test cache with zero TTL."""
        cache = CompletionCache(ttl=0)

        cache.set("test_key", ["data"])

        # Should expire immediately
        result = cache.get("test_key")
        assert result is None, "Zero TTL should expire immediately"

    def test_cache_with_negative_ttl(self):
        """Test cache with negative TTL."""
        cache = CompletionCache(ttl=-1)

        cache.set("test_key", ["data"])

        # Should handle negative TTL gracefully
        result = cache.get("test_key")
        assert result is None or isinstance(result, list)

    def test_cache_with_very_large_ttl(self):
        """Test cache with very large TTL."""
        cache = CompletionCache(ttl=999999999)  # Very large TTL

        cache.set("test_key", ["data"])
        result = cache.get("test_key")

        assert result == ["data"], "Large TTL should preserve data"

    def test_cache_size_limit_edge_cases(self):
        """Test cache size limit edge cases."""
        # Test with size limit of 1
        cache = CompletionCache(max_size=1)

        cache.set("key1", ["data1"])
        cache.set("key2", ["data2"])

        # Should only keep one entry
        stats = cache.get_stats()
        assert stats["total_entries"] <= 1, "Should respect size limit of 1"

    def test_cache_with_zero_size_limit(self):
        """Test cache with zero size limit."""
        cache = CompletionCache(max_size=0)

        cache.set("test_key", ["data"])

        # Should not store anything
        stats = cache.get_stats()
        assert stats["total_entries"] == 0, "Zero size limit should store nothing"

    def test_cache_concurrent_access_edge_cases(self):
        """Test cache concurrent access edge cases."""
        cache = CompletionCache(ttl=0.1)  # Short TTL for testing

        def cache_worker(worker_id):
            for i in range(100):
                key = f"worker_{worker_id}_key_{i}"
                cache.set(key, [f"data_{i}"])
                cache.get(key)

        # Start concurrent workers
        threads = []
        for worker_id in range(5):
            thread = threading.Thread(target=cache_worker, args=(worker_id,))
            threads.append(thread)
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join(timeout=10.0)

        # Cache should still be functional
        cache.set("final_test", ["final_data"])
        result = cache.get("final_test")
        assert result == [
            "final_data"
        ], "Cache should still work after concurrent access"


class TestSafeGetCompletionsEdgeCases:
    """Edge case tests for safe_get_completions function."""

    def test_safe_get_completions_with_none_function(self):
        """Test safe_get_completions with None function."""
        result = safe_get_completions(None, "test")
        assert result == [], "None function should return empty list"

    def test_safe_get_completions_with_non_callable(self):
        """Test safe_get_completions with non-callable object."""
        non_callables = ["string", 123, [], {}, True]

        for non_callable in non_callables:
            result = safe_get_completions(non_callable, "test")
            assert (
                result == []
            ), f"Non-callable {type(non_callable)} should return empty list"

    def test_safe_get_completions_with_function_returning_none(self):
        """Test safe_get_completions with function returning None."""

        def none_function(*args, **kwargs):
            return None

        result = safe_get_completions(none_function, "test")
        assert result == [], "Function returning None should return empty list"

    def test_safe_get_completions_with_function_returning_non_list(self):
        """Test safe_get_completions with function returning non-list."""

        def non_list_function(*args, **kwargs):
            return "not a list"

        result = safe_get_completions(non_list_function, "test")
        assert result == [], "Function returning non-list should return empty list"

    def test_safe_get_completions_with_function_raising_various_exceptions(self):
        """Test safe_get_completions with functions raising various exceptions."""
        exceptions_to_test = [
            ValueError("Value error"),
            TypeError("Type error"),
            AttributeError("Attribute error"),
            KeyError("Key error"),
            IndexError("Index error"),
            FileNotFoundError("File not found"),
            PermissionError("Permission denied"),
            ConnectionError("Connection error"),
            TimeoutError("Timeout error"),
            ImportError("Import error"),
            RuntimeError("Runtime error"),
            MemoryError("Memory error"),
            OSError("OS error"),
            Exception("Generic exception"),
        ]

        for exception in exceptions_to_test:

            def failing_function(*args, **kwargs):
                raise exception

            result = safe_get_completions(failing_function, "test")
            assert (
                result == []
            ), f"Function raising {type(exception).__name__} should return empty list"

    def test_safe_get_completions_with_function_taking_no_args(self):
        """Test safe_get_completions with function that takes no arguments."""

        def no_args_function():
            return ["result"]

        # Should handle gracefully even if function doesn't accept arguments
        result = safe_get_completions(no_args_function, "test", extra="arg")
        # May succeed or fail, but should not crash the test
        assert isinstance(result, list)

    def test_safe_get_completions_with_function_requiring_specific_args(self):
        """Test safe_get_completions with function requiring specific arguments."""

        def specific_args_function(required_arg, required_kwarg=None):
            if required_kwarg is None:
                raise ValueError("Missing required keyword argument")
            return ["result"]

        # Should handle gracefully even if arguments don't match
        result = safe_get_completions(specific_args_function, "test")
        assert result == [], "Function with argument mismatch should return empty list"

    def test_safe_get_completions_with_recursive_function(self):
        """Test safe_get_completions with recursive function that might cause stack overflow."""

        def recursive_function(depth=0):
            if depth > 1000:  # Prevent infinite recursion in test
                raise RecursionError("Maximum recursion depth exceeded")
            return recursive_function(depth + 1)

        result = safe_get_completions(recursive_function)
        assert result == [], "Recursive function should return empty list"

    def test_safe_get_completions_with_slow_function(self):
        """Test safe_get_completions with very slow function."""

        def slow_function(*args, **kwargs):
            time.sleep(10)  # Very slow
            return ["result"]

        start_time = time.time()
        result = safe_get_completions(slow_function, "test")
        elapsed = time.time() - start_time

        # Should either timeout or complete, but not hang indefinitely
        assert elapsed < 15, "Should not hang indefinitely"
        assert isinstance(result, list), "Should return list"


class TestTimeoutDecoratorEdgeCases:
    """Edge case tests for timeout decorator."""

    def test_timeout_with_zero_timeout(self):
        """Test timeout decorator with zero timeout."""

        @with_timeout(0)
        def zero_timeout_function():
            return ["result"]

        result = zero_timeout_function()
        assert result == [], "Zero timeout should return empty list"

    def test_timeout_with_negative_timeout(self):
        """Test timeout decorator with negative timeout."""

        @with_timeout(-1)
        def negative_timeout_function():
            return ["result"]

        result = negative_timeout_function()
        assert result == [], "Negative timeout should return empty list"

    def test_timeout_with_very_large_timeout(self):
        """Test timeout decorator with very large timeout."""

        @with_timeout(999999)
        def large_timeout_function():
            return ["result"]

        result = large_timeout_function()
        assert result == ["result"], "Large timeout should allow completion"

    def test_timeout_with_function_returning_none(self):
        """Test timeout decorator with function returning None."""

        @with_timeout(1)
        def none_function():
            return None

        result = none_function()
        assert result == [], "Function returning None should return empty list"

    def test_timeout_with_function_raising_exception(self):
        """Test timeout decorator with function raising exception."""

        @with_timeout(1)
        def exception_function():
            raise ValueError("Test exception")

        result = exception_function()
        assert result == [], "Function raising exception should return empty list"

    def test_timeout_with_function_at_timeout_boundary(self):
        """Test timeout decorator with function that completes exactly at timeout."""

        @with_timeout(0.1)
        def boundary_function():
            time.sleep(0.09)  # Just under timeout
            return ["result"]

        result = boundary_function()
        # May succeed or timeout depending on timing
        assert isinstance(result, list), "Should return list"


class TestCompletionEngineErrorRecovery:
    """Test error recovery scenarios for CompletionEngine."""

    def test_recovery_after_service_failure(self):
        """Test recovery after service failure."""
        engine = CompletionEngine()

        # Set up failing service
        mock_db = Mock()
        mock_db.get_all_tags.side_effect = Exception("Service failure")

        engine.set_services(instruction_db=mock_db)

        # First call should fail gracefully
        result1 = engine.get_tag_completions("test")
        assert result1 == [], "Failed service should return empty list"

        # Fix the service
        mock_db.get_all_tags.side_effect = None
        mock_db.get_all_tags.return_value = {"recovered", "tags"}

        # Should recover on next call
        result2 = engine.get_tag_completions("test")
        # May or may not work depending on caching, but should not crash
        assert isinstance(result2, list), "Should return list after recovery"

    def test_recovery_after_cache_corruption(self):
        """Test recovery after cache corruption."""
        engine = CompletionEngine()

        # Corrupt the cache
        engine.cache._cache = "corrupted"

        # Should handle corrupted cache gracefully
        result = engine.get_format_completions("json")
        assert isinstance(result, list), "Should handle corrupted cache"

    def test_recovery_after_memory_pressure(self):
        """Test recovery after simulated memory pressure."""
        engine = CompletionEngine()

        # Simulate memory pressure by filling cache with large data
        large_data = ["x" * 10000] * 1000  # Large dataset

        for i in range(100):
            engine.cache.set(f"large_key_{i}", large_data)

        # Should still function after memory pressure
        result = engine.get_format_completions("json")
        assert isinstance(result, list), "Should function after memory pressure"
        assert "json" in result, "Should still find expected results"

    def test_recovery_after_thread_interruption(self):
        """Test recovery after thread interruption."""
        engine = CompletionEngine()

        def interrupted_completion():
            try:
                # Simulate thread interruption
                raise KeyboardInterrupt("Thread interrupted")
            except KeyboardInterrupt:
                # Should handle interruption gracefully
                return engine.get_format_completions("json")

        result = interrupted_completion()
        assert isinstance(result, list), "Should handle thread interruption"


class TestCompletionSystemLimits:
    """Test system limits and boundary conditions."""

    def test_maximum_cache_entries(self):
        """Test behavior at maximum cache entries."""
        cache = CompletionCache(max_size=MAX_CACHE_SIZE)

        # Fill cache to maximum
        for i in range(MAX_CACHE_SIZE + 100):
            cache.set(f"key_{i}", [f"data_{i}"])

        stats = cache.get_stats()
        assert (
            stats["total_entries"] <= MAX_CACHE_SIZE
        ), "Should not exceed maximum cache size"

    def test_maximum_completion_results(self):
        """Test behavior with maximum completion results."""
        engine = CompletionEngine()

        # Mock service returning very large result set
        mock_db = Mock()
        large_tags = {f"tag_{i:06d}" for i in range(10000)}
        mock_db.get_all_tags.return_value = large_tags

        engine.set_services(instruction_db=mock_db)

        result = engine.get_tag_completions("")

        # Should handle large result sets
        assert isinstance(result, list), "Should return list for large result set"
        assert len(result) <= 10000, "Should not exceed expected maximum"

    def test_completion_timeout_boundary(self):
        """Test completion at timeout boundary."""
        engine = CompletionEngine()

        # Mock service that takes exactly the timeout duration
        mock_db = Mock()

        def slow_get_tags():
            time.sleep(COMPLETION_TIMEOUT - 0.01)  # Just under timeout
            return {"slow", "tags"}

        mock_db.get_all_tags.side_effect = slow_get_tags
        engine.set_services(instruction_db=mock_db)

        result = engine.get_tag_completions("slow")
        # May succeed or timeout depending on exact timing
        assert isinstance(result, list), "Should return list at timeout boundary"

    def test_unicode_handling_limits(self):
        """Test unicode handling at various limits."""
        engine = CompletionEngine()

        # Test with various unicode edge cases
        unicode_tests = [
            "\u0000",  # Null character
            "\uffff",  # Maximum BMP character
            "🚀" * 1000,  # Many emoji
            "a" + "\u0301" * 100,  # Many combining characters
            "\U0001f600" * 500,  # Many 4-byte unicode characters
        ]

        for unicode_input in unicode_tests:
            result = engine.get_tag_completions(unicode_input)
            assert isinstance(
                result, list
            ), f"Should handle unicode input: {repr(unicode_input[:50])}"

    def test_memory_usage_limits(self):
        """Test memory usage limits."""
        engine = CompletionEngine()

        # Create many completion requests to test memory usage
        for i in range(1000):
            engine.get_format_completions(f"prefix_{i % 10}")
            engine.get_category_completions(f"cat_{i % 5}")

        # Should still be functional
        result = engine.get_format_completions("json")
        assert "json" in result, "Should still function after many requests"


class TestCompletionDataIntegrity:
    """Test data integrity in various scenarios."""

    def test_completion_result_immutability(self):
        """Test that completion results are not modified by subsequent operations."""
        engine = CompletionEngine()

        result1 = engine.get_format_completions("")
        original_result = result1.copy()

        # Modify the returned result
        if result1:
            result1.append("modified")
            result1[0] = "changed"

        # Get the same completion again
        result2 = engine.get_format_completions("")

        # Original data should be preserved
        assert result2 == original_result, "Completion results should be immutable"

    def test_cache_data_integrity(self):
        """Test cache data integrity under various operations."""
        cache = CompletionCache()

        original_data = ["item1", "item2", "item3"]
        cache.set("test_key", original_data)

        # Modify the original data
        original_data.append("modified")

        # Retrieved data should not be affected
        retrieved_data = cache.get("test_key")
        assert "modified" not in retrieved_data, "Cache should preserve data integrity"

    def test_concurrent_data_integrity(self):
        """Test data integrity under concurrent access."""
        engine = CompletionEngine()

        mock_db = Mock()
        mock_db.get_all_tags.return_value = {"tag1", "tag2", "tag3"}
        engine.set_services(instruction_db=mock_db)

        results = []

        def completion_worker():
            for _ in range(50):
                result = engine.get_tag_completions("")
                results.append(tuple(sorted(result)))  # Convert to tuple for comparison

        # Start concurrent workers
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=completion_worker)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join(timeout=10.0)

        # All results should be identical
        if results:
            first_result = results[0]
            for result in results[1:]:
                assert result == first_result, "Concurrent results should be identical"
