"""
CLI Command Handlers

This module provides individual command handler functions for the AgentSpec CLI,
with proper error handling and user feedback.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..cli.interactive import InteractiveWizard
from ..core.ai_integrator import AIBestPracticesIntegrator
from ..core.context_detector import ContextDetector
from ..core.instruction_database import InstructionDatabase
from ..core.spec_generator import SpecConfig, SpecGenerator
from ..core.template_manager import TemplateManager

logger = logging.getLogger(__name__)


class CommandError(Exception):
    """Exception raised for command execution errors"""

    pass


def list_tags_command(
    instruction_db: InstructionDatabase,
    category: Optional[str] = None,
    verbose: bool = False,
) -> int:
    """
    List all available tags with instruction counts.

    Args:
        instruction_db: InstructionDatabase instance
        category: Optional category filter
        verbose: Show detailed information

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        print("Available tags:")
        print("=" * 50)

        # Load instructions
        instructions = instruction_db.load_instructions()

        if not instructions:
            print("No instructions found.")
            return 0

        # Group tags by category for better organization
        categories = {
            "General": [
                "general",
                "quality",
                "standards",
                "persistence",
                "tracking",
            ],
            "Testing": [
                "testing",
                "tdd",
                "validation",
                "automation",
                "browser",
            ],
            "Frontend": [
                "frontend",
                "ui",
                "react",
                "vue",
                "angular",
                "mobile",
                "responsive",
            ],
            "Backend": [
                "backend",
                "api",
                "database",
                "security",
                "performance",
            ],
            "Languages": ["javascript", "typescript", "python", "type-safety"],
            "DevOps": [
                "docker",
                "ci-cd",
                "deployment",
                "monitoring",
                "backup",
            ],
            "Architecture": [
                "architecture",
                "microservices",
                "modularity",
                "maintainability",
            ],
        }

        all_tags = instruction_db.get_all_tags()

        # Filter by category if specified
        if category:
            if category.title() in categories:
                category_tags = categories[category.title()]
                categories = {category.title(): category_tags}
            else:
                print(f"Unknown category: {category}")
                print(f"Available categories: {', '.join(categories.keys())}")
                return 1

        for cat_name, cat_tags in categories.items():
            print(f"\n{cat_name}:")
            for tag in cat_tags:
                if tag in all_tags:
                    count = sum(1 for inst in instructions.values() if tag in inst.tags)
                    if verbose:
                        # Show sample instructions for this tag
                        sample_instructions = [
                            inst.id
                            for inst in instructions.values()
                            if tag in inst.tags
                        ][:3]
                        sample_text = (
                            f" (e.g., {', '.join(sample_instructions)})"
                            if sample_instructions
                            else ""
                        )
                        print(f"  {tag:<20} ({count} instructions){sample_text}")
                    else:
                        print(f"  {tag:<20} ({count} instructions)")

        # Show any uncategorized tags
        categorized_tags = set()
        for tags in categories.values():
            categorized_tags.update(tags)

        uncategorized = all_tags - categorized_tags
        if uncategorized:
            print("\nOther:")
            for tag in sorted(uncategorized):
                count = sum(1 for inst in instructions.values() if tag in inst.tags)
                print(f"  {tag:<20} ({count} instructions)")

        return 0

    except Exception as e:
        logger.error(f"Error listing tags: {e}")
        print(f"Error: {e}", file=sys.stderr)
        return 1


def list_instructions_command(
    instruction_db: InstructionDatabase,
    tag: Optional[str] = None,
    category: Optional[str] = None,
    verbose: bool = False,
) -> int:
    """
    List instructions, optionally filtered by tag or category.

    Args:
        instruction_db: InstructionDatabase instance
        tag: Optional tag filter
        category: Optional category filter
        verbose: Show detailed information

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        instructions = instruction_db.load_instructions()

        if not instructions:
            print("No instructions found.")
            return 0

        # Filter instructions
        filtered_instructions = []

        if tag:
            filtered_instructions = instruction_db.get_by_tags([tag])
            if not filtered_instructions:
                print(f"No instructions found for tag: {tag}")
                return 0
            print(f"\nInstructions for tag '{tag}':")
        elif category:
            filtered_instructions = instruction_db.get_instructions_by_category(
                category
            )
            if not filtered_instructions:
                print(f"No instructions found for category: {category}")
                return 0
            print(f"\nInstructions for category '{category}':")
        else:
            filtered_instructions = list(instructions.values())
            print(f"\nAll instructions ({len(filtered_instructions)} total):")

        print("=" * 60)

        for instruction in filtered_instructions:
            print(f"\n{instruction.id.replace('_', ' ').title()}:")
            print(f"  ID: {instruction.id}")
            print(f"  Version: {instruction.version}")
            print(f"  Tags: {', '.join(instruction.tags)}")

            if instruction.metadata:
                print(f"  Category: {instruction.metadata.category}")
                print(f"  Priority: {instruction.metadata.priority}")

            if verbose:
                print(f"  Content: {instruction.content}")
                if instruction.conditions:
                    print(f"  Conditions: {len(instruction.conditions)} defined")
                if instruction.parameters:
                    print(f"  Parameters: {len(instruction.parameters)} defined")
                if instruction.dependencies:
                    print(f"  Dependencies: {', '.join(instruction.dependencies)}")
            else:
                # Show truncated content
                content_preview = instruction.content[:100]
                if len(instruction.content) > 100:
                    content_preview += "..."
                print(f"  Content: {content_preview}")

        return 0

    except Exception as e:
        logger.error(f"Error listing instructions: {e}")
        print(f"Error: {e}", file=sys.stderr)
        return 1


def list_templates_command(
    template_manager: TemplateManager,
    project_type: Optional[str] = None,
    verbose: bool = False,
) -> int:
    """
    List available templates.

    Args:
        template_manager: TemplateManager instance
        project_type: Optional project type filter
        verbose: Show detailed information

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        templates = template_manager.load_templates()

        if not templates:
            print("No templates found.")
            return 0

        # Filter by project type if specified
        if project_type:
            filtered_templates = template_manager.get_templates_by_project_type(
                project_type
            )
            if not filtered_templates:
                print(f"No templates found for project type: {project_type}")
                available_types = template_manager.get_all_project_types()
                print(f"Available project types: {', '.join(sorted(available_types))}")
                return 0
            templates_to_show = {t.id: t for t in filtered_templates}
            print(f"\nTemplates for project type '{project_type}':")
        else:
            templates_to_show = templates
            print(f"\nAll templates ({len(templates)} total):")

        print("=" * 60)

        # Group by project type
        by_project_type: Dict[str, List[Any]] = {}
        for template in templates_to_show.values():
            pt = template.project_type
            if pt not in by_project_type:
                by_project_type[pt] = []
            by_project_type[pt].append(template)

        for proj_type, type_templates in sorted(by_project_type.items()):
            if not project_type:  # Only show grouping if not filtering
                print(f"\n## {proj_type.upper().replace('_', ' ')}")

            for template in sorted(type_templates, key=lambda t: t.name):
                print(f"\n{template.name} (ID: {template.id})")
                print(f"  Version: {template.version}")
                print(f"  Description: {template.description}")

                if template.technology_stack:
                    print(f"  Technologies: {', '.join(template.technology_stack)}")

                if template.metadata:
                    print(f"  Complexity: {template.metadata.complexity}")

                if verbose:
                    print(f"  Default tags: {', '.join(template.default_tags)}")
                    if template.required_instructions:
                        print(
                            f"  Required instructions: {len(template.required_instructions)}"
                        )
                    if template.optional_instructions:
                        print(
                            f"  Optional instructions: {len(template.optional_instructions)}"
                        )
                    if template.parameters:
                        print(f"  Parameters: {', '.join(template.parameters.keys())}")

        return 0

    except Exception as e:
        logger.error(f"Error listing templates: {e}")
        print(f"Error: {e}", file=sys.stderr)
        return 1


def generate_spec_command(
    spec_generator: SpecGenerator,
    tags: Optional[List[str]] = None,
    instructions: Optional[List[str]] = None,
    template_id: Optional[str] = None,
    output_file: Optional[str] = None,
    output_format: str = "markdown",
    project_path: Optional[str] = None,
    language: str = "en",
    include_metadata: bool = True,
) -> int:
    """
    Generate a specification based on provided parameters.

    Args:
        spec_generator: SpecGenerator instance
        tags: List of tags to include
        instructions: List of specific instruction IDs
        template_id: Template ID to use
        output_file: Output file path
        output_format: Output format (markdown, json, yaml)
        project_path: Project path for context detection
        language: Language for specification
        include_metadata: Include metadata section

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        # Validate inputs
        if not tags and not instructions and not template_id:
            print(
                "Error: Must specify tags, instructions, or template",
                file=sys.stderr,
            )
            return 1

        # Create configuration
        config = SpecConfig(
            selected_tags=tags or [],
            selected_instructions=instructions or [],
            template_id=template_id,
            output_format=output_format,
            language=language,
            include_metadata=include_metadata,
        )

        # Detect project context if project path provided
        if project_path:
            try:
                context = spec_generator.context_detector.analyze_project(project_path)
                config.project_context = context
                print(f"Detected project type: {context.project_type.value}")
                print(
                    f"Detected technologies: {', '.join([fw.name for fw in context.technology_stack.frameworks])}"
                )
            except Exception as e:
                logger.warning(f"Failed to analyze project context: {e}")
                print(f"Warning: Could not analyze project context: {e}")

        # Generate specification
        print("Generating specification...")
        spec = spec_generator.generate_spec(config)

        # Validate specification
        if spec.validation_result and not spec.validation_result.is_valid:
            print("⚠️  Specification validation warnings:")
            for error in spec.validation_result.errors:
                print(f"  - {error}")

        if spec.validation_result and spec.validation_result.warnings:
            print("ℹ️  Specification warnings:")
            for warning in spec.validation_result.warnings:
                print(f"  - {warning}")

        # Export specification
        if output_file:
            spec_generator.export_spec(spec, output_file)
            print(f"Specification saved to: {output_file}")
        else:
            print("\n" + "=" * 80)
            print(spec.content)

        print(
            f"\nGenerated specification with {len(spec.instructions_used)} instructions"
        )
        return 0

    except Exception as e:
        logger.error(f"Error generating specification: {e}")
        print(f"Error: {e}", file=sys.stderr)
        return 1


def interactive_command(spec_generator: SpecGenerator) -> int:
    """
    Run interactive wizard for specification generation.

    Args:
        spec_generator: SpecGenerator instance

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        wizard = InteractiveWizard()

        # Set the services on the wizard - they're already initialized in __init__
        # Just need to set the spec_generator
        wizard.spec_generator = spec_generator

        result = wizard.run_wizard()

        if not result:
            return 1  # Wizard was cancelled or failed

        # Generate the actual specification using the wizard result
        try:
            # Create SpecConfig from wizard result
            config = SpecConfig(
                selected_tags=result.get("selected_tags", []),
                selected_instructions=[
                    inst["id"] for inst in result.get("instructions", [])
                ],
                template_id=result.get("template_id"),
                output_format="markdown",
                language="en",
                include_metadata=True,
                project_context=result.get("project_context"),
            )

            # Generate specification
            spec = spec_generator.generate_spec(config)

            # Export to file
            output_file = result.get("output_file", "project_spec.md")
            spec_generator.export_spec(spec, output_file)

            print("✅ Specification generated successfully!")
            print(f"📄 Saved to: {output_file}")

            return 0

        except Exception as e:
            logger.error(f"Error generating specification: {e}")
            print(f"Error generating specification: {e}", file=sys.stderr)
            return 1

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return 1
    except Exception as e:
        logger.error(f"Error in interactive mode: {e}")
        print(f"Error: {e}", file=sys.stderr)
        return 1


def analyze_project_command(
    context_detector: ContextDetector,
    project_path: str,
    output_file: Optional[str] = None,
    suggest_instructions: bool = True,
) -> int:
    """
    Analyze a project and detect its context.

    Args:
        context_detector: ContextDetector instance
        project_path: Path to project directory
        output_file: Optional output file for analysis results
        suggest_instructions: Whether to suggest instructions

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        print(f"Analyzing project at: {project_path}")

        # Analyze project
        context = context_detector.analyze_project(project_path)

        # Display results
        print("\n" + "=" * 60)
        print("PROJECT ANALYSIS RESULTS")
        print("=" * 60)

        print(f"\nProject Type: {context.project_type.value}")
        print(f"Confidence Score: {context.confidence_score:.2f}")

        print("\nTechnology Stack:")
        if context.technology_stack.languages:
            print(
                f"  Languages: {', '.join([lang.value for lang in context.technology_stack.languages])}"
            )
        if context.technology_stack.frameworks:
            frameworks_info = []
            for fw in context.technology_stack.frameworks:
                fw_info = fw.name
                if fw.confidence < 1.0:
                    fw_info += f" ({fw.confidence:.1f})"
                frameworks_info.append(fw_info)
            print(f"  Frameworks: {', '.join(frameworks_info)}")
        if context.technology_stack.databases:
            print(f"  Databases: {', '.join(context.technology_stack.databases)}")
        if context.technology_stack.tools:
            print(f"  Tools: {', '.join(context.technology_stack.tools)}")

        print("\nFile Structure:")
        print(f"  Total files: {context.file_structure.total_files}")
        print(f"  Directories: {len(context.file_structure.directories)}")
        if context.file_structure.config_files:
            print(f"  Config files: {len(context.file_structure.config_files)}")
        if context.file_structure.test_files:
            print(f"  Test files: {len(context.file_structure.test_files)}")

        if context.dependencies:
            print(f"\nDependencies: {len(context.dependencies)} found")
            # Show top dependencies
            top_deps = context.dependencies[:5]
            for dep in top_deps:
                version_info = f" ({dep.version})" if dep.version else ""
                print(f"  - {dep.name}{version_info}")
            if len(context.dependencies) > 5:
                print(f"  ... and {len(context.dependencies) - 5} more")

        if context.git_info and context.git_info.is_git_repo:
            print("\nGit Repository:")
            print(f"  Branch: {context.git_info.branch}")
            print(f"  Commits: {context.git_info.commit_count}")
            if context.git_info.remote_url:
                print(f"  Remote: {context.git_info.remote_url}")

        # Suggest instructions if requested
        if suggest_instructions:
            print("\n" + "=" * 60)
            print("INSTRUCTION SUGGESTIONS")
            print("=" * 60)

            suggestions = context_detector.suggest_instructions(context)

            if suggestions:
                print(f"\nTop {min(10, len(suggestions))} suggested instructions:")
                for i, suggestion in enumerate(suggestions[:10], 1):
                    print(f"\n{i}. {suggestion.instruction_id}")
                    print(f"   Confidence: {suggestion.confidence:.2f}")
                    print(f"   Tags: {', '.join(suggestion.tags)}")
                    if suggestion.reasons:
                        print(f"   Reasons: {'; '.join(suggestion.reasons[:2])}")
            else:
                print("\nNo specific instruction suggestions found.")

        # Save to file if requested
        if output_file:
            import json

            analysis_data: Dict[str, Any] = {
                "project_path": context.project_path,
                "project_type": context.project_type.value,
                "confidence_score": context.confidence_score,
                "technology_stack": {
                    "languages": [
                        lang.value for lang in context.technology_stack.languages
                    ],
                    "frameworks": [
                        {"name": fw.name, "confidence": fw.confidence}
                        for fw in context.technology_stack.frameworks
                    ],
                    "databases": context.technology_stack.databases,
                    "tools": context.technology_stack.tools,
                },
                "file_structure": {
                    "total_files": context.file_structure.total_files,
                    "directories": len(context.file_structure.directories),
                    "config_files": len(context.file_structure.config_files),
                    "test_files": len(context.file_structure.test_files),
                },
                "dependencies_count": len(context.dependencies),
            }

            if suggest_instructions and suggestions:
                analysis_data["suggested_instructions"] = [
                    {
                        "id": s.instruction_id,
                        "confidence": s.confidence,
                        "tags": s.tags,
                        "reasons": s.reasons,
                    }
                    for s in suggestions[:10]
                ]

            with open(output_file, "w") as f:
                json.dump(analysis_data, f, indent=2)

            print(f"\nAnalysis results saved to: {output_file}")

        return 0

    except Exception as e:
        logger.error(f"Error analyzing project: {e}")
        print(f"Error: {e}", file=sys.stderr)
        return 1


def validate_spec_command(spec_generator: SpecGenerator, spec_file: str) -> int:
    """
    Validate an existing specification file.

    Args:
        spec_generator: SpecGenerator instance
        spec_file: Path to specification file

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        spec_path = Path(spec_file)
        if not spec_path.exists():
            print(
                f"Error: Specification file not found: {spec_file}",
                file=sys.stderr,
            )
            return 1

        # Read specification content
        with open(spec_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Create a GeneratedSpec for validation
        from ..core.spec_generator import GeneratedSpec

        spec = GeneratedSpec(
            content=content, format="markdown"  # Assume markdown for now
        )

        # Validate
        print(f"Validating specification: {spec_file}")
        validation_result = spec_generator.validate_spec(spec)

        if validation_result.is_valid:
            print("✅ Specification is valid")
        else:
            print("❌ Specification validation failed:")
            for error in validation_result.errors:
                print(f"  - {error}")

        if validation_result.warnings:
            print("\n⚠️  Warnings:")
            for warning in validation_result.warnings:
                print(f"  - {warning}")

        return 0 if validation_result.is_valid else 1

    except Exception as e:
        logger.error(f"Error validating specification: {e}")
        print(f"Error: {e}", file=sys.stderr)
        return 1


def version_command() -> int:
    """
    Display version information.

    Returns:
        Exit code (always 0)
    """
    try:
        # Try to get version from package metadata first
        try:
            import importlib.metadata

            version = importlib.metadata.version("agentspec")
        except (ImportError, importlib.metadata.PackageNotFoundError):
            # Fall back to version from __init__.py
            try:
                from agentspec import __version__

                version = __version__
            except ImportError:
                version = "1.0.1-dev"

        print(f"AgentSpec {version}")
        print("Specification-Driven Development for AI Agents")
        print("https://github.com/keyurgolani/AgentSpec")

        return 0

    except Exception as e:
        logger.error(f"Error displaying version: {e}")
        print("AgentSpec 1.0.1-dev")
        return 0


def integrate_command(
    instruction_db: InstructionDatabase,
    template_manager: TemplateManager,
    context_detector: ContextDetector,
    project_path: str = ".",
    analyze_only: bool = False,
    output_format: str = "text",
) -> int:
    """
    Integrate AI best practices into an existing project.

    Args:
        instruction_db: InstructionDatabase instance
        template_manager: TemplateManager instance
        context_detector: ContextDetector instance
        project_path: Path to the project directory
        analyze_only: Only analyze the project, don't create integration files
        output_format: Output format for analysis results (text or json)

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        project_path_obj = Path(project_path).resolve()

        if not project_path_obj.exists():
            print(
                f"Error: Project path does not exist: {project_path}", file=sys.stderr
            )
            return 1

        if output_format != "json":
            print(f"🔍 Analyzing project: {project_path_obj}")

        integrator = AIBestPracticesIntegrator(
            project_path_obj,
            instruction_db,
            template_manager,
            context_detector,
        )

        # Analyze the project
        analysis = integrator.analyze_project()

        if output_format == "json":
            print(json.dumps(analysis, indent=2))
        else:
            print("\n🔍 Project Analysis Results")
            print(f"{'='*50}")
            print(f"Project Type: {analysis['project_type']}")
            print(f"Technologies: {', '.join(analysis.get('technologies', []))}")
            print(f"AI Tools Present: {analysis['has_ai_tools']}")
            print(f"Security Level: {analysis['security_level']}")
            print(f"Integration Priority: {analysis['integration_priority']}")

            print(
                f"\n📋 Recommended AI Instructions ({len(analysis['recommended_ai_instructions'])}):"
            )
            for instruction in analysis["recommended_ai_instructions"]:
                print(f"  - {instruction}")

            print(
                f"\n📄 Recommended Templates ({len(analysis['recommended_templates'])}):"
            )
            for template in analysis["recommended_templates"]:
                print(f"  - {template}")

        if not analyze_only:
            # Generate integration plan
            plan = integrator.generate_integration_plan(analysis)

            # Create integration files
            integrator.create_integration_files(analysis, plan)

            print("\n✅ AI Best Practices Integration Complete!")
            print(f"📁 Files created in: {project_path_obj / '.agentspec'}")
            print("📖 Review the integration plan: .agentspec/ai_integration_plan.md")
            print(
                "🚀 Start with: agentspec generate --template ai-comprehensive-framework"
            )

        return 0

    except Exception as e:
        logger.error(f"Integration failed: {e}")
        print(f"Error: {e}", file=sys.stderr)
        return 1


def help_command(command: Optional[str] = None) -> int:
    """
    Display help information.

    Args:
        command: Optional specific command to show help for

    Returns:
        Exit code (always 0)
    """
    if command:
        # Show help for specific command
        help_text = {
            "list-tags": """
List available instruction tags.

Usage: agentspec list-tags [OPTIONS]

Options:
  --category TEXT    Filter by category
  --verbose         Show detailed information
            """,
            "list-instructions": """
List instructions, optionally filtered.

Usage: agentspec list-instructions [OPTIONS]

Options:
  --tag TEXT        Filter by tag
  --category TEXT   Filter by category
  --verbose         Show detailed information
            """,
            "list-templates": """
List available templates.

Usage: agentspec list-templates [OPTIONS]

Options:
  --project-type TEXT  Filter by project type
  --verbose           Show detailed information
            """,
            "generate": """
Generate a specification.

Usage: agentspec generate [OPTIONS]

Options:
  --tags TEXT           Comma-separated list of tags
  --instructions TEXT   Comma-separated list of instruction IDs
  --template TEXT       Template ID to use
  --output FILE         Output file path
  --format TEXT         Output format (markdown, json, yaml)
  --project-path PATH   Project path for context detection
  --language TEXT       Language code (default: en)
  --no-metadata        Exclude metadata section
            """,
            "interactive": """
Run interactive wizard.

Usage: agentspec interactive

The interactive wizard will guide you through:
- Project type detection
- Template selection
- Tag and instruction selection
- Specification generation
            """,
            "analyze": """
Analyze a project and detect context.

Usage: agentspec analyze PROJECT_PATH [OPTIONS]

Options:
  --output FILE         Save analysis to file
  --no-suggestions     Don't suggest instructions
            """,
            "validate": """
Validate a specification file.

Usage: agentspec validate SPEC_FILE
            """,
            "integrate": """
Integrate AI best practices into an existing project.

Usage: agentspec integrate [PROJECT_PATH] [OPTIONS]

Arguments:
  PROJECT_PATH         Path to project directory (default: current directory)

Options:
  --analyze-only      Only analyze the project, don't create integration files
  --output-format     Output format for analysis results (text, json)
            """,
        }

        if command in help_text:
            print(help_text[command].strip())
        else:
            print(f"No help available for command: {command}")
    else:
        # Show general help
        print(
            """
AgentSpec - Specification-Driven Development for AI Agents

Usage: agentspec [COMMAND] [OPTIONS]

Commands:
  list-tags         List available instruction tags
  list-instructions List instructions
  list-templates    List available templates
  generate          Generate a specification
  interactive       Run interactive wizard
  analyze           Analyze project context
  validate          Validate specification file
  integrate         Integrate AI best practices into existing project
  version           Show version information
  help              Show this help message

Use 'agentspec help COMMAND' for command-specific help.

Examples:
  agentspec interactive
  agentspec list-tags --category testing
  agentspec generate --tags general,testing --output spec.md
  agentspec analyze ./my-project --output analysis.json
        """.strip()
        )

    return 0
