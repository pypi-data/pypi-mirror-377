"""
CLI module for AgentSpec.

Contains command-line interface components including the main entry point,
interactive wizard, and command handlers.
"""

from .interactive import InteractiveWizard
from .main import main

__all__ = ["main", "InteractiveWizard"]
