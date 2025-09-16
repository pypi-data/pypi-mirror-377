# API Reference

This guide covers using AgentSpec programmatically through its Python API.

## Installation

```bash
pip install agentspec
```

## Quick Start

```python
from agentspec import SpecGenerator, InstructionDatabase, TemplateManager, ContextDetector

# Initialize components
instruction_db = InstructionDatabase()
template_manager = TemplateManager()
context_detector = ContextDetector()
spec_generator = SpecGenerator(
    instruction_db=instruction_db,
    template_manager=template_manager,
    context_detector=context_detector
)

# Generate a specification
from agentspec.core.spec_generator import SpecConfig

config = SpecConfig(
    template_id="react_app",
    output_format="markdown",
    include_metadata=True
)

spec = spec_generator.generate_spec(config)
print(spec.content)
```

## Core Classes

### SpecGenerator

Main class for generating specifications.

```python
from agentspec import SpecGenerator
from agentspec.core.spec_generator import SpecConfig

class SpecGenerator:
    def __init__(
        self,
        instruction_db: InstructionDatabase,
        template_manager: TemplateManager,
        context_detector: Optional[ContextDetector] = None
    ):
        """Initialize SpecGenerator with required dependencies."""

    def generate_spec(self, config: SpecConfig) -> GeneratedSpec:
        """Generate a specification based on configuration."""

    def export_spec(self, spec: GeneratedSpec, output_path: str) -> None:
        """Export specification to file."""

    def validate_spec(self, spec: GeneratedSpec) -> ValidationResult:
        """Validate a generated specification."""
```

#### Example Usage

```python
# Basic generation
config = SpecConfig(template_id="python-api")
spec = spec_generator.generate_spec(config)

# With custom tags
config = SpecConfig(
    selected_tags=["frontend", "testing", "security"],
    output_format="json"
)
spec = spec_generator.generate_spec(config)

# With project context
config = SpecConfig(
    template_id="react_app",
    project_context=context_detector.analyze_project("./my-project")
)
spec = spec_generator.generate_spec(config)
```

### InstructionDatabase

Manages loading and querying instructions.

```python
from agentspec import InstructionDatabase

class InstructionDatabase:
    def __init__(self, instructions_path: Optional[Path] = None):
        """Initialize with optional custom instructions path."""

    def load_instructions(self) -> Dict[str, Instruction]:
        """Load all instructions from data files."""

    def get_by_tags(self, tags: List[str]) -> List[Instruction]:
        """Get instructions matching any of the provided tags."""

    def get_by_id(self, instruction_id: str) -> Optional[Instruction]:
        """Get instruction by ID."""

    def get_all_tags(self) -> Set[str]:
        """Get all available tags."""

    def search_instructions(self, query: str) -> List[Instruction]:
        """Search instructions by content."""
```

#### Example Usage

```python
# Load and query instructions
instruction_db = InstructionDatabase()
instructions = instruction_db.load_instructions()

# Get instructions by tags
testing_instructions = instruction_db.get_by_tags(["testing"])
security_instructions = instruction_db.get_by_tags(["secu
- `analyze_project(project_path: str) -> ProjectContext`
- `suggest_instructions(context: ProjectContext) -> List[InstructionSuggestion]`

### 5. AIBestPracticesIntegrator

Integrates AI development best practices into existing projects.

```python
from agentspec import AIBestPracticesIntegrator

# Initialize
integrator = AIBestPracticesIntegrator()

# Analyze project for AI integration opportunities
analysis = integrator.analyze_project("./my-project")

# Generate integration recommendations
recommendations = integrator.get_integration_recommendations(analysis)
```

### TemplateManager

The `TemplateManager` class handles loading, validation, and recommendation of project templates.

#### Class Definition

```python
from agentspec.core.template_manager import TemplateManager

class TemplateManager:
    def __init__(self, templates_path: Optional[Path] = None,
                 schema_path: Optional[Path] = None)
```

#### Methods

##### `load_templates() -> Dict[str, Template]`

Loads all templates from JSON files and resolves inheritance.

**Returns:**
- `Dict[str, Template]`: Dictionary mapping template IDs to Template objects

**Example:**
```python
manager = TemplateManager()
templates = manager.load_templates()
print(f"Available templates: {list(templates.keys())}")
```

##### `get_template(template_id: str) -> Optional[Template]`

Retrieves a specific template by ID.

**Parameters:**
- `template_id`: ID of the template to retrieve

**Returns:**
- `Optional[Template]`: Template object if found, None otherwise

**Example:**
```python
react_template = manager.get_template("react_app")
if react_template:
    print(f"Template: {react_template.name}")
```

##### `get_recommended_templates(project_context: Dict[str, Any]) -> List[TemplateRecommendation]`

Gets template recommendations based on project context.

**Parameters:**
- `project_context`: Dictionary containing project information

**Returns:**
- `List[TemplateRecommendation]`: Sorted list of recommendations

**Example:**
```python
context = {
    "project_type": "web_frontend",
    "technology_stack": ["react", "typescript"],
    "files": ["package.json", "tsconfig.json"]
}
recommendations = manager.get_recommended_templates(context)
for rec in recommendations:
    print(f"{rec.template.name}: {rec.confidence_score:.2f}")
```

##### `create_template(template: Template) -> str`

Creates a new template and saves it to file.

**Parameters:**
- `template`: Template object to create

**Returns:**
- `str`: Template ID

**Raises:**
- `ValueError`: If template is invalid or ID already exists

**Example:**
```python
new_template = Template(
    id="custom_template",
    name="Custom Template",
    description="My custom template",
    version="1.0.0",
    project_type="web_frontend",
    technology_stack=["custom"],
    default_tags=["custom"]
)
template_id = manager.create_template(new_template)
```

### ContextDetector

The `ContextDetector` class analyzes projects to detect technology stacks and suggest relevant instructions.

#### Class Definition

```python
from agentspec.core.context_detector import ContextDetector

class ContextDetector:
    def __init__(self)
```

#### Methods

##### `analyze_project(project_path: str) -> ProjectContext`

Performs comprehensive project analysis.

**Parameters:**
- `project_path`: Path to the project directory

**Returns:**
- `ProjectContext`: Complete project analysis results

**Raises:**
- `ValueError`: If project path is invalid

**Example:**
```python
detector = ContextDetector()
context = detector.analyze_project("./my-project")
print(f"Project type: {context.project_type.value}")
print(f"Confidence: {context.confidence_score:.2f}")
```

##### `detect_technology_stack(project_path: str) -> TechnologyStack`

Detects technology stack from project files.

**Parameters:**
- `project_path`: Path to the project directory

**Returns:**
- `TechnologyStack`: Detected technologies

**Example:**
```python
stack = detector.detect_technology_stack("./my-project")
print(f"Languages: {[lang.value for lang in stack.languages]}")
print(f"Frameworks: {[fw.name for fw in stack.frameworks]}")
```

##### `suggest_instructions(context: ProjectContext) -> List[InstructionSuggestion]`

Suggests relevant instructions based on project context.

**Parameters:**
- `context`: Project context information

**Returns:**
- `List[InstructionSuggestion]`: Sorted list of suggestions

**Example:**
```python
suggestions = detector.suggest_instructions(context)
for suggestion in suggestions[:5]:  # Top 5
    print(f"{suggestion.instruction_id}: {suggestion.confidence:.2f}")
```

### SpecGenerator

The `SpecGenerator` class generates specifications from instructions and templates.

#### Class Definition

```python
from agentspec.core.spec_generator import SpecGenerator, SpecConfig

class SpecGenerator:
    def __init__(self, instruction_db: Optional[InstructionDatabase] = None,
                 template_manager: Optional[TemplateManager] = None,
                 context_detector: Optional[ContextDetector] = None)
```

#### Methods

##### `generate_spec(config: SpecConfig) -> GeneratedSpec`

Generates a specification based on configuration.

**Parameters:**
- `config`: SpecConfig with generation parameters

**Returns:**
- `GeneratedSpec`: Generated specification with metadata

**Raises:**
- `ValueError`: If configuration is invalid

**Example:**
```python
generator = SpecGenerator()
config = SpecConfig(
    selected_tags=["frontend", "testing"],
    output_format="markdown"
)
spec = generator.generate_spec(config)
print(spec.content)
```

##### `apply_template(template: Template, context: Optional[ProjectContext] = None) -> SpecConfig`

Applies a template to create specification configuration.

**Parameters:**
- `template`: Template to apply
- `context`: Optional project context for customization

**Returns:**
- `SpecConfig`: Configuration based on template

**Example:**
```python
template = template_manager.get_template("react_app")
config = generator.apply_template(template, project_context)
spec = generator.generate_spec(config)
```

##### `validate_spec(spec: GeneratedSpec) -> ValidationResult`

Validates a generated specification.

**Parameters:**
- `spec`: Generated specification to validate

**Returns:**
- `ValidationResult`: Validation status and messages

**Example:**
```python
result = generator.validate_spec(spec)
if not result.is_valid:
    print(f"Validation errors: {result.errors}")
if result.warnings:
    print(f"Warnings: {result.warnings}")
```

##### `export_spec(spec: GeneratedSpec, output_path: Optional[str] = None) -> str`

Exports specification to file or returns as string.

**Parameters:**
- `spec`: Generated specification to export
- `output_path`: Optional file path to save

**Returns:**
- `str`: Specification content

**Example:**
```python
# Export to file
generator.export_spec(spec, "project_spec.md")

# Get as string
content = generator.export_spec(spec)
```



## CLI Modules

### Main CLI

The main CLI entry point provides command-line interface functionality.

```python
from agentspec.cli.main import AgentSpecCLI

cli = AgentSpecCLI()
exit_code = cli.run(['generate', '--tags', 'frontend,testing'])
```

### Command Handlers

Individual command handlers for specific CLI operations.

```python
from agentspec.cli.commands import (
    list_tags_command,
    generate_spec_command,
    analyze_project_command
)

# Use command handlers directly
result = list_tags_command(instruction_db, verbose=True)
```

## Utility Modules

### Configuration Management

```python
from agentspec.utils.config import ConfigManager

manager = ConfigManager()
config = manager.load_config()
value = manager.get_config_value("agentspec.paths.instructions")
```

### Logging Setup

```python
from agentspec.utils.logging import setup_logging

setup_logging(
    log_level="DEBUG",
    log_file="agentspec.log",
    structured=True
)
```



## Data Models

### Core Data Classes

#### Instruction

```python
@dataclass
class Instruction:
    id: str
    version: str
    tags: List[str]
    content: str
    conditions: Optional[List[Condition]] = None
    parameters: Optional[List[Parameter]] = None
    dependencies: Optional[List[str]] = None
    metadata: Optional[InstructionMetadata] = None
    language_variants: Optional[Dict[str, LanguageVariant]] = None
```

#### Template

```python
@dataclass
class Template:
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
```

#### ProjectContext

```python
@dataclass
class ProjectContext:
    project_path: str
    project_type: ProjectType
    technology_stack: TechnologyStack
    dependencies: List[Dependency] = field(default_factory=list)
    file_structure: FileStructure = field(default_factory=FileStructure)
    git_info: Optional[GitInfo] = None
    confidence_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
```



## Examples

### Complete Workflow Example

```python
from agentspec.core import (
    InstructionDatabase, TemplateManager,
    ContextDetector, SpecGenerator, SpecConfig
)

# Initialize components
instruction_db = InstructionDatabase()
template_manager = TemplateManager()
context_detector = ContextDetector()
spec_generator = SpecGenerator(
    instruction_db=instruction_db,
    template_manager=template_manager,
    context_detector=context_detector
)

# Analyze project
project_context = context_detector.analyze_project("./my-project")
print(f"Detected: {project_context.project_type.value}")

# Get template recommendations
recommendations = template_manager.get_recommended_templates({
    "project_type": project_context.project_type.value,
    "technology_stack": [fw.name for fw in project_context.technology_stack.frameworks]
})

# Use best template
if recommendations:
    template = recommendations[0].template
    config = spec_generator.apply_template(template, project_context)
else:
    # Manual configuration
    config = SpecConfig(
        selected_tags=["frontend", "testing", "security"],
        project_context=project_context
    )

# Generate specification
spec = spec_generator.generate_spec(config)

# Validate and export
validation = spec_generator.validate_spec(spec)
if validation.is_valid:
    spec_generator.export_spec(spec, "project_spec.md")
    print("Specification generated successfully!")
else:
    print(f"Validation errors: {validation.errors}")
```

### Custom Instruction Creation

```python
from agentspec.core.instruction_database import (
    Instruction, InstructionMetadata, Condition, Parameter
)

# Create custom instruction
custom_instruction = Instruction(
    id="custom_react_testing",
    version="1.0.0",
    tags=["react", "testing", "custom"],
    content="Implement comprehensive React testing with {test_framework}.",
    conditions=[
        Condition(
            type="technology",
            value="react",
            operator="equals"
        )
    ],
    parameters=[
        Parameter(
            name="test_framework",
            type="string",
            default="jest",
            description="Testing framework to use"
        )
    ],
    metadata=InstructionMetadata(
        category="testing",
        priority=8,
        author="custom_author"
    )
)

# Validate instruction
db = InstructionDatabase()
result = db.validate_instruction(custom_instruction)
if result.is_valid:
    print("Custom instruction is valid!")
```



## Error Handling

All AgentSpec APIs use consistent error handling patterns:

```python
from agentspec.core.instruction_database import InstructionDatabase
from agentspec.core.exceptions import AgentSpecError, ValidationError

try:
    db = InstructionDatabase()
    instructions = db.load_instructions()
except FileNotFoundError as e:
    print(f"Instructions directory not found: {e}")
except ValidationError as e:
    print(f"Validation failed: {e}")
except AgentSpecError as e:
    print(f"AgentSpec error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Performance Considerations

### Large Datasets

For large instruction databases or project analysis:

```python
# Use lazy loading
db = InstructionDatabase()
# Instructions loaded on first access
instructions = db.load_instructions()

# Cache results for repeated queries
cached_instructions = db.get_by_tags(["frontend"])
```

### Memory Management

```python
# Clear caches when needed
db.reload()  # Reloads from files
template_manager.reload()  # Reloads templates
```

### Concurrent Usage

AgentSpec components are thread-safe for read operations:

```python
import threading

def analyze_project(path):
    detector = ContextDetector()
    return detector.analyze_project(path)

# Safe to run concurrently
threads = [
    threading.Thread(target=analyze_project, args=(path,))
    for path in project_paths
]
```

This API documentation provides comprehensive coverage of AgentSpec's Python interface. For more examples and advanced usage patterns, see the [examples directory](../examples/) in the repository.
