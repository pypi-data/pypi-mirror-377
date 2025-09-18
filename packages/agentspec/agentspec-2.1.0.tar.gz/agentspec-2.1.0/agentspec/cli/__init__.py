"""
CLI module for AgentSpec.

Contains command-line interface components including the main entry point,
interactive wizard, command handlers, and completion infrastructure.
"""

from .interactive import InteractiveWizard
from .main import main

__all__ = ["main", "InteractiveWizard"]
