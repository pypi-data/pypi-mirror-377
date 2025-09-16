# Quick Start Guide

Get AgentSpec up and running in 5 minutes.

## Step 1: Install AgentSpec

```bash
pip install agentspec
```

**Verify installation:**
```bash
agentspec --version
# Should show: AgentSpec 2.0.0
```

## Step 2: Choose Your Path

### 🎯 Option A: Use a Template (Recommended)

Perfect if you're starting a new project or want instructions for a specific type of application.

```bash
# See all available templates
agentspec list-templates

# Generate instructions for a React app
agentspec generate --template react_app --output react-instructions.md

# Generate instructions for a Python API
agentspec generate --template python-api --output api-instructions.md

# Generate instructions for an e-commerce app
agentspec generate --template ecommerce-application --output ecommerce-instructions.md
```

### 🔍 Option B: Analyze Existing Project

Perfect if you have an existing project and want AgentSpec to detect what instructions you need.

```bash
# Navigate to your project
cd /path/to/your/project

# Let AgentSpec analyze your project and generate instructions
agentspec analyze . --output analysis.json
agentspec generate --project-path . --tags auto --output project-instructions.md
```

### 🎮 Option C: Interactive Mode

Perfect if you want guidance through the process.

```bash
agentspec interactive
```

This will ask you questions and help you choose the right instructions.

## Step 3: Use Your Instructions

You now have a file (like `react-instructions.md`) with detailed guidelines. Here's how to use it:

### With AI Coding Assistants:

**GitHub Copilot:**
1. Open the instructions file in your editor
2. Keep it open while coding
3. Copilot will use it as context for better suggestions

**ChatGPT/Claude:**
1. Copy the instructions from the file
2. Paste them at the start of your conversation
3. Say: "Please follow these instructions for all code you write"

**Cursor/Other AI IDEs:**
1. Add the instructions file to your project
2. Reference it when asking for code help

## Step 4: Start Coding!

Your AI assistant now has detailed instructions on:
- ✅ Code structure and organization
- ✅ Security best practices
- ✅ Testing requirements
- ✅ Error handling patterns
- ✅ Documentation standards
- ✅ Performance considerations

## Example: React Project

Let's walk through a complete example:

```bash
# 1. Create new project directory
mkdir my-react-app
cd my-react-app

# 2. Generate AgentSpec instructions
agentspec generate --template react_app --output instructions.md

# 3. Look at what was generated
head -20 instructions.md
```

You'll see something like:
```markdown
# AgentSpec - Project Specification

## CORE WORKFLOW INSTRUCTIONS

### Plan and Reflect
Plan thoroughly before every tool call and reflect on the outcome after...

### Use Tools Don't Guess
Use your tools, don't guess. If you're unsure about code or files, open them...

## FRONTEND GUIDELINES

### React Component Architecture
Implement a modular component architecture using React functional components...
```

Now when you ask your AI assistant to create components, it will follow these detailed guidelines!

## What's Next?

### Learn More:
- **[Your First Project](your-first-project.md)** - Complete step-by-step tutorial
- **[Core Concepts](core-concepts.md)** - Understand how AgentSpec works
- **[Working with Templates](working-with-templates.md)** - Customize templates for your needs

### Explore:
- **[All Templates](templates-reference.md)** - See all 15 available templates
- **[All Instructions](instructions-reference.md)** - Browse all 107 instructions
- **[Examples](examples/)** - Real-world usage examples

### Get Help:
- **[Command Line Guide](command-line-guide.md)** - Complete CLI reference
- **[GitHub Issues](https://github.com/keyurgolani/AgentSpec/issues)** - Report problems or request features

## Common Next Steps

**For new projects:**
```bash
# Generate instructions, then initialize your project
agentspec generate --template react_app --output instructions.md
npx create-react-app my-app
cd my-app
# Now use instructions.md with your AI assistant
```

**For existing projects:**
```bash
# Analyze and generate project-specific instructions
agentspec analyze . --output analysis.json
agentspec generate --project-path . --tags auto --output instructions.md
```

**For teams:**
```bash
# Create team-wide standards
agentspec generate --template enterprise-web-application --output team-standards.md
# Share team-standards.md with your team
```

You're now ready to use AgentSpec! 🚀
