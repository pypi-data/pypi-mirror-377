"""
Programming Language Detection

This module provides functionality to detect programming languages used in a project
based on file extensions, content analysis, and pattern matching.
"""

import logging
import os
import re
from pathlib import Path
from typing import Dict, List, Optional

from .types import Language

logger = logging.getLogger(__name__)


class LanguageDetector:
    """Detects programming languages from project files"""

    def __init__(self) -> None:
        """Initialize the language detector with extension mappings and patterns"""
        self._language_extensions = {
            Language.JAVASCRIPT: [".js", ".mjs", ".jsx", ".cjs"],
            Language.TYPESCRIPT: [".ts", ".tsx", ".d.ts"],
            Language.PYTHON: [".py", ".pyw", ".pyi", ".py3"],
            Language.JAVA: [".java", ".class", ".jar"],
            Language.CSHARP: [".cs", ".csx", ".vb"],
            Language.CPP: [
                ".cpp",
                ".cxx",
                ".cc",
                ".c++",
                ".hpp",
                ".hxx",
                ".h++",
            ],
            Language.C: [".c", ".h"],
            Language.GO: [".go", ".mod", ".sum"],
            Language.RUST: [".rs", ".toml"],
            Language.PHP: [".php", ".phtml", ".php3", ".php4", ".php5"],
            Language.RUBY: [".rb", ".rbw", ".rake", ".gemspec"],
            Language.SWIFT: [".swift"],
            Language.KOTLIN: [".kt", ".kts"],
            Language.DART: [".dart"],
            Language.HTML: [".html", ".htm", ".xhtml"],
            Language.CSS: [".css", ".scss", ".sass", ".less", ".styl"],
        }

        # Content patterns for language detection when extensions are ambiguous
        self._language_content_patterns = {
            Language.JAVASCRIPT: [
                r"console\.log",
                r"function\s+\w+",
                r"var\s+\w+",
                r"let\s+\w+",
                r"const\s+\w+",
            ],
            Language.TYPESCRIPT: [
                r"interface\s+\w+",
                r"type\s+\w+\s*=",
                r":\s*string",
                r":\s*number",
                r"export\s+type",
            ],
            Language.PYTHON: [
                r"def\s+\w+",
                r"import\s+\w+",
                r"from\s+\w+\s+import",
                r'if\s+__name__\s*==\s*[\'"]__main__[\'"]',
            ],
            Language.JAVA: [
                r"public\s+class",
                r"public\s+static\s+void\s+main",
                r"import\s+java\.",
            ],
            Language.CSHARP: [
                r"using\s+System",
                r"namespace\s+\w+",
                r"public\s+class",
                r"\[.*\]",
            ],
            Language.GO: [
                r"package\s+\w+",
                r"func\s+\w+",
                r'import\s+[\'"]',
                r"go\s+\w+",
            ],
            Language.RUST: [
                r"fn\s+\w+",
                r"use\s+\w+",
                r"struct\s+\w+",
                r"impl\s+\w+",
            ],
            Language.PHP: [r"<\?php", r"function\s+\w+", r"\$\w+", r"echo\s+"],
            Language.RUBY: [
                r"def\s+\w+",
                r"class\s+\w+",
                r'require\s+[\'"]',
                r"puts\s+",
            ],
        }

    def detect_languages(self, project_path: Path) -> List[Language]:
        """
        Detect programming languages from file extensions and content analysis.

        Args:
            project_path: Path to the project directory

        Returns:
            List of detected programming languages
        """
        languages = set()
        language_file_counts: Dict[str, int] = {}

        for root, dirs, files in os.walk(project_path):
            # Skip hidden directories and common ignore patterns
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".")
                and d
                not in [
                    "node_modules",
                    "__pycache__",
                    "venv",
                    "env",
                    "build",
                    "dist",
                ]
            ]

            for file in files:
                if file.startswith("."):
                    continue

                file_path = Path(root) / file
                ext = file_path.suffix.lower()

                # Detect by file extension
                detected_by_extension = []
                for language, extensions in self._language_extensions.items():
                    if ext in extensions:
                        detected_by_extension.append(language)
                        language_file_counts[language.value] = (
                            language_file_counts.get(language.value, 0) + 1
                        )

                # For ambiguous cases or extensionless files, use content analysis
                if not detected_by_extension or len(detected_by_extension) > 1:
                    content_language = self._detect_language_from_content(file_path)
                    if content_language:
                        detected_by_extension = [content_language]
                        language_file_counts[content_language.value] = (
                            language_file_counts.get(content_language.value, 0) + 1
                        )

                languages.update(detected_by_extension)

        # Filter out languages with very few files (likely false positives)
        filtered_languages = []
        total_files = sum(language_file_counts.values())

        for language in languages:
            file_count = language_file_counts.get(language.value, 0)
            # Include language if it has at least 2 files or represents >5% of total files
            if file_count >= 2 or (total_files > 0 and file_count / total_files > 0.05):
                filtered_languages.append(language)

        return filtered_languages

    def _detect_language_from_content(self, file_path: Path) -> Optional[Language]:
        """
        Detect language from file content using pattern matching.

        Args:
            file_path: Path to the file to analyze

        Returns:
            Detected language or None if no match found
        """
        try:
            # Only analyze reasonably sized text files
            if file_path.stat().st_size > 1024 * 1024:  # Skip files larger than 1MB
                return None

            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(4096)  # Read first 4KB for analysis

            # Score each language based on pattern matches
            language_scores = {}

            for language, patterns in self._language_content_patterns.items():
                score = 0
                for pattern in patterns:
                    matches = len(re.findall(pattern, content, re.IGNORECASE))
                    score += matches

                if score > 0:
                    language_scores[language] = score

            # Return the language with the highest score
            if language_scores:
                return max(language_scores.items(), key=lambda x: x[1])[0]

        except Exception:
            pass  # nosec B110 # Intentionally ignore parsing errors

        return None

    def get_language_statistics(self, project_path: Path) -> Dict[str, Dict[str, int]]:
        """
        Get detailed statistics about language usage in the project.

        Args:
            project_path: Path to the project directory

        Returns:
            Dictionary with language statistics including file counts and line counts
        """
        stats: Dict[str, Dict[str, int]] = {}

        for root, dirs, files in os.walk(project_path):
            # Skip hidden directories and common ignore patterns
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".")
                and d
                not in ["node_modules", "__pycache__", "venv", "env", "build", "dist"]
            ]

            for file in files:
                if file.startswith("."):
                    continue

                file_path = Path(root) / file
                ext = file_path.suffix.lower()

                # Find matching language
                detected_language = None
                for language, extensions in self._language_extensions.items():
                    if ext in extensions:
                        detected_language = language
                        break

                if detected_language:
                    lang_name = detected_language.value
                    if lang_name not in stats:
                        stats[lang_name] = {"files": 0, "lines": 0, "bytes": 0}

                    stats[lang_name]["files"] += 1

                    try:
                        # Count lines and bytes
                        with open(
                            file_path, "r", encoding="utf-8", errors="ignore"
                        ) as f:
                            lines = sum(1 for _ in f)
                        stats[lang_name]["lines"] += lines
                        stats[lang_name]["bytes"] += file_path.stat().st_size
                    except Exception:
                        # If we can't read the file, just count the bytes
                        stats[lang_name]["bytes"] += file_path.stat().st_size

        return stats
