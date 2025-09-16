"""
Instruction Validator

This module provides comprehensive validation functionality for instructions
including schema validation, business rule validation, and format checking.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from .types import Instruction, ValidationResult

try:
    import jsonschema
    from jsonschema import ValidationError as JsonSchemaValidationError

    HAS_JSONSCHEMA = True
except ImportError:
    jsonschema = None  # type: ignore
    JsonSchemaValidationError = Exception  # type: ignore
    HAS_JSONSCHEMA = False

logger = logging.getLogger(__name__)


class InstructionValidator:
    """Validates instructions against schema and business rules"""

    def __init__(self, schema: Optional[Dict] = None):
        """
        Initialize the validator.

        Args:
            schema: JSON schema for instruction validation
        """
        self.schema = schema

    def validate_instruction(self, instruction: Instruction) -> ValidationResult:
        """
        Validate an instruction against the schema and business rules.

        Args:
            instruction: Instruction to validate

        Returns:
            ValidationResult with validation status and any errors/warnings
        """
        errors = []
        warnings = []

        # Convert instruction to dict for schema validation
        instruction_dict = self._instruction_to_dict(instruction)

        # Schema validation
        if self.schema and HAS_JSONSCHEMA:
            try:
                jsonschema.validate(instruction_dict, self.schema)
            except JsonSchemaValidationError as e:
                errors.append(f"Schema validation failed: {e.message}")
        elif self.schema and not HAS_JSONSCHEMA:
            warnings.append("jsonschema not available, skipping schema validation")

        # Business rule validation
        business_errors, business_warnings = self._validate_business_rules(instruction)
        errors.extend(business_errors)
        warnings.extend(business_warnings)

        return ValidationResult(
            is_valid=len(errors) == 0, errors=errors, warnings=warnings
        )

    def _validate_business_rules(
        self, instruction: Instruction
    ) -> Tuple[List[str], List[str]]:
        """Validate business rules for an instruction"""
        errors = []
        warnings = []

        # Basic field validation
        if not instruction.id:
            errors.append("Instruction ID cannot be empty")

        if not instruction.content or len(instruction.content.strip()) < 10:
            errors.append("Instruction content must be at least 10 characters")

        if not instruction.tags:
            errors.append("Instruction must have at least one tag")

        # Version format validation
        try:
            version_parts = instruction.version.split(".")
            if len(version_parts) != 3 or not all(
                part.isdigit() for part in version_parts
            ):
                errors.append("Version must be in semantic versioning format (x.y.z)")
        except Exception:
            errors.append("Invalid version format")

        # ID format validation
        if instruction.id and not self._is_valid_identifier(instruction.id):
            errors.append("Invalid instruction ID format")

        # Tag validation
        for tag in instruction.tags:
            if not self._is_valid_tag(tag):
                errors.append(f"Invalid tag format: {tag}")

        # Parameter validation
        if instruction.parameters:
            for param in instruction.parameters:
                param_errors = self._validate_parameter(param)
                errors.extend(param_errors)

        # Condition validation
        if instruction.conditions:
            for condition in instruction.conditions:
                condition_errors = self._validate_condition(condition)
                errors.extend(condition_errors)

        # Content quality checks
        content_warnings = self._validate_content_quality(instruction.content)
        warnings.extend(content_warnings)

        return errors, warnings

    def _instruction_to_dict(self, instruction: Instruction) -> Dict[str, Any]:
        """Convert instruction to dictionary for schema validation"""
        instruction_dict: Dict[str, Any] = {
            "id": instruction.id,
            "version": instruction.version,
            "tags": instruction.tags,
            "content": instruction.content,
        }

        if instruction.conditions:
            instruction_dict["conditions"] = [
                {
                    "type": cond.type,
                    "value": cond.value,
                    "operator": cond.operator,
                }
                for cond in instruction.conditions
            ]

        if instruction.parameters:
            instruction_dict["parameters"] = [
                {
                    "name": param.name,
                    "type": param.type,
                    "default": param.default,
                    "description": param.description,
                    "required": param.required,
                }
                for param in instruction.parameters
            ]

        if instruction.dependencies:
            instruction_dict["dependencies"] = instruction.dependencies

        if instruction.metadata:
            metadata_dict: Dict[str, Any] = {
                "category": instruction.metadata.category,
                "priority": instruction.metadata.priority,
                "author": instruction.metadata.author,
            }

            if instruction.metadata.created_at:
                metadata_dict["created_at"] = (
                    instruction.metadata.created_at.isoformat()
                )
            if instruction.metadata.updated_at:
                metadata_dict["updated_at"] = (
                    instruction.metadata.updated_at.isoformat()
                )

            instruction_dict["metadata"] = metadata_dict

        return instruction_dict

    def _is_valid_identifier(self, identifier: str) -> bool:
        """Check if identifier follows valid format"""
        import re

        if not identifier or len(identifier) > 100:
            return False

        # Check format: alphanumeric, underscore, hyphen
        if not re.match(r"^[a-zA-Z0-9_-]+$", identifier):
            return False

        # Must start with letter or underscore
        if not re.match(r"^[a-zA-Z_]", identifier):
            return False

        return True

    def _is_valid_tag(self, tag: str) -> bool:
        """Check if tag follows valid format"""
        import re

        if not tag or not tag.strip():
            return False

        # Tag format validation
        return bool(re.match(r"^[a-zA-Z0-9_-]+$", tag))

    def _validate_parameter(self, parameter: Any) -> List[str]:
        """Validate a parameter definition"""
        errors = []

        if not parameter.name:
            errors.append("Parameter name cannot be empty")

        valid_types = ["string", "number", "boolean", "array", "object"]
        if parameter.type not in valid_types:
            errors.append(f"Invalid parameter type: {parameter.type}")

        return errors

    def _validate_condition(self, condition: Any) -> List[str]:
        """Validate a condition definition"""
        errors = []

        valid_types = ["project_type", "technology", "file_exists", "dependency_exists"]
        if condition.type not in valid_types:
            errors.append(f"Invalid condition type: {condition.type}")

        valid_operators = [
            "equals",
            "contains",
            "matches",
            "not_equals",
            "exists",
            "not_exists",
        ]
        if condition.operator not in valid_operators:
            errors.append(f"Invalid condition operator: {condition.operator}")

        if not condition.value:
            errors.append("Condition value cannot be empty")

        return errors

    def _validate_content_quality(self, content: str) -> List[str]:
        """Validate content quality and provide suggestions"""
        warnings = []

        # Check content length
        if len(content) < 50:
            warnings.append("Content is quite short, consider adding more detail")

        # Check for common issues
        if content.count("\n") < 2:
            warnings.append(
                "Content might benefit from better formatting with line breaks"
            )

        # Check for placeholder text
        placeholders = ["TODO", "FIXME", "XXX", "placeholder"]
        for placeholder in placeholders:
            if placeholder.lower() in content.lower():
                warnings.append(f"Content contains placeholder text: {placeholder}")

        return warnings
