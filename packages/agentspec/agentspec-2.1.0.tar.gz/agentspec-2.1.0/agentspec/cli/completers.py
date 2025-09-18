"""
Completion functions for AgentSpec CLI arguments and options.

This module provides static and dynamic completion functions for use with argcomplete.
Static completers handle fixed values like commands and formats, while dynamic completers
handle values that come from AgentSpec services like tags and templates.
"""

import logging
from typing import Any, List

try:
    from argcomplete.completers import DirectoriesCompleter, FilesCompleter

    ARGCOMPLETE_AVAILABLE = True
except ImportError:
    ARGCOMPLETE_AVAILABLE = False

    # Create dummy classes for when argcomplete is not available
    class FilesCompleter:  # type: ignore
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

    class DirectoriesCompleter:  # type: ignore
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass


from .completion import get_completion_engine, safe_get_completions

logger = logging.getLogger(__name__)


def command_completer(prefix: str, parsed_args: Any, **kwargs: Any) -> List[str]:
    """
    Complete main commands with enhanced descriptions and prioritization.

    Handles completion for the main AgentSpec commands. This is a static completer
    since the available commands are fixed.

    Args:
        prefix: Command prefix to complete
        parsed_args: Parsed arguments (unused)
        **kwargs: Additional arguments (unused)

    Returns:
        List of matching command completions

    Requirements: 1.1, 12.1, 12.2 - Command completion with contextual help
    """
    # All available AgentSpec commands with descriptions and priorities
    commands_with_metadata = [
        {
            "name": "generate",
            "description": "Generate specification documents from templates and instructions",
            "priority": 10,
        },
        {
            "name": "interactive",
            "description": "Start interactive wizard for guided spec generation",
            "priority": 9,
        },
        {
            "name": "analyze",
            "description": "Analyze existing project and suggest relevant instructions",
            "priority": 8,
        },
        {
            "name": "list-templates",
            "description": "List available project templates",
            "priority": 7,
        },
        {
            "name": "list-instructions",
            "description": "List available coding instructions",
            "priority": 6,
        },
        {
            "name": "list-tags",
            "description": "List available instruction tags",
            "priority": 5,
        },
        {
            "name": "validate",
            "description": "Validate specification documents",
            "priority": 4,
        },
        {
            "name": "integrate",
            "description": "Integrate with external tools and services",
            "priority": 3,
        },
        {
            "name": "version",
            "description": "Show AgentSpec version information",
            "priority": 2,
        },
        {"name": "help", "description": "Show help information", "priority": 1},
    ]

    # Filter commands that start with the prefix and sort alphabetically
    matching_commands = [
        str(cmd["name"])
        for cmd in commands_with_metadata
        if str(cmd["name"]).startswith(prefix)
    ]

    # Sort alphabetically for consistent completion behavior
    matching_commands.sort()

    logger.debug(f"Command completion for '{prefix}': {len(matching_commands)} matches")
    return matching_commands


def format_completer(prefix: str, parsed_args: Any, **kwargs: Any) -> List[str]:
    """
    Complete output format values for the --format option with descriptions.

    Handles completion for output formats used in generate and other commands.
    Uses the completion engine for dynamic format completion.

    Args:
        prefix: Format prefix to complete
        parsed_args: Parsed arguments (unused)
        **kwargs: Additional arguments (unused)

    Returns:
        List of matching format completions

    Requirements: 7.1, 7.2, 12.1, 12.2 - Format completion with contextual help
    """
    try:
        engine = get_completion_engine()
        if hasattr(engine, "get_format_completions"):
            return safe_get_completions(engine.get_format_completions, prefix)
        else:
            # Fallback to static completion if method doesn't exist
            formats = ["markdown", "json", "yaml"]
            return [fmt for fmt in formats if fmt.startswith(prefix)]
    except Exception:
        # Fallback to static completion on any error
        formats = ["markdown", "json", "yaml"]
        return [fmt for fmt in formats if fmt.startswith(prefix)]


def output_format_completer(prefix: str, parsed_args: Any, **kwargs: Any) -> List[str]:
    """
    Complete integration output format values for the --output-format option with descriptions.

    Handles completion for output formats used specifically in the integrate command.
    Uses the completion engine for dynamic format completion.

    Args:
        prefix: Format prefix to complete
        parsed_args: Parsed arguments (unused)
        **kwargs: Additional arguments (unused)

    Returns:
        List of matching output format completions

    Requirements: 7.3, 12.1, 12.2 - Output format completion with contextual help
    """
    try:
        engine = get_completion_engine()
        if hasattr(engine, "get_output_format_completions"):
            return safe_get_completions(engine.get_output_format_completions, prefix)
        else:
            # Fallback to static completion if method doesn't exist
            formats = ["text", "json"]
            return [fmt for fmt in formats if fmt.startswith(prefix)]
    except Exception:
        # Fallback to static completion on any error
        formats = ["text", "json"]
        return [fmt for fmt in formats if fmt.startswith(prefix)]


def tag_completer(prefix: str, parsed_args: Any, **kwargs: Any) -> List[str]:
    """
    Complete instruction tags from database.

    Handles completion for tag values used in --tags and --tag options.
    This is a dynamic completer that queries the InstructionDatabase for available tags.

    Args:
        prefix: Tag prefix to complete
        parsed_args: Parsed arguments (unused)
        **kwargs: Additional arguments (unused)

    Returns:
        List of matching tag completions

    Requirements: 3.1, 3.2, 3.3, 3.4 - Dynamic tag completion with caching and graceful degradation
    """
    engine = get_completion_engine()
    return safe_get_completions(engine.get_tag_completions, prefix)


def comma_separated_tag_completer(
    prefix: str, parsed_args: Any, **kwargs: Any
) -> List[str]:
    """
    Complete comma-separated tag lists.

    Handles completion for comma-separated tag values, completing only the current
    tag being typed after the last comma. Avoids suggesting already-selected tags.

    Args:
        prefix: Full comma-separated prefix to complete
        parsed_args: Parsed arguments (unused)
        **kwargs: Additional arguments (unused)

    Returns:
        List of matching tag completions for the current tag

    Requirements: 10.1, 10.3, 10.4 - Multi-tag completion with comma separation
    """
    # Split by comma and get the current tag being typed
    if "," in prefix:
        # Split and preserve the original format (including spaces)
        parts = prefix.split(",")
        existing_parts = parts[:-1]
        current_tag = parts[-1].strip()

        # Get existing tags (stripped for comparison)
        existing_tags = [tag.strip() for tag in existing_parts]
    else:
        existing_parts = []
        existing_tags = []
        current_tag = prefix.strip()

    # Get all available tag completions for the current tag
    engine = get_completion_engine()
    available_tags = safe_get_completions(engine.get_tag_completions, current_tag)

    # Filter out already selected tags
    filtered_tags = [tag for tag in available_tags if tag not in existing_tags]

    # If we have existing tags, prepend them to the completions
    if existing_parts:
        prefix_part = ",".join(existing_parts) + ","
        return [f"{prefix_part}{tag}" for tag in filtered_tags]
    else:
        return filtered_tags


def instruction_completer(prefix: str, parsed_args: Any, **kwargs: Any) -> List[str]:
    """
    Complete instruction IDs from database.

    Handles completion for instruction ID values used in --instructions option.
    This is a dynamic completer that queries the InstructionDatabase for available instruction IDs.

    Args:
        prefix: Instruction ID prefix to complete
        parsed_args: Parsed arguments (unused)
        **kwargs: Additional arguments (unused)

    Returns:
        List of matching instruction ID completions

    Requirements: 10.2, 10.3, 10.4 - Dynamic instruction ID completion with caching
    """
    engine = get_completion_engine()
    return safe_get_completions(engine.get_instruction_completions, prefix)


def comma_separated_instruction_completer(
    prefix: str, parsed_args: Any, **kwargs: Any
) -> List[str]:
    """
    Complete comma-separated instruction ID lists.

    Handles completion for comma-separated instruction ID values, completing only the current
    instruction ID being typed after the last comma. Avoids suggesting already-selected IDs.

    Args:
        prefix: Full comma-separated prefix to complete
        parsed_args: Parsed arguments (unused)
        **kwargs: Additional arguments (unused)

    Returns:
        List of matching instruction ID completions for the current ID

    Requirements: 10.2, 10.3, 10.4 - Multi-instruction completion with comma separation
    """
    # Split by comma and get the current instruction ID being typed
    if "," in prefix:
        # Split and preserve the original format (including spaces)
        parts = prefix.split(",")
        existing_parts = parts[:-1]
        current_instruction = parts[-1].strip()

        # Get existing instruction IDs (stripped for comparison)
        existing_instructions = [inst.strip() for inst in existing_parts]
    else:
        existing_parts = []
        existing_instructions = []
        current_instruction = prefix.strip()

    # Get all available instruction ID completions for the current instruction
    engine = get_completion_engine()
    available_instructions = safe_get_completions(
        engine.get_instruction_completions, current_instruction
    )

    # Filter out already selected instruction IDs
    filtered_instructions = [
        inst for inst in available_instructions if inst not in existing_instructions
    ]

    # If we have existing instruction IDs, prepend them to the completions
    if existing_parts:
        prefix_part = ",".join(existing_parts) + ","
        return [f"{prefix_part}{inst}" for inst in filtered_instructions]
    else:
        return filtered_instructions


def template_completer(prefix: str, parsed_args: Any, **kwargs: Any) -> List[str]:
    """
    Complete template IDs from template manager.

    Handles completion for template ID values used in --template option.
    This is a dynamic completer that queries the TemplateManager for available template IDs.

    Args:
        prefix: Template ID prefix to complete
        parsed_args: Parsed arguments (unused)
        **kwargs: Additional arguments (unused)

    Returns:
        List of matching template ID completions

    Requirements: 4.1, 4.2, 4.3, 4.4 - Dynamic template completion with caching and graceful degradation
    """
    engine = get_completion_engine()
    return safe_get_completions(engine.get_template_completions, prefix)


def project_type_completer(prefix: str, parsed_args: Any, **kwargs: Any) -> List[str]:
    """
    Complete project types from template manager.

    Handles completion for project type values used in --project-type option for template filtering.
    This is a dynamic completer that queries the TemplateManager for available project types.

    Args:
        prefix: Project type prefix to complete
        parsed_args: Parsed arguments (unused)
        **kwargs: Additional arguments (unused)

    Returns:
        List of matching project type completions

    Requirements: 4.1, 4.2, 4.3, 4.4 - Dynamic template filtering completion with caching and graceful degradation
    """
    engine = get_completion_engine()
    return safe_get_completions(engine.get_project_type_completions, prefix)


def category_completer(prefix: str, parsed_args: Any, **kwargs: Any) -> List[str]:
    """
    Complete instruction categories with descriptions and prioritization.

    Handles completion for category values used in --category option.
    This is a static completer with predefined categories that supports case-insensitive matching.

    Args:
        prefix: Category prefix to complete
        parsed_args: Parsed arguments (unused)
        **kwargs: Additional arguments (unused)

    Returns:
        List of matching category completions

    Requirements: 5.1, 5.2, 5.3, 5.4, 12.1, 12.2 - Category completion with contextual help
    """
    # Categories with descriptions and priorities
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

    # Case-insensitive filtering and sorting
    matching_categories = [
        str(cat["name"])
        for cat in categories_with_metadata
        if str(cat["name"]).lower().startswith(prefix.lower())
    ]

    # Sort by priority (higher first) then alphabetically
    category_priority = {
        str(cat["name"]): (
            int(cat["priority"]) if isinstance(cat["priority"], (int, str)) else 0
        )
        for cat in categories_with_metadata
    }
    matching_categories.sort(key=lambda x: (-category_priority.get(x, 0), x))

    return matching_categories


# File path completion instances
# These are created as module-level instances to be used by the CLI
if ARGCOMPLETE_AVAILABLE:
    # File completer for output files - allows all files and directories
    output_file_completer = FilesCompleter(directories=True)

    # Directory completer for project paths - only directories
    project_directory_completer = DirectoriesCompleter()

    # Spec file completer for validation - prioritize .md files but allow all
    spec_file_completer = FilesCompleter(
        allowednames=(".md", ".markdown", ".txt"), directories=False
    )
else:
    # Dummy completers when argcomplete is not available
    output_file_completer = FilesCompleter()
    project_directory_completer = DirectoriesCompleter()
    spec_file_completer = FilesCompleter()
