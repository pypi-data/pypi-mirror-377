"""
Unit tests for ContextDetector class.
"""

import json
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest

from agentspec.core.context_detector import (
    ContextDetector,
    Dependency,
    FileStructure,
    Framework,
    InstructionSuggestion,
    Language,
    ProjectContext,
    ProjectType,
    TechnologyStack,
)


class TestContextDetector:
    """Test cases for ContextDetector class."""

    def test_init(self):
        """Test initialization of ContextDetector."""
        detector = ContextDetector()

        assert detector.language_detector is not None
        assert detector.framework_detector is not None
        assert detector._project_type_indicators is not None
        assert hasattr(detector.language_detector, "_language_extensions")
        assert hasattr(detector.framework_detector, "_framework_indicators")

    def test_analyze_project_success(self, context_detector, mock_project_structure):
        """Test successful project analysis."""
        context = context_detector.analyze_project(str(mock_project_structure))

        assert isinstance(context, ProjectContext)
        assert (
            Path(context.project_path).resolve()
            == Path(mock_project_structure).resolve()
        )
        assert context.project_type != ProjectType.UNKNOWN
        assert context.confidence_score > 0
        assert len(context.technology_stack.languages) > 0

    def test_analyze_project_nonexistent_path(self, context_detector):
        """Test project analysis with nonexistent path."""
        with pytest.raises(ValueError, match="Invalid project path"):
            context_detector.analyze_project("/nonexistent/path")

    def test_analyze_project_file_not_directory(self, context_detector, temp_dir):
        """Test project analysis with file instead of directory."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("test")

        with pytest.raises(ValueError, match="Invalid project path"):
            context_detector.analyze_project(str(test_file))

    def test_detect_technology_stack(self, context_detector, mock_project_structure):
        """Test technology stack detection."""
        stack = context_detector.detect_technology_stack(str(mock_project_structure))

        assert isinstance(stack, TechnologyStack)
        assert Language.JAVASCRIPT in stack.languages
        assert any(fw.name == "react" for fw in stack.frameworks)

    def test_detect_languages_from_extensions(self, context_detector, temp_dir):
        """Test language detection from file extensions."""
        # Create files with different extensions
        (temp_dir / "app.js").write_text("console.log('hello');")
        (temp_dir / "component.tsx").write_text(
            "export const Component = () => <div />;"
        )
        (temp_dir / "script.py").write_text("print('hello')")

        languages = context_detector._detect_languages(temp_dir)

        assert Language.JAVASCRIPT in languages
        assert Language.TYPESCRIPT in languages
        assert Language.PYTHON in languages

    def test_detect_language_from_content(self, context_detector, temp_dir):
        """Test language detection from file content."""
        # Create file with JavaScript content but no extension
        js_file = temp_dir / "script"
        js_file.write_text(
            """
        function hello() {
            console.log('Hello World');
            const x = 42;
        }
        """
        )

        detected_language = (
            context_detector.language_detector._detect_language_from_content(js_file)
        )

        assert detected_language == Language.JAVASCRIPT

    def test_detect_frameworks_react(self, context_detector, temp_dir):
        """Test React framework detection."""
        # Create package.json with React dependencies
        package_json = {
            "name": "test-app",
            "dependencies": {"react": "^18.0.0", "react-dom": "^18.0.0"},
        }

        with open(temp_dir / "package.json", "w") as f:
            json.dump(package_json, f)

        # Create React component file
        (temp_dir / "App.jsx").write_text(
            """
        import React from 'react';

        function App() {
            return <div>Hello World</div>;
        }

        export default App;
        """
        )

        frameworks = context_detector._detect_frameworks(temp_dir)

        react_framework = next((fw for fw in frameworks if fw.name == "react"), None)
        assert react_framework is not None
        assert react_framework.confidence > 0.5

    def test_detect_frameworks_django(self, context_detector, temp_dir):
        """Test Django framework detection."""
        # Create requirements.txt with Django
        (temp_dir / "requirements.txt").write_text("Django==4.0.0\npsycopg2==2.9.0")

        # Create Django files
        (temp_dir / "manage.py").write_text(
            """
        import os
        import sys

        if __name__ == '__main__':
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
        """
        )

        (temp_dir / "models.py").write_text(
            """
        from django.db import models

        class User(models.Model):
            name = models.CharField(max_length=100)
        """
        )

        frameworks = context_detector._detect_frameworks(temp_dir)

        django_framework = next((fw for fw in frameworks if fw.name == "django"), None)
        assert django_framework is not None
        assert django_framework.confidence > 0.5

    def test_detect_databases(self, context_detector, temp_dir):
        """Test database detection."""
        # Create package.json with database dependencies
        package_json = {"dependencies": {"pg": "^8.0.0", "redis": "^4.0.0"}}

        with open(temp_dir / "package.json", "w") as f:
            json.dump(package_json, f)

        databases = context_detector._detect_databases(temp_dir)

        assert "postgresql" in databases
        assert "redis" in databases

    def test_detect_tools(self, context_detector, temp_dir):
        """Test development tools detection."""
        # Create tool-specific files
        (temp_dir / "webpack.config.js").write_text("module.exports = {};")
        (temp_dir / "Dockerfile").write_text("FROM node:16")
        (temp_dir / "Makefile").write_text("build:\n\techo 'building'")

        tools = context_detector._detect_tools(temp_dir)

        assert "webpack" in tools
        assert "docker" in tools
        assert "makefile" in tools

    def test_detect_platforms(self, context_detector, temp_dir):
        """Test platform detection."""
        # Create platform-specific indicators
        (temp_dir / "index.html").write_text("<html><body>Hello</body></html>")
        (temp_dir / "server.js").write_text("const express = require('express');")

        android_dir = temp_dir / "android"
        android_dir.mkdir()

        platforms = context_detector._detect_platforms(temp_dir)

        assert "web" in platforms
        assert "server" in platforms
        assert "mobile" in platforms

    def test_suggest_instructions(self, context_detector, sample_project_context):
        """Test instruction suggestions based on context."""
        suggestions = context_detector.suggest_instructions(sample_project_context)

        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

        # Check that suggestions have required fields
        for suggestion in suggestions:
            assert isinstance(suggestion, InstructionSuggestion)
            assert suggestion.instruction_id
            assert isinstance(suggestion.tags, list)
            assert 0 <= suggestion.confidence <= 1

    def test_calculate_confidence(self, context_detector, sample_project_context):
        """Test confidence calculation for suggestions."""
        suggestion = InstructionSuggestion(
            instruction_id="test_instruction",
            tags=["frontend", "react"],
            confidence=0.7,
            reasons=["React framework detected", "Frontend project type"],
        )

        final_confidence = context_detector.calculate_confidence(
            suggestion, sample_project_context
        )

        assert 0 <= final_confidence <= 1
        assert final_confidence >= suggestion.confidence  # Should boost confidence

    def test_get_base_suggestions(self, context_detector):
        """Test base suggestions that apply to all projects."""
        suggestions = context_detector._get_base_suggestions()

        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

        # Should include general suggestions
        suggestion_ids = [s.instruction_id for s in suggestions]
        assert any("general" in s_id or "quality" in s_id for s_id in suggestion_ids)

    def test_get_language_suggestions(self, context_detector):
        """Test language-specific suggestions."""
        suggestions = context_detector._get_language_suggestions(Language.JAVASCRIPT)

        assert isinstance(suggestions, list)

        # Should include JavaScript-specific suggestions
        for suggestion in suggestions:
            assert "javascript" in suggestion.tags or "js" in suggestion.tags

    def test_get_framework_suggestions(self, context_detector):
        """Test framework-specific suggestions."""
        react_framework = Framework(name="react", confidence=0.9)
        suggestions = context_detector._get_framework_suggestions(react_framework)

        assert isinstance(suggestions, list)

        # Should include React-specific suggestions
        for suggestion in suggestions:
            assert "react" in suggestion.tags or "frontend" in suggestion.tags

    def test_get_project_type_suggestions(self, context_detector):
        """Test project type-specific suggestions."""
        suggestions = context_detector._get_project_type_suggestions(
            ProjectType.WEB_FRONTEND
        )

        assert isinstance(suggestions, list)

        # Should include frontend-specific suggestions
        for suggestion in suggestions:
            assert any(tag in ["frontend", "web", "ui"] for tag in suggestion.tags)

    def test_analyze_file_structure(self, context_detector, mock_project_structure):
        """Test file structure analysis."""
        structure = context_detector._analyze_file_structure(mock_project_structure)

        assert isinstance(structure, FileStructure)
        assert structure.total_files > 0
        assert len(structure.directories) > 0
        assert len(structure.config_files) > 0
        assert len(structure.source_files) > 0

    def test_is_config_file(self, context_detector):
        """Test config file identification."""
        assert context_detector._is_config_file("package.json")
        assert context_detector._is_config_file("tsconfig.json")
        assert context_detector._is_config_file("webpack.config.js")
        assert context_detector._is_config_file(".env")
        assert not context_detector._is_config_file("App.js")
        assert not context_detector._is_config_file("README.md")

    def test_is_source_file(self, context_detector):
        """Test source file identification."""
        assert context_detector._is_source_file("App.js")
        assert context_detector._is_source_file("component.tsx")
        assert context_detector._is_source_file("script.py")
        assert context_detector._is_source_file("main.go")
        assert not context_detector._is_source_file("package.json")
        assert not context_detector._is_source_file("README.md")

    def test_is_test_file(self, context_detector):
        """Test test file identification."""
        assert context_detector._is_test_file("App.test.js")
        assert context_detector._is_test_file("component.spec.ts")
        assert context_detector._is_test_file("test_utils.py")
        assert context_detector._is_test_file("utils_test.go")
        assert not context_detector._is_test_file("App.js")
        assert not context_detector._is_test_file("package.json")

    def test_is_documentation_file(self, context_detector):
        """Test documentation file identification."""
        assert context_detector._is_documentation_file("README.md")
        assert context_detector._is_documentation_file("CHANGELOG.md")
        assert context_detector._is_documentation_file("docs/guide.md")
        assert context_detector._is_documentation_file("API.rst")
        assert not context_detector._is_documentation_file("App.js")
        assert not context_detector._is_documentation_file("package.json")

    def test_parse_package_json(self, context_detector, temp_dir):
        """Test parsing package.json dependencies."""
        package_json = {
            "name": "test-app",
            "dependencies": {"react": "^18.0.0", "lodash": "^4.17.21"},
            "devDependencies": {"jest": "^28.0.0", "@types/node": "^18.0.0"},
        }

        package_file = temp_dir / "package.json"
        with open(package_file, "w") as f:
            json.dump(package_json, f)

        dependencies = context_detector.framework_detector._get_package_dependencies(
            temp_dir
        )

        assert len(dependencies) == 4

        # Check runtime dependencies
        runtime_deps = [dep for dep in dependencies if dep.type == "runtime"]
        assert len(runtime_deps) == 2
        assert any(
            dep.name == "react" and dep.version == "^18.0.0" for dep in runtime_deps
        )

        # Check dev dependencies
        dev_deps = [dep for dep in dependencies if dep.type == "dev"]
        assert len(dev_deps) == 2
        assert any(dep.name == "jest" for dep in dev_deps)

    def test_parse_requirements_txt(self, context_detector, temp_dir):
        """Test parsing requirements.txt dependencies."""
        requirements_content = """
        Django==4.0.0
        requests>=2.25.0
        pytest
        # This is a comment
        -e git+https://github.com/user/repo.git#egg=package
        """

        requirements_file = temp_dir / "requirements.txt"
        requirements_file.write_text(requirements_content)

        dependencies = context_detector.framework_detector._get_package_dependencies(
            temp_dir
        )

        assert len(dependencies) >= 3

        # Check specific dependencies
        django_dep = next((dep for dep in dependencies if dep.name == "Django"), None)
        assert django_dep is not None
        assert django_dep.version == "==4.0.0"

        requests_dep = next(
            (dep for dep in dependencies if dep.name == "requests"), None
        )
        assert requests_dep is not None
        assert requests_dep.version == ">=2.25.0"

    def test_detect_project_type_web_frontend(self, context_detector):
        """Test project type detection for web frontend."""
        context = ProjectContext(
            project_path="/test",
            project_type=ProjectType.UNKNOWN,
            technology_stack=TechnologyStack(
                languages=[Language.JAVASCRIPT, Language.TYPESCRIPT],
                frameworks=[Framework(name="react", confidence=0.9)],
            ),
            file_structure=FileStructure(
                config_files=["package.json"],
                source_files=["src/App.js", "src/index.js"],
            ),
        )

        project_type = context_detector._detect_project_type(context)

        assert project_type == ProjectType.WEB_FRONTEND

    def test_detect_project_type_web_backend(self, context_detector):
        """Test project type detection for web backend."""
        context = ProjectContext(
            project_path="/test",
            project_type=ProjectType.UNKNOWN,
            technology_stack=TechnologyStack(
                languages=[Language.PYTHON],
                frameworks=[Framework(name="django", confidence=0.9)],
            ),
            file_structure=FileStructure(
                config_files=["requirements.txt"],
                source_files=["manage.py", "models.py"],
            ),
        )

        project_type = context_detector._detect_project_type(context)

        assert project_type == ProjectType.WEB_BACKEND

    def test_calculate_context_confidence(
        self, context_detector, sample_project_context
    ):
        """Test context confidence calculation."""
        confidence = context_detector._calculate_context_confidence(
            sample_project_context
        )

        assert 0 <= confidence <= 1
        assert confidence > 0  # Should have some confidence for valid context


class TestProjectType:
    """Test cases for ProjectType enum."""

    def test_project_type_values(self):
        """Test ProjectType enum values."""
        assert ProjectType.WEB_FRONTEND.value == "web_frontend"
        assert ProjectType.WEB_BACKEND.value == "web_backend"
        assert ProjectType.FULLSTACK_WEB.value == "fullstack_web"
        assert ProjectType.MOBILE_APP.value == "mobile_app"
        assert ProjectType.UNKNOWN.value == "unknown"


class TestLanguage:
    """Test cases for Language enum."""

    def test_language_values(self):
        """Test Language enum values."""
        assert Language.JAVASCRIPT.value == "javascript"
        assert Language.TYPESCRIPT.value == "typescript"
        assert Language.PYTHON.value == "python"
        assert Language.JAVA.value == "java"
        assert Language.UNKNOWN.value == "unknown"


class TestFramework:
    """Test cases for Framework dataclass."""

    def test_framework_creation(self):
        """Test creating a Framework instance."""
        framework = Framework(
            name="react",
            version="18.0.0",
            confidence=0.9,
            evidence=["package.json dependency", "JSX files found"],
        )

        assert framework.name == "react"
        assert framework.version == "18.0.0"
        assert framework.confidence == 0.9
        assert len(framework.evidence) == 2


class TestDependency:
    """Test cases for Dependency dataclass."""

    def test_dependency_creation(self):
        """Test creating a Dependency instance."""
        dependency = Dependency(
            name="react", version="^18.0.0", type="runtime", source="package.json"
        )

        assert dependency.name == "react"
        assert dependency.version == "^18.0.0"
        assert dependency.type == "runtime"
        assert dependency.source == "package.json"


class TestInstructionSuggestion:
    """Test cases for InstructionSuggestion dataclass."""

    def test_suggestion_creation(self):
        """Test creating an InstructionSuggestion instance."""
        suggestion = InstructionSuggestion(
            instruction_id="react_testing",
            tags=["react", "testing", "frontend"],
            confidence=0.85,
            reasons=["React framework detected", "Test files found"],
            category="testing",
        )

        assert suggestion.instruction_id == "react_testing"
        assert suggestion.tags == ["react", "testing", "frontend"]
        assert suggestion.confidence == 0.85
        assert len(suggestion.reasons) == 2
        assert suggestion.category == "testing"
