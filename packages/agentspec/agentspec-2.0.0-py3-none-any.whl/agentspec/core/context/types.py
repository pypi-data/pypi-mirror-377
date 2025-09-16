"""
Context Detection Types and Enums

This module defines the core types, enums, and dataclasses used throughout
the context detection system for project analysis and technology stack detection.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ProjectType(Enum):
    """Enumeration of supported project types"""

    WEB_FRONTEND = "web_frontend"
    WEB_BACKEND = "web_backend"
    FULLSTACK_WEB = "fullstack_web"
    MOBILE_APP = "mobile_app"
    DESKTOP_APP = "desktop_app"
    CLI_TOOL = "cli_tool"
    LIBRARY = "library"
    MICROSERVICE = "microservice"
    DATA_SCIENCE = "data_science"
    MACHINE_LEARNING = "machine_learning"
    GAME = "game"
    UNKNOWN = "unknown"


class Language(Enum):
    """Enumeration of programming languages"""

    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    PYTHON = "python"
    JAVA = "java"
    CSHARP = "csharp"
    CPP = "cpp"
    C = "c"
    GO = "go"
    RUST = "rust"
    PHP = "php"
    RUBY = "ruby"
    SWIFT = "swift"
    KOTLIN = "kotlin"
    DART = "dart"
    HTML = "html"
    CSS = "css"
    UNKNOWN = "unknown"


@dataclass
class Dependency:
    """Represents a project dependency"""

    name: str
    version: Optional[str] = None
    type: str = "runtime"  # runtime, dev, peer, optional
    source: str = ""  # package.json, requirements.txt, etc.


@dataclass
class Framework:
    """Represents a detected framework"""

    name: str
    version: Optional[str] = None
    confidence: float = 0.0
    evidence: List[str] = field(default_factory=list)


@dataclass
class TechnologyStack:
    """Represents the detected technology stack"""

    languages: List[Language] = field(default_factory=list)
    frameworks: List[Framework] = field(default_factory=list)
    databases: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    platforms: List[str] = field(default_factory=list)


@dataclass
class FileStructure:
    """Represents project file structure analysis"""

    total_files: int = 0
    directories: List[str] = field(default_factory=list)
    file_types: Dict[str, int] = field(default_factory=dict)
    config_files: List[str] = field(default_factory=list)
    source_files: List[str] = field(default_factory=list)
    test_files: List[str] = field(default_factory=list)
    documentation_files: List[str] = field(default_factory=list)


@dataclass
class GitInfo:
    """Represents Git repository information"""

    is_git_repo: bool = False
    branch: Optional[str] = None
    remote_url: Optional[str] = None
    commit_count: int = 0
    contributors: int = 0
    last_commit_date: Optional[str] = None


@dataclass
class ProjectContext:
    """Comprehensive project context information"""

    project_path: str
    project_type: ProjectType
    technology_stack: TechnologyStack
    dependencies: List[Dependency] = field(default_factory=list)
    file_structure: FileStructure = field(default_factory=FileStructure)
    git_info: Optional[GitInfo] = None
    confidence_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InstructionSuggestion:
    """Represents a suggested instruction with confidence scoring"""

    instruction_id: str
    tags: List[str]
    confidence: float
    reasons: List[str] = field(default_factory=list)
    category: str = ""
