"""
Configuration module for AgentSpec.

This module provides configuration file paths and default configurations
for the AgentSpec system.
"""

from pathlib import Path


def get_default_config_path() -> Path:
    """Get the path to the default configuration file"""
    return Path(__file__).parent / "default.yaml"


def get_logging_config_path() -> Path:
    """Get the path to the logging configuration file"""
    return Path(__file__).parent / "logging.yaml"
