"""
Unit tests for completion engine and cache infrastructure.

Tests the CompletionEngine and CompletionCache classes for functionality,
error handling, and performance characteristics.
"""

import time
from unittest.mock import Mock, patch

import pytest

from agentspec.cli.completion import (
    CompletionCache,
    CompletionEngine,
    get_completion_engine,
    reset_completion_engine,
    safe_get_completions,
    safe_initialize_services,
)


class TestCompletionCache:
    """Test cases for CompletionCache class"""

    def test_cache_initialization(self):
        """Test cache initialization with default and custom TTL"""
        # Default TTL
        cache = CompletionCache()
        assert cache.ttl == 300
        assert cache._cache == {}

        # Custom TTL
        cache = CompletionCache(ttl=600)
        assert cache.ttl == 600
        assert cache._cache == {}

    def test_cache_set_and_get(self):
        """Test basic cache set and get operations"""
        cache = CompletionCache(ttl=300)

        # Set data
        test_data = ["tag1", "tag2", "tag3"]
        cache.set("test_key", test_data)

        # Get data
        result = cache.get("test_key")
        assert result == test_data

    def test_cache_miss(self):
        """Test cache miss for non-existent key"""
        cache = CompletionCache()
        result = cache.get("nonexistent_key")
        assert result is None

    def test_cache_expiration(self):
        """Test cache entry expiration based on TTL"""
        cache = CompletionCache(ttl=1)  # 1 second TTL

        # Set data
        test_data = ["tag1", "tag2"]
        cache.set("test_key", test_data)

        # Should be available immediately
        result = cache.get("test_key")
        assert result == test_data

        # Wait for expiration
        time.sleep(1.1)

        # Should be expired and return None
        result = cache.get("test_key")
        assert result is None

        # Key should be removed from cache
        assert "test_key" not in cache._cache

    def test_cache_clear(self):
        """Test cache clear operation"""
        cache = CompletionCache()

        # Add some data
        cache.set("key1", ["data1"])
        cache.set("key2", ["data2"])
        assert len(cache._cache) == 2

        # Clear cache
        cache.clear()
        assert len(cache._cache) == 0
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_cache_overwrite(self):
        """Test overwriting existing cache entries"""
        cache = CompletionCache()

        # Set initial data
        cache.set("test_key", ["old_data"])
        assert cache.get("test_key") == ["old_data"]

        # Overwrite with new data
        cache.set("test_key", ["new_data"])
        assert cache.get("test_key") == ["new_data"]


class TestCompletionEngine:
    """Test cases for CompletionEngine class"""

    def test_engine_initialization(self):
        """Test completion engine initialization"""
        engine = CompletionEngine()
        assert engine.cache is not None
        assert isinstance(engine.cache, CompletionCache)
        assert engine._instruction_db is None
        assert engine._template_manager is None

    def test_set_services(self):
        """Test setting service dependencies"""
        engine = CompletionEngine()
        mock_db = Mock()
        mock_manager = Mock()

        engine.set_services(instruction_db=mock_db, template_manager=mock_manager)

        assert engine._instruction_db is mock_db
        assert engine._template_manager is mock_manager

    def test_tag_completions_without_db(self):
        """Test tag completions when instruction database is not available"""
        engine = CompletionEngine()

        # Mock the instruction database initialization to fail
        with patch.object(engine, "_get_instruction_db", return_value=None):
            result = engine.get_tag_completions("test")
            assert result == []

    def test_tag_completions_with_db(self):
        """Test tag completions with instruction database"""
        engine = CompletionEngine()
        mock_db = Mock()
        mock_db.get_all_tags.return_value = {
            "testing",
            "frontend",
            "backend",
            "test-driven",
            "performance",
        }

        engine.set_services(instruction_db=mock_db)

        # Test prefix matching
        result = engine.get_tag_completions("test")
        expected = ["test-driven", "testing"]  # Sorted
        assert result == expected

        # Test empty prefix
        result = engine.get_tag_completions("")
        assert len(result) == 5
        assert "testing" in result
        assert "frontend" in result

    def test_tag_completions_caching(self):
        """Test tag completions caching behavior"""
        engine = CompletionEngine()
        mock_db = Mock()
        mock_db.get_all_tags.return_value = {"testing", "frontend"}

        engine.set_services(instruction_db=mock_db)

        # First call should hit database
        result1 = engine.get_tag_completions("test")
        assert mock_db.get_all_tags.call_count == 1

        # Second call should use cache
        result2 = engine.get_tag_completions("test")
        assert mock_db.get_all_tags.call_count == 1  # No additional calls
        assert result1 == result2

    def test_tag_completions_error_handling(self):
        """Test tag completions error handling"""
        engine = CompletionEngine()
        mock_db = Mock()
        mock_db.get_all_tags.side_effect = Exception("Database error")

        engine.set_services(instruction_db=mock_db)

        result = engine.get_tag_completions("test")
        assert result == []

    def test_template_completions_without_manager(self):
        """Test template completions when template manager is not available"""
        engine = CompletionEngine()

        # Mock the template manager initialization to fail
        with patch.object(engine, "_get_template_manager", return_value=None):
            result = engine.get_template_completions("react")
            assert result == []

    def test_template_completions_with_manager(self):
        """Test template completions with template manager"""
        engine = CompletionEngine()
        mock_manager = Mock()
        mock_manager.get_all_template_ids.return_value = [
            "react-app",
            "python-api",
            "nodejs-api",
            "react-component",
        ]

        engine.set_services(template_manager=mock_manager)

        # Test prefix matching
        result = engine.get_template_completions("react")
        expected = ["react-app", "react-component"]  # Sorted
        assert result == expected

        # Test empty prefix
        result = engine.get_template_completions("")
        assert len(result) == 4

    def test_template_completions_caching(self):
        """Test template completions caching behavior"""
        engine = CompletionEngine()
        mock_manager = Mock()
        mock_manager.get_all_template_ids.return_value = ["react-app", "python-api"]

        engine.set_services(template_manager=mock_manager)

        # First call should hit template manager
        result1 = engine.get_template_completions("react")
        assert mock_manager.get_all_template_ids.call_count == 1

        # Second call should use cache
        result2 = engine.get_template_completions("react")
        assert mock_manager.get_all_template_ids.call_count == 1  # No additional calls
        assert result1 == result2

    def test_template_completions_error_handling(self):
        """Test template completions error handling"""
        engine = CompletionEngine()
        mock_manager = Mock()
        mock_manager.get_all_template_ids.side_effect = Exception("Manager error")

        engine.set_services(template_manager=mock_manager)

        result = engine.get_template_completions("react")
        assert result == []

    def test_project_type_completions_without_manager(self):
        """Test project type completions when template manager is not available"""
        engine = CompletionEngine()

        # Mock the template manager initialization to fail
        with patch.object(engine, "_get_template_manager", return_value=None):
            result = engine.get_project_type_completions("web")
            assert result == []

    def test_project_type_completions_with_manager(self):
        """Test project type completions with template manager"""
        engine = CompletionEngine()
        mock_manager = Mock()
        mock_manager.get_all_project_types.return_value = {
            "web-application",
            "mobile-app",
            "api-service",
            "web-component",
        }

        engine.set_services(template_manager=mock_manager)

        # Test prefix matching
        result = engine.get_project_type_completions("web")
        expected = ["web-application", "web-component"]  # Sorted
        assert result == expected

        # Test empty prefix
        result = engine.get_project_type_completions("")
        assert len(result) == 4

    def test_project_type_completions_caching(self):
        """Test project type completions caching behavior"""
        engine = CompletionEngine()
        mock_manager = Mock()
        mock_manager.get_all_project_types.return_value = {
            "web-application",
            "mobile-app",
        }

        engine.set_services(template_manager=mock_manager)

        # First call should hit template manager
        result1 = engine.get_project_type_completions("web")
        assert mock_manager.get_all_project_types.call_count == 1

        # Second call should use cache
        result2 = engine.get_project_type_completions("web")
        assert mock_manager.get_all_project_types.call_count == 1  # No additional calls
        assert result1 == result2

    def test_project_type_completions_error_handling(self):
        """Test project type completions error handling"""
        engine = CompletionEngine()
        mock_manager = Mock()
        mock_manager.get_all_project_types.side_effect = Exception("Manager error")

        engine.set_services(template_manager=mock_manager)

        result = engine.get_project_type_completions("web")
        assert result == []

    def test_category_completions(self):
        """Test category completions"""
        engine = CompletionEngine()

        # Test prefix matching (case-insensitive)
        result = engine.get_category_completions("front")
        assert result == ["Frontend"]

        result = engine.get_category_completions("FRONT")
        assert result == ["Frontend"]

        # Test multiple matches
        result = engine.get_category_completions("")
        assert len(result) == 7
        assert "General" in result
        assert "Testing" in result
        assert "Frontend" in result

    def test_category_completions_caching(self):
        """Test category completions caching"""
        engine = CompletionEngine()

        # Categories should be cached after first call
        result1 = engine.get_category_completions("test")
        result2 = engine.get_category_completions("test")
        assert result1 == result2
        assert result1 == ["Testing"]

    def test_format_completions(self):
        """Test output format completions"""
        engine = CompletionEngine()

        # Test prefix matching
        result = engine.get_format_completions("j")
        assert result == ["json"]

        result = engine.get_format_completions("m")
        assert result == ["markdown"]

        # Test empty prefix
        result = engine.get_format_completions("")
        assert len(result) == 3
        assert "markdown" in result
        assert "json" in result
        assert "yaml" in result

    def test_output_format_completions(self):
        """Test integration output format completions"""
        engine = CompletionEngine()

        # Test prefix matching
        result = engine.get_output_format_completions("j")
        assert result == ["json"]

        result = engine.get_output_format_completions("t")
        assert result == ["text"]

        # Test empty prefix
        result = engine.get_output_format_completions("")
        assert len(result) == 2
        assert "text" in result
        assert "json" in result

    def test_instruction_completions_without_db(self):
        """Test instruction completions when instruction database is not available"""
        engine = CompletionEngine()

        # Mock the instruction database initialization to fail
        with patch.object(engine, "_get_instruction_db", return_value=None):
            result = engine.get_instruction_completions("core")
            assert result == []

    def test_instruction_completions_with_db(self):
        """Test instruction completions with instruction database"""
        engine = CompletionEngine()
        mock_db = Mock()
        mock_db.load_instructions.return_value = {
            "core_001": {"id": "core_001", "content": "Core instruction 1"},
            "core_002": {"id": "core_002", "content": "Core instruction 2"},
            "frontend_001": {"id": "frontend_001", "content": "Frontend instruction 1"},
            "testing_001": {"id": "testing_001", "content": "Testing instruction 1"},
        }

        engine.set_services(instruction_db=mock_db)

        # Test prefix matching
        result = engine.get_instruction_completions("core")
        assert result == ["core_001", "core_002"]

        # Test different prefix
        result = engine.get_instruction_completions("frontend")
        assert result == ["frontend_001"]

        # Test empty prefix (should return all)
        result = engine.get_instruction_completions("")
        assert len(result) == 4
        assert "core_001" in result
        assert "frontend_001" in result
        assert "testing_001" in result

    def test_instruction_completions_caching(self):
        """Test instruction completions caching behavior"""
        engine = CompletionEngine()
        mock_db = Mock()
        mock_db.load_instructions.return_value = {
            "core_001": {"id": "core_001", "content": "Core instruction 1"},
            "core_002": {"id": "core_002", "content": "Core instruction 2"},
        }

        engine.set_services(instruction_db=mock_db)

        # First call should hit database
        result1 = engine.get_instruction_completions("core")
        assert result1 == ["core_001", "core_002"]

        # Second call should use cache
        result2 = engine.get_instruction_completions("core")
        assert result2 == ["core_001", "core_002"]

        # Database should only be called once
        mock_db.load_instructions.assert_called_once()

    def test_instruction_completions_error_handling(self):
        """Test instruction completions error handling"""
        engine = CompletionEngine()
        mock_db = Mock()
        mock_db.load_instructions.side_effect = Exception("Database error")

        engine.set_services(instruction_db=mock_db)

        result = engine.get_instruction_completions("core")
        assert result == []


class TestCompletionUtilities:
    """Test cases for completion utility functions"""

    def test_get_completion_engine_singleton(self):
        """Test that get_completion_engine returns singleton instance"""
        engine1 = get_completion_engine()
        engine2 = get_completion_engine()

        assert engine1 is engine2
        assert isinstance(engine1, CompletionEngine)

    def test_safe_get_completions_success(self):
        """Test safe_get_completions with successful function"""

        def mock_completer(prefix):
            return [f"{prefix}_completion"]

        result = safe_get_completions(mock_completer, "test")
        assert result == ["test_completion"]

    def test_safe_get_completions_error(self):
        """Test safe_get_completions with failing function"""

        def failing_completer(prefix):
            raise Exception("Completer error")

        result = safe_get_completions(failing_completer, "test")
        assert result == []

    def test_safe_get_completions_with_kwargs(self):
        """Test safe_get_completions with keyword arguments"""

        def mock_completer(prefix, suffix=""):
            return [f"{prefix}_{suffix}"]

        result = safe_get_completions(mock_completer, "test", suffix="completion")
        assert result == ["test_completion"]


class TestCompletionPerformance:
    """Test cases for completion performance characteristics"""

    def test_cache_performance_with_large_dataset(self):
        """Test cache performance with large datasets"""
        cache = CompletionCache()

        # Generate large dataset
        large_dataset = [f"tag_{i}" for i in range(1000)]

        # Time cache operations
        start_time = time.time()
        cache.set("large_dataset", large_dataset)
        set_time = time.time() - start_time

        start_time = time.time()
        result = cache.get("large_dataset")
        get_time = time.time() - start_time

        # Cache operations should be fast
        assert set_time < 0.1  # Less than 100ms
        assert get_time < 0.1  # Less than 100ms
        assert result == large_dataset

    def test_completion_engine_performance(self):
        """Test completion engine performance with mocked services"""
        engine = CompletionEngine()

        # Mock services with large datasets
        mock_db = Mock()
        mock_db.get_all_tags.return_value = {f"tag_{i}" for i in range(100)}

        mock_manager = Mock()
        mock_manager.get_all_template_ids.return_value = [
            f"template_{i}" for i in range(100)
        ]

        engine.set_services(instruction_db=mock_db, template_manager=mock_manager)

        # Time completion operations
        start_time = time.time()
        tag_result = engine.get_tag_completions("tag_1")
        tag_time = time.time() - start_time

        start_time = time.time()
        template_result = engine.get_template_completions("template_1")
        template_time = time.time() - start_time

        # Completion operations should be fast
        assert tag_time < 0.5  # Less than 500ms
        assert template_time < 0.5  # Less than 500ms
        assert len(tag_result) > 0
        assert len(template_result) > 0

    def test_cache_memory_usage(self):
        """Test cache memory usage and cleanup"""
        cache = CompletionCache(ttl=1)

        # Add multiple entries
        for i in range(10):
            cache.set(f"key_{i}", [f"data_{i}"])

        assert len(cache._cache) == 10

        # Wait for expiration
        time.sleep(1.1)

        # Access all keys to trigger cleanup of expired entries
        for i in range(10):
            result = cache.get(f"key_{i}")
            assert result is None  # All should be expired

        # All expired entries should be cleaned up after access
        assert len(cache._cache) == 0


@pytest.fixture
def mock_completion_engine():
    """Fixture providing a mocked completion engine"""
    engine = CompletionEngine()

    mock_db = Mock()
    mock_db.get_all_tags.return_value = {"testing", "frontend", "backend"}

    mock_manager = Mock()
    mock_manager.get_all_template_ids.return_value = ["react-app", "python-api"]

    engine.set_services(instruction_db=mock_db, template_manager=mock_manager)
    return engine


class TestCompletionIntegration:
    """Integration tests for completion components"""

    def test_engine_with_real_cache_expiration(self, mock_completion_engine):
        """Test completion engine with real cache expiration"""
        # Set short TTL for testing
        mock_completion_engine.cache.ttl = 1

        # First call
        result1 = mock_completion_engine.get_tag_completions("test")
        assert len(result1) > 0

        # Wait for cache expiration
        time.sleep(1.1)

        # Second call should hit database again
        result2 = mock_completion_engine.get_tag_completions("test")
        assert result1 == result2

        # Verify database was called twice
        assert mock_completion_engine._instruction_db.get_all_tags.call_count == 2

    def test_engine_error_recovery(self):
        """Test completion engine error recovery"""
        engine = CompletionEngine()

        # Set up mock that fails first time, succeeds second time
        mock_db = Mock()
        call_count = 0

        def side_effect():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("First call fails")
            return {"testing", "frontend"}

        mock_db.get_all_tags.side_effect = side_effect
        engine.set_services(instruction_db=mock_db)

        # First call should fail gracefully
        result1 = engine.get_tag_completions("test")
        assert result1 == []

        # Clear cache and try again
        engine.cache.clear()

        # Second call should succeed
        result2 = engine.get_tag_completions("test")
        assert len(result2) > 0


class TestComprehensiveErrorHandling:
    """Test cases for comprehensive error handling scenarios"""

    def test_safe_get_completions_import_error(self):
        """Test safe_get_completions with ImportError"""

        def failing_completer(prefix):
            raise ImportError("Missing dependency")

        result = safe_get_completions(failing_completer, "test")
        assert result == []

    def test_safe_get_completions_file_not_found_error(self):
        """Test safe_get_completions with FileNotFoundError"""

        def failing_completer(prefix):
            raise FileNotFoundError("Data file not found")

        result = safe_get_completions(failing_completer, "test")
        assert result == []

    def test_safe_get_completions_permission_error(self):
        """Test safe_get_completions with PermissionError"""

        def failing_completer(prefix):
            raise PermissionError("Access denied")

        result = safe_get_completions(failing_completer, "test")
        assert result == []

    def test_safe_get_completions_timeout_error(self):
        """Test safe_get_completions with TimeoutError"""

        def failing_completer(prefix):
            raise TimeoutError("Operation timed out")

        result = safe_get_completions(failing_completer, "test")
        assert result == []

    def test_safe_get_completions_connection_error(self):
        """Test safe_get_completions with ConnectionError"""

        def failing_completer(prefix):
            raise ConnectionError("Network error")

        result = safe_get_completions(failing_completer, "test")
        assert result == []

    def test_safe_get_completions_value_error(self):
        """Test safe_get_completions with ValueError"""

        def failing_completer(prefix):
            raise ValueError("Invalid value")

        result = safe_get_completions(failing_completer, "test")
        assert result == []

    def test_safe_get_completions_type_error(self):
        """Test safe_get_completions with TypeError"""

        def failing_completer(prefix):
            raise TypeError("Type mismatch")

        result = safe_get_completions(failing_completer, "test")
        assert result == []

    def test_safe_get_completions_invalid_return_type(self):
        """Test safe_get_completions with invalid return type"""

        def invalid_completer(prefix):
            return "not a list"

        result = safe_get_completions(invalid_completer, "test")
        assert result == []

    def test_safe_get_completions_mixed_return_types(self):
        """Test safe_get_completions with mixed return types"""

        def mixed_completer(prefix):
            return ["valid_string", 123, None, "another_string"]

        result = safe_get_completions(mixed_completer, "test")
        assert result == ["valid_string", "another_string"]

    def test_safe_get_completions_none_return(self):
        """Test safe_get_completions with None return"""

        def none_completer(prefix):
            return None

        result = safe_get_completions(none_completer, "test")
        assert result == []


class TestServiceInitializationErrorHandling:
    """Test cases for service initialization error handling"""

    @patch("agentspec.cli.completion.CompletionEngine._get_instruction_db")
    def test_instruction_db_initialization_failure(self, mock_get_db):
        """Test graceful handling of InstructionDatabase initialization failure"""
        # Mock database initialization failure
        mock_get_db.return_value = None

        engine = CompletionEngine()
        result = engine.get_tag_completions("test")

        assert result == []
        mock_get_db.assert_called_once()

    @patch("agentspec.cli.completion.CompletionEngine._get_template_manager")
    def test_template_manager_initialization_failure(self, mock_get_manager):
        """Test graceful handling of TemplateManager initialization failure"""
        # Mock template manager initialization failure
        mock_get_manager.return_value = None

        engine = CompletionEngine()
        result = engine.get_template_completions("test")

        assert result == []
        mock_get_manager.assert_called_once()

    def test_instruction_db_import_error_handling(self):
        """Test handling of ImportError during InstructionDatabase initialization"""
        engine = CompletionEngine()

        with patch(
            "agentspec.cli.completion.CompletionEngine._get_instruction_db"
        ) as mock_get_db:
            mock_get_db.side_effect = ImportError("Cannot import InstructionDatabase")

            result = engine.get_tag_completions("test")
            assert result == []

    def test_template_manager_import_error_handling(self):
        """Test handling of ImportError during TemplateManager initialization"""
        engine = CompletionEngine()

        with patch(
            "agentspec.cli.completion.CompletionEngine._get_template_manager"
        ) as mock_get_manager:
            mock_get_manager.side_effect = ImportError("Cannot import TemplateManager")

            result = engine.get_template_completions("test")
            assert result == []


class TestDataLoadingErrorHandling:
    """Test cases for data loading error handling"""

    def test_tag_completion_with_invalid_prefix_type(self):
        """Test tag completion with invalid prefix type"""
        engine = CompletionEngine()

        # Test with non-string prefix
        result = engine.get_tag_completions(123)
        assert result == []

        result = engine.get_tag_completions(None)
        assert result == []

    def test_template_completion_with_invalid_prefix_type(self):
        """Test template completion with invalid prefix type"""
        engine = CompletionEngine()

        # Test with non-string prefix
        result = engine.get_template_completions(123)
        assert result == []

        result = engine.get_template_completions(None)
        assert result == []

    def test_instruction_completion_with_invalid_prefix_type(self):
        """Test instruction completion with invalid prefix type"""
        engine = CompletionEngine()

        # Test with non-string prefix
        result = engine.get_instruction_completions(123)
        assert result == []

        result = engine.get_instruction_completions(None)
        assert result == []

    def test_tag_completion_with_invalid_data_type(self):
        """Test tag completion when database returns invalid data type"""
        engine = CompletionEngine()

        mock_db = Mock()
        mock_db.get_all_tags.return_value = "not a set or list"
        engine.set_services(instruction_db=mock_db)

        result = engine.get_tag_completions("test")
        assert result == []

    def test_template_completion_with_invalid_data_type(self):
        """Test template completion when manager returns invalid data type"""
        engine = CompletionEngine()

        mock_manager = Mock()
        mock_manager.get_all_template_ids.return_value = "not a set or list"
        engine.set_services(template_manager=mock_manager)

        result = engine.get_template_completions("test")
        assert result == []

    def test_instruction_completion_with_invalid_data_type(self):
        """Test instruction completion when database returns invalid data type"""
        engine = CompletionEngine()

        mock_db = Mock()
        mock_db.load_instructions.return_value = "not a dict"
        engine.set_services(instruction_db=mock_db)

        result = engine.get_instruction_completions("test")
        assert result == []

    def test_tag_completion_with_file_not_found(self):
        """Test tag completion when data files are not found"""
        engine = CompletionEngine()

        mock_db = Mock()
        mock_db.get_all_tags.side_effect = FileNotFoundError("Data file not found")
        engine.set_services(instruction_db=mock_db)

        result = engine.get_tag_completions("test")
        assert result == []

    def test_template_completion_with_permission_error(self):
        """Test template completion with permission error"""
        engine = CompletionEngine()

        mock_manager = Mock()
        mock_manager.get_all_template_ids.side_effect = PermissionError("Access denied")
        engine.set_services(template_manager=mock_manager)

        result = engine.get_template_completions("test")
        assert result == []

    def test_instruction_completion_with_data_corruption(self):
        """Test instruction completion with data corruption error"""
        engine = CompletionEngine()

        mock_db = Mock()
        mock_db.load_instructions.side_effect = ValueError("Corrupted data")
        engine.set_services(instruction_db=mock_db)

        result = engine.get_instruction_completions("test")
        assert result == []


class TestCacheErrorHandling:
    """Test cases for cache error handling scenarios"""

    def test_cache_with_empty_results(self):
        """Test caching of empty results to avoid repeated failures"""
        engine = CompletionEngine()

        mock_db = Mock()
        mock_db.get_all_tags.side_effect = FileNotFoundError("Data file not found")
        engine.set_services(instruction_db=mock_db)

        # First call should attempt to load data and cache empty result
        result1 = engine.get_tag_completions("test")
        assert result1 == []

        # Second call should return cached empty result without calling database again
        result2 = engine.get_tag_completions("test")
        assert result2 == []

        # Database should only be called once
        assert mock_db.get_all_tags.call_count == 1

    def test_cache_with_mixed_data_types(self):
        """Test cache handling of mixed data types in results"""
        engine = CompletionEngine()

        mock_db = Mock()
        mock_db.get_all_tags.return_value = {"valid_tag", 123, None, "another_tag"}
        engine.set_services(instruction_db=mock_db)

        result = engine.get_tag_completions("valid")
        # Should filter out non-string items
        assert result == ["valid_tag"]

    def test_performance_stats_error_tracking(self):
        """Test that performance stats correctly track errors"""
        engine = CompletionEngine()

        # Get initial error count
        initial_stats = engine.get_performance_stats()
        initial_errors = initial_stats["errors"]

        # Cause an error
        mock_db = Mock()
        mock_db.get_all_tags.side_effect = Exception("Test error")
        engine.set_services(instruction_db=mock_db)

        result = engine.get_tag_completions("test")
        assert result == []

        # Check that error count increased
        final_stats = engine.get_performance_stats()
        assert final_stats["errors"] == initial_errors + 1


class TestGracefulDegradationRequirements:
    """Test cases specifically for requirements 3.4, 4.4, and 11.3"""

    def test_requirement_3_4_instruction_database_unavailable(self):
        """Test Requirement 3.4: Graceful degradation when instruction database unavailable"""
        engine = CompletionEngine()

        # Simulate database unavailable
        with patch.object(engine, "_get_instruction_db", return_value=None):
            result = engine.get_tag_completions("test")
            assert result == []  # Should provide empty completions gracefully

    def test_requirement_4_4_template_manager_unavailable(self):
        """Test Requirement 4.4: Graceful degradation when template manager unavailable"""
        engine = CompletionEngine()

        # Simulate template manager unavailable
        with patch.object(engine, "_get_template_manager", return_value=None):
            result = engine.get_template_completions("test")
            assert result == []  # Should provide empty completions gracefully

            result = engine.get_project_type_completions("test")
            assert result == []  # Should provide empty completions gracefully

    def test_requirement_11_3_error_loading_data_graceful_failure(self):
        """Test Requirement 11.3: Graceful failure when encountering errors loading data"""
        engine = CompletionEngine()

        # Test various data loading errors
        mock_db = Mock()
        mock_manager = Mock()

        # Test FileNotFoundError
        mock_db.get_all_tags.side_effect = FileNotFoundError("Data not found")
        mock_manager.get_all_template_ids.side_effect = FileNotFoundError(
            "Templates not found"
        )

        engine.set_services(instruction_db=mock_db, template_manager=mock_manager)

        # Should fail gracefully without blocking completion
        tag_result = engine.get_tag_completions("test")
        template_result = engine.get_template_completions("test")

        assert tag_result == []
        assert template_result == []

        # Test PermissionError
        mock_db.get_all_tags.side_effect = PermissionError("Access denied")
        mock_manager.get_all_template_ids.side_effect = PermissionError("Access denied")

        # Clear cache to force new attempts
        engine.cache.clear()

        tag_result = engine.get_tag_completions("test")
        template_result = engine.get_template_completions("test")

        assert tag_result == []
        assert template_result == []


class TestHelperFunctions:
    """Test cases for helper functions"""

    def test_reset_completion_engine(self):
        """Test reset_completion_engine function"""
        # Get an engine instance
        engine1 = get_completion_engine()
        assert engine1 is not None

        # Reset the engine
        reset_completion_engine()

        # Get a new engine instance
        engine2 = get_completion_engine()
        assert engine2 is not None
        assert engine2 is not engine1  # Should be a different instance

    def test_safe_initialize_services_success(self):
        """Test safe_initialize_services with successful initialization"""
        mock_db = Mock()
        mock_manager = Mock()

        result = safe_initialize_services(
            instruction_db=mock_db, template_manager=mock_manager
        )
        assert result is True

    def test_safe_initialize_services_failure(self):
        """Test safe_initialize_services with initialization failure"""
        # Reset engine to ensure clean state
        reset_completion_engine()

        # Mock get_completion_engine to raise an exception
        with patch("agentspec.cli.completion.get_completion_engine") as mock_get_engine:
            mock_get_engine.side_effect = Exception("Initialization failed")

            result = safe_initialize_services()
            assert result is False

    def test_get_completion_engine_error_recovery(self):
        """Test get_completion_engine error recovery"""
        # Reset engine to ensure clean state
        reset_completion_engine()

        # Mock CompletionEngine to fail on first initialization
        with patch("agentspec.cli.completion.CompletionEngine") as mock_engine_class:
            mock_engine_class.side_effect = [
                Exception("First init fails"),
                CompletionEngine(),
            ]

            # First call should handle the error and create a fallback engine
            engine = get_completion_engine()
            assert engine is not None

            # Should have been called twice (first failure, then success)
            assert mock_engine_class.call_count == 2
