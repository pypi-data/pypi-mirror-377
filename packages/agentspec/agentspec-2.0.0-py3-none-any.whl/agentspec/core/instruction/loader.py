"""
Instruction Loader

This module provides functionality to load instructions from JSON files
with proper parsing, validation, and error handling.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict

from .types import (
    Condition,
    Instruction,
    InstructionMetadata,
    LanguageVariant,
    Parameter,
)

logger = logging.getLogger(__name__)


class InstructionLoader:
    """Loads instructions from JSON files with validation and error handling"""

    def __init__(self, instructions_path: Path):
        """
        Initialize the instruction loader.

        Args:
            instructions_path: Path to the instructions directory
        """
        self.instructions_path = instructions_path

    def load_all_instructions(self) -> Dict[str, Instruction]:
        """
        Load all instructions from JSON files in the instructions directory.

        Returns:
            Dictionary mapping instruction IDs to Instruction objects

        Raises:
            FileNotFoundError: If instructions directory doesn't exist
        """
        if not self.instructions_path.exists():
            raise FileNotFoundError(
                f"Instructions directory not found: {self.instructions_path}"
            )

        instructions: Dict[str, Instruction] = {}

        # Find all JSON files in the instructions directory
        json_files = list(self.instructions_path.glob("*.json"))

        if not json_files:
            logger.warning(f"No instruction files found in {self.instructions_path}")
            return instructions

        # Log the AI-specific instruction files being loaded
        ai_files = [f for f in json_files if "ai-" in f.name]
        if ai_files:
            logger.info(
                f"Loading {len(ai_files)} AI-specific instruction files: "
                f"{[f.name for f in ai_files]}"
            )

        for json_file in json_files:
            try:
                file_instructions = self.load_instruction_file(json_file)
                instructions.update(file_instructions)
            except Exception as e:
                logger.error(f"Failed to load instruction file {json_file}: {e}")
                # Continue loading other files

        logger.info(
            f"Loaded {len(instructions)} instructions from {len(json_files)} files"
        )

        return instructions

    def load_instruction_file(self, file_path: Path) -> Dict[str, Instruction]:
        """
        Load instructions from a single JSON file.

        Args:
            file_path: Path to the JSON file

        Returns:
            Dictionary of loaded instructions
        """
        instructions: Dict[str, Instruction] = {}

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "instructions" not in data:
            raise ValueError(
                f"Invalid instruction file format: missing 'instructions' key "
                f"in {file_path}"
            )

        for instruction_data in data["instructions"]:
            try:
                instruction = self.parse_instruction(instruction_data)

                # Check for duplicate IDs
                if instruction.id in instructions:
                    logger.warning(
                        f"Duplicate instruction ID: {instruction.id} in {file_path} "
                        f"(overwriting)"
                    )

                instructions[instruction.id] = instruction

            except Exception as e:
                logger.error(f"Failed to parse instruction in {file_path}: {e}")

        return instructions

    def parse_instruction(self, data: Dict) -> Instruction:
        """
        Parse instruction data from JSON into Instruction object.

        Args:
            data: Raw instruction data from JSON

        Returns:
            Parsed Instruction object
        """
        # Parse conditions
        conditions = None
        if "conditions" in data and data["conditions"]:
            conditions = [
                Condition(
                    type=cond["type"],
                    value=cond["value"],
                    operator=cond["operator"],
                )
                for cond in data["conditions"]
            ]

        # Parse parameters
        parameters = None
        if "parameters" in data and data["parameters"]:
            parameters = [
                Parameter(
                    name=param["name"],
                    type=param["type"],
                    default=param.get("default"),
                    description=param.get("description", ""),
                    required=param.get("required", False),
                )
                for param in data["parameters"]
            ]

        # Parse language variants
        language_variants = None
        if "language_variants" in data and data["language_variants"]:
            language_variants = {}
            for lang_code, variant_data in data["language_variants"].items():
                # Parse variant parameters if present
                variant_parameters = None
                if "parameters" in variant_data and variant_data["parameters"]:
                    variant_parameters = [
                        Parameter(
                            name=param["name"],
                            type=param["type"],
                            default=param.get("default"),
                            description=param.get("description", ""),
                            required=param.get("required", False),
                        )
                        for param in variant_data["parameters"]
                    ]

                language_variants[lang_code] = LanguageVariant(
                    language=lang_code,
                    content=variant_data["content"],
                    parameters=variant_parameters,
                )

        # Parse metadata
        metadata = None
        if "metadata" in data:
            metadata = self._parse_metadata(data["metadata"])

        return Instruction(
            id=data["id"],
            version=data["version"],
            tags=data["tags"],
            content=data["content"],
            conditions=conditions,
            parameters=parameters,
            dependencies=data.get("dependencies"),
            metadata=metadata,
            language_variants=language_variants,
        )

    def _parse_metadata(self, meta_data: Dict) -> InstructionMetadata:
        """Parse metadata from JSON data"""
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

        return InstructionMetadata(
            category=meta_data["category"],
            priority=meta_data.get("priority", 5),
            author=meta_data.get("author", ""),
            created_at=created_at,
            updated_at=updated_at,
            default_language=meta_data.get("default_language", "en"),
        )
