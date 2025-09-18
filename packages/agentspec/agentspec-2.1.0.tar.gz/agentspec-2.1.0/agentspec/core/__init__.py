"""
Core services module for AgentSpec.

Contains the main business logic components including instruction database,
spec generation, template management, context detection, and AI integration.

This module provides the core functionality for:
- Loading and managing instructions from JSON files
- Generating specifications from templates and instructions
- Detecting project context and technology stacks
- Managing templates for different project types
- Integrating AI best practices into existing projects
"""

from .ai_integrator import AIBestPracticesIntegrator
from .context_detector import ContextDetector
from .instruction_database import InstructionDatabase
from .spec_generator import SpecGenerator
from .template_manager import TemplateManager

__all__ = [
    "InstructionDatabase",
    "SpecGenerator",
    "TemplateManager",
    "ContextDetector",
    "AIBestPracticesIntegrator",
]
