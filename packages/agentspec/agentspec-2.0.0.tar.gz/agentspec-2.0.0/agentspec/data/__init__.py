"""
Data module for AgentSpec.

Contains data files including instruction database, templates, and schemas.
This module provides access to the packaged data resources.
"""

from pathlib import Path

# Get the directory containing this module
DATA_DIR = Path(__file__).parent

# Define paths to data subdirectories
INSTRUCTIONS_DIR = DATA_DIR / "instructions"
TEMPLATES_DIR = DATA_DIR / "templates"
SCHEMAS_DIR = DATA_DIR / "schemas"


def get_data_path(relative_path: str) -> Path:
    """Get absolute path to a data file."""
    return DATA_DIR / relative_path


def get_instructions_path() -> Path:
    """Get path to instructions directory."""
    return INSTRUCTIONS_DIR


def get_templates_path() -> Path:
    """Get path to templates directory."""
    return TEMPLATES_DIR


def get_schemas_path() -> Path:
    """Get path to schemas directory."""
    return SCHEMAS_DIR
