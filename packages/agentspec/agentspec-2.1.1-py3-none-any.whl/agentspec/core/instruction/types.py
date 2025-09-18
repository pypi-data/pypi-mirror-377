"""
Instruction Database Types and Models

This module defines the core types, dataclasses, and models used throughout
the instruction database system for loading, validating, and managing instructions.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class Condition:
    """Represents a condition for instruction applicability"""

    type: str  # project_type, technology, file_exists, dependency_exists
    value: str
    operator: str  # equals, contains, matches, not_equals


@dataclass
class Parameter:
    """Represents a parameter for instruction customization"""

    name: str
    type: str  # string, number, boolean, array
    default: Any = None
    description: str = ""
    required: bool = False


@dataclass
class LanguageVariant:
    """Represents a language-specific variant of instruction content"""

    language: str  # ISO 639-1 language code (e.g., 'en', 'es', 'fr')
    content: str
    parameters: Optional[List[Parameter]] = None


@dataclass
class InstructionMetadata:
    """Metadata for an instruction"""

    category: str
    priority: int = 5
    author: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    default_language: str = "en"


@dataclass
class Instruction:
    """Represents a single AgentSpec instruction"""

    id: str
    version: str
    tags: List[str]
    content: str
    conditions: Optional[List[Condition]] = None
    parameters: Optional[List[Parameter]] = None
    dependencies: Optional[List[str]] = None
    metadata: Optional[InstructionMetadata] = None
    language_variants: Optional[Dict[str, LanguageVariant]] = None


@dataclass
class ValidationResult:
    """Result of instruction validation"""

    is_valid: bool
    errors: List[str]
    warnings: List[str]


@dataclass
class Conflict:
    """Represents a conflict between instructions"""

    instruction1_id: str
    instruction2_id: str
    conflict_type: str
    description: str
    severity: str = "medium"  # low, medium, high


@dataclass
class VersionInfo:
    """Represents version information with semantic versioning support"""

    major: int
    minor: int
    patch: int

    @classmethod
    def from_string(cls, version_str: str) -> "VersionInfo":
        """Parse version string in format 'major.minor.patch'"""
        parts = version_str.split(".")
        if len(parts) != 3:
            raise ValueError(f"Invalid version format: {version_str}")

        try:
            major, minor, patch = map(int, parts)
            return cls(major, minor, patch)
        except ValueError:
            raise ValueError(f"Invalid version format: {version_str}")

    def __str__(self) -> str:
        """String representation of version"""
        return f"{self.major}.{self.minor}.{self.patch}"

    def __lt__(self, other: "VersionInfo") -> bool:
        """Less than comparison"""
        return (self.major, self.minor, self.patch) < (
            other.major,
            other.minor,
            other.patch,
        )

    def __le__(self, other: "VersionInfo") -> bool:
        """Less than or equal comparison"""
        return (self.major, self.minor, self.patch) <= (
            other.major,
            other.minor,
            other.patch,
        )

    def __gt__(self, other: "VersionInfo") -> bool:
        """Greater than comparison"""
        return (self.major, self.minor, self.patch) > (
            other.major,
            other.minor,
            other.patch,
        )

    def __ge__(self, other: "VersionInfo") -> bool:
        """Greater than or equal comparison"""
        return (self.major, self.minor, self.patch) >= (
            other.major,
            other.minor,
            other.patch,
        )

    def __eq__(self, other: object) -> bool:
        """Equality comparison"""
        if not isinstance(other, VersionInfo):
            return False
        return (self.major, self.minor, self.patch) == (
            other.major,
            other.minor,
            other.patch,
        )
