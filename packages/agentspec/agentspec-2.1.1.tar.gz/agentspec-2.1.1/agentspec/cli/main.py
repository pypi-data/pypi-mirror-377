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

try:
    import argcomplete

    ARGCOMPLETE_AVAILABLE = True
except ImportError:
    ARGCOMPLETE_AVAILABLE = False

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
from .completers import (
    comma_separated_instruction_completer,
    comma_separated_tag_completer,
    format_completer,
    output_format_completer,
    tag_completer,
)
from .completion_install import (
    completion_status_command,
    install_completion_command,
    show_completion_command,
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

Shell Completion:
  agentspec --install-completion     # Install completion for current shell
  agentspec --show-completion        # Show completion script
  agentspec --completion-status      # Check completion status

Completion Examples:
  agentspec generate --tags <TAB>    # Complete available tags
  agentspec generate --template <TAB> # Complete template names
  agentspec list-tags --category <TAB> # Complete categories
  agentspec generate --format <TAB>   # Complete output formats
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

        # Completion installation options
        parser.add_argument(
            "--install-completion",
            action="store_true",
            help="Install shell completion for AgentSpec CLI",
        )
        parser.add_argument(
            "--show-completion",
            action="store_true",
            help="Show completion script for manual installation",
        )
        parser.add_argument(
            "--completion-status",
            action="store_true",
            help="Show completion installation status",
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

        # Add completion support
        self._add_completion_support(parser)

        return parser

    def _add_completion_support(self, parser: argparse.ArgumentParser) -> None:
        """
        Add argcomplete completion support to parser.

        Args:
            parser: ArgumentParser to add completion to
        """
        if not ARGCOMPLETE_AVAILABLE:
            return

        try:
            # Import completers
            from .completers import (  # noqa: F401
                category_completer,
                project_type_completer,
                template_completer,
            )

            # Configure completers for subparser actions
            for action in parser._actions:
                if isinstance(action, argparse._SubParsersAction):
                    for choice, subparser in action.choices.items():
                        self._configure_subparser_completers(subparser, choice)

            # Enable argcomplete
            argcomplete.autocomplete(parser)

        except Exception as e:
            # Silently fail if completion setup fails
            if hasattr(logging, "getLogger"):
                logger = logging.getLogger(__name__)
                logger.debug(f"Failed to setup completion: {e}")

    def _configure_subparser_completers(
        self, subparser: argparse.ArgumentParser, command: str
    ) -> None:
        """
        Configure completers for a specific subparser.

        Args:
            subparser: Subparser to configure
            command: Command name for context
        """
        from .completers import (
            category_completer,
            output_file_completer,
            project_directory_completer,
            project_type_completer,
            spec_file_completer,
            template_completer,
        )

        for action in subparser._actions:
            if not hasattr(action, "dest"):
                continue

            dest = action.dest

            # Configure completers based on argument destination
            if dest == "format":
                action.completer = format_completer  # type: ignore
            elif dest == "output_format":
                action.completer = output_format_completer  # type: ignore
            elif dest == "tag":
                action.completer = tag_completer  # type: ignore
            elif dest == "tags":
                action.completer = comma_separated_tag_completer  # type: ignore
            elif dest == "instructions":
                action.completer = comma_separated_instruction_completer  # type: ignore
            elif dest == "template":
                action.completer = template_completer  # type: ignore
            elif dest == "category":
                action.completer = category_completer  # type: ignore
            elif dest == "project_type":
                action.completer = project_type_completer  # type: ignore
            elif dest == "output":
                # File completion for output files - supports files and directories
                if output_file_completer:
                    action.completer = output_file_completer  # type: ignore
            elif dest == "project_path":
                # Directory completion for project paths - directories only
                if project_directory_completer:
                    action.completer = project_directory_completer  # type: ignore
            elif dest == "spec_file":
                # Spec file completion - prioritize markdown files
                if spec_file_completer:
                    action.completer = spec_file_completer  # type: ignore

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

        # Handle completion installation commands first (don't need services)
        if parsed_args.install_completion:
            return install_completion_command()
        elif parsed_args.show_completion:
            return show_completion_command()
        elif parsed_args.completion_status:
            return completion_status_command()

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
