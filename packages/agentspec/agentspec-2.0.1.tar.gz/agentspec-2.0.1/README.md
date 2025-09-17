# AgentSpec

[![Tests](https://github.com/keyurgolani/AgentSpec/workflows/CI/badge.svg)](https://github.com/keyurgolani/AgentSpec/actions)
[![Coverage](https://codecov.io/gh/keyurgolani/AgentSpec/branch/main/graph/badge.svg)](https://codecov.io/gh/keyurgolani/AgentSpec)
[![PyPI version](https://badge.fury.io/py/agentspec.svg)](https://badge.fury.io/py/agentspec)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**Transform AI Code Generation with Professional Instructions**

AgentSpec creates comprehensive instruction guides that transform AI coding assistants (GitHub Copilot, ChatGPT, Claude) from basic code generators into professional development partners. Get production-ready code that follows industry best practices, security standards, and your specific project requirements.

## 🚀 Quick Start

```bash
# Install AgentSpec
pip install agentspec

# Generate instructions for a React app
agentspec generate --template react_app --output react-instructions.md

# Generate instructions for a Python API
agentspec generate --template python-api --output api-instructions.md

# Let AgentSpec analyze your existing project
agentspec analyze ./my-project

# Interactive wizard to guide you through the process
agentspec interactive
```

**What you get:** A comprehensive instruction file that transforms your AI assistant into a professional development partner, ensuring consistent, high-quality code generation.

## ✨ What AgentSpec Does

- **📋 Smart Instructions**: 106 proven coding guidelines organized by technology and domain
- **🎯 Ready-Made Templates**: 15 project templates for common scenarios (React apps, Python APIs, etc.)
- **🔍 Project Analysis**: Automatically detects your tech stack and suggests relevant instructions
- **🤖 AI-Friendly Format**: Instructions designed specifically for AI coding assistants
- **🔒 Security Built-In**: Includes security best practices and vulnerability prevention
- **✅ Quality Focused**: Ensures AI generates professional-grade, tested code

## 🎯 How It Works

### 1. Choose Your Project Type
Pick from 15 templates like "React App", "Python API", "E-commerce Site", etc.

### 2. Get Custom Instructions
AgentSpec generates a detailed instruction file tailored to your project.

### 3. Share with AI
Give the instructions to your AI coding assistant (ChatGPT, Copilot, Claude, etc.).

### 4. Get Better Code
Your AI now follows professional standards and best practices automatically.

## 📋 Available Templates

AgentSpec includes 15 ready-to-use templates:

**Technology Templates:**
- `react_app` - React web applications with TypeScript
- `python-api` - Python REST APIs with FastAPI
- `nodejs-api` - Node.js APIs with Express
- `vue-frontend` - Vue.js applications
- `mobile-app` - Cross-platform mobile apps

**Domain Templates:**
- `saas-application` - SaaS platforms with billing
- `ecommerce-application` - Online stores and marketplaces
- `fintech-application` - Financial applications
- `healthcare-application` - Healthcare platforms
- `data-science-application` - ML and analytics platforms

**Architecture Templates:**
- `web-application` - General web applications
- `enterprise-web-application` - Large-scale enterprise apps
- `microservice` - Microservice architectures

**Methodology Templates:**
- `ai-assisted-development` - AI-first development practices
- `security-focused-development` - Security-critical applications

## 🛠️ Usage Examples

### For New Projects

```bash
# React web application
agentspec generate --template react_app --output react-instructions.md

# Python REST API
agentspec generate --template python-api --output api-instructions.md

# E-commerce platform
agentspec generate --template ecommerce-application --output ecommerce-instructions.md

# SaaS application
agentspec generate --template saas-application --output saas-instructions.md
```

### For Existing Projects

```bash
# Let AgentSpec analyze your project and suggest instructions
agentspec analyze ./my-project

# Generate instructions based on detected technologies
agentspec generate --project-path ./my-project --tags auto --output project-instructions.md
```

### Interactive Mode

```bash
# Guided setup with questions and recommendations
agentspec interactive
```

### Browse Available Options

```bash
# See all templates
agentspec list-templates

# See all instruction categories
agentspec list-tags

# See specific instructions
agentspec list-instructions --tag testing
```

## 💡 Real Example

**Without AgentSpec:**
```
You: "Create a React login form"
AI: Creates basic form with no validation, security issues, no tests
```

**With AgentSpec:**
```
You: "Create a React login form" + AgentSpec instructions
AI: Creates form with:
- Input validation and error handling
- Security best practices (CSRF protection, etc.)
- Accessibility features (ARIA labels, keyboard navigation)
- Comprehensive tests (unit, integration, accessibility)
- TypeScript types and proper documentation
- Performance optimization and loading states
```

The difference: **Production-ready code that follows industry best practices.**

## 📚 Documentation

**New to AgentSpec?**
- **[What is AgentSpec?](docs/what-is-agentspec.md)** - Simple explanation for beginners
- **[Quick Start Guide](docs/quick-start.md)** - Get running in 5 minutes
- **[Your First Project](docs/your-first-project.md)** - Complete step-by-step tutorial

**Reference & Guides:**
- **[Core Concepts](docs/core-concepts.md)** - Understanding instructions, templates, and specs
- **[Command Line Guide](docs/command-line-guide.md)** - Complete CLI reference
- **[Working with Templates](docs/working-with-templates.md)** - Using and customizing templates

**Advanced:**
- **[Instructions Reference](docs/instructions-reference.md)** - All available instructions
- **[Templates Reference](docs/templates-reference.md)** - All available templates
- **[API Documentation](docs/api-reference.md)** - Python API for advanced usage
- **[Examples](examples/)** - Real-world project examples

## 🏷️ Available Templates & Tags

### Templates by Category

**Technology Templates:**
- `react_app` - React applications with TypeScript
- `python-api` - Python REST APIs with FastAPI
- `nodejs-api` - Node.js APIs with Express
- `vue-frontend` - Vue.js applications
- `mobile-app` - Cross-platform mobile apps

**Domain Templates:**
- `saas-application` - SaaS platforms with billing
- `ecommerce-application` - E-commerce platforms
- `fintech-application` - Financial applications
- `healthcare-application` - Healthcare platforms
- `data-science-application` - ML and data platforms

**Architecture Templates:**
- `web-application` - General web applications
- `enterprise-web-application` - Enterprise-scale apps
- `microservice` - Microservice architectures

**Methodology Templates:**
- `ai-assisted-development` - AI-first development
- `security-focused-development` - Security-critical apps

### Instruction Categories

**Core Instructions (Always Included):**
- `core` - Fundamental development practices (25 instructions)
- `workflow` - Development workflow and process (included in core)

**Specialized Instructions:**
- `frontend` - Frontend development (12 instructions)
- `backend` - Backend development (15 instructions)
- `testing` - Testing strategies (9 instructions)
- `security` - Security practices (distributed across categories)
- `performance` - Performance optimization (distributed across categories)

**Technology-Specific:**
- `python`, `javascript`, `typescript` - Language-specific guidelines
- `react`, `vue`, `angular` - Framework-specific practices
- `api`, `database`, `docker` - Technology-specific instructions

## 🔧 Who Should Use AgentSpec?

**Perfect for:**
- **Developers using AI assistants** (GitHub Copilot, ChatGPT, Claude, etc.)
- **Teams** who want consistent coding standards
- **Beginners** learning best practices
- **Experienced developers** scaling their knowledge

**Especially useful if you:**
- Want AI to generate professional-grade code, not just examples
- Need to ensure security and quality in AI-generated code
- Want consistent standards across projects and team members
- Are building production applications with AI assistance

## 🚀 Getting Started

### For Complete Beginners

**Never used AgentSpec before?**

1. **Learn what it does:** Read [What is AgentSpec?](docs/what-is-agentspec.md)
2. **Try it out:** Follow the [Quick Start Guide](docs/quick-start.md) (5 minutes)
3. **Build something:** Complete [Your First Project](docs/your-first-project.md) tutorial

### For Experienced Developers

**Ready to jump in?**

1. **Install:** `pip install agentspec`
2. **Generate instructions:** `agentspec generate --template react_app --output instructions.md`
3. **Share with AI:** Copy instructions.md content to your AI assistant
4. **Start coding:** Ask AI to build features following the instructions

### Need Help Choosing?

- **Interactive setup:** `agentspec interactive` for guided template selection
- **Project analysis:** `agentspec analyze .` to analyze existing projects
- **Browse templates:** `agentspec list-templates` to see all options
- **Get recommendations:** Check the [Templates Guide](docs/working-with-templates.md)

## 🔧 Troubleshooting

**Common issues and solutions:**

**Installation problems:**
```bash
# If pip install fails, try:
pip install --upgrade pip
pip install agentspec

# For Python 3.8 compatibility issues:
pip install "agentspec[dev]" --no-deps
```

**Command not found:**
```bash
# Make sure AgentSpec is in your PATH
which agentspec

# Or run as module:
python -m agentspec --version
```

**Template not working:**
```bash
# List available templates:
agentspec list-templates

# Use exact template ID:
agentspec generate --template react_app --output instructions.md
```

**Need more help?** Check our [GitHub Discussions](https://github.com/keyurgolani/AgentSpec/discussions)

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

```bash
# Quick development setup
git clone https://github.com/keyurgolani/AgentSpec.git
cd AgentSpec
pip install -e ".[dev]"
pytest
```

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🌟 Why AgentSpec Works

- **Proven Instructions**: Based on industry best practices and real-world experience
- **AI-Optimized**: Instructions written specifically for AI understanding
- **Comprehensive**: Covers security, testing, performance, accessibility, and more
- **Flexible**: Works with any AI assistant and any project type
- **Time-Saving**: Get professional code faster than writing detailed prompts every time

## 🚀 Quick Links

**New to AgentSpec?**
- **[What is AgentSpec?](docs/what-is-agentspec.md)** - Simple explanation
- **[Quick Start](docs/quick-start.md)** - Get running in 5 minutes
- **[Your First Project](docs/your-first-project.md)** - Complete tutorial

**Ready to use?**
- **[Examples](examples/)** - Real-world project examples
- **[Command Reference](docs/command-line-guide.md)** - All CLI commands
- **[Templates](docs/templates-reference.md)** - Browse all templates

---

**Get better AI code with AgentSpec - professional instructions for professional results.**
