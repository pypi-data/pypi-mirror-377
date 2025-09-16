"""
Instruction Database Module

This module provides comprehensive instruction management capabilities including
loading, validation, querying, and conflict detection for AgentSpec instructions.

The module is organized into several submodules:
- types: Core types and dataclasses
- loader: Instruction loading from JSON files
- validator: Instruction validation logic
- conflict_detector: Conflict detection between instructions
- query_engine: Instruction querying and filtering
"""

from .types import (
    Condition,
    Conflict,
    Instruction,
    InstructionMetadata,
    LanguageVariant,
    Parameter,
    ValidationResult,
    VersionInfo,
)

__all__ = [
    "Condition",
    "Conflict",
    "Instruction",
    "InstructionMetadata",
    "LanguageVariant",
    "Parameter",
    "ValidationResult",
    "VersionInfo",
]
