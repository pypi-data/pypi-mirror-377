"""
Validation utilities for AgentSpec.

Provides validation functions for configurations, specifications, and data structures.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import jsonschema
from jsonschema import ValidationError


class ValidationUtils:
    """Utility class for validation operations."""

    @staticmethod
    def validate_json_schema(
        data: Dict[str, Any], schema: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate data against JSON schema.

        Returns:
            Tuple of (is_valid, error_messages)
        """
        try:
            jsonschema.validate(data, schema)
            return True, []
        except ValidationError as e:
            return False, [str(e)]
        except Exception as e:
            return False, [f"Validation error: {e}"]

    @staticmethod
    def validate_file_path(
        path: Union[str, Path], must_exist: bool = False
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate file path.

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            path = Path(path)

            # Check if path is absolute or relative
            if not path.is_absolute() and not str(path).startswith("."):
                # Relative path without ./ prefix is okay
                pass

            # Check if file must exist
            if must_exist and not path.exists():
                return False, f"File does not exist: {path}"

            # Check if parent directory exists (for new files)
            if not must_exist and not path.parent.exists():
                return False, f"Parent directory does not exist: {path.parent}"

            return True, None

        except Exception as e:
            return False, f"Invalid path: {e}"

    @staticmethod
    def validate_identifier(identifier: Any) -> Tuple[bool, Optional[str]]:
        """
        Validate identifier (instruction ID, template ID, etc.).

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not identifier:
            return False, "Identifier cannot be empty"

        if not isinstance(identifier, str):
            return False, "Identifier must be a string"

        # Check length
        if len(identifier) > 100:
            return False, "Identifier too long (max 100 characters)"

        # Check format: alphanumeric, underscore, hyphen
        if not re.match(r"^[a-zA-Z0-9_-]+$", identifier):
            return (
                False,
                "Identifier can only contain letters, numbers, underscores, and hyphens",
            )

        # Must start with letter or underscore
        if not re.match(r"^[a-zA-Z_]", identifier):
            return False, "Identifier must start with a letter or underscore"

        return True, None

    @staticmethod
    def validate_version(version: str) -> Tuple[bool, Optional[str]]:
        """
        Validate version string (semantic versioning).

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not version:
            return False, "Version cannot be empty"

        # Basic semantic versioning pattern
        pattern = r"^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*))?(?:\+([a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*))?$"

        if not re.match(pattern, version):
            return (
                False,
                "Version must follow semantic versioning (e.g., 1.0.0, 1.0.0-alpha, 1.0.0+build)",
            )

        return True, None

    @staticmethod
    def validate_tags(tags: Any) -> Tuple[bool, List[str]]:
        """
        Validate list of tags.

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        if not isinstance(tags, list):
            return False, ["Tags must be a list"]

        for tag in tags:
            if not isinstance(tag, str):
                errors.append(f"Tag must be string: {tag}")
                continue

            if not tag.strip():
                errors.append("Tag cannot be empty")
                continue

            # Tag format validation
            if not re.match(r"^[a-zA-Z0-9_-]+$", tag):
                errors.append(f"Invalid tag format: {tag}")

        return len(errors) == 0, errors

    @staticmethod
    def validate_url(url: str) -> Tuple[bool, Optional[str]]:
        """
        Validate URL format.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not url:
            return False, "URL cannot be empty"

        # Basic URL pattern
        url_pattern = re.compile(
            r"^https?://"  # http:// or https://
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
            r"localhost|"  # localhost...
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )

        if not url_pattern.match(url):
            return False, "Invalid URL format"

        return True, None

    @staticmethod
    def validate_email(email: str) -> Tuple[bool, Optional[str]]:
        """
        Validate email format.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not email:
            return False, "Email cannot be empty"

        # Basic email pattern
        email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

        if not email_pattern.match(email):
            return False, "Invalid email format"

        return True, None

    @staticmethod
    def validate_config_structure(config: Any) -> Tuple[bool, List[str]]:
        """
        Validate basic configuration structure.

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        if not isinstance(config, dict):
            return False, ["Configuration must be a dictionary"]

        # Check for required top-level keys
        required_keys = ["agentspec"]
        for key in required_keys:
            if key not in config:
                errors.append(f"Missing required configuration key: {key}")

        # Validate agentspec section if present
        if "agentspec" in config:
            agentspec_config = config["agentspec"]
            if not isinstance(agentspec_config, dict):
                errors.append("'agentspec' configuration must be a dictionary")
            else:
                # Validate version if present
                if "version" in agentspec_config:
                    version = agentspec_config["version"]
                    is_valid, error = ValidationUtils.validate_version(version)
                    if not is_valid:
                        errors.append(f"Invalid version in configuration: {error}")

        return len(errors) == 0, errors

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename by removing/replacing invalid characters.
        """
        # Remove or replace invalid characters
        sanitized = re.sub(r'[<>:"/\\|?*]', "_", filename)

        # Remove leading/trailing whitespace and dots
        sanitized = sanitized.strip(" .")

        # Ensure it's not empty
        if not sanitized:
            sanitized = "untitled"

        # Limit length
        if len(sanitized) > 255:
            sanitized = sanitized[:255]

        return sanitized

    @staticmethod
    def validate_markdown_content(content: str) -> Tuple[bool, List[str]]:
        """
        Validate markdown content for basic structure.

        Returns:
            Tuple of (is_valid, warnings)
        """
        warnings = []

        if not content or not content.strip():
            return False, ["Content cannot be empty"]

        # Check for basic markdown structure
        lines = content.split("\n")

        # Check for at least one header
        has_header = any(line.strip().startswith("#") for line in lines)
        if not has_header:
            warnings.append("No headers found in markdown content")

        # Check for very short content
        if len(content.strip()) < 50:
            warnings.append("Content is very short (less than 50 characters)")

        # Check for common markdown issues
        for i, line in enumerate(lines, 1):
            # Check for unmatched code blocks
            if line.strip().startswith("```"):
                # This is a simple check - a full parser would be more accurate
                pass

        return True, warnings
