# Your First Project

This guide walks you through creating your first project with AgentSpec from start to finish. By the end, you'll have a complete understanding of how to use AgentSpec effectively.

## What We'll Build

We'll create a simple React todo app with AgentSpec guidance. This tutorial covers:
- Setting up AgentSpec
- Generating project instructions
- Using instructions with AI assistants
- Following AgentSpec best practices

## Prerequisites

- Basic knowledge of React and JavaScript
- An AI coding assistant (GitHub Copilot, ChatGPT, Claude, etc.)
- Node.js installed on your computer

## Step 1: Install AgentSpec

First, let's install AgentSpec:

```bash
pip install agentspec
```

Verify it's working:
```bash
agentspec --version
# Should show: AgentSpec 2.0.0
```

If you need help with installation, see the [Quick Start Guide](quick-start.md).

## Step 2: Set Up Your Project

Create a new directory for our todo app:

```bash
mkdir react-todo-app
cd react-todo-app
```

## Step 3: Generate AgentSpec Instructions

Now let's generate instructions specifically for a React project:

```bash
agentspec generate --template react_app --output todo-instructions.md
```

This creates a file called `todo-instructions.md` with comprehensive guidelines for React development.

Let's see what was generated:

```bash
head -30 todo-instructions.md
```

You should see something like:

```markdown
# AgentSpec - Project Specification

Generated: 2024-12-15 10:00:00
Template: React Web Application (v1.0.0)
Total instructions: 37

## CORE WORKFLOW INSTRUCTIONS

### Plan and Reflect
Plan thoroughly before every tool call and reflect on the outcome after...

### Use Tools Don't Guess
Use your tools, don't guess. If you're unsure about code or files, open them...

## FRONTEND GUIDELINES

### React Component Architecture
Implement a modular component architecture using React functional components...
```

## Step 4: Initialize Your React Project

Now let's create the actual React project:

```bash
npx create-react-app . --template typescript
```

This creates a React project with TypeScript support in the current directory.

## Step 5: Share Instructions with Your AI Assistant

Now comes the key part - using your AgentSpec instructions with an AI assistant. Here's how to do it with different AI tools:

### With ChatGPT or Claude:

1. Open your AI assistant
2. Copy the contents of `todo-instructions.md`
3. Start your conversation with:

```
I'm building a React todo app. Please follow these AgentSpec instructions for all code you write:

[Paste the contents of todo-instructions.md here]

Now, help me create a simple todo app with the following features:
- Add new todos
- Mark todos as complete
- Delete todos
- Filter todos (all, active, completed)
```

### With GitHub Copilot:

1. Open `todo-instructions.md` in VS Code
2. Keep it open while you code
3. Copilot will use it as context for suggestions

### With Cursor or other AI IDEs:

1. Add `todo-instructions.md` to your project
2. Reference it when asking for help: "Following the instructions in todo-instructions.md, help me create..."

## Step 6: Build Your Todo App

Now let's build the todo app following AgentSpec guidelines. Ask your AI assistant to help you create:

### 1. Todo Component Structure

Ask your AI: "Following the AgentSpec instructions, create a modular component structure for a todo app with these components: TodoApp, TodoList, TodoItem, AddTodo, and FilterButtons."

The AI should create:
- Functional components with TypeScript
- Proper prop types and interfaces
- Accessibility features
- Error boundaries
- Proper file organization

### 2. State Management

Ask your AI: "Following the AgentSpec instructions, implement state management for the todo app using React hooks."

The AI should implement:
- useState for todo state
- useEffect for persistence
- Custom hooks for todo operations
- Proper error handling

### 3. Testing

Ask your AI: "Following the AgentSpec instructions, create comprehensive tests for the todo app components."

The AI should create:
- Unit tests for each component
- Integration tests for user flows
- Accessibility tests
- Test utilities and helpers

### 4. Styling and Accessibility

Ask your AI: "Following the AgentSpec instructions, add styling and ensure full accessibility compliance."

The AI should implement:
- Responsive design
- WCAG 2.1 AA compliance
- Keyboard navigation
- Screen reader support
- Focus management

## Step 7: Validate Your Work

AgentSpec emphasizes continuous validation. Let's check our work:

### Run the Quality Gates

The AgentSpec instructions include quality gates that must be passed:

```bash
# Check for TypeScript errors
npm run type-check

# Run linting
npm run lint

# Run tests
npm test

# Build the project
npm run build
```

All of these should pass without errors if you've followed the AgentSpec guidelines.

### Manual Validation

Also check:
- ✅ All components are accessible (use screen reader or accessibility tools)
- ✅ App works on mobile devices
- ✅ All user interactions work correctly
- ✅ Error states are handled gracefully
- ✅ Code is well-documented

## Step 8: What You've Learned

Congratulations! You've successfully:

1. **Generated AgentSpec instructions** for a React project
2. **Used instructions with AI assistants** to get better code
3. **Built a complete application** following best practices
4. **Validated your work** against quality standards

### Key Benefits You Experienced

**Better Code Quality:**
- TypeScript integration
- Comprehensive error handling
- Accessibility compliance
- Proper testing coverage

**Consistent Patterns:**
- Modular component architecture
- Standardized file organization
- Consistent naming conventions
- Proper documentation

**Security and Performance:**
- Input validation
- Performance optimization
- Security best practices
- Proper state management

## Next Steps

Now that you've completed your first AgentSpec project, here are some ways to continue learning:

### Explore Other Templates

Try building different types of projects:

```bash
# Build a Python API
agentspec generate --template python-api --output api-instructions.md

# Build an e-commerce app
agentspec generate --template ecommerce-application --output ecommerce-instructions.md

# Build a mobile app
agentspec generate --template mobile-app --output mobile-instructions.md
```

### Analyze Existing Projects

If you have existing projects, let AgentSpec analyze them:

```bash
cd /path/to/existing/project
agentspec analyze . --output analysis.json
agentspec generate --project-path . --tags auto --output project-instructions.md
```

### Customize for Your Team

Create team-wide standards:

```bash
# Generate enterprise-level instructions
agentspec generate --template enterprise-web-application --output team-standards.md

# Share team-standards.md with your team
```

### Learn More

**Core Documentation:**
- **[Core Concepts](core-concepts.md)** - Deeper understanding of instructions and templates
- **[Working with Templates](working-with-templates.md)** - Master template usage and customization
- **[Command Line Guide](command-line-guide.md)** - Complete CLI reference

**Reference Materials:**
- **[Instructions Reference](instructions-reference.md)** - Browse all 107 available instructions
- **[Templates Reference](templates-reference.md)** - Explore all 15 templates
- **[API Documentation](api-reference.md)** - Python API for advanced usage

**Examples:**
- **[Example Projects](examples/)** - Real-world usage examples
- **[GitHub Repository](https://github.com/keyurgolani/AgentSpec)** - Source code and more examples

### Best Practices You've Learned

1. **Always start with AgentSpec instructions** before coding
2. **Use templates for common project types** to get proven instruction combinations
3. **Share instructions with AI assistants** for consistent, high-quality code
4. **Follow the quality gates** to ensure professional-grade output
5. **Validate continuously** throughout development
6. **Keep instructions updated** as your project evolves

### Common Patterns

**For new projects:**
```bash
agentspec generate --template [project-type] --output instructions.md
# Then share instructions.md with your AI assistant
```

**For existing projects:**
```bash
agentspec analyze . --output analysis.json
agentspec generate --project-path . --tags auto --output instructions.md
```

**For teams:**
```bash
agentspec generate --template enterprise-web-application --output team-standards.md
# Share with your team for consistent development practices
```

## Troubleshooting

### Common Issues

**AI assistant not following instructions:**
- Make sure you've shared the complete instructions file
- Try breaking down requests into smaller, more specific tasks
- Reference specific sections: "Following the React Component Architecture section..."

**Quality gates failing:**
- Run each validation step individually to identify the issue
- Check that all dependencies are installed correctly
- Ensure you're using the correct Node.js/Python version

**Instructions seem overwhelming:**
- Start with just the Core Workflow Instructions
- Add specialized instructions gradually as you need them
- Focus on one section at a time

### Getting Help

- **[Command Line Guide](command-line-guide.md)** - Complete CLI reference
- **[GitHub Issues](https://github.com/keyurgolani/AgentSpec/issues)** - Report problems
- **[GitHub Discussions](https://github.com/keyurgolani/AgentSpec/discussions)** - Ask questions

## Congratulations! 🎉

You've successfully completed your first AgentSpec project! You now know how to:

- ✅ Generate AgentSpec instructions for any project type
- ✅ Use instructions with AI assistants for better code quality
- ✅ Follow AgentSpec best practices and quality gates
- ✅ Build applications with proper testing, accessibility, and security
- ✅ Validate your work against professional standards

### What Makes This Different

**Before AgentSpec:**
- Inconsistent code quality from AI assistants
- Missing security and accessibility features
- No systematic approach to validation
- Difficulty maintaining standards across projects

**With AgentSpec:**
- Consistent, high-quality code generation
- Built-in security and accessibility compliance
- Systematic validation and quality gates
- Standardized practices across all projects

You're now ready to use AgentSpec for any project - from simple apps to complex enterprise systems!
