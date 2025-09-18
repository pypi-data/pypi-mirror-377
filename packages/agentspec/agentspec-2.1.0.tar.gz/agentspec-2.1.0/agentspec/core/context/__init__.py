"""
Context Detection Module

This module provides comprehensive project context detection capabilities
including technology stack analysis, project type identification, and
instruction suggestions based on project characteristics.

The module is organized into several submodules:
- types: Core types and dataclasses
- language_detector: Programming language detection
- framework_detector: Framework and library detection
- project_analyzer: High-level project analysis
- suggestion_engine: Instruction suggestion logic
"""

from .types import (
    Dependency,
    FileStructure,
    Framework,
    GitInfo,
    InstructionSuggestion,
    Language,
    ProjectContext,
    ProjectType,
    TechnologyStack,
)

__all__ = [
    "Dependency",
    "FileStructure",
    "Framework",
    "GitInfo",
    "InstructionSuggestion",
    "Language",
    "ProjectContext",
    "ProjectType",
    "TechnologyStack",
]
