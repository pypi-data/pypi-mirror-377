"""
AgentSpec - Specification-driven development toolkit.

A modular toolkit for generating comprehensive development specifications
with smart context detection and template-based generation.
"""

__version__ = "2.0.0"
__author__ = "Keyur Golani"

from .core.ai_integrator import AIBestPracticesIntegrator
from .core.context_detector import ContextDetector
from .core.instruction_database import InstructionDatabase
from .core.spec_generator import SpecGenerator
from .core.template_manager import TemplateManager

__all__ = [
    "SpecGenerator",
    "InstructionDatabase",
    "TemplateManager",
    "ContextDetector",
    "AIBestPracticesIntegrator",
]
