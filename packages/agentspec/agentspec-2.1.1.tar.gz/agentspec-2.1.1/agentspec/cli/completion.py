"""
Completion infrastructure for AgentSpec CLI.

This module provides the core completion engine and cache infrastructure
for shell autocomplete functionality using argcomplete.
"""

# mypy: disable-error-code=unreachable

import logging
import threading
import time
from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)


@dataclass
class CompletionItem:
    """Represents a single completion item with optional description and metadata"""

    value: str
    description: Optional[str] = None
    category: Optional[str] = None
    priority: int = 0  # Higher priority items appear first

    def __str__(self) -> str:
        return self.value


@dataclass
class CompletionResult:
    """Enhanced completion result with descriptions and grouping"""

    items: List[CompletionItem]
    grouped_items: Optional[Dict[str, List[CompletionItem]]] = None

    def to_string_list(self) -> List[str]:
        """Convert to simple string list for argcomplete compatibility"""
        return [item.value for item in self.items]

    def get_sorted_items(self) -> List[CompletionItem]:
        """Get items sorted by priority (descending) then alphabetically"""
        return sorted(self.items, key=lambda x: (-x.priority, x.value.lower()))


# Performance monitoring constants
COMPLETION_TIMEOUT = 1.0  # 1 second maximum timeout
MAX_CACHE_SIZE = 100  # Maximum number of cache entries
CACHE_CLEANUP_THRESHOLD = 0.8  # Cleanup when cache reaches 80% capacity


def with_timeout(
    timeout_seconds: float = COMPLETION_TIMEOUT,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator to add timeout handling to completion functions.

    Args:
        timeout_seconds: Maximum time to wait for completion

    Returns:
        Decorated function that respects timeout
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Handle invalid timeout values
            if timeout_seconds <= 0:
                logger.debug(f"Invalid timeout {timeout_seconds}, returning empty list")
                # Return appropriate empty result based on function name
                if "enhanced" in func.__name__:
                    return CompletionResult(items=[])
                else:
                    return []

            result = []
            exception = None

            def target() -> None:
                nonlocal result, exception
                try:
                    result = func(*args, **kwargs)
                except Exception as e:
                    exception = e

            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(timeout_seconds)

            if thread.is_alive():
                logger.debug(
                    f"Completion function {func.__name__} timed out after {timeout_seconds}s"
                )
                # Return appropriate empty result based on function name
                if "enhanced" in func.__name__:
                    return CompletionResult(items=[])
                else:
                    return []

            if exception:
                logger.debug(f"Completion function {func.__name__} failed: {exception}")
                # Return appropriate empty result based on function name
                if "enhanced" in func.__name__:
                    return CompletionResult(items=[])
                else:
                    return []

            # Handle None results
            if result is None:
                if "enhanced" in func.__name__:
                    return CompletionResult(items=[])
                else:
                    return []

            return result

        return wrapper

    return decorator


class CompletionCache:
    """Lightweight cache for completion data with TTL-based expiration and size limits"""

    def __init__(self, ttl: int = 300, max_size: int = MAX_CACHE_SIZE) -> None:
        """
        Initialize completion cache.

        Args:
            ttl: Time-to-live in seconds (default: 5 minutes)
            max_size: Maximum number of cache entries
        """
        self._cache: Dict[str, Tuple[float, List[str]]] = {}
        self.ttl = ttl
        self.max_size = max_size
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[List[str]]:
        """
        Get cached completion data.

        Args:
            key: Cache key

        Returns:
            Cached completion list or None if not found/expired
        """
        # Validate key for robustness
        if not isinstance(key, str) or not key:
            logger.debug(f"Invalid cache key for get: {key}")
            return None

        with self._lock:
            try:
                if key not in self._cache:
                    return None
            except TypeError:
                # Handle unhashable key types
                logger.debug(f"Unhashable cache key: {key}")
                return None

            timestamp, data = self._cache[key]
            current_time = time.time()

            if current_time - timestamp > self.ttl:
                # Entry expired, remove it
                del self._cache[key]
                logger.debug(f"Cache entry expired and removed: {key}")
                return None

            logger.debug(
                f"Cache hit for key: {key} (age: {current_time - timestamp:.2f}s)"
            )
            return data

    def set(self, key: str, data: List[str]) -> None:
        """
        Cache completion data with automatic cleanup when size limit is reached.

        Args:
            key: Cache key
            data: Completion data to cache
        """
        # Validate inputs for robustness
        if not isinstance(key, str) or not key:
            logger.debug(f"Invalid cache key: {key}")
            return

        if data is None:
            logger.debug("Cannot cache None data")
            return

        if not isinstance(data, list):
            logger.debug(f"Invalid data type for caching: {type(data)}")
            return

        # Handle zero size limit
        if self.max_size <= 0:
            logger.debug("Cache disabled (max_size <= 0)")
            return

        with self._lock:
            current_time = time.time()

            # Check if we need to cleanup before adding new entry
            if len(self._cache) >= self.max_size * CACHE_CLEANUP_THRESHOLD:
                self._cleanup_expired_entries(current_time)

                # If still at capacity after cleanup, remove oldest entries
                if len(self._cache) >= self.max_size:
                    self._remove_oldest_entries()

            # Create a copy to preserve data integrity
            data_copy = list(data)
            self._cache[key] = (current_time, data_copy)
            logger.debug(
                f"Cached completion data for key: {key} ({len(data_copy)} items)"
            )

    def _cleanup_expired_entries(self, current_time: float) -> None:
        """
        Remove expired entries from cache.

        Args:
            current_time: Current timestamp for comparison
        """
        expired_keys = []
        for key, (timestamp, _) in self._cache.items():
            if current_time - timestamp > self.ttl:
                expired_keys.append(key)

        for key in expired_keys:
            del self._cache[key]

        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")

    def _remove_oldest_entries(self) -> None:
        """Remove oldest entries to make room for new ones."""
        # Sort by timestamp and remove oldest 20% of entries
        entries_by_age = sorted(self._cache.items(), key=lambda x: x[1][0])
        entries_to_remove = max(
            1, len(entries_by_age) // 5
        )  # Remove at least 1, up to 20%

        for key, _ in entries_by_age[:entries_to_remove]:
            del self._cache[key]

        logger.debug(f"Removed {entries_to_remove} oldest cache entries to make room")

    def clear(self) -> None:
        """Clear all cached data"""
        with self._lock:
            cache_size = len(self._cache)
            self._cache.clear()
            logger.debug(f"Cleared cache ({cache_size} entries)")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics for monitoring.

        Returns:
            Dictionary with cache statistics
        """
        with self._lock:
            current_time = time.time()
            expired_count = 0
            total_entries = len(self._cache)

            for timestamp, _ in self._cache.values():
                if current_time - timestamp > self.ttl:
                    expired_count += 1

            return {
                "total_entries": total_entries,
                "expired_entries": expired_count,
                "active_entries": total_entries - expired_count,
                "max_size": self.max_size,
                "utilization": (
                    total_entries / self.max_size if self.max_size > 0 else 0
                ),
            }


class CompletionEngine:
    """Central completion engine that coordinates all completion operations"""

    def __init__(self) -> None:
        """Initialize completion engine with cache and performance monitoring"""
        self.cache = CompletionCache()
        self._instruction_db: Optional[Any] = None
        self._template_manager: Optional[Any] = None
        self._service_init_lock = threading.Lock()
        self._category_cache: Dict[str, List[str]] = {}
        self._category_cache_enhanced: Dict[str, CompletionResult] = {}
        self._performance_stats: Dict[str, Union[int, float]] = {
            "total_completions": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "timeouts": 0,
            "errors": 0,
            "avg_response_time": 0.0,
        }

    def set_services(
        self,
        instruction_db: Optional[Any] = None,
        template_manager: Optional[Any] = None,
    ) -> None:
        """
        Set service dependencies for dynamic completions.

        Args:
            instruction_db: InstructionDatabase instance
            template_manager: TemplateManager instance
        """
        with self._service_init_lock:
            self._instruction_db = instruction_db
            self._template_manager = template_manager
            self._services_explicitly_set = True

            # Clear cache when services change to ensure fresh results
            self.cache.clear()

            logger.debug("Services set for completion engine")

    def _get_instruction_db(self) -> Optional[Any]:
        """
        Get InstructionDatabase instance with lazy initialization fallback.

        Returns the service set via set_services, or attempts lazy initialization
        if no service was explicitly set.

        Handles various failure scenarios:
        - Import errors (missing dependencies)
        - File system errors (missing data files, permissions)
        - Configuration errors (invalid config)
        - Initialization timeouts

        Returns:
            InstructionDatabase instance or None if initialization fails

        Requirements: 3.4, 11.3 - Graceful degradation for service initialization failures
        """
        with self._service_init_lock:
            # Return existing service if available
            if self._instruction_db is not None:
                return self._instruction_db

            # Only attempt lazy initialization if no service was explicitly set to None
            if not hasattr(self, "_services_explicitly_set"):
                self._services_explicitly_set = False

            if self._services_explicitly_set and self._instruction_db is None:
                # Service was explicitly set to None, don't try to initialize
                return None

            # Attempt lazy initialization
            start_time = time.time()
            try:
                # Import with error handling
                from ..core.instruction_database import InstructionDatabase

                # Initialize with timeout protection
                self._instruction_db = InstructionDatabase()

                # Verify the database is functional by attempting to load data
                try:
                    # Test basic functionality
                    test_tags = self._instruction_db.get_all_tags()
                    if not isinstance(test_tags, (set, list)):
                        raise ValueError(
                            "InstructionDatabase.get_all_tags() returned invalid type"
                        )
                except Exception as test_error:
                    logger.warning(
                        f"InstructionDatabase initialized but failed functionality test: {test_error}"
                    )
                    self._instruction_db = None
                    self._performance_stats["errors"] += 1
                    return None

                init_time = time.time() - start_time
                logger.debug(
                    f"Successfully initialized InstructionDatabase for completion in {init_time:.3f}s"
                )

            except ImportError as e:
                init_time = time.time() - start_time
                logger.warning(
                    f"Failed to import InstructionDatabase after {init_time:.3f}s: {e}"
                )
                logger.debug(
                    "Completion will degrade gracefully without instruction database"
                )
                self._performance_stats["errors"] += 1
                return None

            except FileNotFoundError as e:
                init_time = time.time() - start_time
                logger.warning(
                    f"InstructionDatabase data files not found after {init_time:.3f}s: {e}"
                )
                logger.debug("Check AgentSpec installation and data file integrity")
                self._performance_stats["errors"] += 1
                return None

            except PermissionError as e:
                init_time = time.time() - start_time
                logger.warning(
                    f"Permission error initializing InstructionDatabase after {init_time:.3f}s: {e}"
                )
                logger.debug("Check file permissions for AgentSpec data directory")
                self._performance_stats["errors"] += 1
                return None

            except (ValueError, TypeError, KeyError) as e:
                init_time = time.time() - start_time
                logger.warning(
                    f"Configuration error initializing InstructionDatabase after {init_time:.3f}s: {e}"
                )
                logger.debug("Check AgentSpec configuration and data file format")
                self._performance_stats["errors"] += 1
                return None

            except Exception as e:
                init_time = time.time() - start_time
                logger.error(
                    f"Unexpected error initializing InstructionDatabase after {init_time:.3f}s: {e}"
                )
                logger.debug(
                    "InstructionDatabase initialization failed with unexpected error",
                    exc_info=True,
                )
                self._performance_stats["errors"] += 1
                return None

            return self._instruction_db

    def _get_template_manager(self) -> Optional[Any]:
        """
        Lazily initialize TemplateManager with comprehensive error handling.

        Handles various failure scenarios:
        - Import errors (missing dependencies)
        - File system errors (missing template files, permissions)
        - Configuration errors (invalid template format)
        - Initialization timeouts

        Returns:
            TemplateManager instance or None if initialization fails

        Requirements: 4.4, 11.3 - Graceful degradation for service initialization failures
        """
        with self._service_init_lock:
            if self._template_manager is None:
                start_time = time.time()
                try:
                    # Import with error handling
                    from ..core.template_manager import TemplateManager

                    # Initialize with timeout protection
                    self._template_manager = TemplateManager()

                    # Verify the template manager is functional by attempting to load data
                    try:
                        # Test basic functionality
                        test_templates = self._template_manager.get_all_template_ids()
                        if not isinstance(test_templates, (set, list)):
                            raise ValueError(
                                "TemplateManager.get_all_template_ids() returned invalid type"
                            )
                    except Exception as test_error:
                        logger.warning(
                            f"TemplateManager initialized but failed functionality test: {test_error}"
                        )
                        self._template_manager = None
                        self._performance_stats["errors"] += 1
                        return None

                    init_time = time.time() - start_time
                    logger.debug(
                        f"Successfully initialized TemplateManager for completion in {init_time:.3f}s"
                    )

                except ImportError as e:
                    init_time = time.time() - start_time
                    logger.warning(
                        f"Failed to import TemplateManager after {init_time:.3f}s: {e}"
                    )
                    logger.debug(
                        "Completion will degrade gracefully without template manager"
                    )
                    self._performance_stats["errors"] += 1
                    return None

                except FileNotFoundError as e:
                    init_time = time.time() - start_time
                    logger.warning(
                        f"TemplateManager template files not found after {init_time:.3f}s: {e}"
                    )
                    logger.debug(
                        "Check AgentSpec installation and template file integrity"
                    )
                    self._performance_stats["errors"] += 1
                    return None

                except PermissionError as e:
                    init_time = time.time() - start_time
                    logger.warning(
                        f"Permission error initializing TemplateManager after {init_time:.3f}s: {e}"
                    )
                    logger.debug(
                        "Check file permissions for AgentSpec template directory"
                    )
                    self._performance_stats["errors"] += 1
                    return None

                except (ValueError, TypeError, KeyError) as e:
                    init_time = time.time() - start_time
                    logger.warning(
                        f"Configuration error initializing TemplateManager after {init_time:.3f}s: {e}"
                    )
                    logger.debug(
                        "Check AgentSpec configuration and template file format"
                    )
                    self._performance_stats["errors"] += 1
                    return None

                except Exception as e:
                    init_time = time.time() - start_time
                    logger.error(
                        f"Unexpected error initializing TemplateManager after {init_time:.3f}s: {e}"
                    )
                    logger.debug(
                        "TemplateManager initialization failed with unexpected error",
                        exc_info=True,
                    )
                    self._performance_stats["errors"] += 1
                    return None

            return self._template_manager

    def _record_completion_stats(
        self,
        start_time: float,
        cache_hit: bool,
        error: bool = False,
        timeout: bool = False,
    ) -> None:
        """
        Record performance statistics for completion operations.

        Args:
            start_time: When the completion operation started
            cache_hit: Whether this was a cache hit
            error: Whether an error occurred
            timeout: Whether the operation timed out
        """
        response_time = time.time() - start_time

        self._performance_stats["total_completions"] += 1
        if cache_hit:
            self._performance_stats["cache_hits"] += 1
        else:
            self._performance_stats["cache_misses"] += 1

        if error:
            self._performance_stats["errors"] += 1
        if timeout:
            self._performance_stats["timeouts"] += 1

        # Update rolling average response time
        total = int(self._performance_stats["total_completions"])
        current_avg = float(self._performance_stats["avg_response_time"])
        self._performance_stats["avg_response_time"] = (
            (current_avg * (total - 1)) + response_time
        ) / total

        logger.debug(
            f"Completion stats - Response time: {response_time:.3f}s, Cache hit: {cache_hit}, Error: {error}, Timeout: {timeout}"
        )

    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics for monitoring.

        Returns:
            Dictionary with performance statistics
        """
        stats: Dict[str, Any] = self._performance_stats.copy()
        stats["cache_stats"] = self.cache.get_stats()
        return stats

    def reset_performance_stats(self) -> None:
        """
        Reset performance statistics for testing.
        """
        self._performance_stats = {
            "total_completions": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "timeouts": 0,
            "errors": 0,
            "avg_response_time": 0.0,
        }

    def get_tag_completions(self, prefix: str) -> List[str]:
        """Legacy method for backward compatibility"""
        # Simply delegate to enhanced method and convert result
        # Let the enhanced method handle all caching and stats
        try:
            result = self.get_tag_completions_enhanced(prefix)
            string_list: List[str] = result.to_string_list()
            return string_list
        except Exception:
            return []

    @with_timeout()
    def get_tag_completions_enhanced(self, prefix: str) -> CompletionResult:
        """
        Get enhanced tag completions with descriptions and categorization.

        Args:
            prefix: Prefix to filter tags

        Returns:
            CompletionResult with tag completions, descriptions, and grouping

        Requirements: 12.1, 12.2, 12.3, 12.4 - Contextual help and descriptions
        """
        start_time = time.time()
        cache_key = f"tags_enhanced:{prefix}"

        # Validate input
        if not isinstance(prefix, str):
            logger.warning(f"Invalid prefix type for tag completion: {type(prefix)}")
            self._record_completion_stats(start_time, cache_hit=False, error=True)
            return CompletionResult(items=[])

        # Check cache first (for enhanced results)
        cached = self.cache.get(cache_key)
        if cached is not None:
            self._record_completion_stats(start_time, cache_hit=True)
            logger.debug(f"Cache hit for enhanced tag completions: {prefix}")
            # Reconstruct CompletionResult from cached data
            items = [CompletionItem(value=item) for item in cached]
            return CompletionResult(items=items)

        try:
            # Attempt to get instruction database with error handling
            instruction_db = self._get_instruction_db()
            if instruction_db is None:
                self._record_completion_stats(start_time, cache_hit=False, error=True)
                logger.debug(
                    "InstructionDatabase not available for tag completion - providing empty completions"
                )
                # Cache empty result to avoid repeated failed attempts
                self.cache.set(cache_key, [])
                return CompletionResult(items=[])

            # Attempt to get tags with data loading error handling
            try:
                all_tags = instruction_db.get_all_tags()
                if not isinstance(all_tags, (set, list)):
                    raise ValueError(
                        f"get_all_tags() returned invalid type: {type(all_tags)}"
                    )

                # Convert to list if it's a set
                if isinstance(all_tags, set):
                    all_tags = list(all_tags)

                # Get tag metadata for descriptions and categorization
                tag_metadata = self._get_tag_metadata(instruction_db, all_tags)

            except (FileNotFoundError, PermissionError) as e:
                logger.warning(f"Data loading error for tag completions: {e}")
                self._record_completion_stats(start_time, cache_hit=False, error=True)
                # Cache empty result to avoid repeated failed attempts
                self.cache.set(cache_key, [])
                return CompletionResult(items=[])

            except Exception as e:
                logger.warning(f"Unexpected error loading tags: {e}")
                self._record_completion_stats(start_time, cache_hit=False, error=True)
                # Cache empty result to avoid repeated failed attempts
                self.cache.set(cache_key, [])
                return CompletionResult(items=[])

            # Filter and validate tags with enhanced metadata
            try:
                completion_items = []
                for tag in all_tags:
                    if isinstance(tag, str) and tag.startswith(prefix):
                        metadata = tag_metadata.get(tag, {})
                        item = CompletionItem(
                            value=tag,
                            description=metadata.get("description"),
                            category=metadata.get("category"),
                            priority=metadata.get("priority", 0),
                        )
                        completion_items.append(item)
                    elif not isinstance(tag, str):
                        logger.debug(f"Skipping non-string tag: {type(tag)}")

                # Sort items alphabetically for consistency with legacy behavior
                completion_items.sort(key=lambda x: x.value)

                # Create result with grouping by category
                result = CompletionResult(items=completion_items)
                result.grouped_items = self._group_items_by_category(completion_items)

                # Cache successful result (just the values for backward compatibility)
                cache_values = [item.value for item in completion_items]
                self.cache.set(cache_key, cache_values)
                self._record_completion_stats(start_time, cache_hit=False)
                logger.debug(
                    f"Generated {len(completion_items)} enhanced tag completions for: {prefix}"
                )
                return result

            except Exception as e:
                logger.warning(f"Error filtering tag completions: {e}")
                self._record_completion_stats(start_time, cache_hit=False, error=True)
                return CompletionResult(items=[])

        except Exception as e:
            self._record_completion_stats(start_time, cache_hit=False, error=True)
            logger.error(f"Unexpected error in get_tag_completions_enhanced: {e}")
            logger.debug(
                "Enhanced tag completion failed with unexpected error", exc_info=True
            )
            return CompletionResult(items=[])

    def _get_tag_metadata(
        self, instruction_db: Any, tags: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get metadata for tags including descriptions and categories.

        Args:
            instruction_db: InstructionDatabase instance
            tags: List of tags to get metadata for

        Returns:
            Dictionary mapping tag names to metadata
        """
        tag_metadata = {}

        try:
            # Load all instructions to analyze tag usage
            instructions = instruction_db.load_instructions()

            # Define tag categories and priorities based on common usage patterns
            tag_categories = {
                # Core development tags
                "core": {
                    "category": "Core",
                    "priority": 10,
                    "description": "Essential development practices",
                },
                "workflow": {
                    "category": "Core",
                    "priority": 9,
                    "description": "Development workflow guidelines",
                },
                "planning": {
                    "category": "Core",
                    "priority": 8,
                    "description": "Project planning and organization",
                },
                # Frontend development
                "frontend": {
                    "category": "Frontend",
                    "priority": 7,
                    "description": "Frontend development practices",
                },
                "react": {
                    "category": "Frontend",
                    "priority": 6,
                    "description": "React framework guidelines",
                },
                "vue": {
                    "category": "Frontend",
                    "priority": 6,
                    "description": "Vue.js framework guidelines",
                },
                "angular": {
                    "category": "Frontend",
                    "priority": 6,
                    "description": "Angular framework guidelines",
                },
                "css": {
                    "category": "Frontend",
                    "priority": 5,
                    "description": "CSS styling guidelines",
                },
                "html": {
                    "category": "Frontend",
                    "priority": 5,
                    "description": "HTML markup guidelines",
                },
                "javascript": {
                    "category": "Frontend",
                    "priority": 6,
                    "description": "JavaScript development practices",
                },
                "typescript": {
                    "category": "Frontend",
                    "priority": 6,
                    "description": "TypeScript development practices",
                },
                # Backend development
                "backend": {
                    "category": "Backend",
                    "priority": 7,
                    "description": "Backend development practices",
                },
                "api": {
                    "category": "Backend",
                    "priority": 6,
                    "description": "API design and implementation",
                },
                "database": {
                    "category": "Backend",
                    "priority": 6,
                    "description": "Database design and management",
                },
                "server": {
                    "category": "Backend",
                    "priority": 5,
                    "description": "Server configuration and management",
                },
                # Programming languages
                "python": {
                    "category": "Languages",
                    "priority": 6,
                    "description": "Python programming guidelines",
                },
                "java": {
                    "category": "Languages",
                    "priority": 6,
                    "description": "Java programming guidelines",
                },
                "csharp": {
                    "category": "Languages",
                    "priority": 6,
                    "description": "C# programming guidelines",
                },
                "go": {
                    "category": "Languages",
                    "priority": 6,
                    "description": "Go programming guidelines",
                },
                "rust": {
                    "category": "Languages",
                    "priority": 6,
                    "description": "Rust programming guidelines",
                },
                # Testing and quality
                "testing": {
                    "category": "Testing",
                    "priority": 8,
                    "description": "Testing strategies and practices",
                },
                "unit-testing": {
                    "category": "Testing",
                    "priority": 7,
                    "description": "Unit testing guidelines",
                },
                "integration-testing": {
                    "category": "Testing",
                    "priority": 6,
                    "description": "Integration testing practices",
                },
                "e2e-testing": {
                    "category": "Testing",
                    "priority": 6,
                    "description": "End-to-end testing strategies",
                },
                "code-quality": {
                    "category": "Testing",
                    "priority": 7,
                    "description": "Code quality and standards",
                },
                # DevOps and deployment
                "devops": {
                    "category": "DevOps",
                    "priority": 6,
                    "description": "DevOps practices and tools",
                },
                "deployment": {
                    "category": "DevOps",
                    "priority": 6,
                    "description": "Deployment strategies",
                },
                "ci-cd": {
                    "category": "DevOps",
                    "priority": 6,
                    "description": "Continuous integration and deployment",
                },
                "docker": {
                    "category": "DevOps",
                    "priority": 5,
                    "description": "Docker containerization",
                },
                "kubernetes": {
                    "category": "DevOps",
                    "priority": 5,
                    "description": "Kubernetes orchestration",
                },
                # Security and performance
                "security": {
                    "category": "Security",
                    "priority": 8,
                    "description": "Security best practices",
                },
                "performance": {
                    "category": "Performance",
                    "priority": 7,
                    "description": "Performance optimization",
                },
                "accessibility": {
                    "category": "Accessibility",
                    "priority": 6,
                    "description": "Accessibility guidelines",
                },
                # Architecture
                "architecture": {
                    "category": "Architecture",
                    "priority": 7,
                    "description": "Software architecture patterns",
                },
                "microservices": {
                    "category": "Architecture",
                    "priority": 6,
                    "description": "Microservices architecture",
                },
                "monolith": {
                    "category": "Architecture",
                    "priority": 5,
                    "description": "Monolithic architecture",
                },
            }

            # Analyze actual tag usage in instructions for dynamic descriptions
            tag_usage: Dict[str, Dict[str, Any]] = {}
            for instruction in instructions.values():
                if hasattr(instruction, "tags") and instruction.tags:
                    for tag in instruction.tags:
                        if isinstance(tag, str):  # Only process string tags
                            if tag not in tag_usage:
                                tag_usage[tag] = {"count": 0, "categories": set()}
                            tag_usage[tag]["count"] = int(tag_usage[tag]["count"]) + 1
                            if (
                                hasattr(instruction, "metadata")
                                and instruction.metadata
                            ):
                                if hasattr(instruction.metadata, "category"):
                                    categories_set = tag_usage[tag]["categories"]
                                    if isinstance(categories_set, set):
                                        categories_set.add(
                                            instruction.metadata.category
                                        )

            # Build metadata for each tag
            for tag in tags:
                if not isinstance(tag, str):
                    continue  # Skip non-string tags

                if tag in tag_categories:
                    tag_metadata[tag] = tag_categories[tag].copy()
                else:
                    # Generate metadata for unknown tags
                    usage = tag_usage.get(tag, {})
                    categories = usage.get("categories", set())

                    # Determine category based on tag name patterns
                    category = "General"
                    try:
                        tag_lower = tag.lower()
                        if any(
                            keyword in tag_lower for keyword in ["test", "spec", "mock"]
                        ):
                            category = "Testing"
                        elif any(
                            keyword in tag_lower
                            for keyword in ["front", "ui", "client"]
                        ):
                            category = "Frontend"
                        elif any(
                            keyword in tag_lower
                            for keyword in ["back", "server", "api"]
                        ):
                            category = "Backend"
                        elif any(
                            keyword in tag_lower
                            for keyword in ["deploy", "ci", "cd", "ops"]
                        ):
                            category = "DevOps"
                        elif any(
                            keyword in tag_lower
                            for keyword in ["secure", "auth", "crypto"]
                        ):
                            category = "Security"
                        elif categories and isinstance(categories, set):
                            # Use the most common category from actual usage
                            category = list(categories)[0]

                        description = f'{tag.replace("-", " ").replace("_", " ").title()} related guidelines'
                    except (AttributeError, TypeError):
                        # Fallback for any string processing errors
                        description = f"{tag} guidelines"

                    tag_metadata[tag] = {
                        "category": category,
                        "priority": min(
                            int(usage.get("count", 0)), 5
                        ),  # Priority based on usage frequency
                        "description": description,
                    }

        except Exception as e:
            logger.debug(f"Error getting tag metadata: {e}")
            # Fallback to basic metadata
            for tag in tags:
                if isinstance(tag, str):
                    try:
                        description = f'{tag.replace("-", " ").replace("_", " ").title()} guidelines'
                    except (AttributeError, TypeError):
                        description = f"{tag} guidelines"

                    tag_metadata[tag] = {
                        "category": "General",
                        "priority": 0,
                        "description": description,
                    }

        return tag_metadata

    def _group_items_by_category(
        self, items: List[CompletionItem]
    ) -> Dict[str, List[CompletionItem]]:
        """
        Group completion items by category.

        Args:
            items: List of completion items to group

        Returns:
            Dictionary mapping category names to lists of items
        """
        grouped: Dict[str, List[CompletionItem]] = {}
        for item in items:
            category = item.category or "General"
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(item)

        # Sort items within each category by priority and name
        for category_items in grouped.values():
            category_items.sort(key=lambda x: (-x.priority, x.value.lower()))

        return grouped

    def get_template_completions(self, prefix: str) -> List[str]:
        """Legacy method for backward compatibility"""
        try:
            result = self.get_template_completions_enhanced(prefix)
            string_list: List[str] = result.to_string_list()
            return string_list
        except Exception:
            return []

    @with_timeout()
    def get_template_completions_enhanced(self, prefix: str) -> CompletionResult:
        """
        Get enhanced template completions with descriptions and categorization.

        Args:
            prefix: Prefix to filter template IDs

        Returns:
            CompletionResult with template completions, descriptions, and grouping

        Requirements: 12.1, 12.2, 12.3, 12.4 - Contextual help and descriptions
        """
        start_time = time.time()
        cache_key = f"templates_enhanced:{prefix}"

        # Validate input
        if not isinstance(prefix, str):
            logger.warning(
                f"Invalid prefix type for template completion: {type(prefix)}"
            )
            self._record_completion_stats(start_time, cache_hit=False, error=True)
            return CompletionResult(items=[])

        # Check cache first (for enhanced results)
        cached = self.cache.get(cache_key)
        if cached is not None:
            self._record_completion_stats(start_time, cache_hit=True)
            logger.debug(f"Cache hit for enhanced template completions: {prefix}")
            # Reconstruct CompletionResult from cached data
            items = [CompletionItem(value=item) for item in cached]
            return CompletionResult(items=items)

        try:
            # Attempt to get template manager with error handling
            template_manager = self._get_template_manager()
            if template_manager is None:
                self._record_completion_stats(start_time, cache_hit=False, error=True)
                logger.debug(
                    "TemplateManager not available for template completion - providing empty completions"
                )
                # Cache empty result to avoid repeated failed attempts
                self.cache.set(cache_key, [])
                return CompletionResult(items=[])

            # Attempt to get templates with data loading error handling
            try:
                # Try to get full template objects for descriptions, fallback to IDs only
                try:
                    template_manager.load_templates()
                    all_templates = getattr(template_manager, "_templates", {})
                    if not isinstance(all_templates, dict):
                        # Fallback to template IDs only
                        template_ids = template_manager.get_all_template_ids()
                        all_templates = {tid: None for tid in template_ids}
                except (AttributeError, TypeError):
                    # Fallback to template IDs only for backward compatibility
                    template_ids = template_manager.get_all_template_ids()
                    if not isinstance(template_ids, (set, list)):
                        raise ValueError(
                            f"get_all_template_ids() returned invalid type: {type(template_ids)}"
                        )
                    all_templates = {tid: None for tid in template_ids}

            except (FileNotFoundError, PermissionError) as e:
                logger.warning(f"Data loading error for template completions: {e}")
                self._record_completion_stats(start_time, cache_hit=False, error=True)
                # Cache empty result to avoid repeated failed attempts
                self.cache.set(cache_key, [])
                return CompletionResult(items=[])

            except Exception as e:
                logger.warning(f"Unexpected error loading templates: {e}")
                self._record_completion_stats(start_time, cache_hit=False, error=True)
                # Cache empty result to avoid repeated failed attempts
                self.cache.set(cache_key, [])
                return CompletionResult(items=[])

            # Filter and validate templates with enhanced metadata
            try:
                completion_items = []
                for template_id, template in all_templates.items():
                    if isinstance(template_id, str) and template_id.startswith(prefix):
                        # Extract description and category from template (if available)
                        if template is not None:
                            description = getattr(template, "description", None)
                            project_type = getattr(template, "project_type", "general")
                            priority = self._get_template_priority(template)
                        else:
                            # Fallback for when template object is not available
                            description = None
                            project_type = "general"
                            priority = 5

                        # Format category for display
                        category = (
                            project_type.replace("-", " ").replace("_", " ").title()
                        )

                        item = CompletionItem(
                            value=template_id,
                            description=description,
                            category=category,
                            priority=priority,
                        )
                        completion_items.append(item)
                    elif not isinstance(template_id, str):
                        logger.debug(
                            f"Skipping non-string template ID: {type(template_id)}"
                        )

                # Sort items alphabetically for consistency with legacy behavior
                completion_items.sort(key=lambda x: x.value)

                # Create result with grouping by project type
                result = CompletionResult(items=completion_items)
                result.grouped_items = self._group_items_by_category(completion_items)

                # Cache successful result (just the values for backward compatibility)
                cache_values = [item.value for item in completion_items]
                self.cache.set(cache_key, cache_values)
                self._record_completion_stats(start_time, cache_hit=False)
                logger.debug(
                    f"Generated {len(completion_items)} enhanced template completions for: {prefix}"
                )
                return result

            except Exception as e:
                logger.warning(f"Error filtering template completions: {e}")
                self._record_completion_stats(start_time, cache_hit=False, error=True)
                return CompletionResult(items=[])

        except Exception as e:
            self._record_completion_stats(start_time, cache_hit=False, error=True)
            logger.error(f"Unexpected error in get_template_completions_enhanced: {e}")
            logger.debug(
                "Enhanced template completion failed with unexpected error",
                exc_info=True,
            )
            return CompletionResult(items=[])

    def _get_template_priority(self, template: Any) -> int:
        """
        Determine priority for template based on complexity and popularity.

        Args:
            template: Template object

        Returns:
            Priority score (higher = more important)
        """
        priority = 5  # Default priority

        try:
            # Adjust priority based on complexity
            if hasattr(template, "metadata") and template.metadata:
                complexity = getattr(template.metadata, "complexity", "intermediate")
                if complexity == "beginner":
                    priority += 3  # Prioritize beginner templates
                elif complexity == "intermediate":
                    priority += 1
                # Advanced templates keep default priority

            # Adjust priority based on project type popularity
            project_type = getattr(template, "project_type", "")
            popular_types = {
                "web-app": 3,
                "api": 2,
                "mobile-app": 2,
                "library": 1,
                "cli": 1,
            }
            priority += popular_types.get(project_type, 0)

            # Boost priority for commonly used technology stacks
            tech_stack = getattr(template, "technology_stack", [])
            popular_techs = {"react", "python", "javascript", "typescript", "node.js"}
            if any(tech.lower() in popular_techs for tech in tech_stack):
                priority += 1

        except Exception as e:
            logger.debug(f"Error calculating template priority: {e}")

        return min(priority, 10)  # Cap at 10

    def get_category_completions(self, prefix: str) -> List[str]:
        """Legacy method for backward compatibility"""
        # Use simple cache for backward compatibility with tests
        cache_key = f"categories:{prefix}"

        # Check if we have a cached result
        if hasattr(self, "_category_cache") and cache_key in self._category_cache:
            logger.debug(f"Cache hit for category completions: {prefix}")
            return self._category_cache[cache_key]

        # Initialize category cache if not exists
        if not hasattr(self, "_category_cache"):
            self._category_cache = {}

        # Get enhanced result and convert to simple list
        result = self.get_category_completions_enhanced(prefix)
        simple_result = result.to_string_list()

        # Cache the simple result
        self._category_cache[cache_key] = simple_result

        return simple_result

    def get_category_completions_enhanced(self, prefix: str) -> CompletionResult:
        """
        Get enhanced category completions with descriptions and prioritization.

        Args:
            prefix: Prefix to filter categories

        Returns:
            CompletionResult with category completions and descriptions
        """
        # Static categories - cache indefinitely using a special cache
        cache_key = f"categories_enhanced:{prefix}"

        # Check if we have a cached result (categories never expire)
        if (
            hasattr(self, "_category_cache_enhanced")
            and cache_key in self._category_cache_enhanced
        ):
            logger.debug(f"Cache hit for enhanced category completions: {prefix}")
            return self._category_cache_enhanced[cache_key]

        # Initialize category cache if not exists
        if not hasattr(self, "_category_cache_enhanced"):
            self._category_cache_enhanced = {}

        # Predefined categories with descriptions and priorities
        categories_with_metadata = [
            {
                "name": "General",
                "description": "General development guidelines and best practices",
                "priority": 10,
            },
            {
                "name": "Testing",
                "description": "Testing strategies, frameworks, and quality assurance",
                "priority": 9,
            },
            {
                "name": "Frontend",
                "description": "Frontend development, UI/UX, and client-side technologies",
                "priority": 8,
            },
            {
                "name": "Backend",
                "description": "Backend development, APIs, and server-side technologies",
                "priority": 8,
            },
            {
                "name": "Languages",
                "description": "Programming language-specific guidelines and patterns",
                "priority": 7,
            },
            {
                "name": "DevOps",
                "description": "DevOps practices, deployment, and infrastructure management",
                "priority": 6,
            },
            {
                "name": "Architecture",
                "description": "Software architecture patterns and system design",
                "priority": 7,
            },
        ]

        # Case-insensitive matching and create completion items
        completion_items = []
        for cat_data in categories_with_metadata:
            name = str(cat_data["name"])
            if name.lower().startswith(prefix.lower()):
                item = CompletionItem(
                    value=name,
                    description=str(cat_data["description"]),
                    category="Categories",
                    priority=(
                        int(cat_data["priority"])
                        if isinstance(cat_data["priority"], (int, str))
                        else 0
                    ),
                )
                completion_items.append(item)

        # Create result with grouping
        result = CompletionResult(items=completion_items)
        result.grouped_items = {"Categories": completion_items}

        # Cache with indefinite TTL for static data
        self._category_cache_enhanced[cache_key] = result
        logger.debug(
            f"Generated {len(completion_items)} enhanced category completions for: {prefix}"
        )
        return result

    def get_format_completions(self, prefix: str) -> List[str]:
        """Legacy method for backward compatibility"""
        result = self.get_format_completions_enhanced(prefix)
        return result.to_string_list()

    def get_format_completions_enhanced(self, prefix: str) -> CompletionResult:
        """
        Get enhanced output format completions with descriptions.

        Args:
            prefix: Prefix to filter formats

        Returns:
            CompletionResult with format completions and descriptions
        """
        formats_with_metadata = [
            {
                "name": "markdown",
                "description": "Markdown format for documentation",
                "priority": 10,
            },
            {
                "name": "json",
                "description": "JSON format for structured data",
                "priority": 8,
            },
            {
                "name": "yaml",
                "description": "YAML format for configuration",
                "priority": 6,
            },
        ]

        completion_items = []
        for fmt_data in formats_with_metadata:
            name = str(fmt_data["name"])
            if name.startswith(prefix):
                item = CompletionItem(
                    value=name,
                    description=str(fmt_data["description"]),
                    category="Output Formats",
                    priority=(
                        int(fmt_data["priority"])
                        if isinstance(fmt_data["priority"], (int, str))
                        else 0
                    ),
                )
                completion_items.append(item)

        result = CompletionResult(items=completion_items)
        result.grouped_items = {"Output Formats": completion_items}
        return result

    def get_output_format_completions(self, prefix: str) -> List[str]:
        """Legacy method for backward compatibility"""
        result = self.get_output_format_completions_enhanced(prefix)
        return result.to_string_list()

    def get_output_format_completions_enhanced(self, prefix: str) -> CompletionResult:
        """
        Get enhanced integration output format completions with descriptions.

        Args:
            prefix: Prefix to filter formats

        Returns:
            CompletionResult with format completions and descriptions
        """
        formats_with_metadata = [
            {
                "name": "text",
                "description": "Plain text format for simple output",
                "priority": 10,
            },
            {
                "name": "json",
                "description": "JSON format for structured integration data",
                "priority": 8,
            },
        ]

        completion_items = []
        for fmt_data in formats_with_metadata:
            name = str(fmt_data["name"])
            if name.startswith(prefix):
                item = CompletionItem(
                    value=name,
                    description=str(fmt_data["description"]),
                    category="Integration Formats",
                    priority=(
                        int(fmt_data["priority"])
                        if isinstance(fmt_data["priority"], (int, str))
                        else 0
                    ),
                )
                completion_items.append(item)

        result = CompletionResult(items=completion_items)
        result.grouped_items = {"Integration Formats": completion_items}
        return result

    @with_timeout()
    def get_instruction_completions(self, prefix: str) -> List[str]:
        """
        Get instruction ID completions with comprehensive error handling and fallback strategies.

        Args:
            prefix: Prefix to filter instruction IDs

        Returns:
            List of matching instruction ID completions

        Requirements: 3.4, 11.3 - Graceful degradation when instruction database unavailable
        """
        start_time = time.time()
        cache_key = f"instructions:{prefix}"

        # Validate input
        if not isinstance(prefix, str):
            logger.warning(
                f"Invalid prefix type for instruction completion: {type(prefix)}"
            )
            self._record_completion_stats(start_time, cache_hit=False, error=True)
            return []

        # Check cache first
        cached = self.cache.get(cache_key)
        if cached is not None:
            self._record_completion_stats(start_time, cache_hit=True)
            logger.debug(f"Cache hit for instruction completions: {prefix}")
            return cached

        try:
            # Attempt to get instruction database with error handling
            instruction_db = self._get_instruction_db()
            if instruction_db is None:
                self._record_completion_stats(start_time, cache_hit=False, error=True)
                logger.debug(
                    "InstructionDatabase not available for instruction completion - providing empty completions"
                )
                # Cache empty result to avoid repeated failed attempts
                self.cache.set(cache_key, [])
                return []

            # Attempt to load instructions with data loading error handling
            try:
                instructions = instruction_db.load_instructions()
                if not isinstance(instructions, dict):
                    raise ValueError(
                        f"load_instructions() returned invalid type: {type(instructions)}"
                    )

            except (FileNotFoundError, PermissionError) as e:
                logger.warning(f"Data loading error for instruction completions: {e}")
                self._record_completion_stats(start_time, cache_hit=False, error=True)
                # Cache empty result to avoid repeated failed attempts
                self.cache.set(cache_key, [])
                return []

            except Exception as e:
                logger.warning(f"Unexpected error loading instructions: {e}")
                self._record_completion_stats(start_time, cache_hit=False, error=True)
                # Cache empty result to avoid repeated failed attempts
                self.cache.set(cache_key, [])
                return []

            # Filter and validate instruction IDs
            try:
                all_instruction_ids = list(instructions.keys())
                matching_instructions = []

                for inst_id in all_instruction_ids:
                    if isinstance(inst_id, str) and inst_id.startswith(prefix):
                        matching_instructions.append(inst_id)
                    elif not isinstance(inst_id, str):
                        logger.debug(
                            f"Skipping non-string instruction ID: {type(inst_id)}"
                        )

                matching_instructions.sort()

                # Cache successful result
                self.cache.set(cache_key, matching_instructions)
                self._record_completion_stats(start_time, cache_hit=False)
                logger.debug(
                    f"Generated {len(matching_instructions)} instruction completions for: {prefix}"
                )
                return matching_instructions

            except Exception as e:
                logger.warning(f"Error filtering instruction completions: {e}")
                self._record_completion_stats(start_time, cache_hit=False, error=True)
                return []

        except Exception as e:
            self._record_completion_stats(start_time, cache_hit=False, error=True)
            logger.error(f"Unexpected error in get_instruction_completions: {e}")
            logger.debug(
                "Instruction completion failed with unexpected error", exc_info=True
            )
            return []

    @with_timeout()
    def get_project_type_completions(self, prefix: str) -> List[str]:
        """
        Get project type completions with comprehensive error handling and fallback strategies.

        Args:
            prefix: Prefix to filter project types

        Returns:
            List of matching project type completions

        Requirements: 4.4, 11.3 - Graceful degradation when template manager unavailable
        """
        start_time = time.time()
        cache_key = f"project_types:{prefix}"

        # Validate input
        if not isinstance(prefix, str):
            logger.warning(
                f"Invalid prefix type for project type completion: {type(prefix)}"
            )
            self._record_completion_stats(start_time, cache_hit=False, error=True)
            return []

        # Check cache first
        cached = self.cache.get(cache_key)
        if cached is not None:
            self._record_completion_stats(start_time, cache_hit=True)
            logger.debug(f"Cache hit for project type completions: {prefix}")
            return cached

        try:
            # Attempt to get template manager with error handling
            template_manager = self._get_template_manager()
            if template_manager is None:
                self._record_completion_stats(start_time, cache_hit=False, error=True)
                logger.debug(
                    "TemplateManager not available for project type completion - providing empty completions"
                )
                # Cache empty result to avoid repeated failed attempts
                self.cache.set(cache_key, [])
                return []

            # Attempt to get project types with data loading error handling
            try:
                all_project_types = template_manager.get_all_project_types()
                if not isinstance(all_project_types, (set, list)):
                    raise ValueError(
                        f"get_all_project_types() returned invalid type: {type(all_project_types)}"
                    )

                # Convert to list if it's a set
                if isinstance(all_project_types, set):
                    all_project_types = list(all_project_types)

            except (FileNotFoundError, PermissionError) as e:
                logger.warning(f"Data loading error for project type completions: {e}")
                self._record_completion_stats(start_time, cache_hit=False, error=True)
                # Cache empty result to avoid repeated failed attempts
                self.cache.set(cache_key, [])
                return []

            except Exception as e:
                logger.warning(f"Unexpected error loading project types: {e}")
                self._record_completion_stats(start_time, cache_hit=False, error=True)
                # Cache empty result to avoid repeated failed attempts
                self.cache.set(cache_key, [])
                return []

            # Filter and validate project types
            try:
                matching_project_types = []
                for project_type in all_project_types:
                    if isinstance(project_type, str) and project_type.startswith(
                        prefix
                    ):
                        matching_project_types.append(project_type)
                    elif not isinstance(project_type, str):
                        logger.debug(
                            f"Skipping non-string project type: {type(project_type)}"
                        )

                matching_project_types.sort()

                # Cache successful result
                self.cache.set(cache_key, matching_project_types)
                self._record_completion_stats(start_time, cache_hit=False)
                logger.debug(
                    f"Generated {len(matching_project_types)} project type completions for: {prefix}"
                )
                return matching_project_types

            except Exception as e:
                logger.warning(f"Error filtering project type completions: {e}")
                self._record_completion_stats(start_time, cache_hit=False, error=True)
                return []

        except Exception as e:
            self._record_completion_stats(start_time, cache_hit=False, error=True)
            logger.error(f"Unexpected error in get_project_type_completions: {e}")
            logger.debug(
                "Project type completion failed with unexpected error", exc_info=True
            )
            return []


# Global completion engine instance
_completion_engine: Optional[CompletionEngine] = None


def get_completion_engine() -> CompletionEngine:
    """
    Get the global completion engine instance with error handling.

    Returns:
        CompletionEngine instance

    Requirements: 11.3 - Graceful degradation for service initialization failures
    """
    global _completion_engine
    if _completion_engine is None:
        try:
            _completion_engine = CompletionEngine()
            logger.debug("Successfully initialized global completion engine")
        except Exception as e:
            logger.error(f"Failed to initialize completion engine: {e}")
            logger.debug("Completion engine initialization failed", exc_info=True)
            # Create a minimal engine that will handle errors gracefully
            _completion_engine = CompletionEngine()
    return _completion_engine


def reset_completion_engine() -> None:
    """
    Reset the global completion engine instance.

    This is useful for testing or when services need to be reinitialized.
    """
    global _completion_engine
    _completion_engine = None
    logger.debug("Reset global completion engine")


def safe_initialize_services(
    instruction_db: Optional[Any] = None, template_manager: Optional[Any] = None
) -> bool:
    """
    Safely initialize completion services with comprehensive error handling.

    Args:
        instruction_db: Optional InstructionDatabase instance
        template_manager: Optional TemplateManager instance

    Returns:
        True if initialization was successful, False otherwise

    Requirements: 3.4, 4.4, 11.3 - Graceful degradation for service initialization failures
    """
    try:
        engine = get_completion_engine()
        engine.set_services(
            instruction_db=instruction_db, template_manager=template_manager
        )
        logger.debug("Successfully initialized completion services")
        return True
    except Exception as e:
        logger.warning(f"Failed to initialize completion services: {e}")
        logger.debug(
            "Service initialization failed - completion will degrade gracefully",
            exc_info=True,
        )
        return False


def safe_get_completions(
    completer_func: Callable[..., List[str]], *args: Any, **kwargs: Any
) -> List[str]:
    """
    Safely execute completion function with comprehensive error handling and performance monitoring.

    This function provides a robust wrapper around completion functions that:
    - Handles all types of exceptions gracefully
    - Provides detailed logging for debugging
    - Monitors performance and timeouts
    - Ensures completion never blocks the CLI
    - Implements fallback strategies for different error types

    Args:
        completer_func: Completion function to execute
        *args: Arguments to pass to completer function
        **kwargs: Keyword arguments to pass to completer function

    Returns:
        List of completions or empty list on error

    Requirements: 3.4, 4.4, 11.3 - Graceful degradation and error handling
    """
    start_time = time.time()
    function_name = getattr(completer_func, "__name__", str(completer_func))

    try:
        # Execute the completion function
        result = completer_func(*args, **kwargs)

        # Validate result type
        if not isinstance(result, list):
            logger.warning(
                f"Completion function {function_name} returned non-list result: {type(result)}"
            )
            return []

        # Validate result contents
        validated_result = []
        for item in result:
            if isinstance(item, str):
                validated_result.append(item)
            else:
                logger.warning(
                    f"Completion function {function_name} returned non-string item: {type(item)}"
                )

        response_time = time.time() - start_time
        logger.debug(
            f"Completion function {function_name} completed successfully in {response_time:.3f}s with {len(validated_result)} results"
        )
        return validated_result

    except ImportError as e:
        # Handle missing dependencies gracefully
        response_time = time.time() - start_time
        logger.warning(
            f"Import error in completion function {function_name} after {response_time:.3f}s: {e}"
        )
        logger.debug(
            "Completion degraded due to missing dependency - this is expected in some environments"
        )
        return []

    except FileNotFoundError as e:
        # Handle missing data files gracefully
        response_time = time.time() - start_time
        logger.warning(
            f"Data file not found in completion function {function_name} after {response_time:.3f}s: {e}"
        )
        logger.debug(
            "Completion degraded due to missing data files - check AgentSpec installation"
        )
        return []

    except PermissionError as e:
        # Handle permission issues gracefully
        response_time = time.time() - start_time
        logger.warning(
            f"Permission error in completion function {function_name} after {response_time:.3f}s: {e}"
        )
        logger.debug(
            "Completion degraded due to permission issues - check file permissions"
        )
        return []

    except TimeoutError as e:
        # Handle timeout errors specifically
        response_time = time.time() - start_time
        logger.warning(
            f"Timeout in completion function {function_name} after {response_time:.3f}s: {e}"
        )
        logger.debug(
            "Completion timed out - consider increasing timeout or optimizing data loading"
        )
        return []

    except (ConnectionError, OSError) as e:
        # Handle network/system errors gracefully
        response_time = time.time() - start_time
        logger.warning(
            f"System/network error in completion function {function_name} after {response_time:.3f}s: {e}"
        )
        logger.debug("Completion degraded due to system/network issues")
        return []

    except (ValueError, TypeError, KeyError, AttributeError) as e:
        # Handle data/logic errors gracefully
        response_time = time.time() - start_time
        logger.warning(
            f"Data error in completion function {function_name} after {response_time:.3f}s: {e}"
        )
        logger.debug(
            "Completion degraded due to data/logic error - check data integrity"
        )
        return []

    except Exception as e:
        # Handle any other unexpected errors
        response_time = time.time() - start_time
        logger.error(
            f"Unexpected error in completion function {function_name} after {response_time:.3f}s: {e}"
        )
        logger.debug(
            "Completion failed with unexpected error - this may indicate a bug",
            exc_info=True,
        )
        return []
