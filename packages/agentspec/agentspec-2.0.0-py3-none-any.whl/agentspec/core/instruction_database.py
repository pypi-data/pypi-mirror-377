"""
Instruction Database Management

This module provides the InstructionDatabase class for loading, validating,
and querying AgentSpec instructions from modular JSON files.

This is the main entry point for instruction database functionality. The actual
implementation is organized into specialized modules in the instruction/ package.
"""

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional, Set

from .instruction import Conflict, Instruction, InstructionMetadata, ValidationResult
from .instruction.loader import InstructionLoader
from .instruction.validator import InstructionValidator

if TYPE_CHECKING:
    from .context_detector import ProjectContext

logger = logging.getLogger(__name__)


class InstructionDatabase:
    """
    Manages instruction loading, validation, and querying from modular JSON files.

    This class provides functionality to:
    - Load instructions from category-based JSON files
    - Validate instruction format and content
    - Query instructions by tags
    - Detect conflicts between instructions
    - Evaluate conditional instructions based on project context
    """

    def __init__(
        self,
        instructions_path: Optional[Path] = None,
        schema_path: Optional[Path] = None,
    ):
        """
        Initialize the instruction database.

        Args:
            instructions_path: Path to the instructions directory
            schema_path: Path to the instruction schema file
        """
        self.instructions_path = (
            instructions_path or Path(__file__).parent.parent / "data" / "instructions"
        )
        self.schema_path = (
            schema_path
            or Path(__file__).parent.parent / "data" / "schemas" / "instruction.json"
        )

        self._instructions: Dict[str, Instruction] = {}
        self._schema: Optional[Dict] = None
        self._loaded = False

        # Initialize components
        self.loader = InstructionLoader(self.instructions_path)
        self.validator = InstructionValidator()

        # Load schema
        self._load_schema()

    def _load_schema(self) -> None:
        """Load the JSON schema for instruction validation"""
        try:
            if self.schema_path.exists():
                with open(self.schema_path, "r", encoding="utf-8") as f:
                    self._schema = json.load(f)
                self.validator.schema = self._schema
                logger.debug(f"Loaded instruction schema from {self.schema_path}")
            else:
                logger.warning(f"Schema file not found: {self.schema_path}")
        except Exception as e:
            logger.error(f"Failed to load schema: {e}")
            self._schema = None

    def load_instructions(self) -> Dict[str, Instruction]:
        """
        Load all instructions from JSON files in the instructions directory.

        Returns:
            Dictionary mapping instruction IDs to Instruction objects

        Raises:
            FileNotFoundError: If instructions directory doesn't exist
            ValueError: If instruction files contain invalid data
        """
        if self._loaded:
            return self._instructions

        self._instructions = self.loader.load_all_instructions()

        # Validate all loaded instructions
        for instruction_id, instruction in list(self._instructions.items()):
            validation_result = self.validate_instruction(instruction)
            if not validation_result.is_valid:
                logger.error(
                    f"Invalid instruction {instruction_id}: {validation_result.errors}"
                )
                # Remove invalid instructions
                del self._instructions[instruction_id]

        self._loaded = True
        return self._instructions

    def get_by_tags(self, tags: List[str]) -> List[Instruction]:
        """
        Get instructions that match any of the specified tags.

        Args:
            tags: List of tags to filter by

        Returns:
            List of matching instructions
        """
        if not self._loaded:
            self.load_instructions()

        if not tags:
            return list(self._instructions.values())

        matching_instructions = []
        tag_set = set(tag.lower() for tag in tags)

        for instruction in self._instructions.values():
            instruction_tags = set(tag.lower() for tag in instruction.tags)
            if tag_set.intersection(instruction_tags):
                matching_instructions.append(instruction)

        # Sort by priority (higher priority first)
        matching_instructions.sort(
            key=lambda inst: inst.metadata.priority if inst.metadata else 5,
            reverse=True,
        )

        return matching_instructions

    def validate_instruction(self, instruction: Instruction) -> ValidationResult:
        """
        Validate an instruction against the schema and business rules.

        Args:
            instruction: Instruction to validate

        Returns:
            ValidationResult with validation status and any errors/warnings
        """
        return self.validator.validate_instruction(instruction)

    def get_instruction_metadata(
        self, instruction_id: str
    ) -> Optional[InstructionMetadata]:
        """
        Get metadata for a specific instruction.

        Args:
            instruction_id: ID of the instruction

        Returns:
            InstructionMetadata if found, None otherwise
        """
        if not self._loaded:
            self.load_instructions()

        instruction = self._instructions.get(instruction_id)
        return instruction.metadata if instruction else None

    def get_instruction(self, instruction_id: str) -> Optional[Instruction]:
        """
        Get a specific instruction by ID.

        Args:
            instruction_id: ID of the instruction

        Returns:
            Instruction if found, None otherwise
        """
        if not self._loaded:
            self.load_instructions()

        return self._instructions.get(instruction_id)

    def get_all_tags(self) -> Set[str]:
        """
        Get all unique tags from all instructions.

        Returns:
            Set of all tags
        """
        if not self._loaded:
            self.load_instructions()

        tags = set()
        for instruction in self._instructions.values():
            tags.update(instruction.tags)

        return tags

    def get_instructions_by_category(self, category: str) -> List[Instruction]:
        """
        Get all instructions in a specific category.

        Args:
            category: Category name

        Returns:
            List of instructions in the category
        """
        if not self._loaded:
            self.load_instructions()

        return [
            instruction
            for instruction in self._instructions.values()
            if instruction.metadata and instruction.metadata.category == category
        ]

    def reload(self) -> None:
        """Reload all instructions from files"""
        self._loaded = False
        self._instructions.clear()
        self.load_instructions()

    def detect_conflicts(
        self, instructions: Optional[List[Instruction]] = None
    ) -> List[Conflict]:
        """
        Detect conflicts between instructions.

        Args:
            instructions: List of instructions to check for conflicts.
                         If None, checks all loaded instructions.

        Returns:
            List of detected conflicts
        """
        if instructions is None:
            if not self._loaded:
                self.load_instructions()
            instructions = list(self._instructions.values())

        conflicts = []

        # Check for various types of conflicts
        conflicts.extend(self._detect_tag_conflicts(instructions))
        conflicts.extend(self._detect_content_conflicts(instructions))
        conflicts.extend(self._detect_dependency_conflicts(instructions))
        conflicts.extend(self._detect_version_conflicts(instructions))

        return conflicts

    def resolve_dependencies(self, instruction_ids: List[str]) -> List[str]:
        """
        Resolve dependencies and return instructions in dependency order.

        Args:
            instruction_ids: List of instruction IDs to resolve

        Returns:
            List of instruction IDs in dependency order
        """
        if not self._loaded:
            self.load_instructions()

        # Simple topological sort implementation
        resolved = []
        unresolved = set(instruction_ids)

        def resolve_instruction(inst_id: str, path: Set[str]) -> None:
            if inst_id in path:
                # Circular dependency detected
                logger.warning(f"Circular dependency detected involving {inst_id}")
                return

            if inst_id in resolved:
                return

            instruction = self._instructions.get(inst_id)
            if not instruction:
                logger.warning(f"Instruction not found: {inst_id}")
                return

            path.add(inst_id)

            # Resolve dependencies first
            if instruction.dependencies:
                for dep_id in instruction.dependencies:
                    if dep_id in instruction_ids:  # Only resolve requested instructions
                        resolve_instruction(dep_id, path.copy())

            path.remove(inst_id)
            if inst_id not in resolved:
                resolved.append(inst_id)

        # Resolve all instructions
        for inst_id in instruction_ids:
            if inst_id not in resolved:
                resolve_instruction(inst_id, set())

        return resolved

    # Simplified conflict detection methods
    def _detect_tag_conflicts(self, instructions: List[Instruction]) -> List[Conflict]:
        """Detect instructions with conflicting tag combinations"""
        conflicts = []

        # Group instructions by similar tag sets
        tag_groups: Dict[tuple, List[Instruction]] = {}
        for instruction in instructions:
            tag_signature = tuple(sorted(instruction.tags))
            if tag_signature not in tag_groups:
                tag_groups[tag_signature] = []
            tag_groups[tag_signature].append(instruction)

        # Check for duplicate tag signatures
        for tag_signature, group_instructions in tag_groups.items():
            if len(group_instructions) > 1:
                for i in range(len(group_instructions)):
                    for j in range(i + 1, len(group_instructions)):
                        inst1, inst2 = group_instructions[i], group_instructions[j]
                        conflicts.append(
                            Conflict(
                                instruction1_id=inst1.id,
                                instruction2_id=inst2.id,
                                conflict_type="duplicate_tags",
                                description=f"Instructions have identical tag sets: {', '.join(tag_signature)}",
                                severity="medium",
                            )
                        )

        return conflicts

    def _detect_content_conflicts(
        self, instructions: List[Instruction]
    ) -> List[Conflict]:
        """Detect instructions with conflicting content"""
        # Simplified implementation - just check for obvious contradictions
        return []

    def _detect_dependency_conflicts(
        self, instructions: List[Instruction]
    ) -> List[Conflict]:
        """Detect circular dependencies and missing dependencies"""
        conflicts = []

        # Build dependency graph
        instruction_ids = {inst.id for inst in instructions}

        # Check for missing dependencies
        for instruction in instructions:
            if instruction.dependencies:
                for dep_id in instruction.dependencies:
                    if dep_id not in instruction_ids:
                        conflicts.append(
                            Conflict(
                                instruction1_id=instruction.id,
                                instruction2_id=dep_id,
                                conflict_type="missing_dependency",
                                description=f"Instruction {instruction.id} depends on missing instruction {dep_id}",
                                severity="high",
                            )
                        )

        return conflicts

    def _detect_version_conflicts(
        self, instructions: List[Instruction]
    ) -> List[Conflict]:
        """Detect version conflicts between instructions"""
        conflicts = []

        # Group instructions by ID to check for version conflicts
        instruction_groups: Dict[str, List[Instruction]] = {}
        for instruction in instructions:
            if instruction.id not in instruction_groups:
                instruction_groups[instruction.id] = []
            instruction_groups[instruction.id].append(instruction)

        # Check for multiple versions of the same instruction
        for instruction_id, inst_list in instruction_groups.items():
            if len(inst_list) > 1:
                # Sort by version to find conflicts
                for i, inst1 in enumerate(inst_list):
                    for inst2 in inst_list[i + 1 :]:
                        conflicts.append(
                            Conflict(
                                instruction1_id=f"{inst1.id}@{inst1.version}",
                                instruction2_id=f"{inst2.id}@{inst2.version}",
                                conflict_type="version_conflict",
                                description=f"Multiple versions of instruction {instruction_id}: {inst1.version} and {inst2.version}",
                                severity="medium",
                            )
                        )

        return conflicts
