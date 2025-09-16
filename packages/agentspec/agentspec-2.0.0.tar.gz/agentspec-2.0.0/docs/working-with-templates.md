# Working with Templates

Templates are pre-configured sets of instructions for specific project types. They're the easiest way to get started with AgentSpec because they provide proven combinations of instructions that work well together.

## Understanding Templates

Think of templates like recipe collections - each template contains the right mix of instructions for a specific type of project.

## Available Templates (15 Total)

AgentSpec provides 15 templates organized into 4 categories:

### 🔧 Technology Templates (5)
Focus on specific programming languages or frameworks:

- **React Frontend** (`react_app`) - Modern React applications with TypeScript
- **Vue Frontend** (`vue-frontend`) - Vue.js applications with modern tooling
- **Python API** (`python-api`) - Python REST APIs using FastAPI
- **Node.js API** (`nodejs-api`) - Node.js REST APIs with Express
- **Mobile App** (`mobile-app`) - Cross-platform mobile applications

### 🏢 Domain Templates (5)
Focus on specific business domains or industries:

- **SaaS Application** (`saas-application`) - Multi-tenant SaaS platforms
- **E-commerce Application** (`ecommerce-application`) - Online retail and marketplace platforms
- **Fintech Application** (`fintech-application`) - Financial technology applications
- **Healthcare Application** (`healthcare-application`) - HIPAA-compliant healthcare applications
- **Data Science Application** (`data-science-application`) - ML and analytics platforms

### 🏗️ Architecture Templates (3)
Focus on system design and structure:

- **Web Application** (`web-application`) - Generic web application foundation
- **Enterprise Web Application** (`enterprise-web-application`) - Large-scale enterprise applications
- **Microservice** (`microservice`) - Distributed microservice architectures

### 📋 Methodology Templates (2)
Focus on development approaches:

- **AI-Assisted Development** (`ai-assisted-development`) - AI-assisted development workflows
- **Security-Focused Development** (`security-focused-development`) - High-security enterprise applications

## How to Use Templates

### 1. List Available Templates

See all templates with descriptions:

```bash
agentspec list-templates
```

Example output:
```
All templates (15 total):
========================

## TECHNOLOGY

React Frontend (ID: react-frontend)
  Version: 1.0.0
  Description: Modern React applications with TypeScript
  Technologies: react, typescript, webpack

Python API (ID: python-api)
  Version: 1.0.0
  Description: Python REST APIs using FastAPI
  Technologies: python, fastapi, postgresql

## DOMAIN

SaaS Application (ID: saas-application)
  Version: 1.0.0
  Description: Multi-tenant SaaS platforms
  Technologies: react, python, postgresql, stripe
```

### 2. Generate Instructions from Template

Use a template to generate instructions:

```bash
# Generate React frontend instructions
agentspec generate --template react_app --output react-instructions.md

# Generate Python API instructions
agentspec generate --template python-api --output api-instructions.md

# Generate e-commerce instructions
agentspec generate --template ecommerce-application --output ecommerce-instructions.md
```

### 3. Get Template Recommendations

Let AgentSpec analyze your project and suggest templates:

```bash
# Analyze current project and suggest templates
agentspec analyze . --output analysis.json

# The analysis will include template recommendations
```

## Template Details

### Technology Templates

#### React Frontend
**Best for:** Modern web applications with React
**Includes instructions for:**
- React component architecture and hooks
- TypeScript integration and type safety
- Modern CSS and responsive design
- Accessibility (WCAG 2.1 AA compliance)
- Testing with Jest and React Testing Library
- Performance optimization
- Build tools and deployment

**Example use cases:**
- Single-page applications (SPAs)
- Progressive web apps (PWAs)
- Admin dashboards
- Customer portals

#### Vue Frontend
**Best for:** Vue.js web applications
**Includes instructions for:**
- Vue 3 composition API
- TypeScript integration
- Vuex state management
- Vue Router for navigation
- Testing with Vue Test Utils
- Performance optimization

#### Python API
**Best for:** Backend services and REST APIs
**Includes instructions for:**
- FastAPI framework setup
- Pydantic models and validation
- Database integration (SQLAlchemy)
- Authentication and authorization
- API documentation (OpenAPI/Swagger)
- Testing with pytest
- Docker containerization

#### Node.js API
**Best for:** JavaScript/TypeScript backend services
**Includes instructions for:**
- Express.js framework
- TypeScript configuration
- Database integration (Prisma/TypeORM)
- Authentication (JWT, OAuth)
- API validation and error handling
- Testing with Jest
- Performance monitoring

#### Mobile App
**Best for:** Cross-platform mobile applications
**Includes instructions for:**
- React Native or Flutter setup
- Native module integration
- State management
- Navigation patterns
- Offline functionality
- App store deployment
- Performance optimization

### Domain Templates

#### SaaS Application
**Best for:** Multi-tenant software-as-a-service platforms
**Includes instructions for:**
- Multi-tenancy architecture
- Subscription and billing integration (Stripe)
- User management and authentication
- Analytics and metrics tracking
- Scalable database design
- API rate limiting
- Security and compliance (GDPR, SOC 2)

#### E-commerce Application
**Best for:** Online retail and marketplace platforms
**Includes instructions for:**
- Product catalog management
- Shopping cart and checkout flow
- Payment processing (multiple providers)
- Inventory management
- Order fulfillment
- Customer reviews and ratings
- SEO optimization
- Performance for high traffic

#### Fintech Application
**Best for:** Financial technology applications
**Includes instructions for:**
- PCI DSS compliance
- Secure payment processing
- Financial data handling
- Regulatory compliance (KYC, AML)
- Audit trails and logging
- Real-time transaction processing
- Risk management
- Data encryption

#### Healthcare Application
**Best for:** HIPAA-compliant healthcare applications
**Includes instructions for:**
- HIPAA compliance requirements
- Patient data security
- Electronic health records (EHR)
- Telemedicine features
- Medical device integration
- Audit logging
- Access controls
- Data backup and recovery

#### Data Science Application
**Best for:** ML and analytics platforms
**Includes instructions for:**
- Data pipeline architecture
- Machine learning model deployment
- Data visualization
- ETL processes
- Model versioning and monitoring
- Jupyter notebook integration
- Big data processing
- API endpoints for ML models

### Architecture Templates

#### Web Application
**Best for:** General-purpose web applications
**Includes instructions for:**
- Modern web architecture patterns
- Frontend-backend separation
- RESTful API design
- Database design and optimization
- Caching strategies
- Security best practices
- Testing strategies
- Deployment and DevOps

#### Enterprise Web Application
**Best for:** Large-scale enterprise applications
**Includes instructions for:**
- Microservices architecture
- Enterprise security requirements
- Scalability and performance
- Integration with enterprise systems
- Compliance and governance
- Advanced monitoring and logging
- Disaster recovery
- Team collaboration patterns

#### Microservice
**Best for:** Distributed microservice architectures
**Includes instructions for:**
- Service decomposition strategies
- Inter-service communication
- API gateway patterns
- Service discovery
- Circuit breaker patterns
- Distributed tracing
- Container orchestration
- DevOps for microservices

### Methodology Templates

#### AI-Assisted Development
**Best for:** Projects using AI coding assistants
**Includes instructions for:**
- Human-in-the-loop architecture
- Prompt engineering best practices
- AI code validation workflows
- Security guardrails for AI-generated code
- Context management across AI sessions
- Quality assurance for AI assistance
- Team collaboration with AI tools

#### Security-Focused Development
**Best for:** High-security enterprise applications
**Includes instructions for:**
- Threat modeling
- Secure coding practices
- Security testing (SAST, DAST)
- Compliance frameworks (SOC 2, ISO 27001)
- Incident response planning
- Security monitoring
- Penetration testing
- Security training requirements

## Choosing the Right Template

### By Project Type

**Building a web frontend?**
- Use **React Frontend** for React projects
- Use **Vue Frontend** for Vue.js projects

**Building an API or backend?**
- Use **Python API** for Python/FastAPI projects
- Use **Node.js API** for JavaScript/TypeScript projects

**Building a mobile app?**
- Use **Mobile App** for React Native or Flutter projects

**Building a complete web application?**
- Use **Web Application** for general web apps
- Use **Enterprise Web Application** for large-scale systems
- Use **Microservice** for distributed architectures

### By Industry/Domain

**Building a business application?**
- Use **SaaS Application** for subscription-based software
- Use **E-commerce Application** for online retail
- Use **Fintech Application** for financial services
- Use **Healthcare Application** for medical software
- Use **Data Science Application** for ML/analytics platforms

### By Development Approach

**Using AI coding assistants?**
- Use **AI-Assisted Development** for AI-enhanced workflows

**Security is critical?**
- Use **Security-Focused Development** for high-security requirements

### Decision Matrix

| Project Type | Recommended Template | Alternative |
|--------------|---------------------|-------------|
| React SPA | `react_app` | `web-application` |
| Vue.js App | `vue-frontend` | `web-application` |
| REST API (Python) | `python-api` | `web-application` |
| REST API (Node.js) | `nodejs-api` | `web-application` |
| Mobile App | `mobile-app` | - |
| Online Store | `ecommerce-application` | `web-application` |
| SaaS Platform | `saas-application` | `enterprise-web-application` |
| Banking App | `fintech-application` | `security-focused-development` |
| Medical App | `healthcare-application` | `security-focused-development` |
| ML Platform | `data-science-application` | `python-api` |
| Enterprise System | `enterprise-web-application` | `microservice` |
| Distributed System | `microservice` | `enterprise-web-application` |

## Customizing Templates

### Adding Extra Instructions

You can add additional instructions to any template:

```bash
# Add security and performance instructions to React template
agentspec generate \
  --template react-frontend \
  --tags +security,+performance \
  --output enhanced-react-instructions.md
```

### Excluding Instructions

Remove instructions that don't apply to your project:

```bash
# Generate template but exclude certain instructions
agentspec generate \
  --template python-api \
  --exclude database,docker \
  --output simple-api-instructions.md
```

### Combining Templates

For complex projects, you might need multiple templates:

```bash
# Generate frontend instructions
agentspec generate --template react-frontend --output frontend-instructions.md

# Generate backend instructions
agentspec generate --template python-api --output backend-instructions.md

# Combine them for full-stack development
```

## Template Examples

### Example 1: E-commerce React App

```bash
# Perfect for online stores with React frontend
agentspec generate --template ecommerce-application --output store-instructions.md
```

**What you get:**
- React component architecture
- Payment processing guidelines
- Security best practices
- Performance optimization
- SEO requirements
- Accessibility compliance
- Testing strategies

### Example 2: Healthcare API

```bash
# Perfect for medical applications requiring HIPAA compliance
agentspec generate --template healthcare-application --output medical-api-instructions.md
```

**What you get:**
- HIPAA compliance requirements
- Secure data handling
- Audit logging
- Access controls
- API security
- Testing for healthcare data
- Deployment security

### Example 3: Fintech Mobile App

```bash
# Combine fintech domain with mobile technology
agentspec generate --template fintech-application --output fintech-instructions.md
agentspec generate --template mobile-app --output mobile-instructions.md
```

**What you get:**
- Financial compliance requirements
- Mobile security best practices
- Payment processing
- Biometric authentication
- Offline functionality
- App store guidelines

## Best Practices for Templates

### 1. Start with the Closest Match

Choose the template that most closely matches your project type, even if it's not perfect. You can always customize it.

### 2. Understand What's Included

Before using a template, review what instructions it includes:

```bash
# See detailed template information
agentspec list-templates --verbose
```

### 3. Customize for Your Needs

Don't feel locked into the template - add or remove instructions as needed for your specific project.

### 4. Use Multiple Templates for Complex Projects

For full-stack applications, consider using separate templates for frontend and backend components.

### 5. Keep Templates Updated

As your project evolves, regenerate instructions to include new requirements:

```bash
# Regenerate with additional requirements
agentspec generate --template react-frontend --tags +accessibility,+performance --output updated-instructions.md
```

## Common Template Combinations

### Full-Stack Web Application
```bash
# Frontend
agentspec generate --template react-frontend --output frontend-instructions.md

# Backend
agentspec generate --template python-api --output backend-instructions.md
```

### SaaS Platform with Mobile App
```bash
# Web platform
agentspec generate --template saas-application --output web-instructions.md

# Mobile app
agentspec generate --template mobile-app --output mobile-instructions.md
```

### Enterprise System
```bash
# Main application
agentspec generate --template enterprise-web-application --output main-instructions.md

# Microservices
agentspec generate --template microservice --output service-instructions.md
```

## Next Steps

Now that you understand templates:

- **[Your First Project](your-first-project.md)** - Complete step-by-step tutorial
- **[Core Concepts](core-concepts.md)** - Deeper understanding of AgentSpec
- **[Command Line Guide](command-line-guide.md)** - Master all CLI commands
- **[Instructions Reference](instructions-reference.md)** - Browse all available instructions
- **[Examples](examples/)** - See templates in action

## Need Help?

- **[Quick Start](quick-start.md)** - Get up and running in 5 minutes
- **[GitHub Issues](https://github.com/keyurgolani/AgentSpec/issues)** - Report problems or request features
- **[GitHub Discussions](https://github.com/keyurgolani/AgentSpec/discussions)** - Ask questions and share experiences
