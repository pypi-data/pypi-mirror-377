# Instructions Reference

Complete reference for all 106 instructions available in AgentSpec, organized by category.

## How Instructions Work

Instructions are specific guidelines that tell AI assistants how to code properly. Each instruction includes:
- **ID**: Unique identifier
- **Tags**: Categories it belongs to
- **Content**: The actual guideline text
- **Priority**: Importance level (1-10)

## Core Instructions (Always Included)

These 25 instructions are automatically included in every specification because they represent fundamental development practices that apply to all projects:

### Core Workflow Instructions

These instructions establish fundamental development practices and are automatically included in every specification:

#### Planning & Reflection
- **Plan and Reflect** - Plan thoroughly before every action and reflect on outcomes
- **Use Tools Don't Guess** - Verify information rather than making assumptions
- **Persist Until Complete** - Continue until tasks are fully solved

#### Context & Analysis
- **Context Management** - Maintain project contexts and project state
- **Thorough Analysis** - Begin tasks with comprehensive code analysis
- **Systematic Debugging** - Use methodical debugging approaches

#### Development Process
- **Incremental Development** - Build features incrementally with validation
- **Error Recovery** - Analyze root causes and implement proper fixes
- **Continuous Validation Loop** - Validate continuously throughout development

#### Quality Standards
- **No Error Policy** - Ensure zero linting, compilation, or build errors
- **Avoid Vibe Coding** - Use disciplined coding with clear requirements

#### AI Collaboration
- **Human-in-the-Loop Architecture** - Maintain developer control over AI assistance
- **AI Code Understanding Requirement** - Never commit code you don't understand
- **Prompt Engineering Discipline** - Use structured prompt engineering techniques

#### Project Setup
- **Project Initialization** - Set up proper project structure and tooling
- **Dependency Management** - Use lock files and audit dependencies
- **Environment Configuration** - Use environment variables for configuration
- **Code Formatting** - Set up automated code formatting
- **Editor Configuration** - Provide consistent editor settings

#### Security Fundamentals
- **Secure Coding Practices** - Follow OWASP secure coding guidelines
- **Secrets Management** - Use dedicated secret management systems

#### Documentation & Learning
- **Documentation Tracking** - Keep documentation synchronized with code
- **Autonomous Decision Making** - Make informed decisions with documentation
- **Learning Adaptation** - Continuously improve development practices
- **Interactive Debugging Sessions** - Conduct effective debugging sessions

## Specialized Instructions by Category

Beyond the core instructions, AgentSpec provides 81 specialized instructions organized by category:

### Frontend Development (12 instructions)

Instructions for building modern user interfaces and web applications:

#### Component Architecture
- **Frontend State Management** - Implement proper state management patterns (Redux, Vuex, NgRx)
- **Component Architecture** - Build reusable, composable components with clear interfaces
- **Progressive Web App** - Implement PWA features with service workers and offline functionality

#### User Experience
- **Mobile Responsiveness** - Ensure full mobile responsiveness and touch-friendly interfaces
- **Accessibility Compliance** - Implement WCAG 2.1 AA compliance with proper ARIA labels
- **Performance Optimization** - Optimize frontend performance with lazy loading and caching

#### Modern Development
- **TypeScript Integration** - Use TypeScript with strict mode and proper type definitions
- **Modern CSS** - Use CSS Grid, Flexbox, and modern CSS features
- **Build Tools** - Configure modern build tools (Webpack, Vite, Parcel)

#### Testing & Quality
- **Frontend Testing** - Implement comprehensive frontend testing strategies
- **Cross-Browser Compatibility** - Ensure compatibility across different browsers
- **SEO Optimization** - Implement proper SEO practices for web applications

### Backend Development (15 instructions)

Instructions for building robust server-side applications and APIs:

#### API Development
- **API Design** - Follow RESTful principles with proper HTTP status codes and versioning
- **GraphQL Implementation** - Implement GraphQL APIs with proper schema design
- **API Documentation** - Create comprehensive API documentation with OpenAPI/Swagger

#### Database & Data
- **Database Optimization** - Optimize queries with proper indexing and connection pooling
- **Data Modeling** - Design efficient database schemas and relationships
- **Database Migrations** - Implement database migrations with rollback capabilities

#### Security & Authentication
- **Authentication & Authorization** - Implement secure authentication and authorization systems
- **Input Validation** - Validate and sanitize all input data
- **Rate Limiting** - Implement API rate limiting and throttling

#### Performance & Scalability
- **Caching Strategies** - Implement effective caching at multiple levels
- **Background Jobs** - Handle long-running tasks with background job processing
- **Load Balancing** - Design for horizontal scaling and load distribution

#### Integration & Communication
- **Message Queues** - Implement asynchronous communication with message queues
- **Third-Party Integrations** - Handle external API integrations with proper error handling
- **Webhook Handling** - Implement robust webhook processing with validation and retry logic

### Testing & Quality Assurance (8 instructions)

Comprehensive testing strategies and quality enforcement:

#### Testing Strategies
- **Test-Driven Development** - Write tests before implementing code
- **Comprehensive Test Suite** - Build unit, integration, and end-to-end tests
- **Test Automation** - Automate testing in CI/CD pipelines
- **Performance Testing** - Test application performance under load

#### Quality Control
- **Code Review Process** - Implement systematic code review practices
- **Static Code Analysis** - Use static analysis tools for code quality
- **Runtime Validation** - Validate application behavior in real environments
- **Quality Metrics** - Track and improve code quality metrics

### Frontend Development

Modern frontend development practices covering UI/UX, accessibility, and performance.

#### Frontend State Management
**Tags**: `frontend`, `state`, `react`, `vue`, `angular`

Implement proper state management patterns (Redux, Vuex, NgRx) for complex applications. Avoid prop drilling and ensure predictable state updates.

#### Accessibility Compliance
**Tags**: `accessibility`, `frontend`, `ui`, `compliance`

Ensure WCAG 2.1 AA compliance with proper ARIA labels, keyboard navigation, color contrast ratios, and screen reader compatibility.

#### Mobile Responsiveness
**Tags**: `frontend`, `mobile`, `responsive`, `ui`

Ensure full mobile responsiveness with touch-friendly interfaces, proper viewport settings, and performance optimization for mobile devices.

### Backend Development

Server-side development practices focusing on APIs, databases, and system architecture.

#### API Design
**Tags**: `api`, `design`, `rest`, `standards`

Follow RESTful principles with proper HTTP status codes, versioning, pagination, filtering, and comprehensive documentation. Implement consistent error responses.

#### Database Optimization
**Tags**: `database`, `performance`, `optimization`, `queries`

Optimize queries with proper indexing, connection pooling, and query analysis. Implement database migrations with rollback capabilities.

#### Security Best Practices
**Tags**: `security`, `authentication`, `authorization`, `validation`

Implement input validation, sanitization, authentication, secure headers, HTTPS, and proper session management. Never commit secrets to version control.

#### Error Handling
**Tags**: `error-handling`, `reliability`, `logging`, `debugging`

Implement comprehensive error handling with structured logging, user-friendly messages, and graceful degradation. Use appropriate log levels.

### Language-Specific Guidelines

#### TypeScript Safety
**Tags**: `typescript`, `javascript`, `type-safety`, `quality`

Never use 'any' types. Use proper type definitions, interfaces, and generics. Enable strict mode and resolve all type errors.

#### Python Type Hints
**Tags**: `python`, `type-safety`, `quality`, `documentation`

Use comprehensive type hints for all functions, parameters, return values, and class attributes. Import typing modules for complex types.

### DevOps & Infrastructure

Deployment, containerization, and operational practices.

#### Docker Containerization
**Tags**: `docker`, `deployment`, `containerization`, `devops`

Containerize with multi-stage Docker builds. Include development, testing, and production configurations. Use docker-compose for complex setups.

#### CI/CD Pipeline
**Tags**: `ci-cd`, `automation`, `deployment`, `testing`

Implement comprehensive CI/CD pipeline with automated testing, code quality checks, security scanning, and deployment automation.

#### Monitoring & Observability
**Tags**: `monitoring`, `observability`, `logging`, `metrics`

Implement comprehensive monitoring with metrics, logs, and traces. Set up alerts for critical failures and performance degradation.

#### Backup & Recovery
**Tags**: `backup`, `recovery`, `reliability`, `data`

Implement automated backup strategies with regular recovery testing. Document disaster recovery plans and RTO/RPO requirements.

### Architecture & Design

System architecture and design patterns for scalable applications.

#### Modular Architecture
**Tags**: `architecture`, `modularity`, `maintainability`, `refactoring`

Break large files into single-responsibility modules, eliminate duplicate code, remove dead code. Ensure each file has one clear conceptual responsibility.

#### Microservices Architecture
**Tags**: `architecture`, `microservices`, `scalability`, `distributed`

Design microservices with proper boundaries, communication patterns, and distributed system concerns like circuit breakers and bulkheads.

#### Performance Optimization
**Tags**: `performance`, `optimization`, `caching`, `efficiency`

Implement caching strategies, optimize database queries, use lazy loading, and monitor performance metrics. Profile code to identify bottlenecks.

### Advanced Features



#### Rate Limiting
**Tags**: `rate-limiting`, `api`, `security`, `performance`

Implement rate limiting with appropriate strategies (fixed window, sliding window, token bucket) based on use case requirements.

#### Webhook Handling
**Tags**: `webhooks`, `api`, `integration`, `reliability`

Implement robust webhook handling with validation, retry logic, idempotency, and security measures like signature verification.

#### Real-time Features
**Tags**: `realtime`, `websockets`, `sse`, `notifications`

Implement real-time features using WebSockets or Server-Sent Events with connection management, reconnection logic, and scalability considerations.

#### Search Functionality
**Tags**: `search`, `elasticsearch`, `indexing`, `performance`

Implement efficient search with proper indexing, full-text search capabilities, faceted search, and search analytics.

#### Payment Processing
**Tags**: `payments`, `security`, `integration`, `compliance`

Implement secure payment processing with PCI compliance, proper error handling, refund capabilities, and webhook handling for payment providers.

#### GDPR Compliance
**Tags**: `gdpr`, `privacy`, `compliance`, `data-protection`

Implement GDPR compliance with consent management, data portability, right to deletion, and privacy by design principles.

## Tag Reference

### By Category

| Category | Tags | Count |
|----------|------|-------|
| **Spec Workflow** | `spec-workflow`, `planning`, `verification`, `quality`, `methodology` | 11 (Always Included) |
| **General** | `general`, `standards`, `documentation`, `design` | 2 |
| **Testing** | `testing`, `tdd`, `validation`, `automation`, `browser` | 5 |
| **Frontend** | `frontend`, `ui`, `react`, `vue`, `angular`, `mobile`, `responsive` | 7 |
| **Backend** | `backend`, `api`, `database`, `security`, `performance` | 5 |
| **Languages** | `javascript`, `typescript`, `python`, `type-safety` | 4 |
| **DevOps** | `docker`, `ci-cd`, `deployment`, `monitoring`, `backup` | 5 |
| **Architecture** | `architecture`, `microservices`, `modularity`, `maintainability` | 4 |

### By Usage Frequency

| Tag | Instructions | Common Use Cases |
|-----|-------------|------------------|
| `spec-workflow` | 11 | All projects (always included) |
| `testing` | 3 | Quality assurance |
| `security` | 3 | Secure applications |
| `api` | 3 | Backend services |
| `frontend` | 2 | UI applications |
| `performance` | 2 | High-load systems |
| `database` | 2 | Data-driven apps |
| `general` | 2 | Project documentation |

## Spec Generation Examples

### Full-Stack Web Application
```bash
python agentspec.py --tags general,testing,frontend,backend,api,database,security,ci-cd
```

**Includes**: Context management, testing frameworks, UI guidelines, API design, database optimization, security practices, deployment automation.

### React Frontend Application
```bash
python agentspec.py --tags general,testing,frontend,react,typescript,accessibility,mobile
```

**Includes**: Component architecture, state management, type safety, accessibility compliance, responsive design.

### Python API Service
```bash
python agentspec.py --tags general,testing,python,api,database,security,monitoring
```

**Includes**: Type hints, API design, database optimization, security practices, observability.

### Microservices Architecture
```bash
python agentspec.py --tags general,testing,microservices,docker,ci-cd,monitoring,security
```

**Includes**: Service boundaries, containerization, deployment pipelines, distributed system patterns.

### Mobile-First Progressive Web App
```bash
python agentspec.py --tags general,testing,frontend,mobile,responsive,realtime,performance
```

**Includes**: Mobile optimization, responsive design, real-time features, performance optimization.

## Custom Instructions

### Adding New Instructions

To extend AgentSpec with custom instructions:

1. **Identify the practice**: What specific development practice does this address?
2. **Define appropriate tags**: Use existing tags when possible
3. **Write clear instruction**: Specific, actionable guidance
4. **Test effectiveness**: Validate with real projects

### Instruction Template

```python
"instruction_key": {
    "tags": ["primary_tag", "secondary_tag", "context_tag"],
    "instruction": "Clear, actionable instruction that an AI agent can follow. Include specific steps, tools, and success criteria."
}
```

### Tag Guidelines

- **Primary tag**: Main category (general, testing, frontend, etc.)
- **Secondary tag**: Specific technology or practice
- **Context tag**: When/where this applies

### Example Custom Instruction

```python
"graphql_optimization": {
    "tags": ["api", "graphql", "performance"],
    "instruction": "Implement GraphQL query optimization with depth limiting (max 10 levels), complexity analysis (max 1000 points), and DataLoader pattern for N+1 prevention. Add query whitelisting for production."
}
```

## Validation Framework

Each generated spec includes validation requirements:

### Quality Gates
1. **Zero Errors**: No linting, compilation, or build errors
2. **Test Coverage**: All new code covered by tests
3. **Documentation**: Public APIs documented
4. **Security**: Security practices followed
5. **Performance**: No performance regressions

### Implementation Checklist
- [ ] Load existing project context
- [ ] Analyze code thoroughly
- [ ] Define clear exit criteria
- [ ] Update context after each step
- [ ] Run tests continuously
- [ ] Validate integration points
- [ ] Update documentation

### Validation Commands
```bash
# Comprehensive validation
bash scripts/validate.sh

# Quick validation
bash scripts/validate.sh --quick

# Generate compliance report
bash scripts/validate.sh --report
```

This reference provides the foundation for creating effective, project-specific specifications that guide AI agents through high-quality development practices.
