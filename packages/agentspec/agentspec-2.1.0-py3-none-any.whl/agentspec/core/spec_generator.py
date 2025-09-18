"""
Specification Generator

This module provides the SpecGenerator class for generating AgentSpec specifications
from instructions and templates with support for context-aware customization.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..utils.config import ConfigManager
from .context_detector import ContextDetector, ProjectContext
from .instruction_database import Instruction, InstructionDatabase, ValidationResult
from .template_manager import Template, TemplateManager

logger = logging.getLogger(__name__)


@dataclass
class SpecConfig:
    """Configuration for specification generation"""

    selected_tags: List[str] = field(default_factory=list)
    selected_instructions: List[str] = field(default_factory=list)
    excluded_instructions: List[str] = field(default_factory=list)
    template_id: Optional[str] = None
    template_parameters: Dict[str, Any] = field(default_factory=dict)
    project_context: Optional[ProjectContext] = None
    output_format: str = "markdown"  # markdown, json, yaml
    include_metadata: bool = True
    language: str = "en"
    custom_sections: Dict[str, str] = field(default_factory=dict)


@dataclass
class GeneratedSpec:
    """Generated specification with metadata"""

    content: str
    format: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    instructions_used: List[str] = field(default_factory=list)
    template_used: Optional[str] = None
    generation_timestamp: datetime = field(default_factory=datetime.now)
    validation_result: Optional[ValidationResult] = None


class SpecGenerator:
    """
    Generates AgentSpec specifications from instructions and templates.

    This class provides functionality to:
    - Generate specifications from selected tags and instructions
    - Apply templates for common project types
    - Validate generated specifications
    - Export specifications in multiple formats
    """

    def __init__(
        self,
        instruction_db: Optional[InstructionDatabase] = None,
        template_manager: Optional[TemplateManager] = None,
        context_detector: Optional[ContextDetector] = None,
        config_manager: Optional[ConfigManager] = None,
    ):
        """
        Initialize the specification generator.

        Args:
            instruction_db: InstructionDatabase instance
            template_manager: TemplateManager instance
            context_detector: ContextDetector instance
            config_manager: ConfigManager instance
        """
        self.instruction_db = instruction_db or InstructionDatabase()
        self.template_manager = template_manager or TemplateManager()
        self.context_detector = context_detector or ContextDetector()
        self.config_manager = config_manager or ConfigManager()

        # Load configuration
        self.config = self.config_manager.load_config()

        # Load instructions and templates
        self.instruction_db.load_instructions()
        self.template_manager.load_templates()

    def generate_spec(self, config: SpecConfig) -> GeneratedSpec:
        """
        Generate a specification based on the provided configuration.

        Args:
            config: SpecConfig with generation parameters

        Returns:
            GeneratedSpec with the generated specification

        Raises:
            ValueError: If configuration is invalid
        """
        logger.info(
            f"Generating specification with {len(config.selected_tags)} tags and "
            f"{len(config.selected_instructions)} instructions"
        )

        # Validate configuration
        self._validate_config(config)

        # Apply template if specified
        if config.template_id:
            config = self._apply_template_to_config(config)

        # Get instructions based on tags and explicit selections
        instructions = self._get_instructions_for_config(config)

        # Filter instructions based on project context
        if config.project_context:
            instructions = self._filter_instructions_by_context(
                instructions, config.project_context
            )

        # Apply parameter substitution
        instructions = self._apply_parameter_substitution(instructions, config)

        # Generate specification content
        content = self._generate_spec_content(instructions, config)

        # Create generated spec
        spec = GeneratedSpec(
            content=content,
            format=config.output_format,
            instructions_used=[inst.id for inst in instructions],
            template_used=config.template_id,
            metadata={
                "tags": config.selected_tags,
                "instruction_count": len(instructions),
                "language": config.language,
                "project_context": (
                    config.project_context.project_type.value
                    if config.project_context
                    else None
                ),
            },
        )

        # Validate generated specification
        spec.validation_result = self.validate_spec(spec)

        logger.info(f"Generated specification with {len(instructions)} instructions")
        return spec

    def apply_template(
        self, template: Template, context: Optional[ProjectContext] = None
    ) -> SpecConfig:
        """
        Apply a template to create a specification configuration.

        Args:
            template: Template to apply
            context: Optional project context for customization

        Returns:
            SpecConfig based on the template
        """
        logger.info(f"Applying template: {template.name}")

        config = SpecConfig(
            selected_tags=template.default_tags.copy(),
            selected_instructions=template.required_instructions.copy(),
            excluded_instructions=template.excluded_instructions.copy(),
            template_id=template.id,
            project_context=context,
        )

        # Add optional instructions based on context
        if context:
            # Get context-specific suggestions
            suggestions = self.context_detector.suggest_instructions(context)

            # Add high-confidence suggestions that match template's optional instructions
            for suggestion in suggestions:
                if (
                    suggestion.confidence > 0.7
                    and suggestion.instruction_id in template.optional_instructions
                    and suggestion.instruction_id not in config.selected_instructions
                ):
                    config.selected_instructions.append(suggestion.instruction_id)

        # Apply template parameters
        if template.parameters:
            for param_name, param in template.parameters.items():
                if param.default is not None:
                    config.template_parameters[param_name] = param.default

        return config

    def validate_spec(self, spec: GeneratedSpec) -> ValidationResult:
        """
        Validate a generated specification.

        Args:
            spec: Generated specification to validate

        Returns:
            ValidationResult with validation status and any errors/warnings
        """
        errors = []
        warnings = []

        # Basic content validation
        if not spec.content or len(spec.content.strip()) < 100:
            errors.append("Specification content is too short (minimum 100 characters)")

        # Check for required sections
        required_sections = [
            "# AgentSpec",
            "## IMPLEMENTATION FRAMEWORK",
            "## QUALITY GATES",
        ]
        for section in required_sections:
            if section not in spec.content:
                errors.append(f"Missing required section: {section}")

        # Validate instruction references
        if spec.instructions_used:
            for instruction_id in spec.instructions_used:
                instruction = self.instruction_db.get_instruction(instruction_id)
                if not instruction:
                    warnings.append(
                        f"Referenced instruction not found: {instruction_id}"
                    )

        # Format-specific validation
        if spec.format == "json":
            try:
                json.loads(spec.content)
            except json.JSONDecodeError as e:
                errors.append(f"Invalid JSON format: {e}")

        # Check for conflicts in used instructions
        if len(spec.instructions_used) > 1:
            used_instructions = [
                self.instruction_db.get_instruction(inst_id)
                for inst_id in spec.instructions_used
            ]
            filtered_instructions = [
                inst for inst in used_instructions if inst is not None
            ]

            conflicts = self.instruction_db.detect_conflicts(
                filtered_instructions if filtered_instructions else None
            )
            for conflict in conflicts:
                if conflict.severity == "high":
                    errors.append(f"Instruction conflict: {conflict.description}")
                else:
                    warnings.append(
                        f"Potential instruction conflict: {conflict.description}"
                    )

        return ValidationResult(
            is_valid=len(errors) == 0, errors=errors, warnings=warnings
        )

    def export_spec(
        self, spec: GeneratedSpec, output_path: Optional[str] = None
    ) -> str:
        """
        Export a generated specification to file or return as string.

        Args:
            spec: Generated specification to export
            output_path: Optional file path to save the specification

        Returns:
            Specification content as string
        """
        content = spec.content

        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)

            logger.info(f"Exported specification to: {output_file}")

        return content

    def _validate_config(self, config: SpecConfig) -> None:
        """Validate specification configuration"""
        if (
            not config.selected_tags
            and not config.selected_instructions
            and not config.template_id
        ):
            raise ValueError("Must specify tags, instructions, or template")

        if config.output_format not in ["markdown", "json", "yaml"]:
            raise ValueError(f"Unsupported output format: {config.output_format}")

        # Validate template exists
        if config.template_id:
            template = self.template_manager.get_template(config.template_id)
            if not template:
                raise ValueError(f"Template not found: {config.template_id}")

    def _apply_template_to_config(self, config: SpecConfig) -> SpecConfig:
        """Apply template settings to configuration"""
        if config.template_id is None:
            return config
        template = self.template_manager.get_template(config.template_id)
        if not template:
            return config

        # Merge template settings with existing config
        if not config.selected_tags:
            config.selected_tags = template.default_tags.copy()
        else:
            # Add template tags that aren't already selected
            for tag in template.default_tags:
                if tag not in config.selected_tags:
                    config.selected_tags.append(tag)

        # Add required instructions
        for instruction_id in template.required_instructions:
            if instruction_id not in config.selected_instructions:
                config.selected_instructions.append(instruction_id)

        # Add excluded instructions
        for instruction_id in template.excluded_instructions:
            if instruction_id not in config.excluded_instructions:
                config.excluded_instructions.append(instruction_id)

        return config

    def _get_instructions_for_config(self, config: SpecConfig) -> List[Instruction]:
        """Get instructions based on configuration"""
        instructions = []
        instruction_ids = set()

        # Add always-included instructions from configuration
        always_include = self.config_manager.get(
            "agentspec.instructions.always_include", []
        )
        for instruction_id in always_include:
            if instruction_id not in instruction_ids:
                always_instruction = self.instruction_db.get_instruction(instruction_id)
                if always_instruction is not None:
                    instructions.append(always_instruction)
                    instruction_ids.add(instruction_id)
                else:
                    logger.warning(
                        f"Always-include instruction not found: {instruction_id}"
                    )

        # Get instructions by tags
        if config.selected_tags:
            tag_instructions = self.instruction_db.get_by_tags(config.selected_tags)
            for instruction in tag_instructions:
                if instruction.id not in instruction_ids:
                    instructions.append(instruction)
                    instruction_ids.add(instruction.id)

        # Add explicitly selected instructions
        for instruction_id in config.selected_instructions:
            if instruction_id not in instruction_ids:
                selected_instruction = self.instruction_db.get_instruction(
                    instruction_id
                )
                if selected_instruction is not None:
                    instructions.append(selected_instruction)
                    instruction_ids.add(instruction_id)

        # Remove excluded instructions (but preserve always-included ones)
        always_include = self.config_manager.get(
            "agentspec.instructions.always_include", []
        )
        if config.excluded_instructions:
            instructions = [
                inst
                for inst in instructions
                if inst.id not in config.excluded_instructions
                or inst.id in always_include
            ]

        # Resolve dependencies
        if instructions:
            instruction_ids_list = [inst.id for inst in instructions]
            ordered_ids = self.instruction_db.resolve_dependencies(instruction_ids_list)

            # Reorder instructions based on dependency resolution
            id_to_instruction = {inst.id: inst for inst in instructions}
            instructions = [
                id_to_instruction[inst_id]
                for inst_id in ordered_ids
                if inst_id in id_to_instruction
            ]

        return instructions

    def _filter_instructions_by_context(
        self, instructions: List[Instruction], context: ProjectContext
    ) -> List[Instruction]:
        """Filter instructions based on project context conditions"""
        filtered_instructions = []

        for instruction in instructions:
            if not instruction.conditions:
                # No conditions, include instruction
                filtered_instructions.append(instruction)
                continue

            # Evaluate all conditions
            include_instruction = True
            for condition in instruction.conditions:
                if not self._evaluate_instruction_condition(condition, context):
                    include_instruction = False
                    break

            if include_instruction:
                filtered_instructions.append(instruction)

        return filtered_instructions

    def _evaluate_instruction_condition(
        self, condition: Any, context: ProjectContext
    ) -> bool:
        """Evaluate a single instruction condition against project context"""
        try:
            condition_type = getattr(condition, "type", None)
            condition_operator = getattr(condition, "operator", None)
            condition_value = getattr(condition, "value", None)

            if condition_type == "project_type":
                if condition_operator == "equals":
                    return context.project_type.value == condition_value
                elif condition_operator == "not_equals":
                    return context.project_type.value != condition_value

            elif condition_type == "technology":
                tech_names = [fw.name for fw in context.technology_stack.frameworks]
                tech_names.extend(
                    [lang.value for lang in context.technology_stack.languages]
                )

                if condition_operator == "equals":
                    return condition_value in tech_names if condition_value else False
                elif condition_operator == "not_equals":
                    return (
                        condition_value not in tech_names if condition_value else True
                    )
                elif condition_operator == "contains":
                    return (
                        any(condition_value in tech for tech in tech_names)
                        if condition_value
                        else False
                    )

            elif condition_type == "file_exists":
                if condition_value is None:
                    return False
                project_path = Path(context.project_path)
                file_path = project_path / condition_value

                if condition_operator == "equals":
                    return bool(file_path.exists())
                elif condition_operator == "not_equals":
                    return not bool(file_path.exists())

            elif condition_type == "dependency_exists":
                dep_names = [dep.name for dep in context.dependencies]

                if condition_operator == "equals":
                    return condition_value in dep_names if condition_value else False
                elif condition_operator == "not_equals":
                    return condition_value not in dep_names if condition_value else True
                elif condition_operator == "contains":
                    return (
                        any(condition_value in dep for dep in dep_names)
                        if condition_value
                        else False
                    )

        except Exception as e:
            logger.warning(f"Error evaluating condition: {e}")

        # Default to including instruction if evaluation fails or no condition matches
        return True

    def _apply_parameter_substitution(
        self, instructions: List[Instruction], config: SpecConfig
    ) -> List[Instruction]:
        """Apply parameter substitution to instruction content"""
        if not config.template_parameters and not config.project_context:
            return instructions

        # Build parameter context
        params = config.template_parameters.copy()

        if config.project_context:
            params.update(
                {
                    "project_name": Path(config.project_context.project_path).name,
                    "project_type": config.project_context.project_type.value,
                    "languages": [
                        lang.value
                        for lang in config.project_context.technology_stack.languages
                    ],
                    "frameworks": [
                        fw.name
                        for fw in config.project_context.technology_stack.frameworks
                    ],
                }
            )

        # Apply substitution to each instruction
        substituted_instructions = []
        for instruction in instructions:
            # Create a copy to avoid modifying the original
            import copy

            new_instruction = copy.deepcopy(instruction)

            # Apply parameter substitution to content
            content = new_instruction.content
            for param_name, param_value in params.items():
                placeholder = f"{{{param_name}}}"
                if isinstance(param_value, list):
                    param_value = ", ".join(str(v) for v in param_value)
                content = content.replace(placeholder, str(param_value))

            new_instruction.content = content
            substituted_instructions.append(new_instruction)

        return substituted_instructions

    def _generate_spec_content(
        self, instructions: List[Instruction], config: SpecConfig
    ) -> str:
        """Generate the specification content based on format"""
        if config.output_format == "json":
            return self._generate_json_spec(instructions, config)
        elif config.output_format == "yaml":
            return self._generate_yaml_spec(instructions, config)
        else:
            return self._generate_markdown_spec(instructions, config)

    def _generate_markdown_spec(
        self, instructions: List[Instruction], config: SpecConfig
    ) -> str:
        """Generate specification in Markdown format"""
        content = []

        # Header
        content.append("# AgentSpec - Project Specification")
        content.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        if config.selected_tags:
            content.append(f"Selected tags: {', '.join(config.selected_tags)}")

        content.append(f"Total instructions: {len(instructions)}")

        if config.template_id:
            template = self.template_manager.get_template(config.template_id)
            if template:
                content.append(f"Template: {template.name}")

        if config.project_context:
            content.append(f"Project type: {config.project_context.project_type.value}")

        content.append("\n" + "=" * 80 + "\n")

        # Group instructions by category
        categories: Dict[str, List[Instruction]] = {}
        for instruction in instructions:
            category = (
                instruction.metadata.category if instruction.metadata else "general"
            )
            if category not in categories:
                categories[category] = []
            categories[category].append(instruction)

        # Generate content by categories
        for category, category_instructions in sorted(categories.items()):
            content.append(f"## {category.upper().replace('_', ' ')} GUIDELINES")
            content.append("")

            for i, instruction in enumerate(category_instructions, 1):
                content.append(f"### {i}. {instruction.id.replace('_', ' ').title()}")
                content.append(f"**Tags**: {', '.join(instruction.tags)}")

                if instruction.metadata and instruction.metadata.priority:
                    content.append(f"**Priority**: {instruction.metadata.priority}")

                content.append("")
                content.append(instruction.content)
                content.append("")

        # Add custom sections
        for section_name, section_content in config.custom_sections.items():
            content.append(f"## {section_name.upper()}")
            content.append("")
            content.append(section_content)
            content.append("")

        # Add implementation framework
        content.extend(self._get_implementation_framework())

        # Add metadata section if requested
        if config.include_metadata:
            content.extend(self._get_metadata_section(instructions, config))

        return "\n".join(content)

    def _generate_json_spec(
        self, instructions: List[Instruction], config: SpecConfig
    ) -> str:
        """Generate specification in JSON format"""
        spec_data: Dict[str, Any] = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "tags": config.selected_tags,
                "instruction_count": len(instructions),
                "template": config.template_id,
                "language": config.language,
            },
            "instructions": [],
        }

        for instruction in instructions:
            inst_data: Dict[str, Any] = {
                "id": instruction.id,
                "version": instruction.version,
                "tags": instruction.tags,
                "content": instruction.content,
            }

            if instruction.metadata:
                inst_data["metadata"] = {
                    "category": instruction.metadata.category,
                    "priority": instruction.metadata.priority,
                }

            spec_data["instructions"].append(inst_data)

        return json.dumps(spec_data, indent=2, ensure_ascii=False)

    def _generate_yaml_spec(
        self, instructions: List[Instruction], config: SpecConfig
    ) -> str:
        """Generate specification in YAML format"""
        try:
            import yaml
        except ImportError:
            raise ImportError("PyYAML is required for YAML output format")

        spec_data: Dict[str, Any] = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "tags": config.selected_tags,
                "instruction_count": len(instructions),
                "template": config.template_id,
                "language": config.language,
            },
            "instructions": [],
        }

        for instruction in instructions:
            inst_data: Dict[str, Any] = {
                "id": instruction.id,
                "version": instruction.version,
                "tags": instruction.tags,
                "content": instruction.content,
            }

            if instruction.metadata:
                inst_data["metadata"] = {
                    "category": instruction.metadata.category,
                    "priority": instruction.metadata.priority,
                }

            spec_data["instructions"].append(inst_data)

        result: str = yaml.dump(spec_data, default_flow_style=False, allow_unicode=True)
        return result

    def _get_implementation_framework(self) -> List[str]:
        """Get the standard implementation framework section"""
        return [
            "## IMPLEMENTATION FRAMEWORK",
            "",
            "### Pre-Development Checklist",
            "- [ ] Analyze codebase thoroughly",
            "- [ ] Define clear exit criteria",
            "- [ ] Review project context for lessons learned",
            "",
            "### During Implementation",
            "- [ ] Run tests continuously",
            "- [ ] Validate integration points",
            "- [ ] Document any deviations from plan",
            "",
            "### Post-Task Validation",
            "- [ ] Run complete test suite (`./test`)",
            "- [ ] Check for linting/build errors",
            "- [ ] Validate browser functionality",
            "- [ ] Update documentation",
            "- [ ] Update project context with lessons learned",
            "",
            "## QUALITY GATES",
            "",
            "Every task must pass these quality gates:",
            "",
            "1. **Zero Errors**: No linting, compilation, or build errors",
            "2. **Test Coverage**: All new code covered by tests",
            "3. **Documentation**: Public APIs documented",
            "4. **Security**: Security best practices followed",
            "5. **Performance**: No performance regressions",
            "",
            "## VALIDATION COMMANDS",
            "",
            "```bash",
            "# Run comprehensive validation",
            "bash scripts/validate.sh",
            "",
            "# Run all tests",
            "./test",
            "",
            "# Generate compliance report",
            "bash scripts/validate.sh --report",
            "```",
            "",
            "---",
            "*Generated by AgentSpec - Specification-Driven Development for AI Agents*",
        ]

    def _get_metadata_section(
        self, instructions: List[Instruction], config: SpecConfig
    ) -> List[str]:
        """Get metadata section for the specification"""
        content = [
            "## SPECIFICATION METADATA",
            "",
            f"- **Generation Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"- **Instructions Used**: {len(instructions)}",
            f"- **Output Format**: {config.output_format}",
            f"- **Language**: {config.language}",
        ]

        if config.template_id:
            template = self.template_manager.get_template(config.template_id)
            if template:
                content.append(f"- **Template**: {template.name} (v{template.version})")

        if config.project_context:
            content.extend(
                [
                    f"- **Project Type**: {config.project_context.project_type.value}",
                    f"- **Confidence Score**: {config.project_context.confidence_score:.2f}",
                ]
            )

        content.append("")
        return content
