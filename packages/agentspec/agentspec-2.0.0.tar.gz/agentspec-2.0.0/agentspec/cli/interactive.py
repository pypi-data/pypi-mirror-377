"""
Interactive CLI Wizard

This module provides the InteractiveWizard class for interactive
specification generation with project detection and smart recommendations.
"""

import logging
import os
import sys
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Import core components
from ..core.context_detector import ContextDetector, ProjectContext, ProjectType
from ..core.instruction_database import InstructionDatabase
from ..core.template_manager import Template, TemplateManager, TemplateRecommendation
from ..utils.config import ConfigManager

logger = logging.getLogger(__name__)


class Colors:
    """ANSI color codes for terminal output"""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Colors
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Background colors
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"

    @classmethod
    def colorize(cls, text: str, color: str) -> str:
        """Colorize text if terminal supports it"""
        if os.getenv("NO_COLOR") or not sys.stdout.isatty():
            return text
        return f"{color}{text}{cls.RESET}"

    @classmethod
    def success(cls, text: str) -> str:
        return cls.colorize(f"✅ {text}", cls.GREEN)

    @classmethod
    def error(cls, text: str) -> str:
        return cls.colorize(f"❌ {text}", cls.RED)

    @classmethod
    def warning(cls, text: str) -> str:
        return cls.colorize(f"⚠️  {text}", cls.YELLOW)

    @classmethod
    def info(cls, text: str) -> str:
        return cls.colorize(f"ℹ️  {text}", cls.BLUE)

    @classmethod
    def highlight(cls, text: str) -> str:
        return cls.colorize(text, cls.BOLD + cls.CYAN)

    @classmethod
    def dim(cls, text: str) -> str:
        return cls.colorize(text, cls.DIM)


class WizardStep(Enum):
    """Enumeration of wizard steps"""

    WELCOME = "welcome"
    PROJECT_DETECTION = "project_detection"
    PROJECT_TYPE_SELECTION = "project_type_selection"
    TEMPLATE_RECOMMENDATION = "template_recommendation"
    TEMPLATE_SELECTION = "template_selection"
    TEMPLATE_CUSTOMIZATION = "template_customization"
    INSTRUCTION_SELECTION = "instruction_selection"
    SPEC_PREVIEW = "spec_preview"
    CONFIRMATION = "confirmation"
    COMPLETE = "complete"


@dataclass
class UserPreferences:
    """User preferences collected during the wizard"""

    project_path: str = "."
    project_type: Optional[ProjectType] = None
    selected_template: Optional[Template] = None
    template_parameters: Dict[str, Any] = field(default_factory=dict)
    selected_tags: Set[str] = field(default_factory=set)
    output_file: str = "project_spec.md"
    complexity_preference: str = "intermediate"  # beginner, intermediate, advanced
    include_optional_instructions: bool = True
    auto_detect_enabled: bool = True


@dataclass
class WizardState:
    """Current state of the wizard"""

    current_step: WizardStep = WizardStep.WELCOME
    step_history: List[WizardStep] = field(default_factory=list)
    project_context: Optional[ProjectContext] = None
    template_recommendations: List[TemplateRecommendation] = field(default_factory=list)
    available_templates: List[Template] = field(default_factory=list)
    user_preferences: UserPreferences = field(default_factory=UserPreferences)
    progress_percentage: int = 0


class InputValidator:
    """Utility class for input validation with helpful error messages"""

    @staticmethod
    def validate_path(path: str) -> Tuple[bool, str]:
        """Validate file system path"""
        if not path.strip():
            return False, "Path cannot be empty"

        expanded_path = os.path.expanduser(path.strip())
        if not os.path.exists(expanded_path):
            return False, f"Path does not exist: {expanded_path}"

        if not os.path.isdir(expanded_path):
            return False, f"Path is not a directory: {expanded_path}"

        if not os.access(expanded_path, os.R_OK):
            return False, f"No read permission for path: {expanded_path}"

        return True, expanded_path

    @staticmethod
    def validate_filename(filename: str) -> Tuple[bool, str]:
        """Validate output filename"""
        if not filename.strip():
            return False, "Filename cannot be empty"

        # Check for invalid characters
        invalid_chars = '<>:"|?*'
        if any(char in filename for char in invalid_chars):
            return (
                False,
                f"Filename contains invalid characters: {invalid_chars}",
            )

        # Check if directory exists
        file_path = Path(filename)
        if file_path.parent != Path(".") and not file_path.parent.exists():
            return False, f"Directory does not exist: {file_path.parent}"

        return True, filename.strip()

    @staticmethod
    def validate_number_range(
        value: str, min_val: int, max_val: int
    ) -> Tuple[bool, int]:
        """Validate number within range"""
        try:
            num = int(value.strip())
            if num < min_val or num > max_val:
                return False, 0
            return True, num
        except ValueError:
            return False, 0

    @staticmethod
    def validate_yes_no(value: str, default: bool = True) -> bool:
        """Validate yes/no input with default"""
        value = value.strip().lower()
        if not value:
            return default
        return value in ["y", "yes", "1", "true"]


class HelpSystem:
    """Contextual help system for the wizard"""

    HELP_TOPICS = {
        "navigation": """
Navigation Commands:
  back, b     - Go back to previous step
  help, h     - Show this help
  quit, q     - Exit the wizard

You can use these commands at most input prompts.
        """,
        "project_detection": """
Project Detection Help:
The wizard analyzes your project files to automatically detect:
• Programming languages used
• Frameworks and libraries
• Project structure patterns
• Configuration files

This helps recommend the most relevant templates and instructions.
If detection fails or is inaccurate, you can manually select your project type.
        """,
        "templates": """
Template Help:
Templates are pre-configured sets of instructions for specific project types.
They include:
• Default instruction tags relevant to the project type
• Required instructions that should always be included
• Optional instructions you can choose to include
• Customizable parameters for project-specific settings

Templates help ensure you don't miss important best practices for your project type.
        """,
        "instructions": """
Instruction Selection Help:
Instructions are specific guidelines for AI agents working on your project.
They cover areas like:
• Code quality and testing practices
• Security and performance considerations
• Framework-specific best practices
• Development workflow guidelines

You can select instructions by:
• Individual tags (specific topics)
• Categories (groups of related tags)
• Using template recommendations
        """,
        "customization": """
Template Customization Help:
Many templates have parameters you can customize:
• String parameters: Text values like project names
• Number parameters: Numeric values like port numbers
• Boolean parameters: Yes/no options for features
• Array parameters: Lists of values

Required parameters must be provided.
Optional parameters will use defaults if not specified.
        """,
    }

    @classmethod
    def show_help(cls, topic: str = "navigation") -> None:
        """Show help for a specific topic"""
        help_text = cls.HELP_TOPICS.get(topic, cls.HELP_TOPICS["navigation"])
        print(Colors.info("Help"))
        print(Colors.dim(help_text.strip()))

    @classmethod
    def show_step_help(cls, step: WizardStep) -> None:
        """Show contextual help for current step"""
        help_map = {
            WizardStep.PROJECT_DETECTION: "project_detection",
            WizardStep.TEMPLATE_RECOMMENDATION: "templates",
            WizardStep.TEMPLATE_SELECTION: "templates",
            WizardStep.TEMPLATE_CUSTOMIZATION: "customization",
            WizardStep.INSTRUCTION_SELECTION: "instructions",
        }

        topic = help_map.get(step, "navigation")
        cls.show_help(topic)


class InteractiveWizard:
    """
    Interactive CLI wizard for specification generation.

    This class provides a step-by-step guided experience for users to:
    - Detect project type automatically
    - Recommend appropriate templates
    - Customize template parameters
    - Select relevant instructions
    - Preview and generate specifications
    """

    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """
        Initialize the interactive wizard.

        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager or ConfigManager()

        # Initialize core components
        self.context_detector = ContextDetector()
        self.template_manager = TemplateManager()
        self.instruction_database = InstructionDatabase()
        self.spec_generator: Optional[Any] = None  # Will be set by commands.py

        # Wizard state
        self.state = WizardState()

        # Step definitions with progress weights
        self.step_weights = {
            WizardStep.WELCOME: 5,
            WizardStep.PROJECT_DETECTION: 15,
            WizardStep.PROJECT_TYPE_SELECTION: 10,
            WizardStep.TEMPLATE_RECOMMENDATION: 15,
            WizardStep.TEMPLATE_SELECTION: 15,
            WizardStep.TEMPLATE_CUSTOMIZATION: 10,
            WizardStep.INSTRUCTION_SELECTION: 15,
            WizardStep.SPEC_PREVIEW: 10,
            WizardStep.CONFIRMATION: 5,
            WizardStep.COMPLETE: 0,
        }

    def run_wizard(self) -> Dict[str, Any]:
        """
        Run the interactive wizard with step-by-step flow.

        Returns:
            Dictionary containing the final specification configuration
        """
        logger.info("Starting interactive wizard")

        try:
            # Initialize components
            self._initialize_components()

            # Run wizard steps
            while self.state.current_step != WizardStep.COMPLETE:
                self._update_progress()
                self._display_progress()

                if self.state.current_step == WizardStep.WELCOME:
                    self._step_welcome()
                elif self.state.current_step == WizardStep.PROJECT_DETECTION:
                    self._step_project_detection()
                elif self.state.current_step == WizardStep.PROJECT_TYPE_SELECTION:
                    self._step_project_type_selection()
                elif self.state.current_step == WizardStep.TEMPLATE_RECOMMENDATION:
                    self._step_template_recommendation()
                elif self.state.current_step == WizardStep.TEMPLATE_SELECTION:
                    self._step_template_selection()
                elif self.state.current_step == WizardStep.TEMPLATE_CUSTOMIZATION:
                    self._step_template_customization()
                elif self.state.current_step == WizardStep.INSTRUCTION_SELECTION:
                    self._step_instruction_selection()
                elif self.state.current_step == WizardStep.SPEC_PREVIEW:
                    self._step_spec_preview()
                elif self.state.current_step == WizardStep.CONFIRMATION:
                    self._step_confirmation()

            # Generate final configuration
            return self._generate_final_config()

        except KeyboardInterrupt:
            print("\n\nWizard cancelled by user.")
            return {}
        except Exception as e:
            logger.error(f"Wizard error: {e}")
            print(f"\nAn error occurred: {e}")
            return {}

    def _initialize_components(self) -> None:
        """Initialize core components"""
        try:
            # Load templates and instructions
            self.template_manager.load_templates()
            self.instruction_database.load_instructions()

            logger.debug("Components initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise

    def _update_progress(self) -> None:
        """Update progress percentage based on current step"""
        completed_weight = 0.0
        total_weight = sum(self.step_weights.values())

        for step in self.state.step_history:
            completed_weight += self.step_weights.get(step, 0)

        # Add partial progress for current step
        current_weight = self.step_weights.get(self.state.current_step, 0)
        completed_weight += current_weight * 0.5  # Assume 50% progress in current step

        progress_float = (completed_weight / total_weight) * 100
        self.state.progress_percentage = min(int(progress_float), 100)

    def _display_progress(self) -> None:
        """Display progress bar and current step"""
        progress = self.state.progress_percentage
        bar_length = 40
        filled_length = int(bar_length * progress // 100)

        # Create colored progress bar
        filled_bar = Colors.colorize("█" * filled_length, Colors.GREEN)
        empty_bar = Colors.colorize("░" * (bar_length - filled_length), Colors.DIM)
        bar = filled_bar + empty_bar

        step_name = self.state.current_step.value.replace("_", " ").title()

        print(f"\n{Colors.highlight('AgentSpec Wizard')} - {step_name}")
        print(f"[{bar}] {Colors.colorize(f'{progress}%', Colors.BOLD)}")
        print(
            Colors.dim("Type 'help' for assistance, 'back' to go back, 'quit' to exit")
        )
        print("-" * 70)

    def _get_input(
        self,
        prompt: str,
        validator: Optional[Any] = None,
        help_topic: Optional[str] = None,
    ) -> Optional[str]:
        """
        Get user input with validation and help support.

        Args:
            prompt: Input prompt to display
            validator: Optional validation function
            help_topic: Optional help topic to show

        Returns:
            Validated input or None if user wants to quit
        """
        while True:
            try:
                user_input = input(f"{prompt} ").strip()

                # Handle special commands
                if user_input.lower() in ["quit", "q", "exit"]:
                    confirm = (
                        input(Colors.warning("Are you sure you want to quit? [y/N]: "))
                        .strip()
                        .lower()
                    )
                    if confirm in ["y", "yes"]:
                        return None
                    continue

                if user_input.lower() in ["help", "h", "?"]:
                    if help_topic:
                        HelpSystem.show_help(help_topic)
                    else:
                        HelpSystem.show_step_help(self.state.current_step)
                    continue

                if user_input.lower() in ["back", "b"]:
                    return "back"

                # Validate input if validator provided
                if validator:
                    is_valid, result = validator(user_input)
                    if is_valid:
                        return str(result) if result is not None else None
                    else:
                        print(Colors.error(f"Invalid input: {result}"))
                        continue

                return user_input

            except KeyboardInterrupt:
                print(Colors.warning("\nUse 'quit' to exit the wizard."))
                continue
            except EOFError:
                return None

    def _show_loading(self, message: str, duration: float = 1.0) -> None:
        """Show loading animation"""
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        end_time = time.time() + duration

        while time.time() < end_time:
            for frame in frames:
                if time.time() >= end_time:
                    break
                print(
                    f"\r{Colors.colorize(frame, Colors.BLUE)} {message}",
                    end="",
                    flush=True,
                )
                time.sleep(0.1)

        print(f"\r{Colors.success(message)}")

    def _confirm_action(self, message: str, default: bool = True) -> bool:
        """Get confirmation with colored prompt"""
        default_text = "[Y/n]" if default else "[y/N]"
        prompt = f"{message} {Colors.dim(default_text)}:"

        response = self._get_input(prompt)
        if response is None:
            return False
        if response == "back":
            return False

        return InputValidator.validate_yes_no(response, default)

    def _step_welcome(self) -> None:
        """Welcome step - introduce the wizard with enhanced UI"""
        # Clear screen and show welcome
        print("\n" * 2)
        print(Colors.highlight("🤖 Welcome to AgentSpec Interactive Wizard!"))
        print(Colors.dim("=" * 60))
        print("This wizard will help you generate a comprehensive specification")
        print("for your project with intelligent recommendations and guidance.")
        print()

        # Show features with icons
        features = [
            "🔍 Automatic project type detection",
            "🎯 Smart template recommendations",
            "📚 Customizable instruction selection",
            "👀 Preview before generation",
            "⚙️  Template parameter customization",
        ]

        print(Colors.colorize("Features:", Colors.BOLD))
        for feature in features:
            print(f"  {feature}")
        print()

        print(Colors.info("You can type 'help' at any time for assistance"))
        print()

        # Get project path with validation
        default_path = os.getcwd()

        def path_validator(path: str) -> Tuple[bool, str]:
            if not path:
                return True, default_path
            return InputValidator.validate_path(path)

        project_path = self._get_input(
            f"Project path {Colors.dim(f'[{default_path}]')}:",
            validator=path_validator,
            help_topic="navigation",
        )

        if project_path is None:
            return  # User quit

        if project_path == "back":
            return  # Stay in current step (can't go back from welcome)

        self.state.user_preferences.project_path = project_path
        print(Colors.success(f"Using project path: {project_path}"))

        # Ask about auto-detection
        auto_detect = self._confirm_action(
            "Enable automatic project detection?", default=True
        )

        self.state.user_preferences.auto_detect_enabled = auto_detect

        if auto_detect:
            print(
                Colors.info(
                    "Auto-detection enabled - the wizard will analyze your project"
                )
            )
        else:
            print(
                Colors.info(
                    "Auto-detection disabled - you'll select project type manually"
                )
            )

        self._advance_step(WizardStep.PROJECT_DETECTION)

    def _step_project_detection(self) -> None:
        """Project detection step - analyze project automatically with enhanced UI"""
        if not self.state.user_preferences.auto_detect_enabled:
            self._advance_step(WizardStep.PROJECT_TYPE_SELECTION)
            return

        # Show loading animation
        self._show_loading("Analyzing your project", 2.0)

        try:
            # Detect project context
            self.state.project_context = self.detect_project_type()

            if self.state.project_context:
                print(Colors.success("Project analysis complete!"))
                print()

                # Show detection results with colors
                project_type = self.state.project_context.project_type.value
                confidence = self.state.project_context.confidence_score

                # Confidence indicator
                if confidence >= 0.8:
                    confidence_color = Colors.GREEN
                    confidence_icon = "🟢"
                elif confidence >= 0.6:
                    confidence_color = Colors.YELLOW
                    confidence_icon = "🟡"
                else:
                    confidence_color = Colors.RED
                    confidence_icon = "🟠"

                print(f"Detected project type: {Colors.highlight(project_type)}")
                print(
                    f"Confidence: {Colors.colorize(f'{confidence:.2f}', confidence_color)} {confidence_icon}"
                )

                # Show detected technologies
                if self.state.project_context.technology_stack.languages:
                    languages = [
                        lang.value
                        for lang in self.state.project_context.technology_stack.languages
                    ]
                    print(
                        f"Languages: {Colors.colorize(', '.join(languages), Colors.CYAN)}"
                    )

                if self.state.project_context.technology_stack.frameworks:
                    frameworks = [
                        fw.name
                        for fw in self.state.project_context.technology_stack.frameworks
                    ]
                    print(
                        f"Frameworks: {Colors.colorize(', '.join(frameworks), Colors.MAGENTA)}"
                    )

                # Show alternative classifications if available
                if "type_scores" in self.state.project_context.metadata:
                    type_scores = self.state.project_context.metadata["type_scores"]
                    alternatives = [
                        (pt, score)
                        for pt, score in type_scores.items()
                        if score > 0.3 and pt != project_type
                    ]
                    alternatives.sort(key=lambda x: x[1], reverse=True)

                    if alternatives:
                        print(f"\n{Colors.dim('Alternative classifications:')}")
                        for i, (alt_type, score) in enumerate(alternatives[:3], 1):
                            print(
                                f"  {i}. {alt_type} {Colors.dim(f'(confidence: {score:.2f})')}"
                            )

                print()

                # Options with validation
                options = [
                    f"Use detected type: {Colors.highlight(project_type)}",
                    "Choose different type manually",
                    "See detailed analysis",
                ]

                print("Options:")
                for i, option in enumerate(options, 1):
                    print(f"{i}. {option}")

                def choice_validator(choice: str) -> Tuple[bool, str]:
                    is_valid, num = InputValidator.validate_number_range(choice, 1, 3)
                    if is_valid:
                        return True, str(num)
                    return False, "Please enter 1, 2, or 3"

                choice = self._get_input(
                    "Select option (1-3) [1]:",
                    validator=choice_validator,
                    help_topic="project_detection",
                )

                if choice is None:
                    return  # User quit

                if choice == "back":
                    self._go_back()
                    return

                if not choice:  # Default to 1
                    choice = "1"

                if choice == "3":
                    self._show_detailed_analysis()
                    # Ask again after showing details
                    if self._confirm_action("Use detected project type?", default=True):
                        choice = "1"
                    else:
                        choice = "2"

                if choice == "2":
                    print(Colors.info("Proceeding to manual project type selection..."))
                    self._advance_step(WizardStep.PROJECT_TYPE_SELECTION)
                    return
                else:
                    # Use detected type (default)
                    self.state.user_preferences.project_type = (
                        self.state.project_context.project_type
                    )
                    print(
                        Colors.success(f"Using detected project type: {project_type}")
                    )
                    self._advance_step(WizardStep.TEMPLATE_RECOMMENDATION)
                    return
            else:
                print(Colors.error("Could not automatically detect project type."))

        except Exception as e:
            logger.error(f"Project detection failed: {e}")
            print(Colors.error(f"Project detection failed: {e}"))

        # Fall back to manual selection
        print(Colors.info("Proceeding to manual project type selection..."))
        self._advance_step(WizardStep.PROJECT_TYPE_SELECTION)

    def _show_detailed_analysis(self) -> None:
        """Show detailed project analysis information"""
        if not self.state.project_context:
            return

        context = self.state.project_context
        print("\n📊 Detailed Project Analysis")
        print("=" * 40)

        # File structure summary
        print(f"Total files: {context.file_structure.total_files}")
        print(f"Directories: {len(context.file_structure.directories)}")

        # File types
        if context.file_structure.file_types:
            print("\nFile types:")
            sorted_types = sorted(
                context.file_structure.file_types.items(),
                key=lambda x: x[1],
                reverse=True,
            )
            for ext, count in sorted_types[:10]:  # Show top 10
                print(f"  {ext}: {count} files")

        # Dependencies
        if context.dependencies:
            print("\nKey dependencies:")
            for dep in context.dependencies[:10]:  # Show first 10
                version_info = f" ({dep.version})" if dep.version else ""
                print(f"  {dep.name}{version_info}")

        # Classification scores
        if "type_scores" in context.metadata:
            print("\nProject type scores:")
            type_scores = context.metadata["type_scores"]
            for project_type, score in sorted(
                type_scores.items(), key=lambda x: x[1], reverse=True
            ):
                if score > 0.1:  # Only show meaningful scores
                    print(f"  {project_type}: {score:.2f}")

        # Git information
        if context.git_info and context.git_info.is_git_repo:
            print("\nGit repository:")
            print(f"  Branch: {context.git_info.branch}")
            print(f"  Commits: {context.git_info.commit_count}")
            if context.git_info.remote_url:
                print(f"  Remote: {context.git_info.remote_url}")

        print()

    def _step_project_type_selection(self) -> None:
        """Manual project type selection step"""
        print("\n📋 Select your project type:")
        print()

        project_types = [
            (
                ProjectType.WEB_FRONTEND,
                "Web Frontend (React, Vue, Angular, etc.)",
            ),
            (ProjectType.WEB_BACKEND, "Web Backend (API, Server)"),
            (ProjectType.FULLSTACK_WEB, "Full-stack Web Application"),
            (ProjectType.MOBILE_APP, "Mobile Application"),
            (ProjectType.DESKTOP_APP, "Desktop Application"),
            (ProjectType.CLI_TOOL, "Command Line Tool"),
            (ProjectType.LIBRARY, "Library/Package"),
            (ProjectType.MICROSERVICE, "Microservice"),
            (ProjectType.DATA_SCIENCE, "Data Science Project"),
            (ProjectType.MACHINE_LEARNING, "Machine Learning Project"),
            (ProjectType.UNKNOWN, "Other/Generic"),
        ]

        for i, (project_type, description) in enumerate(project_types, 1):
            print(f"{i:2d}. {description}")

        while True:
            try:
                choice = input(
                    f"\nSelect project type (1-{len(project_types)}): "
                ).strip()
                if choice.lower() in ["back", "b"]:
                    self._go_back()
                    return

                index = int(choice) - 1
                if 0 <= index < len(project_types):
                    selected_type = project_types[index][0]
                    self.state.user_preferences.project_type = selected_type
                    print(f"Selected: {project_types[index][1]}")
                    break
                else:
                    print("❌ Invalid selection. Please try again.")
            except ValueError:
                print("❌ Please enter a valid number.")

        self._advance_step(WizardStep.TEMPLATE_RECOMMENDATION)

    def _step_template_recommendation(self) -> None:
        """Template recommendation step with scoring and reasoning"""
        print("\n🎯 Finding recommended templates...")

        # Get template recommendations
        self.state.template_recommendations = self.recommend_templates()

        if self.state.template_recommendations:
            print(
                f"\n✅ Found {len(self.state.template_recommendations)} recommended templates:"
            )
            print()

            # Show top recommendations with detailed scoring
            for i, recommendation in enumerate(
                self.state.template_recommendations[:5], 1
            ):
                template = recommendation.template
                confidence = recommendation.confidence_score

                # Confidence indicator
                if confidence >= 0.8:
                    confidence_icon = "🟢"
                elif confidence >= 0.6:
                    confidence_icon = "🟡"
                else:
                    confidence_icon = "🟠"

                print(
                    f"{i}. {confidence_icon} {template.name} (confidence: {confidence:.2f})"
                )
                print(f"   {template.description}")

                if template.technology_stack:
                    print(f"   Technologies: {', '.join(template.technology_stack)}")

                # Show recommendation reasons
                if recommendation.reasons:
                    print("   Why recommended:")
                    for reason in recommendation.reasons[:3]:
                        print(f"     • {reason}")
                    if len(recommendation.reasons) > 3:
                        print(
                            f"     • ... and {len(recommendation.reasons) - 3} more reasons"
                        )

                # Show matching conditions
                if recommendation.matching_conditions:
                    print(
                        f"   Matching conditions: {', '.join(recommendation.matching_conditions[:2])}"
                    )

                print()

            # Show options
            print("Options:")
            print("1. Use recommended templates")
            print("2. See all available templates")
            print("3. Show detailed recommendation analysis")
            print("4. Skip template selection")

            choice = input("Select option (1-4) [1]: ").strip()

            if choice == "2":
                self._show_all_templates()
            elif choice == "3":
                self._show_recommendation_analysis()
                # Ask again after showing analysis
                choice = input("Use recommended templates? [Y/n]: ").strip().lower()
                if choice != "n":
                    self.state.available_templates = [
                        rec.template for rec in self.state.template_recommendations
                    ]
                else:
                    self._show_all_templates()
            elif choice == "4":
                self.state.available_templates = []
            else:
                # Default: use recommendations
                self.state.available_templates = [
                    rec.template for rec in self.state.template_recommendations
                ]
        else:
            print("❌ No specific recommendations found based on project analysis.")
            print("Showing all available templates...")
            self._show_all_templates()

        self._advance_step(WizardStep.TEMPLATE_SELECTION)

    def _show_recommendation_analysis(self) -> None:
        """Show detailed analysis of template recommendations"""
        print("\n📊 Template Recommendation Analysis")
        print("=" * 50)

        if not self.state.template_recommendations:
            print("No recommendations available.")
            return

        for i, recommendation in enumerate(self.state.template_recommendations, 1):
            template = recommendation.template
            print(f"\n{i}. {template.name}")
            print(f"   Overall Score: {recommendation.confidence_score:.3f}")

            # Break down scoring factors
            print("   Scoring factors:")
            for reason in recommendation.reasons:
                print(f"     • {reason}")

            if recommendation.matching_conditions:
                print("   Matching conditions:")
                for condition in recommendation.matching_conditions:
                    print(f"     • {condition}")

            # Show template details
            print("   Template details:")
            print(f"     • Project type: {template.project_type}")
            print(f"     • Version: {template.version}")
            if template.metadata:
                print(f"     • Complexity: {template.metadata.complexity}")
            print(f"     • Default tags: {len(template.default_tags)}")
            print(
                f"     • Required instructions: {len(template.required_instructions)}"
            )
            print(
                f"     • Optional instructions: {len(template.optional_instructions)}"
            )

        input("\nPress Enter to continue...")

    def _show_all_templates(self) -> None:
        """Show all available templates"""
        all_templates = list(self.template_manager.load_templates().values())

        # Filter by project type if selected
        if self.state.user_preferences.project_type:
            project_type_str = self.state.user_preferences.project_type.value
            filtered_templates = [
                t
                for t in all_templates
                if t.project_type.lower() == project_type_str.lower()
                or t.project_type == "generic"
            ]
            self.state.available_templates = filtered_templates or all_templates
        else:
            self.state.available_templates = all_templates

    def _step_template_selection(self) -> None:
        """Template selection step with preview functionality"""
        if not self.state.available_templates:
            print("❌ No templates available.")
            self._advance_step(WizardStep.INSTRUCTION_SELECTION)
            return

        print("\n📝 Select a template:")
        print()

        # Show available templates with information
        for i, template in enumerate(self.state.available_templates, 1):
            print(f"{i:2d}. {template.name}")
            print(f"    {template.description}")
            if template.technology_stack:
                print(f"    Technologies: {', '.join(template.technology_stack)}")
            if template.metadata:
                print(f"    Complexity: {template.metadata.complexity}")
                if template.metadata.tags:
                    print(
                        f"    Tags: {', '.join(template.metadata.tags[:3])}{'...' if len(template.metadata.tags) > 3 else ''}"
                    )
            print(f"    Instructions: {len(template.default_tags)} default tags")
            print()

        print(f"{len(self.state.available_templates) + 1:2d}. Skip template selection")
        print(f"{len(self.state.available_templates) + 2:2d}. Preview template details")

        while True:
            try:
                choice = input(
                    f"\nSelect option (1-{len(self.state.available_templates) + 2}): "
                ).strip()
                if choice.lower() in ["back", "b"]:
                    self._go_back()
                    return

                index = int(choice) - 1

                if index == len(self.state.available_templates):
                    # Skip template selection
                    self.state.user_preferences.selected_template = None
                    self._advance_step(WizardStep.INSTRUCTION_SELECTION)
                    return
                elif index == len(self.state.available_templates) + 1:
                    # Preview template details
                    self._preview_template_details()
                    continue
                elif 0 <= index < len(self.state.available_templates):
                    selected_template = self.state.available_templates[index]

                    # Show template preview before selection
                    if self._confirm_template_selection(selected_template):
                        self.state.user_preferences.selected_template = (
                            selected_template
                        )
                        print(f"Selected: {selected_template.name}")

                        # Check if template has parameters
                        if selected_template.parameters:
                            self._advance_step(WizardStep.TEMPLATE_CUSTOMIZATION)
                        else:
                            self._advance_step(WizardStep.INSTRUCTION_SELECTION)
                        return
                else:
                    print("❌ Invalid selection. Please try again.")
            except ValueError:
                print("❌ Please enter a valid number.")

    def _preview_template_details(self) -> None:
        """Show detailed preview of available templates"""
        print("\n📋 Template Details Preview")
        print("=" * 50)

        for i, template in enumerate(self.state.available_templates, 1):
            print(f"\n{i}. {template.name} (v{template.version})")
            print(f"   Description: {template.description}")
            print(f"   Project Type: {template.project_type}")

            if template.technology_stack:
                print(f"   Technologies: {', '.join(template.technology_stack)}")

            print(
                f"   Default Tags ({len(template.default_tags)}): {', '.join(template.default_tags[:5])}{'...' if len(template.default_tags) > 5 else ''}"
            )

            if template.required_instructions:
                print(
                    f"   Required Instructions: {len(template.required_instructions)}"
                )

            if template.optional_instructions:
                print(
                    f"   Optional Instructions: {len(template.optional_instructions)}"
                )

            if template.parameters:
                print(f"   Customizable Parameters: {len(template.parameters)}")
                for param_name, param in list(template.parameters.items())[:3]:
                    required_text = " (required)" if param.required else ""
                    print(f"     • {param_name}: {param.type}{required_text}")
                if len(template.parameters) > 3:
                    print(f"     ... and {len(template.parameters) - 3} more")

            if template.metadata:
                print(f"   Complexity: {template.metadata.complexity}")
                if template.metadata.author:
                    print(f"   Author: {template.metadata.author}")

        input("\nPress Enter to continue...")

    def _confirm_template_selection(self, template: Template) -> bool:
        """Show template preview and confirm selection"""
        print(f"\n🔍 Template Preview: {template.name}")
        print("-" * 40)
        print(f"Description: {template.description}")
        print(f"Version: {template.version}")
        print(f"Project Type: {template.project_type}")

        if template.technology_stack:
            print(f"Technologies: {', '.join(template.technology_stack)}")

        print("\nThis template will include:")
        print(f"• {len(template.default_tags)} default instruction tags")

        if template.required_instructions:
            print(f"• {len(template.required_instructions)} required instructions")

        if template.optional_instructions:
            print(f"• {len(template.optional_instructions)} optional instructions")

        if template.parameters:
            print(f"• {len(template.parameters)} customizable parameters")

        # Show sample of default tags
        if template.default_tags:
            print(
                f"\nDefault tags: {', '.join(template.default_tags[:8])}{'...' if len(template.default_tags) > 8 else ''}"
            )

        # Show parameters if any
        if template.parameters:
            print("\nCustomizable parameters:")
            for param_name, param in list(template.parameters.items())[:5]:
                required_text = " (required)" if param.required else ""
                default_text = (
                    f" [default: {param.default}]" if param.default is not None else ""
                )
                print(
                    f"  • {param_name}: {param.description}{required_text}{default_text}"
                )
            if len(template.parameters) > 5:
                print(f"  ... and {len(template.parameters) - 5} more parameters")

        confirm = input("\nSelect this template? [Y/n]: ").strip().lower()
        return confirm != "n"

    def _step_template_customization(self) -> None:
        """Template customization step"""
        template = self.state.user_preferences.selected_template
        if not template or not template.parameters:
            self._advance_step(WizardStep.INSTRUCTION_SELECTION)
            return

        print(f"\n⚙️  Customize template: {template.name}")
        print("Configure the following parameters:")
        print()

        for param_name, param in template.parameters.items():
            print(f"Parameter: {param_name}")
            print(f"Type: {param.type}")
            print(f"Description: {param.description}")

            if param.default is not None:
                print(f"Default: {param.default}")

            if param.options:
                print(f"Options: {', '.join(map(str, param.options))}")

            # Get user input
            while True:
                if param.required:
                    prompt = f"Enter value for {param_name}: "
                else:
                    default_text = (
                        f" [{param.default}]"
                        if param.default is not None
                        else " [optional]"
                    )
                    prompt = f"Enter value for {param_name}{default_text}: "

                value = input(prompt).strip()

                if not value and not param.required:
                    value = param.default
                    break
                elif not value and param.required:
                    print("❌ This parameter is required.")
                    continue

                # Validate value
                if self._validate_parameter_value(param, value):
                    self.state.user_preferences.template_parameters[param_name] = value
                    break
                else:
                    print("❌ Invalid value. Please try again.")

            print()

        self._advance_step(WizardStep.INSTRUCTION_SELECTION)

    def _validate_parameter_value(self, parameter: Any, value: str) -> bool:
        """Validate parameter value based on type and constraints"""
        try:
            if parameter.type == "number":
                float(value)
            elif parameter.type == "boolean":
                if value.lower() not in [
                    "true",
                    "false",
                    "yes",
                    "no",
                    "1",
                    "0",
                ]:
                    return False
            elif parameter.type == "array":
                # Simple validation - check if it looks like a list
                if not (value.startswith("[") and value.endswith("]")):
                    return False

            # Check options constraint
            if parameter.options and value not in parameter.options:
                return False

            return True
        except ValueError:
            return False

    def _step_instruction_selection(self) -> None:
        """Instruction selection step"""
        print("\n📚 Select instruction categories:")
        print()

        # Get available tags from template or all instructions
        if self.state.user_preferences.selected_template:
            template = self.state.user_preferences.selected_template
            suggested_tags = set(template.default_tags)
            if template.required_instructions:
                # Get tags from required instructions
                for inst_id in template.required_instructions:
                    instruction = self.instruction_database.get_instruction(inst_id)
                    if instruction:
                        suggested_tags.update(instruction.tags)
        else:
            suggested_tags = set()

        # Get all available tags
        all_tags = self.instruction_database.get_all_tags()

        # Organize tags by category
        categories = self._organize_tags_by_category(all_tags)

        print("Available categories (✓ = recommended):")
        print()

        for category, tags in categories.items():
            recommended_in_category = suggested_tags.intersection(tags)
            marker = "✓" if recommended_in_category else " "
            print(f"[{marker}] {category.upper()}")

            for tag in sorted(tags):
                tag_marker = "✓" if tag in suggested_tags else " "
                instruction_count = len(self.instruction_database.get_by_tags([tag]))
                print(f"    [{tag_marker}] {tag} ({instruction_count} instructions)")
            print()

        # Tag selection
        print("Selection options:")
        print("1. Use recommended tags")
        print("2. Select categories")
        print("3. Select individual tags")
        print("4. Select all tags")

        choice = input("\nChoose selection method (1-4): ").strip()

        if choice == "1":
            self.state.user_preferences.selected_tags = suggested_tags
            print(f"Selected {len(suggested_tags)} recommended tags")
        elif choice == "2":
            self._select_tag_categories(categories)
        elif choice == "3":
            self._select_individual_tags(all_tags)
        elif choice == "4":
            self.state.user_preferences.selected_tags = all_tags
            print(f"Selected all {len(all_tags)} tags")
        else:
            print("❌ Invalid choice, using recommended tags")
            self.state.user_preferences.selected_tags = suggested_tags

        self._advance_step(WizardStep.SPEC_PREVIEW)

    def _organize_tags_by_category(self, tags: Set[str]) -> Dict[str, Set[str]]:
        """Organize tags into categories"""
        categories = {
            "general": {
                "general",
                "quality",
                "standards",
                "persistence",
                "tracking",
            },
            "testing": {
                "testing",
                "tdd",
                "validation",
                "automation",
                "browser",
            },
            "frontend": {
                "frontend",
                "ui",
                "react",
                "vue",
                "angular",
                "mobile",
                "responsive",
            },
            "backend": {
                "backend",
                "api",
                "database",
                "security",
                "performance",
            },
            "devops": {
                "docker",
                "ci-cd",
                "deployment",
                "monitoring",
                "backup",
            },
            "languages": {"javascript", "typescript", "python", "type-safety"},
            "architecture": {
                "architecture",
                "microservices",
                "modularity",
                "maintainability",
            },
        }

        # Add tags to appropriate categories
        result = {}
        for category, category_tags in categories.items():
            matching_tags = tags.intersection(category_tags)
            if matching_tags:
                result[category] = matching_tags

        # Add uncategorized tags
        categorized_tags = set()
        for category_tags in result.values():
            categorized_tags.update(category_tags)

        uncategorized = tags - categorized_tags
        if uncategorized:
            result["other"] = uncategorized

        return result

    def _select_tag_categories(self, categories: Dict[str, Set[str]]) -> None:
        """Allow user to select entire categories"""
        selected_tags = set()

        print("\nSelect categories (enter numbers separated by commas):")
        category_list = list(categories.items())

        for i, (category, tags) in enumerate(category_list, 1):
            print(f"{i}. {category.upper()} ({len(tags)} tags)")

        choice = input("Categories to include: ").strip()

        try:
            indices = [int(x.strip()) - 1 for x in choice.split(",") if x.strip()]
            for index in indices:
                if 0 <= index < len(category_list):
                    category_tags = category_list[index][1]
                    selected_tags.update(category_tags)
        except ValueError:
            print("❌ Invalid input, no categories selected")

        self.state.user_preferences.selected_tags = selected_tags
        print(f"Selected {len(selected_tags)} tags from categories")

    def _select_individual_tags(self, all_tags: Set[str]) -> None:
        """Allow user to select individual tags"""
        print("\nEnter tags separated by commas:")
        print("Available tags:", ", ".join(sorted(all_tags)))

        choice = input("Tags to include: ").strip()

        selected_tags = set()
        if choice:
            input_tags = [tag.strip() for tag in choice.split(",")]
            for tag in input_tags:
                if tag in all_tags:
                    selected_tags.add(tag)
                else:
                    print(f"❌ Unknown tag: {tag}")

        self.state.user_preferences.selected_tags = selected_tags
        print(f"Selected {len(selected_tags)} individual tags")

    def _step_spec_preview(self) -> None:
        """Spec preview step"""
        print("\n👀 Specification Preview")
        print("=" * 50)

        # Generate preview
        config = self._generate_final_config()

        print(f"Project Path: {config.get('project_path', 'N/A')}")
        print(f"Project Type: {config.get('project_type', 'N/A')}")
        print(f"Template: {config.get('template_name', 'None')}")
        print(f"Selected Tags: {len(config.get('selected_tags', []))} tags")
        print(f"Instructions: {len(config.get('instructions', []))} instructions")

        if config.get("selected_tags"):
            print(f"Tags: {', '.join(sorted(config['selected_tags']))}")

        print()

        # Ask for output file
        default_output = self.state.user_preferences.output_file
        output_file = input(f"Output file [{default_output}]: ").strip()
        if output_file:
            self.state.user_preferences.output_file = output_file

        self._advance_step(WizardStep.CONFIRMATION)

    def _step_confirmation(self) -> None:
        """Final confirmation step with summary"""
        print(f"\n{Colors.success('Ready to generate specification!')}")
        print()

        # Summary with colors and icons
        config = self._generate_final_config()

        print(Colors.highlight("📋 Generation Summary"))
        print(Colors.dim("-" * 40))

        print(
            f"📁 Project: {Colors.colorize(config.get('project_path', 'N/A'), Colors.CYAN)}"
        )
        print(
            f"🏷️  Type: {Colors.colorize(config.get('project_type', 'N/A'), Colors.MAGENTA)}"
        )

        if config.get("template_name"):
            print(
                f"📝 Template: {Colors.colorize(config['template_name'], Colors.BLUE)}"
            )

        print(
            f"🏷️  Tags: {Colors.colorize(str(len(config.get('selected_tags', []))), Colors.GREEN)} selected"
        )
        print(
            f"📚 Instructions: {Colors.colorize(str(len(config.get('instructions', []))), Colors.GREEN)} total"
        )
        print(
            f"📄 Output: {Colors.colorize(self.state.user_preferences.output_file, Colors.YELLOW)}"
        )

        if config.get("selected_tags"):
            print(f"\n{Colors.dim('Selected tags:')}")
            tags_display = ", ".join(sorted(config["selected_tags"])[:10])
            if len(config["selected_tags"]) > 10:
                tags_display += f" ... and {len(config['selected_tags']) - 10} more"
            print(Colors.dim(f"  {tags_display}"))

        print()

        # Final confirmation with options
        print("Options:")
        print("1. Generate specification")
        print("2. Go back to preview")
        print("3. Change output filename")

        def choice_validator(choice: str) -> Tuple[bool, str]:
            is_valid, num = InputValidator.validate_number_range(choice, 1, 3)
            if is_valid:
                return True, str(num)
            return False, "Please enter 1, 2, or 3"

        choice = self._get_input("Select option (1-3) [1]:", validator=choice_validator)

        if choice is None:
            return  # User quit

        if choice == "back":
            self._go_back()
            return

        if not choice:  # Default to 1
            choice = "1"

        if choice == "3":
            # Change output filename
            def filename_validator(filename: str) -> Tuple[bool, str]:
                if not filename:
                    return False, "Filename cannot be empty"
                return InputValidator.validate_filename(filename)

            new_filename = self._get_input(
                f"New output filename [{self.state.user_preferences.output_file}]:",
                validator=filename_validator,
            )

            if new_filename and new_filename != "back":
                self.state.user_preferences.output_file = new_filename
                print(Colors.success(f"Output filename updated: {new_filename}"))

            # Stay in confirmation step
            return

        elif choice == "2":
            # Go back to preview
            self.state.current_step = WizardStep.SPEC_PREVIEW
            return

        else:
            # Proceed to generate specification (actual generation happens in command handler)
            print(Colors.success("✅ Generating specification"))
            self._advance_step(WizardStep.COMPLETE)

    def _advance_step(self, next_step: WizardStep) -> None:
        """Advance to the next wizard step"""
        self.state.step_history.append(self.state.current_step)
        self.state.current_step = next_step

    def _go_back(self) -> None:
        """Go back to the previous step"""
        if self.state.step_history:
            self.state.current_step = self.state.step_history.pop()
        else:
            print("❌ Cannot go back further")

    def _generate_final_config(self) -> Dict[str, Any]:
        """Generate final configuration dictionary"""
        prefs = self.state.user_preferences

        # Get instructions for selected tags
        instructions = []
        if prefs.selected_tags:
            instructions = self.instruction_database.get_by_tags(
                list(prefs.selected_tags)
            )

        # Add template instructions if template is selected
        if prefs.selected_template:
            template_instructions = []

            # Add required instructions
            for inst_id in prefs.selected_template.required_instructions:
                instruction = self.instruction_database.get_instruction(inst_id)
                if instruction:
                    template_instructions.append(instruction)

            # Add optional instructions if enabled
            if prefs.include_optional_instructions:
                for inst_id in prefs.selected_template.optional_instructions:
                    instruction = self.instruction_database.get_instruction(inst_id)
                    if instruction:
                        template_instructions.append(instruction)

            # Merge with selected instructions (avoid duplicates)
            existing_ids = {inst.id for inst in instructions}
            for inst in template_instructions:
                if inst.id not in existing_ids:
                    instructions.append(inst)

        return {
            "project_path": prefs.project_path,
            "project_type": (prefs.project_type.value if prefs.project_type else None),
            "template_name": (
                prefs.selected_template.name if prefs.selected_template else None
            ),
            "template_id": (
                prefs.selected_template.id if prefs.selected_template else None
            ),
            "template_parameters": prefs.template_parameters,
            "selected_tags": list(prefs.selected_tags),
            "instructions": [
                {"id": inst.id, "content": inst.content, "tags": inst.tags}
                for inst in instructions
            ],
            "output_file": prefs.output_file,
            "complexity_preference": prefs.complexity_preference,
            "project_context": self.state.project_context,
        }

    def detect_project_type(self) -> Optional[ProjectContext]:
        """
        Detect project type using ContextDetector with automatic project analysis.

        Returns:
            ProjectContext if detection successful, None otherwise
        """
        try:
            project_path = self.state.user_preferences.project_path
            context = self.context_detector.analyze_project(project_path)

            if context:
                # Enhance context with additional classification
                context = self._enhance_project_classification(context)

                # Log detection details
                logger.info(
                    f"Project type detected: {context.project_type.value} "
                    f"(confidence: {context.confidence_score:.2f})"
                )

                if context.technology_stack.languages:
                    languages = [
                        lang.value for lang in context.technology_stack.languages
                    ]
                    logger.info(f"Detected languages: {', '.join(languages)}")

                if context.technology_stack.frameworks:
                    frameworks = [fw.name for fw in context.technology_stack.frameworks]
                    logger.info(f"Detected frameworks: {', '.join(frameworks)}")

            return context

        except Exception as e:
            logger.error(f"Project type detection failed: {e}")
            return None

    def _enhance_project_classification(
        self, context: ProjectContext
    ) -> ProjectContext:
        """
        Enhance project classification with confidence scores and additional analysis.

        Args:
            context: Initial project context from ContextDetector

        Returns:
            ProjectContext with improved classification
        """
        # Create classification confidence scores for different project types
        type_scores = {}

        # Analyze file structure patterns
        file_structure = context.file_structure

        # Web frontend indicators
        frontend_score = 0.0
        if any("index.html" in f for f in file_structure.source_files):
            frontend_score += 0.3
        if any(ext in file_structure.file_types for ext in [".jsx", ".tsx", ".vue"]):
            frontend_score += 0.4
        if any("package.json" in f for f in file_structure.config_files):
            frontend_score += 0.2
        if any(
            fw.name in ["react", "vue", "angular"]
            for fw in context.technology_stack.frameworks
        ):
            frontend_score += 0.5

        type_scores[ProjectType.WEB_FRONTEND] = min(frontend_score, 1.0)

        # Web backend indicators
        backend_score = 0.0
        backend_files = [
            "server.js",
            "app.py",
            "main.py",
            "manage.py",
            "server.py",
        ]
        if any(f in file_structure.source_files for f in backend_files):
            backend_score += 0.4
        if any(
            fw.name in ["django", "flask", "fastapi", "express"]
            for fw in context.technology_stack.frameworks
        ):
            backend_score += 0.5
        if context.technology_stack.databases:
            backend_score += 0.3

        type_scores[ProjectType.WEB_BACKEND] = min(backend_score, 1.0)

        # Full-stack indicators
        fullstack_score = 0.0
        if any(
            fw.name in ["nextjs", "nuxt"] for fw in context.technology_stack.frameworks
        ):
            fullstack_score += 0.6
        if (
            type_scores.get(ProjectType.WEB_FRONTEND, 0) > 0.3
            and type_scores.get(ProjectType.WEB_BACKEND, 0) > 0.3
        ):
            fullstack_score += 0.4

        type_scores[ProjectType.FULLSTACK_WEB] = min(fullstack_score, 1.0)

        # Mobile app indicators
        mobile_score = 0.0
        mobile_dirs = ["android", "ios", "mobile"]
        if any(d in file_structure.directories for d in mobile_dirs):
            mobile_score += 0.5
        mobile_files = [
            "App.js",
            "App.tsx",
            "MainActivity.java",
            "AppDelegate.swift",
        ]
        if any(f in file_structure.source_files for f in mobile_files):
            mobile_score += 0.4
        if any("react-native" in dep.name for dep in context.dependencies):
            mobile_score += 0.4

        type_scores[ProjectType.MOBILE_APP] = min(mobile_score, 1.0)

        # CLI tool indicators
        cli_score = 0.0
        cli_files = ["cli.py", "main.py", "bin/", "__main__.py"]
        if any(
            f in file_structure.source_files or f in file_structure.directories
            for f in cli_files
        ):
            cli_score += 0.4
        cli_deps = ["click", "argparse", "commander", "yargs"]
        if any(
            cli_dep in dep.name for dep in context.dependencies for cli_dep in cli_deps
        ):
            cli_score += 0.3
        if any(
            "#!/usr/bin/env" in f for f in file_structure.source_files[:10]
        ):  # Check first few files
            cli_score += 0.2

        type_scores[ProjectType.CLI_TOOL] = min(cli_score, 1.0)

        # Library indicators
        library_score = 0.0
        lib_files = [
            "setup.py",
            "pyproject.toml",
            "package.json",
            "lib/",
            "src/",
        ]
        if any(
            f in file_structure.config_files or f in file_structure.directories
            for f in lib_files
        ):
            library_score += 0.4
        if "LICENSE" in file_structure.source_files or "README" in str(
            file_structure.source_files
        ):
            library_score += 0.2

        type_scores[ProjectType.LIBRARY] = min(library_score, 1.0)

        # Update project type if we have a better classification
        if type_scores:
            best_type = max(type_scores.items(), key=lambda x: x[1])
            if best_type[1] > context.confidence_score and best_type[1] > 0.5:
                context.project_type = best_type[0]
                context.confidence_score = best_type[1]

                # Add classification metadata
                context.metadata["type_scores"] = {
                    pt.value: score for pt, score in type_scores.items()
                }
                context.metadata["classification_method"] = "detailed_analysis"

        return context

    def recommend_templates(self) -> List[TemplateRecommendation]:
        """
        Get template recommendations based on project context.

        Returns:
            List of template recommendations
        """
        try:
            # Build project context for template recommendation
            project_context: Dict[str, Any] = {}

            if self.state.user_preferences.project_type:
                project_context["project_type"] = (
                    self.state.user_preferences.project_type.value
                )

            if self.state.project_context:
                # Add detected information
                project_context["technology_stack"] = [
                    lang.value
                    for lang in self.state.project_context.technology_stack.languages
                ] + [
                    fw.name
                    for fw in self.state.project_context.technology_stack.frameworks
                ]

                project_context["dependencies"] = [
                    dep.name for dep in self.state.project_context.dependencies
                ]

                project_context["files"] = (
                    self.state.project_context.file_structure.config_files
                    + self.state.project_context.file_structure.source_files
                )

            project_context["complexity_preference"] = (
                self.state.user_preferences.complexity_preference
            )

            return self.template_manager.get_recommended_templates(project_context)

        except Exception as e:
            logger.error(f"Template recommendation failed: {e}")
            return []
