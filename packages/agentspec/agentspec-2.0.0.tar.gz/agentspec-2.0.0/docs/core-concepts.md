# Core Concepts

Understanding the key concepts in AgentSpec will help you use it more effectively.

## The Three Building Blocks

AgentSpec works with three main components:

### 1. 📋 Instructions

**What they are:** Specific guidelines that tell AI assistants how to code properly.

**Think of them like:** Individual rules in a style guide.

**Examples:**
- "Always validate user input before processing"
- "Write tests for every new function"
- "Use TypeScript strict mode"
- "Implement proper error handling"

**How many:** 106 instructions available, organized into categories like:
- **Core** (25 instructions) - Always included, fundamental practices
- **Frontend** (12 instructions) - UI/UX development
- **Backend** (15 instructions) - Server-side development
- **Testing** (9 instructions) - Quality assurance
- **Security** - Integrated throughout all categories
- **Performance** - Integrated throughout all categories
- And more specialized categories...

### 2. 🎯 Templates

**What they are:** Pre-configured sets of instructions for specific project types.

**Think of them like:** Recipe collections for different types of cooking.

**Examples:**
- **React Frontend** → Includes React, TypeScript, testing, and accessibility instructions
- **Python API** → Includes Python, API design, database, and security instructions
- **E-commerce App** → Includes payment processing, security, and performance instructions

**How many:** 15 templates available:

**Technology Templates:**
- React Frontend
- Vue Frontend
- Python API
- Node.js API
- Mobile App

**Domain Templates:**
- SaaS Application
- E-commerce Application
- Fintech Application
- Healthcare Application
- Data Science Application

**Architecture Templates:**
- Web Application
- Enterprise Web Application
- Microservice

**Methodology Templates:**
- AI-Assisted Development
- Security-Focused Development

### 3. 📄 Specifications

**What they are:** The final document that combines instructions into a comprehensive guide.

**Think of them like:** A complete manual for your specific project.

**What they contain:**
- Selected instructions relevant to your project
- Implementation framework (step-by-step process)
- Quality gates (requirements that must be met)
- Validation commands (how to check your work)

## How They Work Together

```
Template → Selects → Instructions → Generates → Specification
```

**Example Flow:**
1. You choose "React Frontend" template
2. Template selects relevant instructions (React, TypeScript, testing, etc.)
3. AgentSpec generates a specification document
4. You share this specification with your AI assistant
5. AI follows the specification to write better code

## Understanding Instructions in Detail

### Instruction Categories

**Core Instructions (Always Included):**
These are fundamental practices that apply to every project:
- Plan and reflect before acting
- Use tools, don't guess
- Persist until complete
- Maintain context across sessions
- Follow incremental development
- Ensure zero errors
- Avoid "vibe coding" (unclear requirements)

**Specialized Instructions:**
These apply to specific technologies or domains:
- **Frontend**: Component architecture, accessibility, responsive design
- **Backend**: API design, database optimization, security
- **Testing**: TDD, comprehensive test suites, validation
- **Security**: Secure coding, secrets management, compliance
- **Performance**: Optimization, caching, monitoring

### Instruction Structure

Each instruction includes:
- **ID**: Unique identifier (e.g., `react_component_architecture`)
- **Tags**: Categories it belongs to (e.g., `frontend`, `react`, `components`)
- **Content**: The actual guideline text
- **Priority**: How important it is (1-10)
- **Metadata**: Author, creation date, version

## Understanding Templates in Detail

### Template Types

**Technology Templates:**
Focus on specific programming languages or frameworks
- Include language-specific best practices
- Framework-specific patterns
- Tooling and setup instructions

**Domain Templates:**
Focus on specific business domains or industries
- Include domain-specific requirements
- Compliance and regulatory guidelines
- Industry best practices

**Architecture Templates:**
Focus on system design and structure
- Scalability patterns
- Integration approaches
- Deployment strategies

**Methodology Templates:**
Focus on development approaches
- AI-assisted development practices
- Security-first development
- Agile/DevOps practices

### Template Structure

Each template includes:
- **Basic Info**: Name, description, version
- **Project Type**: What kind of project this is for
- **Technology Stack**: Required technologies
- **Required Instructions**: Must-have guidelines
- **Optional Instructions**: Nice-to-have guidelines
- **Parameters**: Customizable options

## Understanding Specifications in Detail

### Specification Sections

A generated specification typically includes:

**1. Header Information**
- Generation timestamp
- Selected tags and instructions
- Project context (if analyzed)

**2. Core Workflow Instructions**
- Always included fundamental practices
- Universal development guidelines

**3. Specialized Instructions**
- Technology-specific guidelines
- Domain-specific requirements
- Selected based on your template/tags

**4. Implementation Framework**
- Pre-development checklist
- During implementation steps
- Post-development validation

**5. Quality Gates**
- Requirements that must be met
- Validation criteria
- Success metrics

**6. Validation Commands**
- Scripts to run for verification
- Testing procedures
- Quality checks

### Specification Formats

AgentSpec can generate specifications in multiple formats:

**Markdown (Default):**
- Human-readable
- Great for sharing with AI assistants
- Easy to edit and customize

**JSON:**
- Machine-readable
- Good for programmatic use
- Integration with other tools

**YAML:**
- Configuration-friendly
- Good for CI/CD integration
- Structured but readable

## Project Analysis

AgentSpec can analyze existing projects to understand:

### What It Detects

**Technology Stack:**
- Programming languages (JavaScript, Python, etc.)
- Frameworks (React, Django, Express, etc.)
- Databases (PostgreSQL, MongoDB, etc.)
- Tools (Jest, ESLint, Docker, etc.)

**Project Structure:**
- File organization
- Configuration files
- Dependencies
- Test setup

**Context Information:**
- Project type (web app, API, mobile app)
- Complexity level
- Development stage

### How It Uses This Information

**Instruction Suggestions:**
- Recommends relevant instructions based on detected technologies
- Prioritizes suggestions by confidence level
- Explains why each instruction is suggested

**Template Recommendations:**
- Suggests templates that match your project
- Provides confidence scores
- Explains the reasoning

## Customization Options

### Tag-Based Selection

Instead of using templates, you can select instructions by tags:

```bash
# Select specific areas of focus
agentspec generate --tags frontend,testing,security

# Combine multiple concerns
agentspec generate --tags react,typescript,accessibility,performance
```

### Project-Specific Generation

Let AgentSpec analyze your project and auto-select relevant instructions:

```bash
# Analyze project and generate appropriate instructions
agentspec analyze . --output analysis.json
agentspec generate --project-path . --tags auto
```

### Custom Instructions

You can add your own instructions:
1. Create custom instruction files
2. Configure AgentSpec to use them
3. Include them in your specifications

## Best Practices for Using AgentSpec

### 1. Start with Templates
- Use templates for new projects
- They provide proven combinations of instructions
- Easier than selecting individual instructions

### 2. Analyze Existing Projects
- Let AgentSpec detect your technology stack
- Get personalized instruction recommendations
- Ensure nothing important is missed

### 3. Customize as Needed
- Add project-specific requirements
- Remove irrelevant instructions
- Adjust for team preferences

### 4. Keep Specifications Updated
- Re-generate as your project evolves
- Update when adding new technologies
- Maintain consistency across team

### 5. Share with Your Team
- Use specifications as team standards
- Include in project documentation
- Reference in code reviews

## Common Workflows

### New Project Workflow
1. Choose appropriate template
2. Generate specification
3. Share with AI assistant
4. Start development following guidelines

### Existing Project Workflow
1. Analyze project structure
2. Review suggested instructions
3. Generate project-specific specification
4. Integrate into development process

### Team Standardization Workflow
1. Select enterprise or domain template
2. Customize for team needs
3. Generate team specification
4. Share across organization

## Next Steps

Now that you understand the core concepts:

- **[Working with Templates](working-with-templates.md)** - Learn to use and customize templates
- **[Your First Project](your-first-project.md)** - Complete step-by-step tutorial
- **[Command Line Guide](command-line-guide.md)** - Master the CLI tools
- **[Instructions Reference](instructions-reference.md)** - Browse all available instructions
- **[Templates Reference](templates-reference.md)** - Explore all templates
