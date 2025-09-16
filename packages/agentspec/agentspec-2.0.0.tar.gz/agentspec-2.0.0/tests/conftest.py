"""
Pytest configuration and shared fixtures for AgentSpec tests.
"""

import json
import tempfile
from pathlib import Path
from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest

from agentspec.core.context_detector import (
    ContextDetector,
    FileStructure,
    Framework,
    Language,
    ProjectContext,
    ProjectType,
    TechnologyStack,
)
from agentspec.core.instruction import (
    Condition,
    Instruction,
    InstructionMetadata,
    LanguageVariant,
    Parameter,
)
from agentspec.core.instruction_database import InstructionDatabase
from agentspec.core.spec_generator import SpecConfig, SpecGenerator
from agentspec.core.template_manager import (
    Template,
    TemplateCondition,
    TemplateManager,
    TemplateMetadata,
    TemplateParameter,
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_instruction():
    """Create a sample instruction for testing."""
    metadata = InstructionMetadata(category="testing", priority=5, author="test_author")

    return Instruction(
        id="test_instruction",
        version="1.0.0",
        tags=["testing", "quality"],
        content="This is a test instruction for unit testing.",
        metadata=metadata,
    )


@pytest.fixture
def sample_instruction_with_conditions():
    """Create a sample instruction with conditions for testing."""
    conditions = [
        Condition(type="project_type", value="web_frontend", operator="equals")
    ]

    parameters = [
        Parameter(
            name="test_param",
            type="string",
            default="default_value",
            description="Test parameter",
        )
    ]

    metadata = InstructionMetadata(category="frontend", priority=7)

    return Instruction(
        id="conditional_instruction",
        version="2.0.0",
        tags=["frontend", "react"],
        content="Frontend-specific instruction with {test_param}.",
        conditions=conditions,
        parameters=parameters,
        metadata=metadata,
    )


@pytest.fixture
def sample_template():
    """Create a sample template for testing."""
    parameters = {
        "project_name": TemplateParameter(
            name="project_name",
            type="string",
            default="my-project",
            description="Name of the project",
        )
    }

    conditions = [
        TemplateCondition(
            type="file_exists", value="package.json", operator="exists", weight=0.8
        )
    ]

    metadata = TemplateMetadata(
        category="web", complexity="intermediate", tags=["react", "frontend"]
    )

    return Template(
        id="react_app",
        name="React Application",
        description="Template for React applications",
        version="1.0.0",
        project_type="web_frontend",
        technology_stack=["react", "javascript"],
        default_tags=["frontend", "react", "testing"],
        required_instructions=["test_instruction"],
        optional_instructions=["conditional_instruction"],
        parameters=parameters,
        conditions=conditions,
        metadata=metadata,
    )


@pytest.fixture
def sample_project_context():
    """Create a sample project context for testing."""
    tech_stack = TechnologyStack(
        languages=[Language.JAVASCRIPT, Language.TYPESCRIPT],
        frameworks=[Framework(name="react", version="18.0.0", confidence=0.9)],
        databases=["postgresql"],
        tools=["webpack", "jest"],
        platforms=["web"],
    )

    file_structure = FileStructure(
        total_files=50,
        directories=["src", "public", "tests"],
        file_types={".js": 20, ".ts": 15, ".json": 5},
        config_files=["package.json", "tsconfig.json"],
        source_files=["src/App.js", "src/index.js"],
        test_files=["tests/App.test.js"],
    )

    return ProjectContext(
        project_path="/test/project",
        project_type=ProjectType.WEB_FRONTEND,
        technology_stack=tech_stack,
        file_structure=file_structure,
        confidence_score=0.85,
    )


@pytest.fixture
def mock_instruction_files(temp_dir):
    """Create mock instruction files for testing."""
    instructions_dir = temp_dir / "instructions"
    instructions_dir.mkdir()

    # Create sample instruction files
    general_instructions = {
        "instructions": [
            {
                "id": "general_quality",
                "version": "1.0.0",
                "tags": ["general", "quality"],
                "content": "Maintain high code quality standards.",
                "metadata": {"category": "general", "priority": 5},
            }
        ]
    }

    testing_instructions = {
        "instructions": [
            {
                "id": "unit_testing",
                "version": "1.0.0",
                "tags": ["testing", "unit"],
                "content": "Write comprehensive unit tests.",
                "metadata": {"category": "testing", "priority": 8},
            }
        ]
    }

    # Add spec workflow instructions for testing
    spec_workflow_instructions = {
        "instructions": [
            {
                "id": "plan_and_reflect",
                "version": "1.0.0",
                "tags": ["spec", "workflow", "planning", "reflection", "methodology"],
                "content": "Plan thoroughly before every tool call and reflect on the outcome after. Always think through what you're trying to accomplish, what tools you need, and what the expected result should be. After each action, evaluate whether it achieved the intended goal and adjust your approach if needed.",
                "metadata": {
                    "category": "spec-workflow",
                    "priority": 10,
                    "author": "AgentSpec",
                    "created_at": "2024-12-15T00:00:00Z",
                    "updated_at": "2024-12-15T00:00:00Z",
                },
            },
            {
                "id": "use_tools_dont_guess",
                "version": "1.0.0",
                "tags": ["spec", "workflow", "verification", "accuracy", "tools"],
                "content": "Use your tools, don't guess. If you're unsure about code or files, open them - do not hallucinate. Always verify information by reading files, checking directory structures, or running commands rather than making assumptions about what exists or how things work.",
                "metadata": {
                    "category": "spec-workflow",
                    "priority": 10,
                    "author": "AgentSpec",
                    "created_at": "2024-12-15T00:00:00Z",
                    "updated_at": "2024-12-15T00:00:00Z",
                },
            },
            {
                "id": "persist_until_complete",
                "version": "1.0.0",
                "tags": [
                    "spec",
                    "workflow",
                    "persistence",
                    "completion",
                    "thoroughness",
                ],
                "content": "Persist in your work. Keep going until the job is completely solved before ending your turn. Don't stop at partial solutions or leave tasks half-finished. Ensure all requirements are met, all tests pass, and the implementation is fully functional before considering the work done.",
                "metadata": {
                    "category": "spec-workflow",
                    "priority": 10,
                    "author": "AgentSpec",
                    "created_at": "2024-12-15T00:00:00Z",
                    "updated_at": "2024-12-15T00:00:00Z",
                },
            },
            {
                "id": "context_management",
                "version": "1.0.0",
                "tags": ["spec", "workflow", "persistence", "resume", "tracking"],
                "content": "Document progress and maintain clear records of development steps, decisions made, and next actions for each development task.",
                "metadata": {
                    "category": "spec-workflow",
                    "priority": 9,
                    "author": "AgentSpec",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-12-15T00:00:00Z",
                },
            },
            {
                "id": "thorough_analysis",
                "version": "1.0.0",
                "tags": ["spec", "workflow", "analysis", "debugging", "investigation"],
                "content": "Begin every task with thorough code analysis, identify exact locations to fix, and define crisp exit criteria. Perform comprehensive code review before making changes.",
                "metadata": {
                    "category": "spec-workflow",
                    "priority": 9,
                    "author": "AgentSpec",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-12-15T00:00:00Z",
                },
            },
            {
                "id": "no_error_policy",
                "version": "1.0.0",
                "tags": ["spec", "workflow", "quality", "testing", "integration"],
                "content": "After every task, ensure zero linting, compilation, build or deployment errors. Fix all issues before marking task complete. Verify backend-frontend integration consistency.",
                "metadata": {
                    "category": "spec-workflow",
                    "priority": 10,
                    "author": "AgentSpec",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-12-15T00:00:00Z",
                },
            },
            {
                "id": "incremental_development",
                "version": "1.0.0",
                "tags": [
                    "spec",
                    "workflow",
                    "development",
                    "incremental",
                    "validation",
                ],
                "content": "Implement features incrementally with frequent validation. Make small, focused changes that can be easily reviewed and rolled back. Validate each step before proceeding to the next.",
                "metadata": {
                    "category": "spec-workflow",
                    "priority": 10,
                    "author": "AgentSpec",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-12-15T00:00:00Z",
                },
            },
            {
                "id": "error_recovery",
                "version": "1.0.0",
                "tags": [
                    "spec",
                    "workflow",
                    "error-handling",
                    "recovery",
                    "resilience",
                ],
                "content": "When errors occur, analyze the root cause, implement proper fixes, and add safeguards to prevent recurrence. Document error patterns and solutions for future reference.",
                "metadata": {
                    "category": "spec-workflow",
                    "priority": 8,
                    "author": "AgentSpec",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-12-15T00:00:00Z",
                },
            },
            {
                "id": "continuous_validation_loop",
                "version": "1.0.0",
                "tags": ["spec", "workflow", "validation", "testing", "quality"],
                "content": "Implement continuous validation as core workflow: Prompt → Generate → Validate → Refine. Use multi-faceted validation: automated testing, manual state inspection, direct application interaction. Leverage AI to generate tailored validation plans and test checklists. Never skip validation to maintain quality at speed.",
                "metadata": {
                    "category": "spec-workflow",
                    "priority": 10,
                    "author": "Research Integration",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-12-15T00:00:00Z",
                },
            },
            {
                "id": "avoid_vibe_coding",
                "version": "1.0.0",
                "tags": ["spec", "workflow", "discipline", "quality", "validation"],
                "content": "Avoid 'vibe coding' (high-level descriptions with minimal scrutiny) for enterprise systems. Use disciplined AI-assisted coding: iterative process with well-defined steps, continuous validation, and refinement. Never commit code you don't fully understand. Focus on higher-order tasks: business context, architectural trade-offs, correctness verification.",
                "metadata": {
                    "category": "spec-workflow",
                    "priority": 10,
                    "author": "Research Integration",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-12-15T00:00:00Z",
                },
            },
            {
                "id": "systematic_debugging",
                "version": "1.0.0",
                "tags": [
                    "spec",
                    "workflow",
                    "debugging",
                    "troubleshooting",
                    "methodology",
                ],
                "content": "Use systematic debugging approaches: reproduce the issue consistently, isolate the problem area, form hypotheses, test incrementally. Document findings and solutions for future reference.",
                "metadata": {
                    "category": "spec-workflow",
                    "priority": 8,
                    "author": "AgentSpec",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-12-15T00:00:00Z",
                },
            },
        ]
    }

    with open(instructions_dir / "general.json", "w") as f:
        json.dump(general_instructions, f)

    with open(instructions_dir / "testing.json", "w") as f:
        json.dump(testing_instructions, f)

    with open(instructions_dir / "spec-workflow.json", "w") as f:
        json.dump(spec_workflow_instructions, f)

    return instructions_dir


@pytest.fixture
def mock_template_files(temp_dir):
    """Create mock template files for testing."""
    templates_dir = temp_dir / "templates"
    templates_dir.mkdir()

    # Create sample template file
    react_template = {
        "id": "react_app",
        "name": "React Application",
        "description": "Template for React applications",
        "version": "1.0.0",
        "project_type": "web_frontend",
        "technology_stack": ["react", "javascript"],
        "default_tags": ["frontend", "react", "testing"],
        "required_instructions": ["unit_testing"],
        "optional_instructions": ["general_quality"],
        "parameters": {
            "project_name": {
                "type": "string",
                "default": "my-react-app",
                "description": "Name of the React project",
            }
        },
        "metadata": {"category": "web", "complexity": "intermediate"},
    }

    with open(templates_dir / "react_app.json", "w") as f:
        json.dump(react_template, f)

    return templates_dir


@pytest.fixture
def mock_project_structure(temp_dir):
    """Create a mock project structure for testing."""
    project_dir = temp_dir / "test_project"
    project_dir.mkdir()

    # Create package.json
    package_json = {
        "name": "test-project",
        "version": "1.0.0",
        "dependencies": {"react": "^18.0.0", "react-dom": "^18.0.0"},
        "devDependencies": {"jest": "^28.0.0", "@testing-library/react": "^13.0.0"},
    }

    with open(project_dir / "package.json", "w") as f:
        json.dump(package_json, f)

    # Create source files
    src_dir = project_dir / "src"
    src_dir.mkdir()

    with open(src_dir / "App.js", "w") as f:
        f.write(
            """
import React from 'react';

function App() {
  return <div>Hello World</div>;
}

export default App;
        """
        )

    with open(src_dir / "index.js", "w") as f:
        f.write(
            """
import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';

ReactDOM.render(<App />, document.getElementById('root'));
        """
        )

    # Create test files
    tests_dir = project_dir / "tests"
    tests_dir.mkdir()

    with open(tests_dir / "App.test.js", "w") as f:
        f.write(
            """
import { render } from '@testing-library/react';
import App from '../src/App';

test('renders hello world', () => {
  render(<App />);
});
        """
        )

    return project_dir


@pytest.fixture
def instruction_database(mock_instruction_files):
    """Create an InstructionDatabase instance with mock data."""
    return InstructionDatabase(instructions_path=mock_instruction_files)


@pytest.fixture
def template_manager(mock_template_files):
    """Create a TemplateManager instance with mock data."""
    return TemplateManager(templates_path=mock_template_files)


@pytest.fixture
def context_detector():
    """Create a ContextDetector instance."""
    return ContextDetector()


@pytest.fixture
def spec_generator(instruction_database, template_manager, context_detector):
    """Create a SpecGenerator instance with dependencies."""
    return SpecGenerator(
        instruction_db=instruction_database,
        template_manager=template_manager,
        context_detector=context_detector,
    )


# Mock external dependencies
@pytest.fixture
def mock_git_repo():
    """Mock git repository information."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "main\n"
        yield mock_run


@pytest.fixture
def mock_file_system():
    """Mock file system operations."""
    with patch("pathlib.Path.exists") as mock_exists, patch(
        "pathlib.Path.is_dir"
    ) as mock_is_dir, patch("os.walk") as mock_walk:
        mock_exists.return_value = True
        mock_is_dir.return_value = True
        mock_walk.return_value = [
            ("/test", ["src"], ["package.json"]),
            ("/test/src", [], ["App.js", "index.js"]),
        ]

        yield {"exists": mock_exists, "is_dir": mock_is_dir, "walk": mock_walk}


# Utility functions for tests
def create_test_instruction(
    instruction_id: str = "test_inst", tags: list = None, content: str = "Test content"
) -> Instruction:
    """Helper function to create test instructions."""
    if tags is None:
        tags = ["test"]

    return Instruction(
        id=instruction_id,
        version="1.0.0",
        tags=tags,
        content=content,
        metadata=InstructionMetadata(category="test"),
    )


def create_test_template(
    template_id: str = "test_template", project_type: str = "web_frontend"
) -> Template:
    """Helper function to create test templates."""
    return Template(
        id=template_id,
        name="Test Template",
        description="A test template",
        version="1.0.0",
        project_type=project_type,
        technology_stack=["test"],
        default_tags=["test"],
        metadata=TemplateMetadata(category="test"),
    )


def assert_validation_result(
    result,
    should_be_valid: bool = True,
    expected_errors: int = 0,
    expected_warnings: int = 0,
):
    """Helper function to assert validation results."""
    assert result.is_valid == should_be_valid
    assert len(result.errors) == expected_errors
    assert len(result.warnings) == expected_warnings
