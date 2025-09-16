"""
Framework and Technology Detection

This module provides functionality to detect frameworks, libraries, databases,
and other technologies used in a project based on various indicators.
"""

import json
import logging
import re
from pathlib import Path
from typing import List

from .types import Dependency, Framework

logger = logging.getLogger(__name__)


class FrameworkDetector:
    """Detects frameworks and technologies from project indicators"""

    def __init__(self) -> None:
        """Initialize the framework detector with indicator mappings"""
        self._framework_indicators = {
            "react": {
                "files": ["package.json"],
                "dependencies": ["react", "react-dom", "react-scripts"],
                "files_patterns": [r".*\.jsx?$", r".*\.tsx?$"],
                "content_patterns": [
                    r"import.*react",
                    r'from [\'"]react[\'"]',
                    r"React\.",
                    r"useState",
                    r"useEffect",
                ],
            },
            "vue": {
                "files": ["package.json", "vue.config.js"],
                "dependencies": ["vue", "@vue/cli"],
                "files_patterns": [r".*\.vue$"],
                "content_patterns": [
                    r"<template>",
                    r"Vue\.",
                    r"createApp",
                    r"defineComponent",
                ],
            },
            "angular": {
                "files": ["package.json", "angular.json", "tsconfig.json"],
                "dependencies": ["@angular/core", "@angular/cli"],
                "files_patterns": [
                    r".*\.component\.ts$",
                    r".*\.service\.ts$",
                    r".*\.module\.ts$",
                ],
                "content_patterns": [
                    r"@Component",
                    r"@Injectable",
                    r"@NgModule",
                    r"import.*@angular",
                ],
            },
            "svelte": {
                "files": ["package.json", "svelte.config.js"],
                "dependencies": ["svelte", "@sveltejs/kit"],
                "files_patterns": [r".*\.svelte$"],
                "content_patterns": [r"<script>", r"export let", r"\$:"],
            },
            "django": {
                "files": [
                    "requirements.txt",
                    "setup.py",
                    "manage.py",
                    "pyproject.toml",
                ],
                "dependencies": ["django", "Django"],
                "files_patterns": [
                    r".*settings\.py$",
                    r".*urls\.py$",
                    r".*models\.py$",
                    r".*views\.py$",
                ],
                "content_patterns": [
                    r"from django",
                    r"DJANGO_SETTINGS_MODULE",
                    r"django\.",
                    r"models\.Model",
                ],
            },
            "flask": {
                "files": [
                    "requirements.txt",
                    "setup.py",
                    "app.py",
                    "pyproject.toml",
                ],
                "dependencies": ["flask", "Flask"],
                "content_patterns": [
                    r"from flask",
                    r"Flask\(__name__\)",
                    r"@app\.route",
                    r"flask\.",
                ],
            },
            "fastapi": {
                "files": [
                    "requirements.txt",
                    "setup.py",
                    "main.py",
                    "pyproject.toml",
                ],
                "dependencies": ["fastapi", "uvicorn"],
                "content_patterns": [
                    r"from fastapi",
                    r"FastAPI\(",
                    r"@app\.get",
                    r"@app\.post",
                ],
            },
            "express": {
                "files": ["package.json", "server.js", "app.js"],
                "dependencies": ["express"],
                "content_patterns": [
                    r'require\([\'"]express[\'"]',
                    r'from [\'"]express[\'"]',
                    r"express\(\)",
                    r"app\.get",
                    r"app\.post",
                ],
            },
            "nestjs": {
                "files": ["package.json", "nest-cli.json"],
                "dependencies": ["@nestjs/core", "@nestjs/common"],
                "files_patterns": [
                    r".*\.controller\.ts$",
                    r".*\.service\.ts$",
                    r".*\.module\.ts$",
                ],
                "content_patterns": [
                    r"@Controller",
                    r"@Injectable",
                    r"@Module",
                    r'from [\'"]@nestjs',
                ],
            },
            "nextjs": {
                "files": ["package.json", "next.config.js", "next.config.mjs"],
                "dependencies": ["next", "react"],
                "files_patterns": [
                    r"pages/.*\.js$",
                    r"pages/.*\.tsx?$",
                    r"app/.*\.tsx?$",
                ],
                "content_patterns": [
                    r'from [\'"]next/',
                    r"import.*next/",
                    r"getStaticProps",
                    r"getServerSideProps",
                ],
            },
            "nuxt": {
                "files": ["package.json", "nuxt.config.js", "nuxt.config.ts"],
                "dependencies": ["nuxt", "@nuxt/"],
                "content_patterns": [
                    r'from [\'"]nuxt',
                    r"export.*nuxtConfig",
                    r"defineNuxtConfig",
                ],
            },
            "gatsby": {
                "files": ["package.json", "gatsby-config.js"],
                "dependencies": ["gatsby"],
                "content_patterns": [r"gatsby-", r"graphql`", r"StaticQuery"],
            },
            "spring": {
                "files": ["pom.xml", "build.gradle", "application.properties"],
                "dependencies": ["spring-boot", "spring-core"],
                "files_patterns": [
                    r".*Application\.java$",
                    r".*Controller\.java$",
                ],
                "content_patterns": [
                    r"@SpringBootApplication",
                    r"@RestController",
                    r"@Service",
                    r"import.*springframework",
                ],
            },
            "laravel": {
                "files": ["composer.json", "artisan"],
                "dependencies": ["laravel/framework"],
                "files_patterns": [r"app/.*\.php$", r"routes/.*\.php$"],
                "content_patterns": [
                    r"use Illuminate",
                    r"Artisan::",
                    r"Route::",
                ],
            },
            "rails": {
                "files": ["Gemfile", "config/application.rb"],
                "dependencies": ["rails"],
                "files_patterns": [r"app/.*\.rb$", r"config/.*\.rb$"],
                "content_patterns": [
                    r"Rails\.",
                    r"ActiveRecord::",
                    r"class.*Controller",
                ],
            },
            "dotnet": {
                "files": ["*.csproj", "*.sln", "Program.cs"],
                "dependencies": ["Microsoft.AspNetCore"],
                "files_patterns": [r".*\.cs$"],
                "content_patterns": [
                    r"using Microsoft",
                    r"namespace",
                    r"\[ApiController\]",
                ],
            },
        }

    def detect_frameworks(self, project_path: Path) -> List[Framework]:
        """
        Detect frameworks from various indicators.

        Args:
            project_path: Path to the project directory

        Returns:
            List of detected frameworks with confidence scores
        """
        frameworks = []

        for framework_name, indicators in self._framework_indicators.items():
            confidence = 0.0
            evidence = []

            # Check for required files
            if "files" in indicators:
                for file_name in indicators["files"]:
                    if (project_path / file_name).exists():
                        confidence += 0.3
                        evidence.append(f"Found {file_name}")

            # Check dependencies
            if "dependencies" in indicators:
                deps = self._get_package_dependencies(project_path)
                for dep in indicators["dependencies"]:
                    if any(dep in d.name for d in deps):
                        confidence += 0.4
                        evidence.append(f"Found dependency: {dep}")

            # Check file patterns
            if "files_patterns" in indicators:
                for pattern in indicators["files_patterns"]:
                    if self._find_files_matching_pattern(project_path, pattern):
                        confidence += 0.2
                        evidence.append(f"Found files matching: {pattern}")

            # Check content patterns
            if "content_patterns" in indicators:
                for pattern in indicators["content_patterns"]:
                    if self._find_content_matching_pattern(project_path, pattern):
                        confidence += 0.3
                        evidence.append(f"Found content matching: {pattern}")

            if confidence > 0.3:  # Minimum threshold
                frameworks.append(
                    Framework(
                        name=framework_name,
                        confidence=min(confidence, 1.0),
                        evidence=evidence,
                    )
                )

        return frameworks

    def detect_databases(self, project_path: Path) -> List[str]:
        """
        Detect database usage from dependencies and config files.

        Args:
            project_path: Path to the project directory

        Returns:
            List of detected databases
        """
        databases = set()

        # Check dependencies
        deps = self._get_package_dependencies(project_path)
        db_indicators = {
            "postgresql": ["psycopg2", "pg", "postgres"],
            "mysql": ["mysql", "pymysql", "mysql2"],
            "sqlite": ["sqlite3", "sqlite"],
            "mongodb": ["pymongo", "mongoose", "mongodb"],
            "redis": ["redis", "redis-py"],
            "elasticsearch": ["elasticsearch", "elastic"],
        }

        for db_name, indicators in db_indicators.items():
            for indicator in indicators:
                if any(indicator in dep.name.lower() for dep in deps):
                    databases.add(db_name)

        # Check config files for database URLs
        config_patterns = {
            "postgresql": [r"postgres://", r"postgresql://"],
            "mysql": [r"mysql://", r"mysql2://"],
            "mongodb": [r"mongodb://", r"mongo://"],
            "redis": [r"redis://"],
        }

        for db_name, patterns in config_patterns.items():
            for pattern in patterns:
                if self._find_content_matching_pattern(project_path, pattern):
                    databases.add(db_name)

        return list(databases)

    def detect_tools(self, project_path: Path) -> List[str]:
        """
        Detect development tools and build systems.

        Args:
            project_path: Path to the project directory

        Returns:
            List of detected tools
        """
        tools = set()

        # Tool indicators based on config files
        tool_files = {
            "webpack": ["webpack.config.js", "webpack.config.ts"],
            "vite": ["vite.config.js", "vite.config.ts"],
            "rollup": ["rollup.config.js"],
            "parcel": [".parcelrc"],
            "docker": ["Dockerfile", "docker-compose.yml", "docker-compose.yaml"],
            "kubernetes": ["k8s/", "kubernetes/", "*.yaml"],
            "terraform": ["*.tf", "terraform/"],
            "ansible": ["playbook.yml", "ansible/"],
            "jenkins": ["Jenkinsfile"],
            "github-actions": [".github/workflows/"],
            "gitlab-ci": [".gitlab-ci.yml"],
            "travis": [".travis.yml"],
            "circleci": [".circleci/"],
            "eslint": [".eslintrc*"],
            "prettier": [".prettierrc*"],
            "jest": ["jest.config.js"],
            "pytest": ["pytest.ini", "pyproject.toml"],
            "makefile": ["Makefile", "makefile"],
            "cmake": ["CMakeLists.txt"],
            "gradle": ["build.gradle", "gradlew"],
            "maven": ["pom.xml"],
        }

        for tool_name, file_patterns in tool_files.items():
            for pattern in file_patterns:
                if "*" in pattern:
                    # Use glob pattern
                    if list(project_path.glob(pattern)):
                        tools.add(tool_name)
                        break
                else:
                    # Direct file check
                    if (project_path / pattern).exists():
                        tools.add(tool_name)
                        break

        return list(tools)

    def detect_platforms(self, project_path: Path) -> List[str]:
        """
        Detect target platforms and deployment environments.

        Args:
            project_path: Path to the project directory

        Returns:
            List of detected platforms
        """
        platforms = set()

        # Platform indicators
        platform_indicators = {
            "web": ["index.html", "public/", "static/", "assets/"],
            "mobile": ["android/", "ios/", "mobile/"],
            "desktop": ["electron/", "tauri/", "desktop/"],
            "server": [
                "server/",
                "backend/",
                "api/",
                "server.js",
                "app.js",
                "main.py",
                "manage.py",
            ],
            "cloud": ["serverless.yml", "sam.yaml", "template.yaml"],
            "aws": [".aws/", "cloudformation/", "cdk/"],
            "gcp": ["gcp/", "google-cloud/"],
            "azure": ["azure/", ".azure/"],
            "heroku": ["Procfile", "app.json"],
            "vercel": ["vercel.json", ".vercel/"],
            "netlify": ["netlify.toml", "_redirects"],
        }

        for platform_name, indicators in platform_indicators.items():
            for indicator in indicators:
                if (project_path / indicator).exists():
                    platforms.add(platform_name)
                    break

        return list(platforms)

    def _get_package_dependencies(self, project_path: Path) -> List[Dependency]:
        """Get dependencies from various package files"""
        dependencies = []

        # Node.js package.json
        package_json = project_path / "package.json"
        if package_json.exists():
            try:
                with open(package_json, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Regular dependencies
                for name, version in data.get("dependencies", {}).items():
                    dependencies.append(
                        Dependency(
                            name=name,
                            version=version,
                            type="runtime",
                            source="package.json",
                        )
                    )

                # Dev dependencies
                for name, version in data.get("devDependencies", {}).items():
                    dependencies.append(
                        Dependency(
                            name=name,
                            version=version,
                            type="dev",
                            source="package.json",
                        )
                    )
            except (json.JSONDecodeError, OSError):
                pass

        # Python requirements.txt
        requirements_txt = project_path / "requirements.txt"
        if requirements_txt.exists():
            try:
                with open(requirements_txt, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            # Parse requirement line (name==version, etc.)
                            match = re.match(r"([a-zA-Z0-9_-]+)([>=<!=]+)?(.*)?", line)
                            if match:
                                name = match.group(1)
                                operator = match.group(2) if match.group(2) else ""
                                version_part = match.group(3) if match.group(3) else ""
                                version = (
                                    operator + version_part
                                    if operator and version_part
                                    else version_part
                                )
                                dependencies.append(
                                    Dependency(
                                        name=name,
                                        version=version,
                                        source="requirements.txt",
                                    )
                                )
            except OSError:
                pass

        # Python pyproject.toml
        pyproject_toml = project_path / "pyproject.toml"
        if pyproject_toml.exists():
            try:
                try:
                    import tomllib
                except ImportError:
                    import tomli as tomllib

                with open(pyproject_toml, "rb") as f:
                    data = tomllib.load(f)

                # Poetry dependencies
                if "tool" in data and "poetry" in data["tool"]:
                    poetry_deps = data["tool"]["poetry"].get("dependencies", {})
                    for name, version in poetry_deps.items():
                        if name != "python":  # Skip Python version requirement
                            version_str = version if isinstance(version, str) else None
                            dependencies.append(
                                Dependency(
                                    name=name,
                                    version=version_str,
                                    source="pyproject.toml",
                                )
                            )

                # PEP 621 dependencies
                if "project" in data:
                    project_deps = data["project"].get("dependencies", [])
                    for dep in project_deps:
                        match = re.match(r"([a-zA-Z0-9_-]+)([>=<!=]+)?(.*)?", dep)
                        if match:
                            name = match.group(1)
                            version = match.group(3) if match.group(3) else None
                            dependencies.append(
                                Dependency(
                                    name=name, version=version, source="pyproject.toml"
                                )
                            )
            except (ImportError, OSError):
                pass

        return dependencies

    def _find_files_matching_pattern(self, project_path: Path, pattern: str) -> bool:
        """Check if any files match the given regex pattern"""
        try:
            compiled_pattern = re.compile(pattern)
            for file_path in project_path.rglob("*"):
                if file_path.is_file() and compiled_pattern.match(str(file_path.name)):
                    return True
        except re.error:
            pass
        return False

    def _find_content_matching_pattern(self, project_path: Path, pattern: str) -> bool:
        """Check if any file content matches the given regex pattern"""
        try:
            compiled_pattern = re.compile(pattern, re.IGNORECASE)
            for file_path in project_path.rglob("*"):
                if (
                    file_path.is_file() and file_path.stat().st_size < 1024 * 1024
                ):  # Skip large files
                    try:
                        with open(
                            file_path, "r", encoding="utf-8", errors="ignore"
                        ) as f:
                            content = f.read(4096)  # Read first 4KB
                            if compiled_pattern.search(content):
                                return True
                    except (OSError, UnicodeDecodeError):
                        continue
        except re.error:
            pass
        return False
