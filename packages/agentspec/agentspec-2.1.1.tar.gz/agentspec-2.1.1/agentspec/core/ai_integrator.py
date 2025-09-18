"""
AI Best Practices Integrator

This module provides functionality to integrate AI best practices into existing
AgentSpec projects by analyzing their current setup and recommending appropriate
AI instructions and templates.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from .context_detector import ContextDetector
from .instruction_database import InstructionDatabase
from .template_manager import TemplateManager

logger = logging.getLogger(__name__)


class AIBestPracticesIntegrator:
    """Integrates AI best practices into existing AgentSpec projects"""

    def __init__(
        self,
        project_path: Path,
        instruction_db: InstructionDatabase,
        template_manager: TemplateManager,
        context_detector: ContextDetector,
    ):
        self.project_path = project_path
        self.agentspec_path = project_path / ".agentspec"
        self.instruction_db = instruction_db
        self.template_manager = template_manager
        self.context_detector = context_detector

    def analyze_project(self) -> Dict[str, Any]:
        """Analyze the project to determine appropriate AI integrations"""
        analysis: Dict[str, Any] = {
            "project_type": "unknown",
            "technologies": [],
            "has_ai_tools": False,
            "security_level": "basic",
            "team_size": "unknown",
            "current_ai_instructions": [],
            "recommended_ai_instructions": [],
            "recommended_templates": [],
            "integration_priority": "medium",
        }

        # Detect project context
        try:
            context = self.context_detector.analyze_project(str(self.project_path))
            analysis["project_type"] = context.project_type.value
            analysis["technologies"] = [
                fw.name for fw in context.technology_stack.frameworks
            ]
            analysis["technologies"].extend(
                [lang.value for lang in context.technology_stack.languages]
            )
        except Exception as e:
            logger.warning(f"Could not detect project context: {e}")

        # Check for existing AI tool usage
        analysis["has_ai_tools"] = self._detect_ai_tools()

        # Analyze existing AgentSpec configuration
        if self.agentspec_path.exists():
            analysis.update(self._analyze_existing_config())

        # Determine security requirements
        analysis["security_level"] = self._assess_security_requirements(analysis)

        # Generate recommendations
        analysis["recommended_ai_instructions"] = self._recommend_ai_instructions(
            analysis
        )
        analysis["recommended_templates"] = self._recommend_templates(analysis)
        analysis["integration_priority"] = self._assess_integration_priority(analysis)

        return analysis

    def _detect_ai_tools(self) -> bool:
        """Detect if the project already uses AI development tools"""
        ai_indicators = [
            ".copilot",
            ".cursor",
            "copilot.yml",
            ".github/copilot",
            "ai-config.json",
            ".ai",
            "prompts/",
            ".prompts/",
        ]

        for indicator in ai_indicators:
            if (self.project_path / indicator).exists():
                return True

        # Check for AI-related dependencies
        package_files = [
            "package.json",
            "requirements.txt",
            "pyproject.toml",
            "Gemfile",
        ]
        ai_packages = ["@copilot", "openai", "anthropic", "langchain", "llamaindex"]

        for package_file in package_files:
            file_path = self.project_path / package_file
            if file_path.exists():
                try:
                    content = file_path.read_text()
                    if any(pkg in content for pkg in ai_packages):
                        return True
                except (OSError, UnicodeDecodeError) as e:
                    logger.debug(f"Could not read {file_path}: {e}")
                    continue

        return False

    def _analyze_existing_config(self) -> Dict[str, Any]:
        """Analyze existing AgentSpec configuration"""
        config: Dict[str, Any] = {}

        # Check for existing AI instructions
        current_ai_instructions: List[str] = []

        # Look for project spec
        spec_files = list(self.agentspec_path.glob("*spec*.md"))
        if spec_files:
            try:
                spec_content = spec_files[0].read_text()
                # Simple heuristic to detect AI-related content
                ai_keywords = ["ai", "copilot", "assistant", "prompt", "llm", "gpt"]
                if any(keyword in spec_content.lower() for keyword in ai_keywords):
                    current_ai_instructions.append("basic_ai_usage")
            except (OSError, UnicodeDecodeError) as e:
                logger.debug(f"Could not read spec file {spec_files[0]}: {e}")

        config["current_ai_instructions"] = current_ai_instructions
        return config

    def _assess_security_requirements(self, analysis: Dict) -> str:
        """Assess the required security level based on project characteristics"""
        # Check for enterprise indicators
        enterprise_indicators = [
            "enterprise" in str(self.project_path).lower(),
            (self.project_path / "SECURITY.md").exists(),
            (self.project_path / "COMPLIANCE.md").exists(),
            "healthcare" in analysis.get("project_type", "").lower(),
            "finance" in analysis.get("project_type", "").lower(),
            "banking" in analysis.get("project_type", "").lower(),
        ]

        if any(enterprise_indicators):
            return "enterprise"

        # Check for security-focused technologies
        security_techs = ["security", "auth", "oauth", "jwt", "encryption", "crypto"]
        if any(tech in security_techs for tech in analysis.get("technologies", [])):
            return "intermediate"

        return "basic"

    def _recommend_ai_instructions(self, analysis: Dict) -> List[str]:
        """Recommend AI instructions based on project analysis"""
        recommendations = []

        # Always recommend foundational AI instructions
        foundational = [
            "human_in_the_loop_architect",
            "rich_scratchpad_context",
            "continuous_validation_loop",
            "avoid_vibe_coding",
            "never_commit_unknown_code",
        ]
        recommendations.extend(foundational)

        # Add prompt engineering if AI tools detected
        if analysis["has_ai_tools"]:
            prompt_engineering = [
                "clarity_context_constraints",
                "chain_of_thought_prompting",
                "decomposition_prompting",
            ]
            recommendations.extend(prompt_engineering)

        # Add security based on security level
        if analysis["security_level"] in ["intermediate", "enterprise"]:
            security = [
                "productivity_risk_paradox",
                "validation_guardrails",
                "regulatory_compliance_guardrails",
            ]
            recommendations.extend(security)

        if analysis["security_level"] == "enterprise":
            enterprise_security = [
                "enterprise_guardrail_implementation",
                "alignment_guardrails",
            ]
            recommendations.extend(enterprise_security)

        # Add domain-specific recommendations
        technologies = analysis.get("technologies", [])

        if any(
            tech.lower() in ["react", "vue", "angular", "frontend"]
            for tech in technologies
        ):
            frontend = [
                "automated_accessibility_audits",
                "frontend_performance_optimization",
                "intelligent_component_generation",
            ]
            recommendations.extend(frontend)

        if any(
            tech.lower() in ["node", "python", "java", "backend", "api"]
            for tech in technologies
        ):
            backend = [
                "ai_driven_tdd",
                "api_data_model_generation",
                "backend_incremental_complexity",
            ]
            recommendations.extend(backend)

        if any(
            tech.lower() in ["docker", "kubernetes", "ci", "cd", "devops"]
            for tech in technologies
        ):
            devops = [
                "ai_enhanced_ci_cd",
                "proactive_vulnerability_management",
                "intelligent_monitoring_observability",
            ]
            recommendations.extend(devops)

        return list(set(recommendations))  # Remove duplicates

    def _recommend_templates(self, analysis: Dict) -> List[str]:
        """Recommend templates based on project analysis"""
        recommendations = []

        # Always recommend prompt engineering template
        recommendations.append("ai-prompt-engineering")

        # Recommend security framework for intermediate+ security
        if analysis["security_level"] in ["intermediate", "enterprise"]:
            recommendations.append("ai-security-framework")

        # Recommend comprehensive framework for complex projects
        if (
            len(analysis.get("technologies", [])) > 3
            or analysis["has_ai_tools"]
            or analysis["security_level"] == "enterprise"
        ):
            recommendations.append("ai-comprehensive-framework")

        return recommendations

    def _assess_integration_priority(self, analysis: Dict) -> str:
        """Assess the priority level for AI integration"""
        high_priority_indicators = [
            analysis["has_ai_tools"],
            analysis["security_level"] == "enterprise",
            len(analysis.get("technologies", [])) > 5,
        ]

        if any(high_priority_indicators):
            return "high"

        medium_priority_indicators = [
            analysis["security_level"] == "intermediate",
            len(analysis.get("technologies", [])) > 2,
        ]

        if any(medium_priority_indicators):
            return "medium"

        return "low"

    def generate_integration_plan(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a detailed integration plan"""
        plan: Dict[str, Any] = {
            "phases": [],
            "estimated_duration": "2-4 weeks",
            "prerequisites": [],
            "success_metrics": [],
        }

        # Phase 1: Foundation
        foundation_phase = {
            "name": "Foundation Setup",
            "duration": "1 week",
            "instructions": [
                "human_in_the_loop_architect",
                "rich_scratchpad_context",
                "never_commit_unknown_code",
            ],
            "tasks": [
                "Set up rich scratchpad document",
                "Establish AI collaboration principles",
                "Train team on basic AI best practices",
            ],
        }
        plan["phases"].append(foundation_phase)

        # Phase 2: Security (if needed)
        if analysis["security_level"] in ["intermediate", "enterprise"]:
            security_phase = {
                "name": "Security Implementation",
                "duration": "1-2 weeks",
                "instructions": [
                    "productivity_risk_paradox",
                    "validation_guardrails",
                    "regulatory_compliance_guardrails",
                ],
                "tasks": [
                    "Implement security guardrails",
                    "Set up compliance monitoring",
                    "Configure validation pipelines",
                ],
            }
            plan["phases"].append(security_phase)

        # Phase 3: Domain Specialization
        domain_instructions = []
        technologies = analysis.get("technologies", [])

        if any(
            tech.lower() in ["react", "vue", "angular", "frontend"]
            for tech in technologies
        ):
            domain_instructions.extend(
                ["automated_accessibility_audits", "frontend_performance_optimization"]
            )

        if any(
            tech.lower() in ["node", "python", "java", "backend"]
            for tech in technologies
        ):
            domain_instructions.extend(["ai_driven_tdd", "api_data_model_generation"])

        if domain_instructions:
            domain_phase = {
                "name": "Domain Specialization",
                "duration": "1-2 weeks",
                "instructions": domain_instructions,
                "tasks": [
                    "Implement domain-specific AI practices",
                    "Set up specialized validation",
                    "Train team on domain techniques",
                ],
            }
            plan["phases"].append(domain_phase)

        # Set overall duration based on phases
        total_weeks = sum(
            int(phase["duration"].split()[0].split("-")[-1])
            for phase in plan["phases"]
            if isinstance(phase, dict) and "duration" in phase
        )
        plan["estimated_duration"] = f"{total_weeks} weeks"

        # Prerequisites
        plan["prerequisites"] = [
            "AgentSpec v1.0+ installed",
            "Team familiar with basic AI tools",
            "Project has established development workflow",
        ]

        if analysis["security_level"] == "enterprise":
            plan["prerequisites"].extend(
                [
                    "Security team approval",
                    "Compliance requirements documented",
                    "Identity provider integration available",
                ]
            )

        # Success metrics
        plan["success_metrics"] = [
            "Zero AI-generated security vulnerabilities in production",
            "Improved code quality metrics",
            "Reduced time-to-delivery for new features",
            "High developer satisfaction with AI tools",
        ]

        return plan

    def create_integration_files(self, analysis: Dict, plan: Dict) -> None:
        """Create the necessary files for AI integration"""
        # Ensure .agentspec directory exists
        self.agentspec_path.mkdir(exist_ok=True)

        # Create AI configuration file
        ai_config = {
            "ai_assistance": {
                "enabled": True,
                "collaboration_mode": "peer_programmer",
                "context_management": {
                    "rich_scratchpad_enabled": True,
                    "scratchpad_path": ".agentspec/ai_scratchpad.md",
                },
                "validation_framework": {
                    "continuous_validation": True,
                    "zero_tolerance_policy": True,
                },
            },
            "security_guardrails": {
                "enabled": analysis["security_level"] != "basic",
                "implementation_level": analysis["security_level"],
            },
            "prompt_engineering": {
                "default_technique": "chain_of_thought",
                "complexity_handling": "incremental",
            },
        }

        config_path = self.agentspec_path / "ai_config.json"
        with open(config_path, "w") as f:
            json.dump(ai_config, f, indent=2)

        logger.info(f"Created AI configuration: {config_path}")

        # Create rich scratchpad template
        scratchpad_content = f"""# AI Development Scratchpad

## Project Context
- **Project**: {self.project_path.name}
- **Technologies**: {', '.join(analysis.get('technologies', []))}
- **Security Level**: {analysis['security_level']}
- **AI Tools**: {'Detected' if analysis['has_ai_tools'] else 'Not detected'}

## Current Session Context
<!-- Update this section at the start of each AI session -->

### Objective
<!-- What are you trying to accomplish? -->

### Context Gathered
<!-- Key information discovered during analysis -->

### Changes Made
<!-- Step-by-step record of changes -->

### Issues Encountered
<!-- Problems found and solutions applied -->

### Next Steps
<!-- What needs to be done next -->

## Prompt Library
<!-- Store successful prompts for reuse -->

### Code Generation Prompts
<!-- Effective prompts for generating code -->

### Review and Debugging Prompts
<!-- Prompts for code review and debugging -->

### Architecture and Design Prompts
<!-- Prompts for architectural discussions -->

## Lessons Learned
<!-- Key insights and best practices discovered -->

## Validation Checklist
- [ ] Code compiles without errors
- [ ] All tests pass
- [ ] Security scan clean
- [ ] Performance acceptable
- [ ] Documentation updated
"""

        scratchpad_path = self.agentspec_path / "ai_scratchpad.md"
        with open(scratchpad_path, "w") as f:
            f.write(scratchpad_content)

        logger.info(f"Created AI scratchpad: {scratchpad_path}")

        # Create integration plan document
        plan_content = f"""# AI Best Practices Integration Plan

## Project Analysis
- **Project Type**: {analysis['project_type']}
- **Technologies**: {', '.join(analysis.get('technologies', []))}
- **Security Level**: {analysis['security_level']}
- **AI Tools Present**: {analysis['has_ai_tools']}
- **Integration Priority**: {analysis['integration_priority']}

## Recommended Instructions
{chr(10).join(f"- {instruction}" for instruction in analysis['recommended_ai_instructions'])}

## Recommended Templates
{chr(10).join(f"- {template}" for template in analysis['recommended_templates'])}

## Implementation Phases

"""

        for i, phase in enumerate(plan["phases"], 1):
            plan_content += f"""### Phase {i}: {phase['name']}
**Duration**: {phase['duration']}

**Instructions to Implement**:
{chr(10).join(f"- {instruction}" for instruction in phase['instructions'])}

**Tasks**:
{chr(10).join(f"- {task}" for task in phase['tasks'])}

"""

        plan_content += f"""## Prerequisites
{chr(10).join(f"- {prereq}" for prereq in plan['prerequisites'])}

## Success Metrics
{chr(10).join(f"- {metric}" for metric in plan['success_metrics'])}

## Estimated Duration
{plan['estimated_duration']}

## Next Steps
1. Review this integration plan with your team
2. Ensure all prerequisites are met
3. Begin with Phase 1: Foundation Setup
4. Generate AgentSpec specifications using recommended templates
5. Implement instructions phase by phase
6. Monitor success metrics and adjust as needed

## Commands to Run

```bash
# Generate comprehensive AI specification
agentspec generate --template ai-comprehensive-framework --output ai-development-spec.md

# Generate security-focused specification (if enterprise level)
agentspec generate --template ai-security-framework --output ai-security-spec.md

# Generate domain-specific specifications as needed
agentspec generate --tags ai-frontend,accessibility --output ai-frontend-spec.md
agentspec generate --tags ai-backend,tdd,api --output ai-backend-spec.md
agentspec generate --tags ai-devops,ci-cd,monitoring --output ai-devops-spec.md
```
"""

        plan_path = self.agentspec_path / "ai_integration_plan.md"
        with open(plan_path, "w") as f:
            f.write(plan_content)

        logger.info(f"Created integration plan: {plan_path}")
