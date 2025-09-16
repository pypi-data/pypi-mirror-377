"""
Template Management

This module provides the TemplateManager class for loading, validating,
and managing AgentSpec templates for different project types.
"""

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

try:
    import jsonschema
    from jsonschema import ValidationError as JsonSchemaValidationError

    HAS_JSONSCHEMA = True
except ImportError:
    jsonschema = None  # type: ignore
    JsonSchemaValidationError = Exception  # type: ignore
    HAS_JSONSCHEMA = False

logger = logging.getLogger(__name__)


@dataclass
class TemplateCondition:
    """Represents a condition for template recommendation"""

    type: str  # file_exists, dependency_exists, project_structure, technology_detected
    value: str
    operator: str  # equals, contains, matches, not_equals, exists, not_exists
    weight: float = 1.0


@dataclass
class TemplateParameter:
    """Represents a parameter for template customization"""

    name: str
    type: str  # string, number, boolean, array, object
    default: Any = None
    description: str = ""
    required: bool = False
    options: Optional[List[Any]] = None


@dataclass
class TemplateInheritance:
    """Represents template inheritance configuration"""

    parent: str
    override_mode: str = "merge"  # merge, replace, extend


@dataclass
class TemplateMetadata:
    """Metadata for a template"""

    category: str
    complexity: str = "intermediate"  # beginner, intermediate, advanced
    author: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class Template:
    """Represents a specification template"""

    id: str
    name: str
    description: str
    version: str
    project_type: str
    technology_stack: List[str]
    default_tags: List[str]
    required_instructions: List[str] = field(default_factory=list)
    optional_instructions: List[str] = field(default_factory=list)
    excluded_instructions: List[str] = field(default_factory=list)
    parameters: Dict[str, TemplateParameter] = field(default_factory=dict)
    inheritance: Optional[TemplateInheritance] = None
    conditions: List[TemplateCondition] = field(default_factory=list)
    metadata: Optional[TemplateMetadata] = None
    _applied_parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TemplateRecommendation:
    """Represents a template recommendation with scoring"""

    template: Template
    confidence_score: float
    matching_conditions: List[str]
    reasons: List[str]


@dataclass
class ValidationResult:
    """Result of template validation"""

    is_valid: bool
    errors: List[str]
    warnings: List[str]


class TemplateManager:
    """
    Manages specification templates and presets for different project types.

    This class provides functionality to:
    - Load templates from JSON files
    - Validate template format and content
    - Recommend templates based on project context
    - Handle template inheritance and customization
    """

    def __init__(
        self,
        templates_path: Optional[Path] = None,
        schema_path: Optional[Path] = None,
    ):
        """
        Initialize the template manager.

        Args:
            templates_path: Path to the templates directory
            schema_path: Path to the template schema file
        """
        self.templates_path = (
            templates_path or Path(__file__).parent.parent / "data" / "templates"
        )
        self.schema_path = (
            schema_path
            or Path(__file__).parent.parent / "data" / "schemas" / "template.json"
        )

        self._templates: Dict[str, Template] = {}
        self._schema: Optional[Dict] = None
        self._loaded = False

        # Load schema
        self._load_schema()

    def _load_schema(self) -> None:
        """Load the JSON schema for template validation"""
        try:
            if self.schema_path.exists():
                with open(self.schema_path, "r", encoding="utf-8") as f:
                    self._schema = json.load(f)
                logger.debug(f"Loaded template schema from {self.schema_path}")
            else:
                logger.warning(f"Schema file not found: {self.schema_path}")
        except Exception as e:
            logger.error(f"Failed to load schema: {e}")
            self._schema = None

    def load_templates(self) -> Dict[str, Template]:
        """
        Load all templates from JSON files in the templates directory.

        Returns:
            Dictionary mapping template IDs to Template objects

        Raises:
            FileNotFoundError: If templates directory doesn't exist
            ValueError: If template files contain invalid data
        """
        if self._loaded:
            return self._templates

        if not self.templates_path.exists():
            logger.warning(f"Templates directory not found: {self.templates_path}")
            self.templates_path.mkdir(parents=True, exist_ok=True)
            return self._templates

        self._templates.clear()

        # Find all JSON files in the templates directory and subdirectories
        json_files = list(self.templates_path.glob("**/*.json"))

        if not json_files:
            logger.warning(f"No template files found in {self.templates_path}")
            return self._templates

        for json_file in json_files:
            try:
                self._load_template_file(json_file)
            except Exception as e:
                logger.error(f"Failed to load template file {json_file}: {e}")
                # Continue loading other files

        # Resolve template inheritance after all templates are loaded
        self._resolve_inheritance()

        self._loaded = True
        logger.info(
            f"Loaded {len(self._templates)} templates from {len(json_files)} files"
        )

        return self._templates

    def _load_template_file(self, file_path: Path) -> None:
        """Load template from a single JSON file"""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        template = self._parse_template(data)

        # Validate template
        validation_result = self.validate_template(template)
        if not validation_result.is_valid:
            logger.error(f"Invalid template {template.id}: {validation_result.errors}")
            return

        # Check for duplicate IDs
        if template.id in self._templates:
            logger.warning(f"Duplicate template ID: {template.id} (overwriting)")

        self._templates[template.id] = template

    def _parse_template(self, data: Dict) -> Template:
        """Parse template data from JSON into Template object"""
        # Parse parameters
        parameters = {}
        if "parameters" in data and data["parameters"]:
            for param_name, param_data in data["parameters"].items():
                parameters[param_name] = TemplateParameter(
                    name=param_name,
                    type=param_data["type"],
                    default=param_data.get("default"),
                    description=param_data.get("description", ""),
                    required=param_data.get("required", False),
                    options=param_data.get("options"),
                )

        # Parse inheritance
        inheritance = None
        if "inheritance" in data and data["inheritance"]:
            inheritance_data = data["inheritance"]
            inheritance = TemplateInheritance(
                parent=inheritance_data["parent"],
                override_mode=inheritance_data.get("override_mode", "merge"),
            )

        # Parse conditions
        conditions = []
        if "conditions" in data and data["conditions"]:
            for cond_data in data["conditions"]:
                conditions.append(
                    TemplateCondition(
                        type=cond_data["type"],
                        value=cond_data["value"],
                        operator=cond_data["operator"],
                        weight=cond_data.get("weight", 1.0),
                    )
                )

        # Parse metadata
        metadata = None
        if "metadata" in data:
            meta_data = data["metadata"]
            created_at = None
            updated_at = None

            if "created_at" in meta_data:
                created_at = datetime.fromisoformat(
                    meta_data["created_at"].replace("Z", "+00:00")
                )
            if "updated_at" in meta_data:
                updated_at = datetime.fromisoformat(
                    meta_data["updated_at"].replace("Z", "+00:00")
                )

            metadata = TemplateMetadata(
                category=meta_data["category"],
                complexity=meta_data.get("complexity", "intermediate"),
                author=meta_data.get("author", ""),
                created_at=created_at,
                updated_at=updated_at,
                tags=meta_data.get("tags", []),
            )

        return Template(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            version=data["version"],
            project_type=data["project_type"],
            technology_stack=data.get("technology_stack", []),
            default_tags=data["default_tags"],
            required_instructions=data.get("required_instructions", []),
            optional_instructions=data.get("optional_instructions", []),
            excluded_instructions=data.get("excluded_instructions", []),
            parameters=parameters,
            inheritance=inheritance,
            conditions=conditions,
            metadata=metadata,
        )

    def _resolve_inheritance(self) -> None:
        """Resolve template inheritance relationships"""
        for template in self._templates.values():
            if template.inheritance:
                self._apply_inheritance(template)

    def _apply_inheritance(self, template: Template) -> None:
        """Apply inheritance from parent template"""
        if not template.inheritance:
            return

        parent_template = self._templates.get(template.inheritance.parent)
        if not parent_template:
            logger.warning(f"Parent template not found: {template.inheritance.parent}")
            return

        # Recursively apply parent's inheritance first
        if parent_template.inheritance:
            self._apply_inheritance(parent_template)

        override_mode = template.inheritance.override_mode

        if override_mode == "merge":
            # Merge lists, child takes precedence for conflicts
            template.default_tags = list(
                set(parent_template.default_tags + template.default_tags)
            )
            template.required_instructions = list(
                set(
                    parent_template.required_instructions
                    + template.required_instructions
                )
            )
            template.optional_instructions = list(
                set(
                    parent_template.optional_instructions
                    + template.optional_instructions
                )
            )
            template.excluded_instructions = list(
                set(
                    parent_template.excluded_instructions
                    + template.excluded_instructions
                )
            )
            template.technology_stack = list(
                set(parent_template.technology_stack + template.technology_stack)
            )

            # Merge parameters, child overrides parent
            merged_parameters = parent_template.parameters.copy()
            merged_parameters.update(template.parameters)
            template.parameters = merged_parameters

            # Merge conditions
            template.conditions = parent_template.conditions + template.conditions

        elif override_mode == "extend":
            # Only add from parent what's not already in child
            template.default_tags.extend(
                [
                    tag
                    for tag in parent_template.default_tags
                    if tag not in template.default_tags
                ]
            )
            template.required_instructions.extend(
                [
                    inst
                    for inst in parent_template.required_instructions
                    if inst not in template.required_instructions
                ]
            )
            template.optional_instructions.extend(
                [
                    inst
                    for inst in parent_template.optional_instructions
                    if inst not in template.optional_instructions
                ]
            )
            template.technology_stack.extend(
                [
                    tech
                    for tech in parent_template.technology_stack
                    if tech not in template.technology_stack
                ]
            )

            # Add parent parameters that don't exist in child
            for param_name, param in parent_template.parameters.items():
                if param_name not in template.parameters:
                    template.parameters[param_name] = param

            # Add parent conditions
            template.conditions.extend(parent_template.conditions)

        # For "replace" mode, child completely overrides parent (no action needed)

    def get_template(self, template_id: str) -> Optional[Template]:
        """
        Get a specific template by ID.

        Args:
            template_id: ID of the template

        Returns:
            Template if found, None otherwise
        """
        if not self._loaded:
            self.load_templates()

        return self._templates.get(template_id)

    def create_template(self, template: Template) -> str:
        """
        Create a new template and save it to file.

        Args:
            template: Template to create

        Returns:
            Template ID

        Raises:
            ValueError: If template is invalid or ID already exists
        """
        # Validate template
        validation_result = self.validate_template(template)
        if not validation_result.is_valid:
            raise ValueError(f"Invalid template: {validation_result.errors}")

        # Check for duplicate ID
        if template.id in self._templates:
            raise ValueError(f"Template with ID {template.id} already exists")

        # Convert template to JSON
        template_data = self._template_to_dict(template)

        # Save to file
        template_file = self.templates_path / f"{template.id}.json"
        with open(template_file, "w", encoding="utf-8") as f:
            json.dump(template_data, f, indent=2, default=str)

        # Add to loaded templates
        self._templates[template.id] = template

        logger.info(f"Created template {template.id} at {template_file}")
        return template.id

    def _template_to_dict(self, template: Template) -> Dict[str, Any]:
        """Convert Template object to dictionary for JSON serialization"""
        data: Dict[str, Any] = {
            "id": template.id,
            "name": template.name,
            "description": template.description,
            "version": template.version,
            "project_type": template.project_type,
            "technology_stack": template.technology_stack,
            "default_tags": template.default_tags,
        }

        if template.required_instructions:
            data["required_instructions"] = template.required_instructions

        if template.optional_instructions:
            data["optional_instructions"] = template.optional_instructions

        if template.excluded_instructions:
            data["excluded_instructions"] = template.excluded_instructions

        if template.parameters:
            data["parameters"] = {}
            for param_name, param in template.parameters.items():
                param_data = {
                    "type": param.type,
                    "description": param.description,
                    "required": param.required,
                }
                if param.default is not None:
                    param_data["default"] = param.default
                if param.options:
                    param_data["options"] = param.options
                data["parameters"][param_name] = param_data

        if template.inheritance:
            data["inheritance"] = {
                "parent": template.inheritance.parent,
                "override_mode": template.inheritance.override_mode,
            }

        if template.conditions:
            data["conditions"] = [
                {
                    "type": cond.type,
                    "value": cond.value,
                    "operator": cond.operator,
                    "weight": cond.weight,
                }
                for cond in template.conditions
            ]

        if template.metadata:
            metadata_dict = {
                "category": template.metadata.category,
                "complexity": template.metadata.complexity,
                "author": template.metadata.author,
                "tags": template.metadata.tags,
            }

            if template.metadata.created_at:
                metadata_dict["created_at"] = template.metadata.created_at.isoformat()
            if template.metadata.updated_at:
                metadata_dict["updated_at"] = template.metadata.updated_at.isoformat()

            data["metadata"] = metadata_dict

        return data

    def validate_template(self, template: Template) -> ValidationResult:
        """
        Validate a template against the schema and business rules.

        Args:
            template: Template to validate

        Returns:
            ValidationResult with validation status and any errors/warnings
        """
        errors = []
        warnings = []

        # Convert template to dict for schema validation
        template_dict = self._template_to_dict(template)

        # Schema validation
        if self._schema and HAS_JSONSCHEMA:
            try:
                jsonschema.validate(template_dict, self._schema)
            except JsonSchemaValidationError as e:
                errors.append(f"Schema validation failed: {e.message}")
        elif self._schema and not HAS_JSONSCHEMA:
            warnings.append("jsonschema not available, skipping schema validation")

        # Business rule validation
        if not template.id:
            errors.append("Template ID cannot be empty")

        if not template.name:
            errors.append("Template name cannot be empty")

        if not template.description or len(template.description.strip()) < 10:
            errors.append("Template description must be at least 10 characters")

        if not template.default_tags:
            errors.append("Template must have at least one default tag")

        # Version format validation
        try:
            version_parts = template.version.split(".")
            if len(version_parts) != 3 or not all(
                part.isdigit() for part in version_parts
            ):
                errors.append("Version must be in semantic versioning format (x.y.z)")
        except Exception:
            errors.append("Invalid version format")

        # Inheritance validation
        if template.inheritance:
            if template.inheritance.parent == template.id:
                errors.append("Template cannot inherit from itsel")

        # Parameter validation
        for param_name, param in template.parameters.items():
            if not param_name:
                errors.append("Parameter name cannot be empty")
            if param.type not in [
                "string",
                "number",
                "boolean",
                "array",
                "object",
            ]:
                errors.append(f"Invalid parameter type: {param.type}")

        # Condition validation
        for condition in template.conditions:
            if condition.weight < 0 or condition.weight > 1:
                errors.append(
                    f"Condition weight must be between 0 and 1: {condition.weight}"
                )

        return ValidationResult(
            is_valid=len(errors) == 0, errors=errors, warnings=warnings
        )

    def get_recommended_templates(
        self, project_context: Dict[str, Any]
    ) -> List[TemplateRecommendation]:
        """
        Get recommended templates based on project context.

        Args:
            project_context: Dictionary containing project information like:
                - project_type: str
                - technology_stack: List[str]
                - dependencies: List[str]
                - file_structure: Dict
                - etc.

        Returns:
            List of template recommendations sorted by confidence score
        """
        if not self._loaded:
            self.load_templates()

        recommendations = []

        for template in self._templates.values():

            score, matching_conditions, reasons = self._calculate_template_score(
                template, project_context
            )

            if score > 0:
                recommendations.append(
                    TemplateRecommendation(
                        template=template,
                        confidence_score=score,
                        matching_conditions=matching_conditions,
                        reasons=reasons,
                    )
                )

        # Sort by confidence score (highest first)
        recommendations.sort(key=lambda r: r.confidence_score, reverse=True)

        return recommendations

    def _calculate_template_score(
        self, template: Template, project_context: Dict[str, Any]
    ) -> Tuple[float, List[str], List[str]]:
        """Calculate recommendation score for a template based on project context"""
        score = 0.0
        matching_conditions = []
        reasons = []

        # Base score for project type match
        project_type = project_context.get("project_type", "").lower()
        if template.project_type.lower() == project_type:
            score += 0.4
            reasons.append(f"Project type matches: {template.project_type}")
        elif template.project_type == "generic":
            score += 0.1
            reasons.append("Generic template applicable to any project")

        # Technology stack matching
        tech_stack = project_context.get("technology_stack", [])
        if tech_stack and template.technology_stack:
            tech_matches = set(tech.lower() for tech in tech_stack).intersection(
                set(tech.lower() for tech in template.technology_stack)
            )
            if tech_matches:
                tech_score = len(tech_matches) / len(template.technology_stack)
                score += tech_score * 0.3
                reasons.append(f"Technology stack matches: {', '.join(tech_matches)}")

        # Evaluate template conditions
        for condition in template.conditions:
            if self._evaluate_condition(condition, project_context):
                score += condition.weight * 0.2
                matching_conditions.append(f"{condition.type}:{condition.value}")
                reasons.append(
                    f"Condition met: {condition.type} {condition.operator} {condition.value}"
                )

        # Complexity bonus/penalty based on project context
        if template.metadata:
            complexity_preference = project_context.get(
                "complexity_preference", "intermediate"
            )
            if template.metadata.complexity == complexity_preference:
                score += 0.1
                reasons.append(
                    f"Complexity level matches preference: {complexity_preference}"
                )

        return min(score, 1.0), matching_conditions, reasons

    def _evaluate_condition(
        self, condition: TemplateCondition, project_context: Dict[str, Any]
    ) -> bool:
        """Evaluate a single template condition against project context"""
        try:
            if condition.type == "file_exists":
                files = project_context.get("files", [])
                if condition.operator == "exists":
                    return condition.value in files
                elif condition.operator == "not_exists":
                    return condition.value not in files
                elif condition.operator == "contains":
                    return any(condition.value in file for file in files)
                elif condition.operator == "matches":
                    pattern = re.compile(condition.value)
                    return any(pattern.search(file) for file in files)

            elif condition.type == "dependency_exists":
                dependencies = project_context.get("dependencies", [])
                if condition.operator == "exists":
                    return condition.value in dependencies
                elif condition.operator == "not_exists":
                    return condition.value not in dependencies
                elif condition.operator == "contains":
                    return any(condition.value in dep for dep in dependencies)

            elif condition.type == "technology_detected":
                tech_stack = project_context.get("technology_stack", [])
                tech_stack_lower = [tech.lower() for tech in tech_stack]
                if condition.operator == "equals":
                    return condition.value.lower() in tech_stack_lower
                elif condition.operator == "not_equals":
                    return condition.value.lower() not in tech_stack_lower
                elif condition.operator == "contains":
                    return any(
                        condition.value.lower() in tech.lower() for tech in tech_stack
                    )

            elif condition.type == "project_structure":
                structure = project_context.get("project_structure", {})
                if condition.operator == "exists":
                    return condition.value in structure
                elif condition.operator == "not_exists":
                    return condition.value not in structure

        except Exception as e:
            logger.warning(
                f"Error evaluating condition {condition.type}:{condition.value}: {e}"
            )

        return False

    def get_templates_by_project_type(self, project_type: str) -> List[Template]:
        """
        Get all templates for a specific project type.

        Args:
            project_type: Project type to filter by

        Returns:
            List of templates for the project type
        """
        if not self._loaded:
            self.load_templates()

        return [
            template
            for template in self._templates.values()
            if template.project_type.lower() == project_type.lower()
        ]

    def get_templates_by_technology(self, technology: str) -> List[Template]:
        """
        Get all templates that support a specific technology.

        Args:
            technology: Technology to filter by

        Returns:
            List of templates supporting the technology
        """
        if not self._loaded:
            self.load_templates()

        return [
            template
            for template in self._templates.values()
            if any(
                tech.lower() == technology.lower() for tech in template.technology_stack
            )
        ]

    def reload(self) -> None:
        """Reload all templates from files"""
        self._loaded = False
        self._templates.clear()
        self.load_templates()

    def get_all_project_types(self) -> Set[str]:
        """
        Get all unique project types from loaded templates.

        Returns:
            Set of project types
        """
        if not self._loaded:
            self.load_templates()

        return {template.project_type for template in self._templates.values()}

    def get_all_technologies(self) -> Set[str]:
        """
        Get all unique technologies from loaded templates.

        Returns:
            Set of technologies
        """
        if not self._loaded:
            self.load_templates()

        technologies = set()
        for template in self._templates.values():
            technologies.update(template.technology_stack)

        return technologies

    def apply_template_customization(
        self, template: Template, parameter_values: Dict[str, Any]
    ) -> Template:
        """
        Apply parameter customization to a template.

        Args:
            template: Template to customize
            parameter_values: Dictionary of parameter values to apply

        Returns:
            Customized template with parameters applied
        """
        # Create a copy of the template to avoid modifying the original
        import copy

        customized_template = copy.deepcopy(template)

        # Validate parameter values
        for param_name, param_value in parameter_values.items():
            if param_name not in template.parameters:
                logger.warning(f"Unknown parameter: {param_name}")
                continue

            param_def = template.parameters[param_name]

            # Type validation
            if not self._validate_parameter_value(param_def, param_value):
                logger.warning(
                    f"Invalid value for parameter {param_name}: {param_value}"
                )
                continue

        # Apply parameter substitution to template content
        customized_template = self._substitute_parameters(
            customized_template, parameter_values
        )

        return customized_template

    def _validate_parameter_value(
        self, parameter: TemplateParameter, value: Any
    ) -> bool:
        """Validate a parameter value against its definition"""
        if parameter.type == "string" and not isinstance(value, str):
            return False
        elif parameter.type == "number" and not isinstance(value, (int, float)):
            return False
        elif parameter.type == "boolean" and not isinstance(value, bool):
            return False
        elif parameter.type == "array" and not isinstance(value, list):
            return False
        elif parameter.type == "object" and not isinstance(value, dict):
            return False

        # Check if value is in allowed options
        if parameter.options and value not in parameter.options:
            return False

        return True

    def _substitute_parameters(
        self, template: Template, parameter_values: Dict[str, Any]
    ) -> Template:
        """Substitute parameter values in template content"""
        # Merge with default values
        final_values = {}
        for param_name, param_def in template.parameters.items():
            if param_name in parameter_values:
                final_values[param_name] = parameter_values[param_name]
            elif param_def.default is not None:
                final_values[param_name] = param_def.default

        # Apply conditional logic based on parameters
        template = self._apply_conditional_instructions(template, final_values)

        # Substitute parameter placeholders in instruction content
        # This would be used when generating the actual specification
        # For now, we just store the parameter values for later use
        template._applied_parameters = final_values

        return template

    def _apply_conditional_instructions(
        self, template: Template, parameter_values: Dict[str, Any]
    ) -> Template:
        """Apply conditional instruction inclusion based on parameter values"""
        # Example: If state_management parameter is "redux", include redux-specific instructions
        if "state_management" in parameter_values:
            state_mgmt = parameter_values["state_management"]
            if state_mgmt == "redux":
                if "redux_setup" not in template.optional_instructions:
                    template.optional_instructions.append("redux_setup")
            elif state_mgmt == "zustand":
                if "zustand_setup" not in template.optional_instructions:
                    template.optional_instructions.append("zustand_setup")

        # Example: If testing_framework parameter is specified, include related instructions
        if "testing_framework" in parameter_values:
            testing_fw = parameter_values["testing_framework"]
            if testing_fw == "jest":
                if "jest_configuration" not in template.optional_instructions:
                    template.optional_instructions.append("jest_configuration")
            elif testing_fw == "vitest":
                if "vitest_configuration" not in template.optional_instructions:
                    template.optional_instructions.append("vitest_configuration")

        return template

    def compose_templates(
        self, template_ids: List[str], composition_mode: str = "merge"
    ) -> Template:
        """
        Compose multiple templates into a single template.

        Args:
            template_ids: List of template IDs to compose
            composition_mode: How to handle conflicts ("merge", "priority", "union")

        Returns:
            Composed template

        Raises:
            ValueError: If templates cannot be composed or don't exist
        """
        if not template_ids:
            raise ValueError("At least one template ID must be provided")

        if not self._loaded:
            self.load_templates()

        # Get all templates
        templates = []
        for template_id in template_ids:
            template = self._templates.get(template_id)
            if not template:
                raise ValueError(f"Template not found: {template_id}")
            templates.append(template)

        # Start with the first template as base
        base_template = templates[0]
        composed_template = Template(
            id=f"composed_{'-'.join(template_ids)}",
            name=f"Composed: {', '.join(t.name for t in templates)}",
            description=f"Composed template from: {', '.join(template_ids)}",
            version="1.0.0",
            project_type=base_template.project_type,
            technology_stack=base_template.technology_stack.copy(),
            default_tags=base_template.default_tags.copy(),
            required_instructions=base_template.required_instructions.copy(),
            optional_instructions=base_template.optional_instructions.copy(),
            excluded_instructions=base_template.excluded_instructions.copy(),
            parameters=base_template.parameters.copy(),
            conditions=base_template.conditions.copy(),
            metadata=base_template.metadata,
        )

        # Compose with remaining templates
        for template in templates[1:]:
            if composition_mode == "merge":
                # Merge all lists, removing duplicates
                composed_template.technology_stack = list(
                    set(composed_template.technology_stack + template.technology_stack)
                )
                composed_template.default_tags = list(
                    set(composed_template.default_tags + template.default_tags)
                )
                composed_template.required_instructions = list(
                    set(
                        composed_template.required_instructions
                        + template.required_instructions
                    )
                )
                composed_template.optional_instructions = list(
                    set(
                        composed_template.optional_instructions
                        + template.optional_instructions
                    )
                )
                composed_template.excluded_instructions = list(
                    set(
                        composed_template.excluded_instructions
                        + template.excluded_instructions
                    )
                )
                composed_template.conditions.extend(template.conditions)

                # Merge parameters (later templates override earlier ones)
                composed_template.parameters.update(template.parameters)

            elif composition_mode == "union":
                # Union of all elements
                composed_template.technology_stack.extend(
                    [
                        tech
                        for tech in template.technology_stack
                        if tech not in composed_template.technology_stack
                    ]
                )
                composed_template.default_tags.extend(
                    [
                        tag
                        for tag in template.default_tags
                        if tag not in composed_template.default_tags
                    ]
                )
                composed_template.optional_instructions.extend(
                    [
                        inst
                        for inst in template.optional_instructions
                        if inst not in composed_template.optional_instructions
                    ]
                )
                composed_template.conditions.extend(template.conditions)

                # Add parameters that don't exist
                for param_name, param in template.parameters.items():
                    if param_name not in composed_template.parameters:
                        composed_template.parameters[param_name] = param

        return composed_template

    def preview_template(
        self,
        template_id: str,
        parameter_values: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a preview of what a template would produce.

        Args:
            template_id: ID of the template to preview
            parameter_values: Optional parameter values to apply

        Returns:
            Dictionary containing preview information
        """
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")

        # Apply customization if parameters provided
        if parameter_values:
            template = self.apply_template_customization(template, parameter_values)

        preview = {
            "template_info": {
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "project_type": template.project_type,
                "complexity": (
                    template.metadata.complexity if template.metadata else "unknown"
                ),
            },
            "technology_stack": template.technology_stack,
            "instructions": {
                "required": template.required_instructions,
                "optional": template.optional_instructions,
                "excluded": template.excluded_instructions,
            },
            "tags_to_include": template.default_tags,
            "parameters": {
                param_name: {
                    "type": param.type,
                    "description": param.description,
                    "default": param.default,
                    "required": param.required,
                    "options": param.options,
                }
                for param_name, param in template.parameters.items()
            },
        }

        if hasattr(template, "_applied_parameters"):
            preview["applied_parameters"] = template._applied_parameters

        return preview

    def get_template_recommendations_with_explanations(
        self, project_context: Dict[str, Any], max_recommendations: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get template recommendations with detailed explanations.

        Args:
            project_context: Project context information
            max_recommendations: Maximum number of recommendations to return

        Returns:
            List of recommendation dictionaries with detailed explanations
        """
        recommendations = self.get_recommended_templates(project_context)

        detailed_recommendations = []
        for rec in recommendations[:max_recommendations]:
            detailed_rec = {
                "template": {
                    "id": rec.template.id,
                    "name": rec.template.name,
                    "description": rec.template.description,
                    "project_type": rec.template.project_type,
                    "complexity": (
                        rec.template.metadata.complexity
                        if rec.template.metadata
                        else "unknown"
                    ),
                    "technology_stack": rec.template.technology_stack,
                },
                "score": rec.confidence_score,
                "matching_conditions": rec.matching_conditions,
                "reasons": rec.reasons,
                "preview": self.preview_template(rec.template.id),
            }
            detailed_recommendations.append(detailed_rec)

        return detailed_recommendations

    def find_similar_templates(
        self, template_id: str, similarity_threshold: float = 0.3
    ) -> List[Tuple[Template, float]]:
        """
        Find templates similar to the given template.

        Args:
            template_id: ID of the reference template
            similarity_threshold: Minimum similarity score (0.0 to 1.0)

        Returns:
            List of tuples containing (template, similarity_score)
        """
        if not self._loaded:
            self.load_templates()

        reference_template = self._templates.get(template_id)
        if not reference_template:
            raise ValueError(f"Template not found: {template_id}")

        similar_templates = []

        for template in self._templates.values():
            if template.id == template_id:
                continue

            similarity_score = self._calculate_template_similarity(
                reference_template, template
            )

            if similarity_score >= similarity_threshold:
                similar_templates.append((template, similarity_score))

        # Sort by similarity score (highest first)
        similar_templates.sort(key=lambda x: x[1], reverse=True)

        return similar_templates

    def _calculate_template_similarity(
        self, template1: Template, template2: Template
    ) -> float:
        """Calculate similarity score between two templates"""
        score = 0.0

        # Project type similarity
        if template1.project_type == template2.project_type:
            score += 0.3

        # Technology stack similarity
        tech1 = set(tech.lower() for tech in template1.technology_stack)
        tech2 = set(tech.lower() for tech in template2.technology_stack)
        if tech1 and tech2:
            tech_similarity = len(tech1.intersection(tech2)) / len(tech1.union(tech2))
            score += tech_similarity * 0.25

        # Tag similarity
        tags1 = set(tag.lower() for tag in template1.default_tags)
        tags2 = set(tag.lower() for tag in template2.default_tags)
        if tags1 and tags2:
            tag_similarity = len(tags1.intersection(tags2)) / len(tags1.union(tags2))
            score += tag_similarity * 0.2

        # Complexity similarity
        if template1.metadata and template2.metadata:
            complexity_map = {"beginner": 1, "intermediate": 2, "advanced": 3}
            c1 = complexity_map.get(template1.metadata.complexity, 2)
            c2 = complexity_map.get(template2.metadata.complexity, 2)
            complexity_similarity = 1.0 - abs(c1 - c2) / 2.0
            score += complexity_similarity * 0.15

        # Category similarity
        if (
            template1.metadata
            and template2.metadata
            and template1.metadata.category == template2.metadata.category
        ):
            score += 0.1

        return min(score, 1.0)

    def get_template_analytics(self) -> Dict[str, Any]:
        """
        Get analytics about the loaded templates.

        Returns:
            Dictionary containing template analytics
        """
        if not self._loaded:
            self.load_templates()

        analytics: Dict[str, Any] = {
            "total_templates": len(self._templates),
            "project_types": {},
            "technologies": {},
            "complexity_levels": {},
            "categories": {},
            "inheritance_relationships": 0,
            "parameterized_templates": 0,
            "conditional_templates": 0,
        }

        for template in self._templates.values():
            # Project type distribution
            project_type = template.project_type
            analytics["project_types"][project_type] = (
                analytics["project_types"].get(project_type, 0) + 1
            )

            # Technology distribution
            for tech in template.technology_stack:
                analytics["technologies"][tech] = (
                    analytics["technologies"].get(tech, 0) + 1
                )

            # Complexity distribution
            if template.metadata:
                complexity = template.metadata.complexity
                analytics["complexity_levels"][complexity] = (
                    analytics["complexity_levels"].get(complexity, 0) + 1
                )

                # Category distribution
                category = template.metadata.category
                analytics["categories"][category] = (
                    analytics["categories"].get(category, 0) + 1
                )

            # Feature counts
            if template.inheritance:
                analytics["inheritance_relationships"] += 1

            if template.parameters:
                analytics["parameterized_templates"] += 1

            if template.conditions:
                analytics["conditional_templates"] += 1

        return analytics

    def validate_template_ecosystem(self) -> Dict[str, Any]:
        """
        Validate the entire template ecosystem for consistency and completeness.

        Returns:
            Dictionary containing validation results
        """
        if not self._loaded:
            self.load_templates()

        validation_results: Dict[str, Any] = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": [],
        }

        # Check for missing parent templates
        for template in self._templates.values():
            if template.inheritance:
                parent_id = template.inheritance.parent
                if parent_id not in self._templates:
                    validation_results["errors"].append(
                        f"Template {template.id} references missing parent template: {parent_id}"
                    )
                    validation_results["is_valid"] = False

        # Check for circular inheritance
        inheritance_graph = {}
        for template in self._templates.values():
            if template.inheritance:
                inheritance_graph[template.id] = template.inheritance.parent

        def has_circular_inheritance(template_id: str, visited: Set[str]) -> bool:
            if template_id in visited:
                return True
            if template_id not in inheritance_graph:
                return False

            visited.add(template_id)
            return has_circular_inheritance(inheritance_graph[template_id], visited)

        for template_id in inheritance_graph:
            if has_circular_inheritance(template_id, set()):
                validation_results["errors"].append(
                    f"Circular inheritance detected involving template: {template_id}"
                )
                validation_results["is_valid"] = False

        # Check for project type coverage
        project_types = self.get_all_project_types()
        expected_types = {
            "web-app",
            "api",
            "mobile-app",
            "desktop-app",
            "library",
            "cli-tool",
        }
        missing_types = expected_types - project_types
        if missing_types:
            validation_results["suggestions"].append(
                f"Consider adding templates for missing project types: {', '.join(missing_types)}"
            )

        # Check for technology coverage
        technologies = self.get_all_technologies()
        popular_technologies = {
            "react",
            "vue",
            "angular",
            "python",
            "node.js",
            "java",
            "go",
            "rust",
        }
        missing_tech = popular_technologies - {tech.lower() for tech in technologies}
        if missing_tech:
            validation_results["suggestions"].append(
                f"Consider adding templates for popular technologies: {', '.join(missing_tech)}"
            )

        return validation_results
