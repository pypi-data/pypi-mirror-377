# Example: Full-Stack Web Application with AgentSpec

This example demonstrates how to use AgentSpec for a complete full-stack web application project.

## Project Overview

**Technology Stack**: React, TypeScript, Node.js, Express, PostgreSQL, Redis
**Features**: User authentication, real-time chat, file uploads, payment processing

## Step 1: Initialize AgentSpec

```bash
# Clone or copy AgentSpec to your project
cp /path/to/agentspec.py .
cp /path/to/setup.sh .

# Initialize AgentSpec
bash setup.sh

# Generate comprehensive spec
python agentspec.py --interactive
```

### Interactive Selection Process

```
🤖 AgentSpec - Interactive Specification Generator
=======================================================

Available categories:
1. GENERAL (4 tags)
2. TESTING (3 tags)
3. FRONTEND (6 tags)
4. BACKEND (5 tags)
5. DEVOPS (5 tags)
6. LANGUAGES (4 tags)
7. ARCHITECTURE (4 tags)

Select category (1-7): 1
Tags in GENERAL:
1. [ ] general (4 instructions)
2. [ ] quality (6 instructions)
3. [ ] standards (4 instructions)
4. [ ] persistence (2 instructions)

Select tags by number: all
Added all general tags

Select category (1-7): 2
[Select testing tags...]

Select category (1-7): 3
[Select frontend, react, typescript, accessibility...]

Select category (1-7): 4
[Select backend, api, database, security...]

Select category (1-7): done

Selected tags: general,quality,testing,frontend,react,typescript,backend,api,database,security,realtime,payments
Enter output filename: fullstack_spec.md
```

## Step 2: Project Structure

After setup, your project structure:

```
fullstack-webapp/
├── .agentspec                    # AgentSpec configuration
├── fullstack_spec.md            # Generated specification
├── project_context.md           # Shared project knowledge
├── scripts/
│   └── validate.sh              # Validation suite
├── docs/
│   └── DEVELOPMENT.md           # Development guide
├──
├── frontend/                    # React application
│   ├── src/
│   ├── package.json
│   └── tsconfig.json
├──
├── backend/                     # Node.js API
│   ├── src/
│   ├── package.json
│   └── Dockerfile
├──
└── tests/
    └── run_tests.py              # Comprehensive test suite
```

## Step 3: Development Workflow

### Task 1: User Authentication System

#### Task Documentation
```markdown
# Task: User Authentication System

## Objective
Implement secure user authentication with JWT tokens, including:
- User registration and login endpoints
- Password hashing with bcrypt
- JWT token generation and validation
- Protected route middleware
- Frontend login/logout UI

## Context Gathered
- Reviewed existing codebase structure
- Identified security requirements (OWASP guidelines)
- Chose bcrypt for password hashing (12 rounds)
- Selected jsonwebtoken library for JWT handling
- Frontend will use React Context for auth state

## Changes Made
- [Step 1] ✅ Created User model with encrypted password field
- [Step 2] ✅ Added auth middleware for JWT validation
- [Step 3] ✅ Implemented registration endpoint with validation
- [Step 4] ✅ Added login endpoint with rate limiting
- [Step 5] ✅ Created protected route wrapper
- [Step 6] ✅ Built frontend auth context and hooks
- [Step 7] ✅ Added login/logout UI components

## Issues Encountered
- JWT secret not in environment variables → Added to .env template
- Password validation too weak → Enhanced with complexity requirements
- CORS issues with auth endpoints → Updated CORS configuration

## Next Steps
- Add password reset functionality
- Implement remember me option
- Add OAuth integration (Google/GitHub)

## Status
- [x] Implementation completed
- [x] Unit tests written and passing
- [x] Integration tests passing
- [x] Frontend integration working
- [x] Documentation updated
- [x] Security review completed
```

#### Implementation Process

```bash
# Before starting implementation
python agentspec.py --tag-info security  # Review security requirements

# During implementation - after each step
bash scripts/validate.sh --quick         # Quick validation

# Final validation
bash scripts/validate.sh                 # Full validation
./test                                  # Run all tests
```

### Task 2: Real-time Chat Feature

#### Implementation Context
```markdown
# Implementation: Real-time Chat Feature

## Objective
Implement real-time chat functionality using WebSockets

## Context Gathered
- Analyzed existing authentication system
- Chose Socket.IO for WebSocket implementation
- Designed message schema and room management
- Planned integration with existing user system

## Changes Made
- [Step 1] ✅ Set up Socket.IO server configuration
- [Step 2] ✅ Created message model and database schema
- [Step 3] ✅ Implemented room management system
- [Step 4] ✅ Added message persistence and history
- [Step 5] ✅ Built frontend chat components
- [Step 6] ✅ Added typing indicators and online status
- [Step 7] ✅ Implemented message encryption

## Issues Encountered
- Socket.IO CORS configuration needed adjustment
- Message ordering issues → Added timestamp-based sorting
- Memory leaks in connection handling → Implemented proper cleanup

## Status
- [x] Implementation completed
- [x] Load testing completed (1000 concurrent users)
- [x] Security review passed
- [x] Documentation updated
```

### Task 3: Payment Processing Integration

#### Implementation Context
```markdown
# Implementation: Payment Processing Integration

## Objective
Integrate Stripe payment processing with proper security and error handling

## Context Gathered
- Reviewed Stripe documentation and best practices
- Analyzed PCI compliance requirements
- Designed subscription and one-time payment flows
- Planned webhook handling for payment events

## Changes Made
- [Step 1] ✅ Set up Stripe SDK and configuration
- [Step 2] ✅ Created payment intent endpoints
- [Step 3] ✅ Implemented subscription management
- [Step 4] ✅ Added webhook handling with signature verification
- [Step 5] ✅ Built frontend payment components
- [Step 6] ✅ Added payment history and receipts
- [Step 7] ✅ Implemented refund functionality

## Issues Encountered
- Webhook signature verification failing → Fixed endpoint URL configuration
- Test mode vs live mode confusion → Added environment-specific configuration
- Currency handling edge cases → Added proper formatting and validation

## Status
- [x] Implementation completed
- [x] PCI compliance review passed
- [x] Webhook testing completed
- [x] Error handling comprehensive
- [x] Documentation updated
```

## Step 4: Validation and Quality Assurance

### Comprehensive Test Suite (`test`)

```bash
#!/bin/bash
# Comprehensive test suite for fullstack webapp

set -e

echo "🧪 Running comprehensive test suite..."

# Backend tests
echo "Testing Backend..."
cd backend
npm run lint
npm run type-check
npm test
npm run test:integration
cd ..

# Frontend tests
echo "Testing Frontend..."
cd frontend
npm run lint
npm run type-check
npm test -- --watchAll=false
npm run build
cd ..

# Security tests
echo "Running Security Tests..."
cd backend && npm audit --audit-level moderate && cd ..
cd frontend && npm audit --audit-level moderate && cd ..

# E2E tests
echo "Running E2E Tests..."
cd frontend && npx cypress run --headless && cd ..

# API tests
echo "Testing API Endpoints..."
curl -f http://localhost:3001/health || exit 1

echo "✅ All tests passed successfully!"
```

### Validation Results

```bash
bash scripts/validate.sh
```

```
🔍 AgentSpec Validation Suite

[INFO] Checking project structure...
✅ Project structure validated

[INFO] Validating project contexts...
✅ Valid context: user_authentication.md
✅ Valid context: realtime_chat.md
✅ Valid context: payment_processing.md

[INFO] Running tests...
✅ All tests passed

===============================================
✅ AgentSpec validation completed successfully
```

## Step 5: Project Context Documentation

### Updated `project_context.md`

```markdown
# Project Context

## Project Overview
- **Name**: FullStack WebApp
- **Technology Stack**: React, TypeScript, Node.js, Express, PostgreSQL, Redis, Socket.IO, Stripe
- **Last Updated**: 2025-01-15

## Failed Commands & Alternatives
| Failed Command | Error | Working Alternative | Notes |
|----------------|--------|-------------------|-------|
| `npm run test` | Jest config issue | `npx jest --config=jest.config.js` | Custom config needed |
| `docker-compose up` | Port conflict | `docker-compose up -d --remove-orphans` | Clean up needed first |
| `stripe listen` | Webhook timeout | `stripe listen --forward-to localhost:3001/webhooks/stripe` | Specify full URL |

## Debug & Temporary Files
| File Path | Purpose | Created Date | Status |
|-----------|---------|--------------|--------|
| `debug_auth.js` | JWT token debugging | 2025-01-10 | Removed ✓ |
| `test_payments.js` | Stripe integration testing | 2025-01-12 | Kept for future use |
| `socket_debug.html` | WebSocket connection testing | 2025-01-14 | Removed ✓ |

## Lessons Learned
- JWT secrets must be properly configured in all environments
- Socket.IO requires careful CORS configuration for production
- Stripe webhooks need proper signature verification
- TypeScript strict mode catches many runtime errors early
- Database migrations should be tested in staging first
- Real-time features need comprehensive load testing

## Current Issues
- [ ] Frontend bundle size optimization needed
- [ ] API response times could be improved for large datasets
- [ ] Mobile responsiveness needs testing on actual devices
- [ ] Payment webhook retry logic could be more robust

## Environment Setup
```bash
# Required environment variables
cp .env.example .env
# Edit database credentials, JWT secrets, Stripe keys, etc.

# Install dependencies
cd frontend && npm install
cd ../backend && npm install

# Start development services
docker-compose up -d postgres redis
cd backend && npm run dev
cd ../frontend && npm start
```
```

## Step 6: Deployment and Monitoring

### Production Deployment Checklist

Based on AgentSpec guidelines:

- [x] All tests passing
- [x] Security audit completed
- [x] Performance testing completed
- [x] Documentation updated
- [x] Environment variables configured
- [x] Database migrations tested
- [x] Monitoring and logging configured
- [x] Backup strategy implemented
- [x] Error handling comprehensive
- [x] Rate limiting configured

### Monitoring Setup

Following AgentSpec monitoring guidelines:

```javascript
// backend/src/monitoring.js
const prometheus = require('prom-client');

// Metrics collection
const httpRequestDuration = new prometheus.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status']
});

const activeConnections = new prometheus.Gauge({
  name: 'websocket_active_connections',
  help: 'Number of active WebSocket connections'
});

// Error tracking
const errorCounter = new prometheus.Counter({
  name: 'application_errors_total',
  help: 'Total number of application errors',
  labelNames: ['type', 'severity']
});
```

## Results and Benefits

### Metrics After AgentSpec Implementation

- **Development Speed**: 40% faster task completion
- **Code Quality**: 95% reduction in production bugs
- **Test Coverage**: 98% coverage maintained
- **Documentation**: 100% API coverage
- **Team Onboarding**: 60% faster for new developers
- **Context Preservation**: 100% task resumption success rate

### Key Success Factors

1. **Systematic Approach**: AgentSpec's structured workflow prevented scope creep
2. **Quality Gates**: Zero-tolerance policy caught issues early
3. **Context Management**: Project contexts enabled seamless collaboration
4. **Validation Framework**: Automated checks maintained consistency
5. **Documentation**: Living documentation stayed current with implementation

## Conclusion

AgentSpec transformed our full-stack development process by:

- Providing clear, actionable guidelines for every aspect of development
- Enabling resumable development through comprehensive project contexts
- Enforcing quality standards through automated validation
- Facilitating team collaboration with shared project knowledge
- Maintaining high code quality and security standards throughout

The specification-driven approach resulted in a production-ready application with robust architecture, comprehensive testing, and maintainable codebase.

**Next Steps**: Expand AgentSpec usage to mobile app development and microservices architecture.
