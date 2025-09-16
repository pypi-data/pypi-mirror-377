# Templates Reference

Complete reference for all 15 templates available in AgentSpec.

## Template Categories

Templates are organized into 4 categories:

- **Technology** (5 templates) - Specific programming languages/frameworks
- **Domain** (5 templates) - Business domains and industries
- **Architecture** (3 templates) - System design patterns
- **Methodology** (2 templates) - Development approaches

## Technology Templates

### React Frontend (`react_app`)

**Best for:** Modern React web applications
**Version:** 1.0.0
**Technologies:** React, TypeScript, Vite, Jest, Tailwind CSS

**Includes instructions for:**
- React component architecture with hooks
- TypeScript integration and type safety
- Modern CSS and responsive design
- Accessibility (WCAG 2.1 AA compliance)
- Testing with Jest and React Testing Library
- Performance optimization
- Build tools and deployment

**Use when building:**
- Single-page applications (SPAs)
- Progressive web apps (PWAs)
- Admin dashboards
- Customer portals

**Example:**
```bash
agentspec generate --template react_app --output react-instructions.md
```

### Vue Frontend (`vue-frontend`)

**Best for:** Vue.js web applications
**Version:** 1.0.0
**Technologies:** Vue 3, TypeScript, Vite, Pinia

**Includes instructions for:**
- Vue 3 Composition API
- TypeScript integration
- Vuex/Pinia state management
- Vue Router for navigation
- Testing with Vue Test Utils
- Performance optimization

**Use when building:**
- Vue.js single-page applications
- Progressive web apps with Vue
- Component libraries
- Admin interfaces

**Example:**
```bash
agentspec generate --template vue-frontend --output vue-instructions.md
```

### Python API (`python-api`)

**Best for:** Backend services and REST APIs
**Version:** 1.0.0
**Technologies:** Python, FastAPI, SQLAlchemy, PostgreSQL

**Includes instructions for:**
- FastAPI framework setup
- Pydantic models and validation
- Database integration (SQLAlchemy)
- Authentication and authorization
- API documentation (OpenAPI/Swagger)
- Testing with pytest
- Docker containerization

**Use when building:**
- REST APIs
- Microservices
- Data processing services
- Integration services

**Example:**
```bash
agentspec generate --template python-api --output api-instructions.md
```

### Node.js API (`nodejs-api`)

**Best for:** JavaScript/TypeScript backend services
**Version:** 1.0.0
**Technologies:** Node.js, Express, TypeScript, Prisma

**Includes instructions for:**
- Express.js framework
- TypeScript configuration
- Database integration (Prisma/TypeORM)
- Authentication (JWT, OAuth)
- API validation and error handling
- Testing with Jest
- Performance monitoring

**Use when building:**
- REST APIs with Node.js
- Real-time services (WebSocket)
- GraphQL APIs
- Serverless functions

**Example:**
```bash
agentspec generate --template nodejs-api --output nodejs-instructions.md
```

### Mobile App (`mobile-app`)

**Best for:** Cross-platform mobile applications
**Version:** 1.0.0
**Technologies:** React Native, TypeScript, Expo

**Includes instructions for:**
- React Native or Flutter setup
- Native module integration
- State management (Redux/MobX)
- Navigation patterns
- Offline functionality
- App store deployment
- Performance optimization

**Use when building:**
- iOS and Android apps
- Cross-platform mobile apps
- Hybrid applications
- Mobile-first PWAs

**Example:**
```bash
agentspec generate --template mobile-app --output mobile-instructions.md
```

## Domain Templates

### SaaS Application (`saas-application`)

**Best for:** Multi-tenant software-as-a-service platforms
**Version:** 1.0.0
**Technologies:** React, Python, PostgreSQL, Stripe

**Includes instructions for:**
- Multi-tenancy architecture
- Subscription and billing integration (Stripe)
- User management and authentication
- Analytics and metrics tracking
- Scalable database design
- API rate limiting
- Security and compliance (GDPR, SOC 2)

**Use when building:**
- Subscription-based software
- B2B SaaS platforms
- Multi-tenant applications
- Business software tools

**Example:**
```bash
agentspec generate --template saas-application --output saas-instructions.md
```

### E-commerce Application (`ecommerce-application`)

**Best for:** Online retail and marketplace platforms
**Version:** 1.0.0
**Technologies:** React, Node.js, PostgreSQL, Stripe

**Includes instructions for:**
- Product catalog management
- Shopping cart and checkout flow
- Payment processing (multiple providers)
- Inventory management
- Order fulfillment
- Customer reviews and ratings
- SEO optimization
- Performance for high traffic

**Use when building:**
- Online stores
- Marketplace platforms
- B2B e-commerce
- Digital product sales

**Example:**
```bash
agentspec generate --template ecommerce-application --output ecommerce-instructions.md
```

### Fintech Application (`fintech-application`)

**Best for:** Financial technology applications
**Version:** 1.0.0
**Technologies:** React, Python, PostgreSQL, Redis

**Includes instructions for:**
- PCI DSS compliance
- Secure payment processing
- Financial data handling
- Regulatory compliance (KYC, AML)
- Audit trails and logging
- Real-time transaction processing
- Risk management
- Data encryption

**Use when building:**
- Banking applications
- Payment processors
- Investment platforms
- Cryptocurrency exchanges
- Financial dashboards

**Example:**
```bash
agentspec generate --template fintech-application --output fintech-instructions.md
```

### Healthcare Application (`healthcare-application`)

**Best for:** HIPAA-compliant healthcare applications
**Version:** 1.0.0
**Technologies:** React, Python, PostgreSQL, Redis

**Includes instructions for:**
- HIPAA compliance requirements
- Patient data security
- Electronic health records (EHR)
- Telemedicine features
- Medical device integration
- Audit logging
- Access controls
- Data backup and recovery

**Use when building:**
- Electronic health records
- Telemedicine platforms
- Medical device software
- Healthcare analytics
- Patient portals

**Example:**
```bash
agentspec generate --template healthcare-application --output healthcare-instructions.md
```

### Data Science Application (`data-science-application`)

**Best for:** ML and analytics platforms
**Version:** 1.0.0
**Technologies:** Python, Jupyter, PostgreSQL, Redis

**Includes instructions for:**
- Data pipeline architecture
- Machine learning model deployment
- Data visualization
- ETL processes
- Model versioning and monitoring
- Jupyter notebook integration
- Big data processing
- API endpoints for ML models

**Use when building:**
- Machine learning platforms
- Data analytics dashboards
- ETL pipelines
- Model serving APIs
- Research platforms

**Example:**
```bash
agentspec generate --template data-science-application --output datascience-instructions.md
```

## Architecture Templates

### Web Application (`web-application`)

**Best for:** General-purpose web applications
**Version:** 1.0.0
**Technologies:** React, Node.js, PostgreSQL

**Includes instructions for:**
- Modern web architecture patterns
- Frontend-backend separation
- RESTful API design
- Database design and optimization
- Caching strategies
- Security best practices
- Testing strategies
- Deployment and DevOps

**Use when building:**
- General web applications
- Content management systems
- Business applications
- Portfolio websites

**Example:**
```bash
agentspec generate --template web-application --output webapp-instructions.md
```

### Enterprise Web Application (`enterprise-web-application`)

**Best for:** Large-scale enterprise applications
**Version:** 1.0.0
**Technologies:** React, Java/Python, PostgreSQL, Redis

**Includes instructions for:**
- Microservices architecture
- Enterprise security requirements
- Scalability and performance
- Integration with enterprise systems
- Compliance and governance
- Advanced monitoring and logging
- Disaster recovery
- Team collaboration patterns

**Use when building:**
- Enterprise software
- Large-scale systems
- Corporate applications
- Mission-critical systems

**Example:**
```bash
agentspec generate --template enterprise-web-application --output enterprise-instructions.md
```

### Microservice (`microservice`)

**Best for:** Distributed microservice architectures
**Version:** 1.0.0
**Technologies:** Docker, Kubernetes, API Gateway

**Includes instructions for:**
- Service decomposition strategies
- Inter-service communication
- API gateway patterns
- Service discovery
- Circuit breaker patterns
- Distributed tracing
- Container orchestration
- DevOps for microservices

**Use when building:**
- Distributed systems
- Scalable architectures
- Cloud-native applications
- Service-oriented architectures

**Example:**
```bash
agentspec generate --template microservice --output microservice-instructions.md
```

## Methodology Templates

### AI-Assisted Development (`ai-assisted-development`)

**Best for:** Projects using AI coding assistants
**Version:** 1.0.0
**Technologies:** Any (methodology-focused)

**Includes instructions for:**
- Human-in-the-loop architecture
- Prompt engineering best practices
- AI code validation workflows
- Security guardrails for AI-generated code
- Context management across AI sessions
- Quality assurance for AI assistance
- Team collaboration with AI tools

**Use when building:**
- Any project with AI assistance
- Teams adopting AI tools
- AI-enhanced workflows
- Quality-focused AI development

**Example:**
```bash
agentspec generate --template ai-assisted-development --output ai-instructions.md
```

### Security-Focused Development (`security-focused-development`)

**Best for:** High-security enterprise applications
**Version:** 1.0.0
**Technologies:** Any (security-focused)

**Includes instructions for:**
- Threat modeling
- Secure coding practices
- Security testing (SAST, DAST)
- Compliance frameworks (SOC 2, ISO 27001)
- Incident response planning
- Security monitoring
- Penetration testing
- Security training requirements

**Use when building:**
- High-security applications
- Government systems
- Financial services
- Healthcare systems
- Defense applications

**Example:**
```bash
agentspec generate --template security-focused-development --output security-instructions.md
```

## Template Selection Guide

### By Project Type

| Project Type | Primary Template | Alternative |
|--------------|------------------|-------------|
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

### By Industry

| Industry | Recommended Template | Reason |
|----------|---------------------|---------|
| Software/Tech | `saas-application` | Multi-tenancy, subscriptions |
| Retail/E-commerce | `ecommerce-application` | Payment processing, inventory |
| Finance/Banking | `fintech-application` | Compliance, security |
| Healthcare | `healthcare-application` | HIPAA compliance |
| Research/Analytics | `data-science-application` | ML pipelines, data processing |
| Enterprise/Corporate | `enterprise-web-application` | Scalability, integration |

### By Team Size

| Team Size | Recommended Template | Reason |
|-----------|---------------------|---------|
| 1-3 developers | Technology templates | Simple, focused |
| 4-10 developers | Domain templates | Business-focused |
| 10+ developers | Architecture templates | Scalability, structure |
| Enterprise teams | `enterprise-web-application` | Governance, standards |

## Using Templates

### Basic Usage

```bash
# Generate instructions from template
agentspec generate --template TEMPLATE_ID --output instructions.md

# List all templates
agentspec list-templates

# Get template details
agentspec list-templates --verbose
```

### Customization

```bash
# Add extra instructions
agentspec generate --template react_app --tags security,performance

# Combine templates (generate separately)
agentspec generate --template react_app --output frontend.md
agentspec generate --template python-api --output backend.md
```

### Template Recommendations

```bash
# Get recommendations based on project analysis
agentspec analyze . --output analysis.json
# Review analysis.json for template suggestions
```

## Next Steps

- **[Working with Templates](working-with-templates.md)** - Detailed guide on using templates
- **[Instructions Reference](instructions-reference.md)** - Browse all 107 instructions
- **[Your First Project](your-first-project.md)** - Step-by-step tutorial
- **[Command Line Guide](command-line-guide.md)** - Complete CLI reference
