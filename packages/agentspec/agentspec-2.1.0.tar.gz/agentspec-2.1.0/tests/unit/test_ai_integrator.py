"""
Unit tests for AI Best Practices Integrator
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from agentspec.core.ai_integrator import AIBestPracticesIntegrator
from agentspec.core.context_detector import ContextDetector, ProjectContext, ProjectType
from agentspec.core.instruction_database import InstructionDatabase
from agentspec.core.template_manager import TemplateManager


class TestAIBestPracticesIntegrator:
    """Test cases for AIBestPracticesIntegrator"""

    @pytest.fixture
    def mock_services(self):
        """Create mock services for testing"""
        instruction_db = Mock(spec=InstructionDatabase)
        template_manager = Mock(spec=TemplateManager)
        context_detector = Mock(spec=ContextDetector)
        return instruction_db, template_manager, context_detector

    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)

            # Create some basic project files
            (project_path / "package.json").write_text('{"name": "test-project"}')
            (project_path / "src").mkdir()
            (project_path / "src" / "index.js").write_text("console.log('hello');")

            yield project_path

    def test_init(self, temp_project, mock_services):
        """Test integrator initialization"""
        instruction_db, template_manager, context_detector = mock_services

        integrator = AIBestPracticesIntegrator(
            temp_project, instruction_db, template_manager, context_detector
        )

        assert integrator.project_path == temp_project
        assert integrator.agentspec_path == temp_project / ".agentspec"
        assert integrator.instruction_db == instruction_db
        assert integrator.template_manager == template_manager
        assert integrator.context_detector == context_detector

    def test_detect_ai_tools_with_copilot(self, temp_project, mock_services):
        """Test AI tool detection with Copilot"""
        instruction_db, template_manager, context_detector = mock_services

        # Create Copilot indicator
        (temp_project / ".copilot").mkdir()

        integrator = AIBestPracticesIntegrator(
            temp_project, instruction_db, template_manager, context_detector
        )

        assert integrator._detect_ai_tools() is True

    def test_detect_ai_tools_with_package_dependency(self, temp_project, mock_services):
        """Test AI tool detection with package dependencies"""
        instruction_db, template_manager, context_detector = mock_services

        # Update package.json with AI dependency
        package_json = {"name": "test-project", "dependencies": {"openai": "^4.0.0"}}
        (temp_project / "package.json").write_text(json.dumps(package_json))

        integrator = AIBestPracticesIntegrator(
            temp_project, instruction_db, template_manager, context_detector
        )

        assert integrator._detect_ai_tools() is True

    def test_detect_ai_tools_none_found(self, temp_project, mock_services):
        """Test AI tool detection when none are found"""
        instruction_db, template_manager, context_detector = mock_services

        integrator = AIBestPracticesIntegrator(
            temp_project, instruction_db, template_manager, context_detector
        )

        assert integrator._detect_ai_tools() is False

    def test_assess_security_requirements_basic(self, temp_project, mock_services):
        """Test basic security level assessment"""
        instruction_db, template_manager, context_detector = mock_services

        integrator = AIBestPracticesIntegrator(
            temp_project, instruction_db, template_manager, context_detector
        )

        analysis = {"project_type": "web_application", "technologies": []}
        security_level = integrator._assess_security_requirements(analysis)

        assert security_level == "basic"

    def test_assess_security_requirements_enterprise(self, temp_project, mock_services):
        """Test enterprise security level assessment"""
        instruction_db, template_manager, context_detector = mock_services

        # Create enterprise indicators
        (temp_project / "SECURITY.md").write_text("Security policy")

        integrator = AIBestPracticesIntegrator(
            temp_project, instruction_db, template_manager, context_detector
        )

        analysis = {"project_type": "web_application", "technologies": []}
        security_level = integrator._assess_security_requirements(analysis)

        assert security_level == "enterprise"

    def test_assess_security_requirements_intermediate(
        self, temp_project, mock_services
    ):
        """Test intermediate security level assessment"""
        instruction_db, template_manager, context_detector = mock_services

        integrator = AIBestPracticesIntegrator(
            temp_project, instruction_db, template_manager, context_detector
        )

        analysis = {
            "project_type": "web_application",
            "technologies": ["auth", "oauth"],
        }
        security_level = integrator._assess_security_requirements(analysis)

        assert security_level == "intermediate"

    def test_recommend_ai_instructions_basic(self, temp_project, mock_services):
        """Test basic AI instruction recommendations"""
        instruction_db, template_manager, context_detector = mock_services

        integrator = AIBestPracticesIntegrator(
            temp_project, instruction_db, template_manager, context_detector
        )

        analysis = {
            "has_ai_tools": False,
            "security_level": "basic",
            "technologies": [],
        }

        recommendations = integrator._recommend_ai_instructions(analysis)

        # Should include foundational instructions
        foundational = [
            "human_in_the_loop_architect",
            "rich_scratchpad_context",
            "continuous_validation_loop",
            "avoid_vibe_coding",
            "never_commit_unknown_code",
        ]

        for instruction in foundational:
            assert instruction in recommendations

    def test_recommend_ai_instructions_with_ai_tools(self, temp_project, mock_services):
        """Test AI instruction recommendations with AI tools present"""
        instruction_db, template_manager, context_detector = mock_services

        integrator = AIBestPracticesIntegrator(
            temp_project, instruction_db, template_manager, context_detector
        )

        analysis = {"has_ai_tools": True, "security_level": "basic", "technologies": []}

        recommendations = integrator._recommend_ai_instructions(analysis)

        # Should include prompt engineering instructions
        prompt_engineering = [
            "clarity_context_constraints",
            "chain_of_thought_prompting",
            "decomposition_prompting",
        ]

        for instruction in prompt_engineering:
            assert instruction in recommendations

    def test_recommend_ai_instructions_frontend(self, temp_project, mock_services):
        """Test AI instruction recommendations for frontend projects"""
        instruction_db, template_manager, context_detector = mock_services

        integrator = AIBestPracticesIntegrator(
            temp_project, instruction_db, template_manager, context_detector
        )

        analysis = {
            "has_ai_tools": False,
            "security_level": "basic",
            "technologies": ["react", "typescript"],
        }

        recommendations = integrator._recommend_ai_instructions(analysis)

        # Should include frontend-specific instructions
        frontend_instructions = [
            "automated_accessibility_audits",
            "frontend_performance_optimization",
            "intelligent_component_generation",
        ]

        for instruction in frontend_instructions:
            assert instruction in recommendations

    def test_recommend_templates_basic(self, temp_project, mock_services):
        """Test basic template recommendations"""
        instruction_db, template_manager, context_detector = mock_services

        integrator = AIBestPracticesIntegrator(
            temp_project, instruction_db, template_manager, context_detector
        )

        analysis = {
            "has_ai_tools": False,
            "security_level": "basic",
            "technologies": [],
        }

        recommendations = integrator._recommend_templates(analysis)

        # Should always recommend prompt engineering template
        assert "ai-prompt-engineering" in recommendations

    def test_recommend_templates_comprehensive(self, temp_project, mock_services):
        """Test comprehensive template recommendations"""
        instruction_db, template_manager, context_detector = mock_services

        integrator = AIBestPracticesIntegrator(
            temp_project, instruction_db, template_manager, context_detector
        )

        analysis = {
            "has_ai_tools": True,
            "security_level": "enterprise",
            "technologies": ["react", "node", "docker", "kubernetes"],
        }

        recommendations = integrator._recommend_templates(analysis)

        # Should recommend comprehensive framework
        assert "ai-comprehensive-framework" in recommendations
        assert "ai-security-framework" in recommendations

    def test_assess_integration_priority(self, temp_project, mock_services):
        """Test integration priority assessment"""
        instruction_db, template_manager, context_detector = mock_services

        integrator = AIBestPracticesIntegrator(
            temp_project, instruction_db, template_manager, context_detector
        )

        # Test high priority
        high_priority_analysis = {
            "has_ai_tools": True,
            "security_level": "enterprise",
            "technologies": ["react", "node", "docker", "kubernetes", "python", "java"],
        }
        assert integrator._assess_integration_priority(high_priority_analysis) == "high"

        # Test medium priority
        medium_priority_analysis = {
            "has_ai_tools": False,
            "security_level": "intermediate",
            "technologies": ["react", "node", "docker"],
        }
        assert (
            integrator._assess_integration_priority(medium_priority_analysis)
            == "medium"
        )

        # Test low priority
        low_priority_analysis = {
            "has_ai_tools": False,
            "security_level": "basic",
            "technologies": ["html"],
        }
        assert integrator._assess_integration_priority(low_priority_analysis) == "low"

    @patch("agentspec.core.ai_integrator.logger")
    def test_analyze_project_success(self, mock_logger, temp_project, mock_services):
        """Test successful project analysis"""
        instruction_db, template_manager, context_detector = mock_services

        # Mock context detection
        mock_context = Mock()
        mock_context.project_type.value = "web_application"
        mock_framework = Mock()
        mock_framework.name = "React"
        mock_context.technology_stack.frameworks = [mock_framework]
        mock_language = Mock()
        mock_language.value = "JavaScript"
        mock_context.technology_stack.languages = [mock_language]
        context_detector.analyze_project.return_value = mock_context

        integrator = AIBestPracticesIntegrator(
            temp_project, instruction_db, template_manager, context_detector
        )

        analysis = integrator.analyze_project()

        assert analysis["project_type"] == "web_application"
        assert "React" in analysis["technologies"]
        assert "JavaScript" in analysis["technologies"]
        assert "recommended_ai_instructions" in analysis
        assert "recommended_templates" in analysis
        assert "integration_priority" in analysis

    def test_generate_integration_plan(self, temp_project, mock_services):
        """Test integration plan generation"""
        instruction_db, template_manager, context_detector = mock_services

        integrator = AIBestPracticesIntegrator(
            temp_project, instruction_db, template_manager, context_detector
        )

        analysis = {
            "has_ai_tools": True,
            "security_level": "intermediate",
            "technologies": ["react", "node"],
        }

        plan = integrator.generate_integration_plan(analysis)

        assert "phases" in plan
        assert "estimated_duration" in plan
        assert "prerequisites" in plan
        assert "success_metrics" in plan
        assert len(plan["phases"]) >= 1  # Should have at least foundation phase

    def test_create_integration_files(self, temp_project, mock_services):
        """Test integration file creation"""
        instruction_db, template_manager, context_detector = mock_services

        integrator = AIBestPracticesIntegrator(
            temp_project, instruction_db, template_manager, context_detector
        )

        analysis = {
            "project_type": "web_application",
            "technologies": ["react", "typescript"],
            "security_level": "intermediate",
            "has_ai_tools": True,
            "integration_priority": "high",
            "recommended_ai_instructions": ["human_in_the_loop_architect"],
            "recommended_templates": ["ai-comprehensive-framework"],
        }

        plan = {
            "phases": [
                {
                    "name": "Foundation Setup",
                    "duration": "1 week",
                    "instructions": ["human_in_the_loop_architect"],
                    "tasks": ["Set up scratchpad"],
                }
            ],
            "estimated_duration": "2 weeks",
            "prerequisites": ["AgentSpec installed"],
            "success_metrics": ["Zero vulnerabilities"],
        }

        integrator.create_integration_files(analysis, plan)

        # Check that files were created
        agentspec_dir = temp_project / ".agentspec"
        assert agentspec_dir.exists()
        assert (agentspec_dir / "ai_config.json").exists()
        assert (agentspec_dir / "ai_scratchpad.md").exists()
        assert (agentspec_dir / "ai_integration_plan.md").exists()

        # Check AI config content
        with open(agentspec_dir / "ai_config.json") as f:
            config = json.load(f)

        assert config["ai_assistance"]["enabled"] is True
        assert config["security_guardrails"]["enabled"] is True
        assert config["security_guardrails"]["implementation_level"] == "intermediate"
