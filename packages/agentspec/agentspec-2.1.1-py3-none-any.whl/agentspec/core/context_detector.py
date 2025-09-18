"""
Context Detection System

This module provides the ContextDetector class for analyzing projects and detecting
technology stacks, frameworks, and project characteristics to suggest relevant
instructions and templates.

This is the main entry point for context detection functionality. The actual
detection logic is organized into specialized modules in the context/ package.
"""

import logging
import os
import subprocess  # nosec B404 # Used safely for git commands
from pathlib import Path
from typing import Any, Dict, List

from .context import (
    Dependency,
    FileStructure,
    Framework,
    GitInfo,
    InstructionSuggestion,
    Language,
    ProjectContext,
    ProjectType,
    TechnologyStack,
)
from .context.framework_detector import FrameworkDetector
from .context.language_detector import LanguageDetector

logger = logging.getLogger(__name__)


class ContextDetector:
    """
    Detects project context and suggests relevant instructions based on
    technology stack, project structure, and other characteristics.

    This class coordinates various detection modules to provide thorough
    project analysis including language detection, framework identification,
    and instruction suggestions.
    """

    def __init__(self) -> None:
        """Initialize the context detector with specialized detectors"""
        self.language_detector = LanguageDetector()
        self.framework_detector = FrameworkDetector()

        # Project type indicators for classification
        self._project_type_indicators = {
            ProjectType.WEB_FRONTEND: {
                "frameworks": ["react", "vue", "angular", "svelte"],
                "files": ["index.html", "public/index.html", "src/index.html"],
                "dependencies": ["webpack", "vite", "parcel", "rollup"],
            },
            ProjectType.WEB_BACKEND: {
                "frameworks": ["django", "flask", "express", "fastapi", "spring"],
                "files": ["server.js", "app.py", "main.py", "manage.py"],
                "dependencies": ["express", "django", "flask", "fastapi"],
            },
            ProjectType.FULLSTACK_WEB: {
                "frameworks": ["nextjs", "nuxt", "gatsby"],
                "files": ["next.config.js", "nuxt.config.js", "gatsby-config.js"],
                "dependencies": ["next", "nuxt", "gatsby"],
            },
            ProjectType.MOBILE_APP: {
                "files": ["android/", "ios/", "App.js", "App.tsx"],
                "dependencies": ["react-native", "flutter", "ionic"],
            },
            ProjectType.CLI_TOOL: {
                "files": ["bin/", "cli.py", "main.py", "index.js"],
                "dependencies": ["click", "argparse", "commander", "yargs"],
            },
            ProjectType.LIBRARY: {
                "files": [
                    "setup.py",
                    "pyproject.toml",
                    "package.json",
                    "lib/",
                ],
                "dependencies": ["setuptools", "poetry"],
            },
        }

    def analyze_project(self, project_path: str) -> ProjectContext:
        """
        Perform comprehensive project analysis.

        Args:
            project_path: Path to the project directory

        Returns:
            ProjectContext with analysis results
        """
        project_dir = Path(project_path).resolve()

        if not project_dir.exists() or not project_dir.is_dir():
            raise ValueError(f"Invalid project path: {project_dir}")

        logger.info(f"Analyzing project at: {project_dir}")

        # Initialize context
        context = ProjectContext(
            project_path=str(project_dir),
            project_type=ProjectType.UNKNOWN,
            technology_stack=TechnologyStack(),
        )

        # Analyze file structure
        context.file_structure = self._analyze_file_structure(project_dir)

        # Detect technology stack
        context.technology_stack = self.detect_technology_stack(str(project_dir))

        # Detect dependencies
        context.dependencies = self.framework_detector._get_package_dependencies(
            project_dir
        )

        # Detect project type
        context.project_type = self._detect_project_type(context)

        # Analyze Git repository
        context.git_info = self._analyze_git_repository(project_dir)

        # Calculate confidence score
        context.confidence_score = self._calculate_context_confidence(context)

        # Add metadata
        context.metadata = self._collect_metadata(project_dir, context)

        logger.info(
            f"Project analysis complete. Type: {context.project_type.value}, "
            f"Confidence: {context.confidence_score:.2f}"
        )

        return context

    def detect_technology_stack(self, project_path: str) -> TechnologyStack:
        """
        Detect technology stack from project files.

        Args:
            project_path: Path to the project directory

        Returns:
            TechnologyStack with detected technologies
        """
        project_dir = Path(project_path)
        stack = TechnologyStack()

        # Detect languages
        stack.languages = self.language_detector.detect_languages(project_dir)

        # Detect frameworks
        stack.frameworks = self.framework_detector.detect_frameworks(project_dir)

        # Detect databases
        stack.databases = self.framework_detector.detect_databases(project_dir)

        # Detect tools
        stack.tools = self.framework_detector.detect_tools(project_dir)

        # Detect platforms
        stack.platforms = self.framework_detector.detect_platforms(project_dir)

        return stack

    def suggest_instructions(
        self, context: ProjectContext
    ) -> List[InstructionSuggestion]:
        """
        Suggest relevant instructions based on project context.

        Args:
            context: Project context information

        Returns:
            List of instruction suggestions with confidence scores
        """
        suggestions = []

        # Base suggestions for all projects
        suggestions.extend(self._get_base_suggestions())

        # Language-specific suggestions
        for language in context.technology_stack.languages:
            suggestions.extend(self._get_language_suggestions(language))

        # Framework-specific suggestions
        for framework in context.technology_stack.frameworks:
            suggestions.extend(self._get_framework_suggestions(framework))

        # Project type suggestions
        suggestions.extend(self._get_project_type_suggestions(context.project_type))

        # Dependency-based suggestions
        suggestions.extend(self._get_dependency_suggestions(context.dependencies))

        # File structure suggestions
        suggestions.extend(self._get_structure_suggestions(context.file_structure))

        # Calculate final confidence scores
        for suggestion in suggestions:
            suggestion.confidence = self.calculate_confidence(suggestion, context)

        # Sort by confidence and remove duplicates
        unique_suggestions: Dict[str, InstructionSuggestion] = {}
        for suggestion in suggestions:
            key = suggestion.instruction_id
            if (
                key not in unique_suggestions
                or suggestion.confidence > unique_suggestions[key].confidence
            ):
                unique_suggestions[key] = suggestion

        final_suggestions = list(unique_suggestions.values())
        final_suggestions.sort(key=lambda s: s.confidence, reverse=True)

        return final_suggestions

    def calculate_confidence(
        self, suggestion: InstructionSuggestion, context: ProjectContext
    ) -> float:
        """
        Calculate confidence score for an instruction suggestion.

        Args:
            suggestion: Instruction suggestion
            context: Project context

        Returns:
            Confidence score between 0.0 and 1.0
        """
        base_confidence = suggestion.confidence

        # Boost confidence based on multiple evidence sources
        evidence_boost = min(len(suggestion.reasons) * 0.1, 0.3)

        # Boost confidence for popular frameworks/languages
        popularity_boost = 0.0
        for framework in context.technology_stack.frameworks:
            if framework.name in [
                "react",
                "vue",
                "angular",
                "django",
                "flask",
            ]:
                popularity_boost += 0.1

        # Boost confidence based on project maturity (file count, git history)
        maturity_boost = 0.0
        if context.file_structure.total_files > 50:
            maturity_boost += 0.1
        if context.git_info and context.git_info.commit_count > 10:
            maturity_boost += 0.1

        # Calculate final confidence
        final_confidence = min(
            base_confidence + evidence_boost + popularity_boost + maturity_boost,
            1.0,
        )

        return final_confidence

    def _analyze_file_structure(self, project_path: Path) -> FileStructure:
        """Analyze project file structure"""
        structure = FileStructure()

        try:
            # Walk through all files
            for root, dirs, files in os.walk(project_path):
                # Skip hidden directories and common ignore patterns
                dirs[:] = [
                    d
                    for d in dirs
                    if not d.startswith(".")
                    and d not in ["node_modules", "__pycache__", "venv", "env"]
                ]

                rel_root = os.path.relpath(root, project_path)
                if rel_root != ".":
                    structure.directories.append(rel_root)

                for file in files:
                    if file.startswith("."):
                        continue

                    structure.total_files += 1
                    file_path = os.path.join(root, file)
                    rel_file_path = os.path.relpath(file_path, project_path)

                    # Categorize files
                    ext = Path(file).suffix.lower()
                    structure.file_types[ext] = structure.file_types.get(ext, 0) + 1

                    # Identify special file types
                    if self._is_config_file(file):
                        structure.config_files.append(rel_file_path)
                    elif self._is_source_file(file):
                        structure.source_files.append(rel_file_path)
                    elif self._is_test_file(file):
                        structure.test_files.append(rel_file_path)
                    elif self._is_documentation_file(file):
                        structure.documentation_files.append(rel_file_path)

        except Exception as e:
            logger.error(f"Error analyzing file structure: {e}")

        return structure

    def _detect_project_type(self, context: ProjectContext) -> ProjectType:
        """Detect project type based on context analysis"""
        type_scores = {}

        for project_type, indicators in self._project_type_indicators.items():
            score = 0.0

            # Check frameworks
            if "frameworks" in indicators:
                framework_names = [
                    fw.name for fw in context.technology_stack.frameworks
                ]
                for framework in indicators["frameworks"]:
                    if framework in framework_names:
                        score += 0.4

            # Check files
            if "files" in indicators:
                for file_pattern in indicators["files"]:
                    if (Path(context.project_path) / file_pattern).exists():
                        score += 0.3

            # Check dependencies
            if "dependencies" in indicators:
                dep_names = [dep.name for dep in context.dependencies]
                for dependency in indicators["dependencies"]:
                    if any(dependency in dep for dep in dep_names):
                        score += 0.3

            type_scores[project_type] = score

        # Store scores in metadata for debugging
        context.metadata["type_scores"] = {
            pt.value: score for pt, score in type_scores.items()
        }

        # Return the type with the highest score, or UNKNOWN if no good match
        if type_scores:
            best_type = max(type_scores.items(), key=lambda x: x[1])
            if best_type[1] > 0.3:  # Minimum confidence threshold
                return best_type[0]

        return ProjectType.UNKNOWN

    def _analyze_git_repository(self, project_path: Path) -> GitInfo:
        """Analyze Git repository information"""
        git_info = GitInfo()

        try:
            # Check if it's a git repository
            git_dir = project_path / ".git"
            if git_dir.exists():
                git_info.is_git_repo = True

                # Get current branch
                try:
                    result = subprocess.run(
                        ["git", "branch", "--show-current"],
                        cwd=project_path,
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )
                    if result.returncode == 0:
                        git_info.branch = result.stdout.strip()
                except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                    pass

                # Get remote URL
                try:
                    result = subprocess.run(
                        ["git", "remote", "get-url", "origin"],
                        cwd=project_path,
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )
                    if result.returncode == 0:
                        git_info.remote_url = result.stdout.strip()
                except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                    pass

                # Get commit count
                try:
                    result = subprocess.run(
                        ["git", "rev-list", "--count", "HEAD"],
                        cwd=project_path,
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )
                    if result.returncode == 0:
                        git_info.commit_count = int(result.stdout.strip())
                except (
                    subprocess.TimeoutExpired,
                    subprocess.SubprocessError,
                    ValueError,
                ):
                    pass

        except Exception as e:
            logger.debug(f"Error analyzing git repository: {e}")

        return git_info

    def _calculate_context_confidence(self, context: ProjectContext) -> float:
        """Calculate overall confidence score for the context analysis"""
        confidence = 0.0

        # Project type confidence
        if context.project_type != ProjectType.UNKNOWN:
            confidence += 0.3

        # Technology stack confidence
        if context.technology_stack.languages:
            confidence += 0.2
        if context.technology_stack.frameworks:
            confidence += 0.2

        # File structure confidence
        if context.file_structure.total_files > 10:
            confidence += 0.1
        if context.file_structure.config_files:
            confidence += 0.1

        # Dependencies confidence
        if context.dependencies:
            confidence += 0.1

        return min(confidence, 1.0)

    def _collect_metadata(
        self, project_path: Path, context: ProjectContext
    ) -> Dict[str, Any]:
        """Collect additional metadata about the project"""
        metadata = context.metadata.copy()

        # Add project name
        metadata["project_name"] = project_path.name

        # Add language statistics
        if hasattr(self.language_detector, "get_language_statistics"):
            metadata["language_stats"] = self.language_detector.get_language_statistics(
                project_path
            )

        return metadata

    def _is_config_file(self, filename: str) -> bool:
        """Check if file is a configuration file"""
        config_patterns = [
            "config",
            "conf",
            ".json",
            ".yaml",
            ".yml",
            ".toml",
            ".ini",
            ".env",
            "package.json",
            "requirements.txt",
            "Dockerfile",
            "Makefile",
        ]
        return any(pattern in filename.lower() for pattern in config_patterns)

    def _is_source_file(self, filename: str) -> bool:
        """Check if file is a source code file"""
        source_extensions = [
            ".py",
            ".js",
            ".ts",
            ".jsx",
            ".tsx",
            ".java",
            ".cs",
            ".cpp",
            ".c",
            ".go",
            ".rs",
            ".php",
            ".rb",
            ".swift",
            ".kt",
            ".dart",
        ]
        return any(filename.lower().endswith(ext) for ext in source_extensions)

    def _is_test_file(self, filename: str) -> bool:
        """Check if file is a test file"""
        test_patterns = ["test", "spec", "__test__", ".test.", ".spec."]
        return any(pattern in filename.lower() for pattern in test_patterns)

    def _is_documentation_file(self, filename: str) -> bool:
        """Check if file is a documentation file"""
        doc_patterns = ["readme", "doc", "docs", ".md", ".rst", ".txt"]
        return any(pattern in filename.lower() for pattern in doc_patterns)

    # Suggestion methods - simplified versions
    def _get_base_suggestions(self) -> List[InstructionSuggestion]:
        """Get base instruction suggestions for all projects"""
        return [
            InstructionSuggestion(
                instruction_id="general_quality_standards",
                tags=["general", "quality"],
                confidence=0.8,
                reasons=["Applicable to all projects"],
                category="general",
            ),
            InstructionSuggestion(
                instruction_id="testing_best_practices",
                tags=["testing", "quality"],
                confidence=0.7,
                reasons=["Testing is important for all projects"],
                category="testing",
            ),
        ]

    def _get_language_suggestions(
        self, language: Language
    ) -> List[InstructionSuggestion]:
        """Get language-specific suggestions"""
        suggestions = []

        if language == Language.PYTHON:
            suggestions.append(
                InstructionSuggestion(
                    instruction_id="python_best_practices",
                    tags=["python", "quality"],
                    confidence=0.9,
                    reasons=[f"Project uses {language.value}"],
                    category="language",
                )
            )
        elif language == Language.JAVASCRIPT:
            suggestions.append(
                InstructionSuggestion(
                    instruction_id="javascript_best_practices",
                    tags=["javascript", "quality"],
                    confidence=0.9,
                    reasons=[f"Project uses {language.value}"],
                    category="language",
                )
            )

        return suggestions

    def _get_framework_suggestions(
        self, framework: Framework
    ) -> List[InstructionSuggestion]:
        """Get framework-specific suggestions"""
        suggestions = []

        if framework.name == "react":
            suggestions.append(
                InstructionSuggestion(
                    instruction_id="react_best_practices",
                    tags=["react", "frontend"],
                    confidence=framework.confidence,
                    reasons=[f"Project uses {framework.name}"],
                    category="framework",
                )
            )

        return suggestions

    def _get_project_type_suggestions(
        self, project_type: ProjectType
    ) -> List[InstructionSuggestion]:
        """Get project type-specific suggestions"""
        suggestions = []

        if project_type == ProjectType.WEB_FRONTEND:
            suggestions.append(
                InstructionSuggestion(
                    instruction_id="frontend_best_practices",
                    tags=["frontend", "web"],
                    confidence=0.8,
                    reasons=[f"Project type is {project_type.value}"],
                    category="project_type",
                )
            )

        return suggestions

    def _get_dependency_suggestions(
        self, dependencies: List[Dependency]
    ) -> List[InstructionSuggestion]:
        """Get dependency-based suggestions"""
        return []  # Simplified for now

    def _get_structure_suggestions(
        self, file_structure: FileStructure
    ) -> List[InstructionSuggestion]:
        """Get file structure-based suggestions"""
        suggestions = []

        if file_structure.test_files:
            suggestions.append(
                InstructionSuggestion(
                    instruction_id="test_organization",
                    tags=["testing", "organization"],
                    confidence=0.6,
                    reasons=["Project has test files"],
                    category="structure",
                )
            )

        return suggestions

    # Private methods expected by tests - wrappers around existing functionality
    def _detect_languages(self, project_path: Path) -> List[Language]:
        """Detect languages in the project (wrapper for tests)"""
        return self.language_detector.detect_languages(project_path)

    def _detect_frameworks(self, project_path: Path) -> List[Framework]:
        """Detect frameworks in the project (wrapper for tests)"""
        return self.framework_detector.detect_frameworks(project_path)

    def _detect_databases(self, project_path: Path) -> List[str]:
        """Detect databases in the project (wrapper for tests)"""
        return self.framework_detector.detect_databases(project_path)

    def _detect_tools(self, project_path: Path) -> List[str]:
        """Detect tools in the project (wrapper for tests)"""
        return self.framework_detector.detect_tools(project_path)

    def _detect_platforms(self, project_path: Path) -> List[str]:
        """Detect platforms in the project (wrapper for tests)"""
        return self.framework_detector.detect_platforms(project_path)
