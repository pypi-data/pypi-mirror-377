"""
Main CLI Entry Point

This module provides the main CLI entry point for AgentSpec with argument parsing,
subcommands, dependency injection, and service initialization.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional

from .. import __version__
from ..core.context_detector import ContextDetector
from ..core.instruction_database import InstructionDatabase
from ..core.spec_generator import SpecGenerator
from ..core.template_manager import TemplateManager
from ..utils.config import ConfigManager
from ..utils.logging import setup_logging
from .commands import (
    analyze_project_command,
    generate_spec_command,
    help_command,
    integrate_command,
    interactive_command,
    list_instructions_command,
    list_tags_command,
    list_templates_command,
    validate_spec_command,
    version_command,
)


class AgentSpecCLI:
    """Main CLI application class with dependency injection and service management"""

    def __init__(self) -> None:
        """Initialize CLI with service dependencies"""
        self.config_manager: Optional[ConfigManager] = None
        self.instruction_db: Optional[InstructionDatabase] = None
        self.template_manager: Optional[TemplateManager] = None
        self.context_detector: Optional[ContextDetector] = None
        self.spec_generator: Optional[SpecGenerator] = None
        self.logger: Optional[logging.Logger] = None

    def initialize_services(self, config_path: Optional[str] = None) -> None:
        """
        Initialize all services with dependency injection.

        Args:
            config_path: Optional path to configuration file
        """
        try:
            # Initialize configuration manager
            project_path = Path(config_path).parent if config_path else None
            self.config_manager = ConfigManager(project_path)
            config = self.config_manager.load_config()

            # Setup logging
            logging_config = config.get("logging", {})
            setup_logging(
                log_level=logging_config.get("level", "INFO"),
                structured=logging_config.get("structured", False),
                console_output=logging_config.get("console", True),
            )
            self.logger = logging.getLogger(__name__)
            self.logger.info("Initializing AgentSpec CLI services")

            # Initialize core services
            paths_config = config.get("paths", {})

            # Instruction database
            instructions_path = None
            if "instructions" in paths_config:
                instructions_path = Path(paths_config["instructions"])

            self.instruction_db = InstructionDatabase(
                instructions_path=instructions_path
            )

            # Template manager
            templates_path = None
            if "templates" in paths_config:
                templates_path = Path(paths_config["templates"])

            self.template_manager = TemplateManager(templates_path=templates_path)

            # Context detector
            self.context_detector = ContextDetector()

            # Spec generator (depends on other services)
            self.spec_generator = SpecGenerator(
                instruction_db=self.instruction_db,
                template_manager=self.template_manager,
                context_detector=self.context_detector,
            )

            self.logger.info("All services initialized successfully")

        except Exception as e:
            print(f"Error initializing services: {e}", file=sys.stderr)
            sys.exit(1)

    def create_parser(self) -> argparse.ArgumentParser:
        """Create the main argument parser with all subcommands"""
        parser = argparse.ArgumentParser(
            prog="agentspec",
            description="AgentSpec - Specification-Driven Development for AI Agents",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  agentspec interactive
  agentspec list-tags --category testing
  agentspec generate --tags general,testing --output spec.md
  agentspec analyze ./my-project --output analysis.json
  agentspec integrate ./my-project --analyze-only
  agentspec validate my-spec.md
            """,
        )

        # Global options
        parser.add_argument(
            "--config", "-c", metavar="FILE", help="Configuration file path"
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Enable verbose output",
        )
        parser.add_argument(
            "--quiet",
            "-q",
            action="store_true",
            help="Suppress non-error output",
        )
        parser.add_argument(
            "--version",
            action="version",
            version=f"%(prog)s {__version__}",
            help="Show version information",
        )

        # Create subparsers
        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        # List tags command
        tags_parser = subparsers.add_parser(
            "list-tags", help="List available instruction tags"
        )
        tags_parser.add_argument(
            "--category", metavar="CATEGORY", help="Filter by category"
        )
        tags_parser.add_argument(
            "--verbose", action="store_true", help="Show detailed information"
        )

        # List instructions command
        instructions_parser = subparsers.add_parser(
            "list-instructions", help="List instructions"
        )
        instructions_parser.add_argument("--tag", metavar="TAG", help="Filter by tag")
        instructions_parser.add_argument(
            "--category", metavar="CATEGORY", help="Filter by category"
        )
        instructions_parser.add_argument(
            "--verbose", action="store_true", help="Show detailed information"
        )

        # List templates command
        templates_parser = subparsers.add_parser(
            "list-templates", help="List available templates"
        )
        templates_parser.add_argument(
            "--project-type", metavar="TYPE", help="Filter by project type"
        )
        templates_parser.add_argument(
            "--verbose", action="store_true", help="Show detailed information"
        )

        # Generate command
        generate_parser = subparsers.add_parser(
            "generate", help="Generate a specification"
        )
        generate_parser.add_argument(
            "--tags",
            metavar="TAG1,TAG2,...",
            help="Comma-separated list of tags to include",
        )
        generate_parser.add_argument(
            "--instructions",
            metavar="ID1,ID2,...",
            help="Comma-separated list of instruction IDs",
        )
        generate_parser.add_argument(
            "--template", metavar="TEMPLATE_ID", help="Template ID to use"
        )
        generate_parser.add_argument(
            "--output", "-o", metavar="FILE", help="Output file path"
        )
        generate_parser.add_argument(
            "--format",
            choices=["markdown", "json", "yaml"],
            default="markdown",
            help="Output format",
        )
        generate_parser.add_argument(
            "--project-path",
            metavar="PATH",
            help="Project path for context detection",
        )
        generate_parser.add_argument(
            "--language", default="en", help="Language code (default: en)"
        )
        generate_parser.add_argument(
            "--no-metadata",
            action="store_true",
            help="Exclude metadata section",
        )

        # Interactive command
        subparsers.add_parser("interactive", help="Run interactive wizard")

        # Analyze command
        analyze_parser = subparsers.add_parser(
            "analyze", help="Analyze project context"
        )
        analyze_parser.add_argument(
            "project_path",
            metavar="PROJECT_PATH",
            help="Path to project directory",
        )
        analyze_parser.add_argument(
            "--output",
            "-o",
            metavar="FILE",
            help="Save analysis results to file",
        )
        analyze_parser.add_argument(
            "--no-suggestions",
            action="store_true",
            help="Don't suggest instructions",
        )

        # Validate command
        validate_parser = subparsers.add_parser(
            "validate", help="Validate specification file"
        )
        validate_parser.add_argument(
            "spec_file", metavar="SPEC_FILE", help="Path to specification file"
        )

        # Integrate command
        integrate_parser = subparsers.add_parser(
            "integrate", help="Integrate AI best practices into existing project"
        )
        integrate_parser.add_argument(
            "project_path",
            nargs="?",
            default=".",
            metavar="PROJECT_PATH",
            help="Path to project directory (default: current directory)",
        )
        integrate_parser.add_argument(
            "--analyze-only",
            action="store_true",
            help="Only analyze the project, don't create integration files",
        )
        integrate_parser.add_argument(
            "--output-format",
            choices=["text", "json"],
            default="text",
            help="Output format for analysis results",
        )

        # Version command
        subparsers.add_parser("version", help="Show version information")

        # Help command
        help_parser = subparsers.add_parser("help", help="Show help information")
        help_parser.add_argument(
            "help_target",
            nargs="?",
            metavar="COMMAND",
            help="Show help for specific command",
        )

        return parser

    def run(self, args: Optional[List[str]] = None) -> int:
        """
        Run the CLI application.

        Args:
            args: Optional command line arguments (uses sys.argv if None)

        Returns:
            Exit code (0 for success, non-zero for error)
        """
        parser = self.create_parser()
        try:
            parsed_args = parser.parse_args(args)
        except SystemExit as e:
            # Handle invalid commands gracefully
            return int(e.code) if e.code is not None else 1

        # Handle global options
        if parsed_args.quiet:
            logging.getLogger().setLevel(logging.ERROR)
        elif parsed_args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        # Initialize services (except for version and help commands)
        if parsed_args.command not in ["version", "help"]:
            try:
                self.initialize_services(parsed_args.config)
            except KeyboardInterrupt:
                print("\nOperation cancelled by user.", file=sys.stderr)
                return 1
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Error initializing services: {e}")
                print(f"Error initializing services: {e}", file=sys.stderr)
                return 1

        # Route to appropriate command handler
        try:
            if parsed_args.command == "list-tags":
                if self.instruction_db is None:
                    print(
                        "Error: InstructionDatabase not initialized",
                        file=sys.stderr,
                    )
                    return 1
                return list_tags_command(
                    self.instruction_db,
                    category=parsed_args.category,
                    verbose=parsed_args.verbose,
                )

            elif parsed_args.command == "list-instructions":
                if self.instruction_db is None:
                    print(
                        "Error: InstructionDatabase not initialized",
                        file=sys.stderr,
                    )
                    return 1
                return list_instructions_command(
                    self.instruction_db,
                    tag=parsed_args.tag,
                    category=parsed_args.category,
                    verbose=parsed_args.verbose,
                )

            elif parsed_args.command == "list-templates":
                if self.template_manager is None:
                    print(
                        "Error: TemplateManager not initialized",
                        file=sys.stderr,
                    )
                    return 1
                return list_templates_command(
                    self.template_manager,
                    project_type=parsed_args.project_type,
                    verbose=parsed_args.verbose,
                )

            elif parsed_args.command == "generate":
                tags = None
                if parsed_args.tags:
                    tags = [tag.strip() for tag in parsed_args.tags.split(",")]

                instructions = None
                if parsed_args.instructions:
                    instructions = [
                        inst.strip() for inst in parsed_args.instructions.split(",")
                    ]

                if self.spec_generator is None:
                    print("Error: SpecGenerator not initialized", file=sys.stderr)
                    return 1
                return generate_spec_command(
                    self.spec_generator,
                    tags=tags,
                    instructions=instructions,
                    template_id=parsed_args.template,
                    output_file=parsed_args.output,
                    output_format=parsed_args.format,
                    project_path=parsed_args.project_path,
                    language=parsed_args.language,
                    include_metadata=not parsed_args.no_metadata,
                )

            elif parsed_args.command == "interactive":
                if self.spec_generator is None:
                    print("Error: SpecGenerator not initialized", file=sys.stderr)
                    return 1
                return interactive_command(self.spec_generator)

            elif parsed_args.command == "analyze":
                if self.context_detector is None:
                    print(
                        "Error: ContextDetector not initialized",
                        file=sys.stderr,
                    )
                    return 1
                return analyze_project_command(
                    self.context_detector,
                    project_path=parsed_args.project_path,
                    output_file=parsed_args.output,
                    suggest_instructions=not parsed_args.no_suggestions,
                )

            elif parsed_args.command == "validate":
                if self.spec_generator is None:
                    print("Error: SpecGenerator not initialized", file=sys.stderr)
                    return 1
                return validate_spec_command(
                    self.spec_generator, spec_file=parsed_args.spec_file
                )

            elif parsed_args.command == "integrate":
                if (
                    self.instruction_db is None
                    or self.template_manager is None
                    or self.context_detector is None
                ):
                    print("Error: Required services not initialized", file=sys.stderr)
                    return 1
                return integrate_command(
                    self.instruction_db,
                    self.template_manager,
                    self.context_detector,
                    project_path=parsed_args.project_path,
                    analyze_only=parsed_args.analyze_only,
                    output_format=parsed_args.output_format,
                )

            elif parsed_args.command == "version":
                return version_command()

            elif parsed_args.command == "help":
                return help_command(
                    parsed_args.help_target
                    if hasattr(parsed_args, "help_target")
                    else None
                )

            else:
                # No command specified, show help
                parser.print_help()
                return 0

        except KeyboardInterrupt:
            print("\nOperation cancelled by user.", file=sys.stderr)
            return 1
        except Exception as e:
            if self.logger:
                self.logger.error(f"Unexpected error: {e}")
            print(f"Error: {e}", file=sys.stderr)
            return 1


def main() -> int:
    """Main entry point for the CLI application"""
    try:
        cli = AgentSpecCLI()
        return cli.run()
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
