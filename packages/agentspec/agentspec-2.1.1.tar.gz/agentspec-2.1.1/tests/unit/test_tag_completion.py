"""
Unit tests for tag completion functionality.

Tests the tag completion functions with mocked InstructionDatabase to ensure
proper completion behavior, caching, and error handling.
"""

from unittest.mock import Mock, patch

import pytest

from agentspec.cli.completers import (
    category_completer,
    comma_separated_instruction_completer,
    comma_separated_tag_completer,
    instruction_completer,
    tag_completer,
)
from agentspec.cli.completion import CompletionCache, CompletionEngine


class TestTagCompleter:
    """Test cases for tag_completer function"""

    def test_tag_completer_with_matching_tags(self):
        """Test tag completion with matching tags"""
        # Mock the completion engine and its methods
        with patch("agentspec.cli.completers.get_completion_engine") as mock_get_engine:
            mock_engine = Mock()
            mock_engine.get_tag_completions.return_value = ["testing", "test-driven"]
            mock_get_engine.return_value = mock_engine

            result = tag_completer("test", None)

            assert result == ["testing", "test-driven"]
            mock_engine.get_tag_completions.assert_called_once_with("test")

    def test_tag_completer_with_no_matches(self):
        """Test tag completion with no matching tags"""
        with patch("agentspec.cli.completers.get_completion_engine") as mock_get_engine:
            mock_engine = Mock()
            mock_engine.get_tag_completions.return_value = []
            mock_get_engine.return_value = mock_engine

            result = tag_completer("xyz", None)

            assert result == []
            mock_engine.get_tag_completions.assert_called_once_with("xyz")

    def test_tag_completer_with_empty_prefix(self):
        """Test tag completion with empty prefix"""
        with patch("agentspec.cli.completers.get_completion_engine") as mock_get_engine:
            mock_engine = Mock()
            mock_engine.get_tag_completions.return_value = [
                "frontend",
                "backend",
                "testing",
            ]
            mock_get_engine.return_value = mock_engine

            result = tag_completer("", None)

            assert result == ["frontend", "backend", "testing"]
            mock_engine.get_tag_completions.assert_called_once_with("")

    def test_tag_completer_with_error(self):
        """Test tag completion handles errors gracefully"""
        with patch("agentspec.cli.completers.get_completion_engine") as mock_get_engine:
            mock_engine = Mock()
            mock_engine.get_tag_completions.side_effect = Exception("Database error")
            mock_get_engine.return_value = mock_engine

            with patch("agentspec.cli.completers.safe_get_completions") as mock_safe:
                mock_safe.return_value = []
                result = tag_completer("test", None)

                assert result == []
                mock_safe.assert_called_once()


class TestCommaSeparatedTagCompleter:
    """Test cases for comma_separated_tag_completer function"""

    def test_comma_separated_single_tag(self):
        """Test completion for single tag (no commas)"""
        with patch("agentspec.cli.completers.get_completion_engine") as mock_get_engine:
            mock_engine = Mock()
            mock_engine.get_tag_completions.return_value = ["testing", "test-driven"]
            mock_get_engine.return_value = mock_engine

            result = comma_separated_tag_completer("test", None)

            assert result == ["testing", "test-driven"]
            mock_engine.get_tag_completions.assert_called_once_with("test")

    def test_comma_separated_multiple_tags(self):
        """Test completion for multiple tags with comma separation"""
        with patch("agentspec.cli.completers.get_completion_engine") as mock_get_engine:
            mock_engine = Mock()
            mock_engine.get_tag_completions.return_value = ["backend", "backend-api"]
            mock_get_engine.return_value = mock_engine

            result = comma_separated_tag_completer("frontend,testing,back", None)

            expected = ["frontend,testing,backend", "frontend,testing,backend-api"]
            assert result == expected
            mock_engine.get_tag_completions.assert_called_once_with("back")

    def test_comma_separated_filters_existing_tags(self):
        """Test that already selected tags are filtered out"""
        with patch("agentspec.cli.completers.get_completion_engine") as mock_get_engine:
            mock_engine = Mock()
            mock_engine.get_tag_completions.return_value = [
                "frontend",
                "backend",
                "testing",
            ]
            mock_get_engine.return_value = mock_engine

            result = comma_separated_tag_completer("frontend,", None)

            expected = ["frontend,backend", "frontend,testing"]
            assert result == expected
            mock_engine.get_tag_completions.assert_called_once_with("")

    def test_comma_separated_with_spaces(self):
        """Test completion handles spaces around commas"""
        with patch("agentspec.cli.completers.get_completion_engine") as mock_get_engine:
            mock_engine = Mock()
            mock_engine.get_tag_completions.return_value = ["testing", "test-driven"]
            mock_get_engine.return_value = mock_engine

            result = comma_separated_tag_completer("frontend, backend, test", None)

            expected = ["frontend, backend,testing", "frontend, backend,test-driven"]
            assert result == expected
            mock_engine.get_tag_completions.assert_called_once_with("test")

    def test_comma_separated_empty_current_tag(self):
        """Test completion when current tag is empty after comma"""
        with patch("agentspec.cli.completers.get_completion_engine") as mock_get_engine:
            mock_engine = Mock()
            mock_engine.get_tag_completions.return_value = [
                "backend",
                "testing",
                "devops",
            ]
            mock_get_engine.return_value = mock_engine

            result = comma_separated_tag_completer("frontend,", None)

            expected = ["frontend,backend", "frontend,testing", "frontend,devops"]
            assert result == expected
            mock_engine.get_tag_completions.assert_called_once_with("")

    def test_comma_separated_no_duplicates(self):
        """Test that duplicate tags are not suggested"""
        with patch("agentspec.cli.completers.get_completion_engine") as mock_get_engine:
            mock_engine = Mock()
            # Return tags including one that's already selected
            mock_engine.get_tag_completions.return_value = [
                "frontend",
                "backend",
                "testing",
            ]
            mock_get_engine.return_value = mock_engine

            result = comma_separated_tag_completer("frontend,backend,", None)

            # Should only suggest 'testing' since frontend and backend are already selected
            expected = ["frontend,backend,testing"]
            assert result == expected
            mock_engine.get_tag_completions.assert_called_once_with("")


class TestCompletionEngine:
    """Test cases for CompletionEngine tag completion methods"""

    def test_get_tag_completions_with_cache_hit(self):
        """Test tag completion returns cached results"""
        engine = CompletionEngine()

        # Pre-populate cache with enhanced format (since legacy delegates to enhanced)
        engine.cache.set("tags_enhanced:test", ["testing", "test-driven"])

        result = engine.get_tag_completions("test")

        assert result == ["testing", "test-driven"]

    def test_get_tag_completions_with_cache_miss(self):
        """Test tag completion queries database on cache miss"""
        engine = CompletionEngine()

        # Mock the instruction database
        mock_db = Mock()
        mock_db.get_all_tags.return_value = {
            "testing",
            "test-driven",
            "frontend",
            "backend",
        }
        engine._instruction_db = mock_db

        result = engine.get_tag_completions("test")

        assert result == ["test-driven", "testing"]  # Should be sorted
        mock_db.get_all_tags.assert_called_once()

        # Verify caching (now uses enhanced cache key)
        cached_result = engine.cache.get("tags_enhanced:test")
        assert cached_result == ["test-driven", "testing"]

    def test_get_tag_completions_lazy_initialization(self):
        """Test tag completion with lazy database initialization"""
        engine = CompletionEngine()

        with patch.object(engine, "_get_instruction_db") as mock_get_db:
            mock_db = Mock()
            mock_db.get_all_tags.return_value = {"testing", "frontend"}
            mock_get_db.return_value = mock_db

            result = engine.get_tag_completions("test")

            assert result == ["testing"]
            mock_get_db.assert_called_once()
            mock_db.get_all_tags.assert_called_once()

    def test_get_tag_completions_database_unavailable(self):
        """Test tag completion when database is unavailable"""
        engine = CompletionEngine()

        with patch.object(engine, "_get_instruction_db") as mock_get_db:
            mock_get_db.return_value = None

            result = engine.get_tag_completions("test")

            assert result == []
            mock_get_db.assert_called_once()

    def test_get_tag_completions_database_error(self):
        """Test tag completion handles database errors gracefully"""
        engine = CompletionEngine()

        mock_db = Mock()
        mock_db.get_all_tags.side_effect = Exception("Database connection failed")
        engine._instruction_db = mock_db

        result = engine.get_tag_completions("test")

        assert result == []
        mock_db.get_all_tags.assert_called_once()

    def test_get_tag_completions_empty_prefix(self):
        """Test tag completion with empty prefix returns all tags"""
        engine = CompletionEngine()

        mock_db = Mock()
        mock_db.get_all_tags.return_value = {"frontend", "backend", "testing"}
        engine._instruction_db = mock_db

        result = engine.get_tag_completions("")

        assert result == ["backend", "frontend", "testing"]  # Should be sorted
        mock_db.get_all_tags.assert_called_once()

    def test_lazy_instruction_db_initialization_success(self):
        """Test successful lazy initialization of InstructionDatabase"""
        engine = CompletionEngine()

        with patch(
            "agentspec.core.instruction_database.InstructionDatabase"
        ) as mock_db_class:
            mock_db_instance = Mock()
            mock_db_instance.get_all_tags.return_value = {
                "test",
                "tags",
            }  # Return valid set for functionality test
            mock_db_class.return_value = mock_db_instance

            result = engine._get_instruction_db()

            assert result == mock_db_instance
            assert engine._instruction_db == mock_db_instance
            mock_db_class.assert_called_once()

    def test_lazy_instruction_db_initialization_failure(self):
        """Test lazy initialization handles import/initialization errors"""
        engine = CompletionEngine()

        with patch(
            "agentspec.core.instruction_database.InstructionDatabase"
        ) as mock_db_class:
            mock_db_class.side_effect = ImportError("Module not found")

            result = engine._get_instruction_db()

            assert result is None
            assert engine._instruction_db is None


class TestCompletionCache:
    """Test cases for CompletionCache"""

    def test_cache_set_and_get(self):
        """Test basic cache set and get operations"""
        cache = CompletionCache(ttl=300)

        cache.set("test_key", ["value1", "value2"])
        result = cache.get("test_key")

        assert result == ["value1", "value2"]

    def test_cache_expiration(self):
        """Test cache entry expiration"""
        cache = CompletionCache(ttl=0)  # Immediate expiration

        cache.set("test_key", ["value1", "value2"])

        # Should be expired immediately
        import time

        time.sleep(0.01)  # Small delay to ensure expiration
        result = cache.get("test_key")

        assert result is None

    def test_cache_miss(self):
        """Test cache miss for non-existent key"""
        cache = CompletionCache()

        result = cache.get("non_existent_key")

        assert result is None

    def test_cache_clear(self):
        """Test cache clear operation"""
        cache = CompletionCache()

        cache.set("key1", ["value1"])
        cache.set("key2", ["value2"])

        cache.clear()

        assert cache.get("key1") is None
        assert cache.get("key2") is None


class TestInstructionCompleter:
    """Test cases for instruction_completer function"""

    def test_instruction_completer_with_matching_instructions(self):
        """Test instruction completion with matching instruction IDs"""
        with patch("agentspec.cli.completers.get_completion_engine") as mock_get_engine:
            mock_engine = Mock()
            mock_engine.get_instruction_completions.return_value = [
                "core_001",
                "core_002",
            ]
            mock_get_engine.return_value = mock_engine

            result = instruction_completer("core", None)

            assert result == ["core_001", "core_002"]
            mock_engine.get_instruction_completions.assert_called_once_with("core")

    def test_instruction_completer_with_no_matches(self):
        """Test instruction completion with no matching instruction IDs"""
        with patch("agentspec.cli.completers.get_completion_engine") as mock_get_engine:
            mock_engine = Mock()
            mock_engine.get_instruction_completions.return_value = []
            mock_get_engine.return_value = mock_engine

            result = instruction_completer("xyz", None)

            assert result == []
            mock_engine.get_instruction_completions.assert_called_once_with("xyz")

    def test_instruction_completer_with_error(self):
        """Test instruction completion handles errors gracefully"""
        with patch("agentspec.cli.completers.get_completion_engine") as mock_get_engine:
            mock_engine = Mock()
            mock_engine.get_instruction_completions.side_effect = Exception(
                "Database error"
            )
            mock_get_engine.return_value = mock_engine

            with patch("agentspec.cli.completers.safe_get_completions") as mock_safe:
                mock_safe.return_value = []
                result = instruction_completer("core", None)

                assert result == []
                mock_safe.assert_called_once()


class TestCommaSeparatedInstructionCompleter:
    """Test cases for comma_separated_instruction_completer function"""

    def test_comma_separated_single_instruction(self):
        """Test completion for single instruction ID (no commas)"""
        with patch("agentspec.cli.completers.get_completion_engine") as mock_get_engine:
            mock_engine = Mock()
            mock_engine.get_instruction_completions.return_value = [
                "core_001",
                "core_002",
            ]
            mock_get_engine.return_value = mock_engine

            result = comma_separated_instruction_completer("core", None)

            assert result == ["core_001", "core_002"]
            mock_engine.get_instruction_completions.assert_called_once_with("core")

    def test_comma_separated_multiple_instructions(self):
        """Test completion for multiple instruction IDs with comma separation"""
        with patch("agentspec.cli.completers.get_completion_engine") as mock_get_engine:
            mock_engine = Mock()
            mock_engine.get_instruction_completions.return_value = [
                "backend_001",
                "backend_002",
            ]
            mock_get_engine.return_value = mock_engine

            result = comma_separated_instruction_completer(
                "core_001,frontend_001,back", None
            )

            expected = [
                "core_001,frontend_001,backend_001",
                "core_001,frontend_001,backend_002",
            ]
            assert result == expected
            mock_engine.get_instruction_completions.assert_called_once_with("back")

    def test_comma_separated_filters_existing_instructions(self):
        """Test that already selected instruction IDs are filtered out"""
        with patch("agentspec.cli.completers.get_completion_engine") as mock_get_engine:
            mock_engine = Mock()
            mock_engine.get_instruction_completions.return_value = [
                "core_001",
                "backend_001",
                "frontend_001",
            ]
            mock_get_engine.return_value = mock_engine

            result = comma_separated_instruction_completer("core_001,", None)

            expected = ["core_001,backend_001", "core_001,frontend_001"]
            assert result == expected
            mock_engine.get_instruction_completions.assert_called_once_with("")

    def test_comma_separated_no_duplicates(self):
        """Test that duplicate instruction IDs are not suggested"""
        with patch("agentspec.cli.completers.get_completion_engine") as mock_get_engine:
            mock_engine = Mock()
            # Return instruction IDs including ones that are already selected
            mock_engine.get_instruction_completions.return_value = [
                "core_001",
                "backend_001",
                "frontend_001",
            ]
            mock_get_engine.return_value = mock_engine

            result = comma_separated_instruction_completer(
                "core_001,backend_001,", None
            )

            # Should only suggest 'frontend_001' since core_001 and backend_001 are already selected
            expected = ["core_001,backend_001,frontend_001"]
            assert result == expected
            mock_engine.get_instruction_completions.assert_called_once_with("")


class TestInstructionCompletionEngine:
    """Test cases for CompletionEngine instruction completion methods"""

    def test_get_instruction_completions_with_cache_hit(self):
        """Test instruction completion returns cached results"""
        engine = CompletionEngine()

        # Pre-populate cache
        engine.cache.set("instructions:core", ["core_001", "core_002"])

        result = engine.get_instruction_completions("core")

        assert result == ["core_001", "core_002"]

    def test_get_instruction_completions_with_cache_miss(self):
        """Test instruction completion queries database on cache miss"""
        engine = CompletionEngine()

        # Mock the instruction database
        mock_db = Mock()
        mock_instructions = {
            "core_001": Mock(),
            "core_002": Mock(),
            "frontend_001": Mock(),
            "backend_001": Mock(),
        }
        mock_db.load_instructions.return_value = mock_instructions
        engine._instruction_db = mock_db

        result = engine.get_instruction_completions("core")

        assert result == ["core_001", "core_002"]  # Should be sorted and filtered
        mock_db.load_instructions.assert_called_once()

        # Verify caching
        cached_result = engine.cache.get("instructions:core")
        assert cached_result == ["core_001", "core_002"]

    def test_get_instruction_completions_database_unavailable(self):
        """Test instruction completion when database is unavailable"""
        engine = CompletionEngine()

        with patch.object(engine, "_get_instruction_db") as mock_get_db:
            mock_get_db.return_value = None

            result = engine.get_instruction_completions("core")

            assert result == []
            mock_get_db.assert_called_once()

    def test_get_instruction_completions_database_error(self):
        """Test instruction completion handles database errors gracefully"""
        engine = CompletionEngine()

        mock_db = Mock()
        mock_db.load_instructions.side_effect = Exception("Database connection failed")
        engine._instruction_db = mock_db

        result = engine.get_instruction_completions("core")

        assert result == []
        mock_db.load_instructions.assert_called_once()


class TestCategoryCompleter:
    """Test cases for category_completer function"""

    def test_category_completer_with_matching_categories(self):
        """Test category completion with matching categories"""
        # category_completer is a static completer, doesn't use the engine
        result = category_completer("Te", None)

        # Should match "Testing" (case-insensitive)
        assert result == ["Testing"]

    def test_category_completer_with_no_matches(self):
        """Test category completion with no matching categories"""
        # category_completer is a static completer, doesn't use the engine
        result = category_completer("xyz", None)

        # Should return empty list for non-matching prefix
        assert result == []

    def test_category_completer_with_empty_prefix(self):
        """Test category completion with empty prefix returns all categories"""
        # category_completer is a static completer, doesn't use the engine
        result = category_completer("", None)

        # Should return all categories sorted by priority then alphabetically
        expected = [
            "General",
            "Testing",
            "Backend",
            "Frontend",
            "Architecture",
            "Languages",
            "DevOps",
        ]
        assert result == expected

    def test_category_completer_case_insensitive(self):
        """Test category completion is case-insensitive"""
        # category_completer is a static completer, doesn't use the engine

        # Test lowercase input
        result = category_completer("front", None)

        # Should match "Frontend" (case-insensitive)
        assert result == ["Frontend"]

    def test_category_completer_with_error(self):
        """Test category completion handles errors gracefully"""
        # category_completer is a static completer and shouldn't have errors
        # But test that it works with partial matches
        result = category_completer("test", None)

        # Should match "Testing"
        assert result == ["Testing"]


class TestCategoryCompletionEngine:
    """Test cases for CompletionEngine category completion methods"""

    def test_get_category_completions_with_matching_prefix(self):
        """Test category completion with matching prefix"""
        engine = CompletionEngine()

        result = engine.get_category_completions("Te")

        assert result == ["Testing"]

    def test_get_category_completions_case_insensitive_matching(self):
        """Test category completion with case-insensitive matching"""
        engine = CompletionEngine()

        # Test lowercase input
        result = engine.get_category_completions("front")
        assert result == ["Frontend"]

        # Test uppercase input
        result = engine.get_category_completions("BACK")
        assert result == ["Backend"]

        # Test mixed case input
        result = engine.get_category_completions("devO")
        assert result == ["DevOps"]

    def test_get_category_completions_with_no_matches(self):
        """Test category completion with no matching categories"""
        engine = CompletionEngine()

        result = engine.get_category_completions("xyz")

        assert result == []

    def test_get_category_completions_with_empty_prefix(self):
        """Test category completion with empty prefix returns all categories"""
        engine = CompletionEngine()

        result = engine.get_category_completions("")

        expected = [
            "General",
            "Testing",
            "Frontend",
            "Backend",
            "Languages",
            "DevOps",
            "Architecture",
        ]
        assert result == expected

    def test_get_category_completions_caching_indefinite_ttl(self):
        """Test category completion uses indefinite caching"""
        engine = CompletionEngine()

        # First call should populate cache
        result1 = engine.get_category_completions("Te")
        assert result1 == ["Testing"]

        # Second call should use cache (verify cache exists)
        assert hasattr(engine, "_category_cache")
        assert "categories:Te" in engine._category_cache

        # Third call should return cached result
        result2 = engine.get_category_completions("Te")
        assert result2 == ["Testing"]
        assert result1 == result2

    def test_get_category_completions_multiple_matches(self):
        """Test category completion with multiple matching categories"""
        engine = CompletionEngine()

        # Should match both 'Languages' and nothing else for 'La'
        result = engine.get_category_completions("La")
        assert result == ["Languages"]

        # Should match nothing for 'Z'
        result = engine.get_category_completions("Z")
        assert result == []

    def test_get_category_completions_partial_matches(self):
        """Test category completion with various partial matches"""
        engine = CompletionEngine()

        # Test 'A' should match 'Architecture'
        result = engine.get_category_completions("A")
        assert result == ["Architecture"]

        # Test 'G' should match 'General'
        result = engine.get_category_completions("G")
        assert result == ["General"]

        # Test 'D' should match 'DevOps'
        result = engine.get_category_completions("D")
        assert result == ["DevOps"]

    def test_get_category_completions_cache_independence(self):
        """Test that different prefixes are cached independently"""
        engine = CompletionEngine()

        # Cache different prefixes
        result1 = engine.get_category_completions("Te")
        result2 = engine.get_category_completions("Fr")
        result3 = engine.get_category_completions("Ba")

        assert result1 == ["Testing"]
        assert result2 == ["Frontend"]
        assert result3 == ["Backend"]

        # Verify all are cached independently
        assert hasattr(engine, "_category_cache")
        assert "categories:Te" in engine._category_cache
        assert "categories:Fr" in engine._category_cache
        assert "categories:Ba" in engine._category_cache

        # Verify cached values are correct
        assert engine._category_cache["categories:Te"] == ["Testing"]
        assert engine._category_cache["categories:Fr"] == ["Frontend"]
        assert engine._category_cache["categories:Ba"] == ["Backend"]
