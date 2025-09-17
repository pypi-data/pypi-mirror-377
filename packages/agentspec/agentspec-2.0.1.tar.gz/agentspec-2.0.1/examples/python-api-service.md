# Example: Python API Service with AgentSpec

This example demonstrates how to use AgentSpec for a Python REST API service using FastAPI, with database integration, authentication, and comprehensive testing.

## Project Overview

**Technology Stack**: Python 3.11, FastAPI, PostgreSQL, SQLAlchemy, Alembic, Redis, JWT Authentication
**Features**: RESTful API, database ORM, caching, authentication, rate limiting, monitoring

## Step 1: Initialize Project with AgentSpec

```bash
# Create project directory
mkdir my-python-api
cd my-python-api

# Generate Python API specification
agentspec generate --template python-api --output python-api-spec.md
```

## Step 2: Review Generated Specification

The generated `python-api-spec.md` includes:

```markdown
# AgentSpec - Project Specification
Generated: 2024-12-15 10:00:00
Template: Python API (v1.0.0)
Total instructions: 18

## BACKEND GUIDELINES

### 1. API Design Standards
**Tags**: api, design, rest, standards
**Priority**: 9

Follow RESTful principles with proper HTTP status codes, versioning, pagination,
filtering, and comprehensive documentation. Implement consistent error responses.

### 2. Python Type Hints
**Tags**: python, type-safety, quality, documentation
**Priority**: 8

Use comprehensive type hints for all functions, parameters, return values,
and class attributes. Import typing modules for complex types.

### 3. Database Optimization
**Tags**: database, performance, optimization, queries
**Priority**: 8

Optimize queries with proper indexing, connection pooling, and query analysis.
Implement database migrations with rollback capabilities.

### 4. Security Best Practices
**Tags**: security, authentication, authorization, validation
**Priority**: 10

Implement input validation, sanitization, authentication, secure headers,
HTTPS, and proper session management. Never commit secrets to version control.

## IMPLEMENTATION FRAMEWORK

### Pre-Development Checklist

- [ ] Analyze codebase thoroughly
- [ ] Define clear exit criteria
- [ ] Review project context for lessons learned

### During Implementation
- [ ] Update project context after each significant step
- [ ] Run tests continuously
- [ ] Validate integration points
- [ ] Document any deviations from plan

### Post-Task Validation
- [ ] Run complete test suite (`pytest`)
- [ ] Check for linting/type errors (`mypy`, `flake8`)
- [ ] Validate API endpoints with automated tests
- [ ] Update documentation
- [ ] Update project context with lessons learned

## QUALITY GATES

Every task must pass these quality gates:

1. **Zero Errors**: No linting, type checking, or runtime errors
2. **Test Coverage**: All new code covered by tests (minimum 90%)
3. **Documentation**: All API endpoints documented with OpenAPI
4. **Security**: Security best practices followed and validated
5. **Performance**: Response times under 200ms for standard endpoints
```

## Step 3: Project Structure Setup

Following AgentSpec guidelines, create the project structure:

```
my-python-api/
├── .agentspec/                  # AgentSpec configuration
├── project_context.md           # Shared project knowledge
├── python-api-spec.md          # Generated specification
├──
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   ├── database.py             # Database connection
│   ├──
│   ├── api/                    # API routes
│   │   ├── __init__.py
│   │   ├── v1/                 # API version 1
│   │   │   ├── __init__.py
│   │   │   ├── auth.py         # Authentication endpoints
│   │   │   ├── users.py        # User management
│   │   │   └── items.py        # Business logic endpoints
│   │   └── dependencies.py     # Shared dependencies
│   ├──
│   ├── models/                 # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── item.py
│   ├──
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── item.py
│   ├──
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   └── user_service.py
│   ├──
│   └── utils/                  # Utility functions
│       ├── __init__.py
│       ├── security.py
│       └── validators.py
├──
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Test configuration
│   ├── test_auth.py
│   ├── test_users.py
│   └── test_items.py
├──
├── alembic/                    # Database migrations
├── requirements.txt
├── pyproject.toml
├── pytest.ini
├── mypy.ini
└── docker-compose.yml
```

## Step 4: Development Workflow

### Task 1: Database Models and Migrations

#### Task Documentation
```bash

```

#### Task Documentation
```markdown
# Task: Database Models and Migrations

## Objective
Set up database infrastructure with:
- SQLAlchemy models for User and Item entities
- Alembic migrations for schema management
- Database connection pooling
- Proper indexing strategy

## Context Gathered
- Analyzed data requirements and relationships
- Designed database schema with normalization
- Chose PostgreSQL for ACID compliance
- Planned indexing strategy for performance

## Changes Made
- [Step 1] ✅ Created User model with authentication fields
- [Step 2] ✅ Built Item model with foreign key relationships
- [Step 3] ✅ Set up Alembic configuration and initial migration
- [Step 4] ✅ Configured database connection with pooling
- [Step 5] ✅ Added proper indexes for query optimization
- [Step 6] ✅ Implemented soft delete functionality
- [Step 7] ✅ Created database seeding scripts

## Issues Encountered
- Alembic auto-generation missing indexes → Added manual index creation
- Connection pool exhaustion → Configured proper pool settings
- Migration rollback issues → Added proper down() methods

## Next Steps
- Add database backup and restore procedures
- Implement read replicas for scaling
- Add database monitoring and alerting

## Status
- [x] Implementation completed
- [x] All migrations tested (up and down)
- [x] Performance benchmarks passed
- [x] Documentation updated
```

### Task 2: Authentication System

#### Implementation Context
```markdown
# Implementation: Authentication System

## Objective
Implement secure authentication with:
- JWT token-based authentication
- Password hashing with bcrypt
- Role-based access control (RBAC)
- Token refresh mechanism

## Context Gathered
- Reviewed OWASP authentication guidelines
- Chose JWT for stateless authentication
- Designed role hierarchy and permissions
- Planned token lifecycle management

## Changes Made
- [Step 1] ✅ Implemented password hashing with bcrypt
- [Step 2] ✅ Created JWT token generation and validation
- [Step 3] ✅ Built authentication middleware
- [Step 4] ✅ Added role-based access control
- [Step 5] ✅ Implemented token refresh endpoint
- [Step 6] ✅ Created user registration and login endpoints
- [Step 7] ✅ Added comprehensive security testing

## Issues Encountered
- JWT secret management → Used environment variables with validation
- Token expiration handling → Added proper refresh token flow
- Rate limiting for auth endpoints → Implemented Redis-based rate limiting

## Status
- [x] Implementation completed
- [x] Security audit passed
- [x] All tests passing
- [x] Documentation complete
```

### Task 3: API Endpoints and Business Logic

#### Implementation Context
```markdown
# Implementation: API Endpoints and Business Logic

## Objective
Implement core API endpoints with:
- RESTful resource management
- Input validation with Pydantic
- Proper error handling and responses
- API documentation with OpenAPI

## Context Gathered
- Designed API resource structure
- Planned validation schemas
- Analyzed error handling patterns
- Reviewed OpenAPI documentation standards

## Changes Made
- [Step 1] ✅ Created Pydantic schemas for request/response validation
- [Step 2] ✅ Implemented CRUD operations for User resources
- [Step 3] ✅ Built Item management endpoints
- [Step 4] ✅ Added pagination and filtering capabilities
- [Step 5] ✅ Implemented comprehensive error handling
- [Step 6] ✅ Generated OpenAPI documentation
- [Step 7] ✅ Added API versioning support

## Issues Encountered
- Pydantic validation errors → Improved error message formatting
- Circular import issues → Restructured module dependencies
- OpenAPI schema generation → Fixed type hints for proper documentation

## Status
- [x] Implementation completed
- [x] All endpoints tested
- [x] API documentation complete
- [x] Performance benchmarks met
```

## Step 5: Testing Strategy

Following AgentSpec testing guidelines:

### Test Structure
```
tests/
├── conftest.py              # Test configuration and fixtures
├── test_auth.py            # Authentication tests
├── test_users.py           # User endpoint tests
├── test_items.py           # Item endpoint tests
├── test_models.py          # Database model tests
├── test_services.py        # Business logic tests
├── integration/            # Integration tests
└── performance/            # Performance tests
```

### Test Implementation
```python
# Example API test following AgentSpec guidelines
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database import get_db
from tests.conftest import override_get_db

client = TestClient(app)

def test_create_user_success():
    """Test successful user creation with proper validation."""
    user_data = {
        "email": "test@example.com",
        "password": "SecurePassword123!",
        "full_name": "Test User"
    }

    response = client.post("/api/v1/users/", json=user_data)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert "password" not in data  # Password should not be returned

def test_create_user_invalid_email():
    """Test user creation with invalid email format."""
    user_data = {
        "email": "invalid-email",
        "password": "SecurePassword123!",
        "full_name": "Test User"
    }

    response = client.post("/api/v1/users/", json=user_data)

    assert response.status_code == 422
    assert "email" in response.json()["detail"][0]["loc"]

def test_authenticate_user():
    """Test user authentication with valid credentials."""
    # First create a user
    user_data = {
        "email": "auth@example.com",
        "password": "SecurePassword123!",
        "full_name": "Auth User"
    }
    client.post("/api/v1/users/", json=user_data)

    # Then authenticate
    auth_data = {
        "username": "auth@example.com",
        "password": "SecurePassword123!"
    }

    response = client.post("/api/v1/auth/token", data=auth_data)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_protected_endpoint_requires_auth():
    """Test that protected endpoints require authentication."""
    response = client.get("/api/v1/users/me")

    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]

@pytest.mark.asyncio
async def test_database_transaction_rollback():
    """Test that database transactions rollback on errors."""
    # This test ensures data integrity during failures
    pass  # Implementation would test actual rollback scenarios
```

## Step 6: Performance and Monitoring

### Performance Testing
```python
# performance/test_load.py
import asyncio
import aiohttp
import time
from statistics import mean, median

async def load_test_endpoint(session, url, num_requests=100):
    """Load test an API endpoint."""
    response_times = []

    async def make_request():
        start_time = time.time()
        async with session.get(url) as response:
            await response.text()
            return time.time() - start_time

    tasks = [make_request() for _ in range(num_requests)]
    response_times = await asyncio.gather(*tasks)

    return {
        "mean_response_time": mean(response_times),
        "median_response_time": median(response_times),
        "max_response_time": max(response_times),
        "min_response_time": min(response_times)
    }

async def main():
    async with aiohttp.ClientSession() as session:
        results = await load_test_endpoint(
            session,
            "http://localhost:8000/api/v1/items/",
            num_requests=1000
        )

        print(f"Load Test Results:")
        print(f"Mean Response Time: {results['mean_response_time']:.3f}s")
        print(f"Median Response Time: {results['median_response_time']:.3f}s")

        # AgentSpec quality gate: responses under 200ms
        assert results['median_response_time'] < 0.2, "Response time exceeds 200ms threshold"

if __name__ == "__main__":
    asyncio.run(main())
```

### Monitoring Setup
```python
# app/monitoring.py
from prometheus_client import Counter, Histogram, generate_latest
import time
from fastapi import Request, Response

# Metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

async def add_prometheus_middleware(request: Request, call_next):
    """Add Prometheus metrics to all requests."""
    start_time = time.time()

    response = await call_next(request)

    # Record metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()

    REQUEST_DURATION.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(time.time() - start_time)

    return response
```

## Step 7: Validation and Quality Assurance

### Comprehensive Test Suite
```bash
#!/bin/bash
# test script following AgentSpec guidelines

set -e

echo "🧪 Running Python API Test Suite..."

# Type checking
echo "Running MyPy type checking..."
mypy app/

# Linting
echo "Running Flake8 linting..."
flake8 app/ tests/

# Security scanning
echo "Running Bandit security scan..."
bandit -r app/

# Unit and integration tests
echo "Running Pytest..."
pytest --cov=app --cov-report=html --cov-fail-under=90

# API documentation validation
echo "Validating OpenAPI schema..."
python -c "from app.main import app; print('OpenAPI schema valid')"

# Performance tests
echo "Running performance tests..."
python tests/performance/test_load.py

# Database migration tests
echo "Testing database migrations..."
alembic upgrade head
alembic downgrade base
alembic upgrade head

echo "✅ All tests passed successfully!"
```

### Project Context Documentation

```markdown
# Project Context - Python API Service

## Project Overview
- **Name**: My Python API
- **Technology Stack**: Python 3.11, FastAPI, PostgreSQL, Redis, JWT
- **Last Updated**: 2024-01-15

## Failed Commands & Alternatives
| Failed Command | Error | Working Alternative | Notes |
|----------------|--------|-------------------|-------|
| `alembic upgrade head` | Connection error | Check DATABASE_URL env var | Need proper connection string |
| `pytest --cov=app` | Import errors | `python -m pytest --cov=app` | Module path issues |
| `uvicorn app.main:app` | Port in use | `uvicorn app.main:app --port 8001` | Default port conflict |

## Lessons Learned
- Type hints catch many runtime errors during development
- Database connection pooling is crucial for performance
- JWT token expiration should be configurable per environment
- API versioning should be planned from the beginning
- Comprehensive logging is essential for debugging production issues

## Current Issues
- [ ] Implement database connection retry logic
- [ ] Add API rate limiting per user
- [ ] Optimize database queries for large datasets
- [ ] Add comprehensive API documentation examples

## Performance Metrics
- **Average Response Time**: 45ms
- **95th Percentile**: 120ms
- **Database Query Time**: 15ms average
- **Test Coverage**: 94%
- **Memory Usage**: 85MB average
```

## Results and Benefits

### Metrics After AgentSpec Implementation

- **Development Speed**: 50% faster API development
- **Code Quality**: 94% test coverage maintained
- **Security**: Zero security vulnerabilities detected
- **Performance**: 45ms average response time
- **Type Safety**: 100% type coverage with MyPy
- **API Documentation**: 100% endpoint coverage

### Key Success Factors

1. **Type Safety**: Comprehensive type hints prevented runtime errors
2. **Testing Strategy**: High test coverage caught regressions early
3. **Security Focus**: Built-in security practices prevented vulnerabilities
4. **Performance Monitoring**: Continuous monitoring prevented performance degradation
5. **Documentation**: Auto-generated API docs improved developer experience

## Environment-Specific Usage

### Amazon Kiro IDE
```bash
# Use the generated specification as context for AI-assisted development
# Reference the quality gates for automated validation
# Follow the implementation framework for systematic development
```

### Microsoft SpecKit
```bash
# Import the specification for project planning and tracking
# Use the validation framework for quality assurance
# Leverage the testing guidelines for comprehensive coverage
```

### VS Code with GitHub Copilot
```bash
# Use the specification as context for better AI suggestions
# Reference the coding standards when accepting AI-generated code
# Follow the security guidelines for safe AI-assisted development
```

## Conclusion

AgentSpec transformed our Python API development by:

- Providing clear architectural guidelines for API design
- Enforcing security and performance standards
- Enabling systematic testing and quality assurance
- Facilitating team collaboration through shared specifications
- Maintaining high code quality throughout development

The specification-driven approach resulted in a production-ready API service with excellent performance, security, and maintainability.

**Next Steps**: Extend AgentSpec usage to microservices architecture and containerized deployments.
