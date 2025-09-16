# Example: SaaS Application with AgentSpec

This example demonstrates how to use AgentSpec for a multi-tenant SaaS platform with subscription management, analytics, and AI-powered features.

## Project Overview

**Technology Stack**: React, Node.js, PostgreSQL, Stripe, Redis, Docker, Kubernetes
**Features**: Multi-tenancy, subscription billing, user analytics, AI features, white-labeling

## Step 1: Initialize Project with AgentSpec

```bash
# Create project directory
mkdir my-saas-application
cd my-saas-application

# Generate SaaS-specific specification
agentspec generate --template saas-application --output saas-spec.md
```

## Step 2: Review Generated Specification

The generated `saas-spec.md` includes:

```markdown
# AgentSpec - Project Specification
Generated: 2024-01-15 10:00:00
Template: SaaS Platform (v1.0.0)
Total instructions: 22

## SAAS GUIDELINES

### 1. Multi-Tenant Architecture
**Tags**: saas, multi-tenant, architecture, scalability
**Priority**: 10

Implement proper tenant isolation using schema-based separation with shared
application code. Ensure data security and performance across tenants.

### 2. Subscription Management
**Tags**: saas, subscription, billing, stripe
**Priority**: 9

Integrate with Stripe for subscription billing, plan management, usage tracking,
and automated invoicing. Handle plan upgrades, downgrades, and cancellations.

### 3. User Analytics Implementation
**Tags**: saas, analytics, tracking, insights
**Priority**: 8

Implement comprehensive user analytics with event tracking, funnel analysis,
cohort analysis, and custom dashboards for business insights.

### 4. AI Feature Integration
**Tags**: saas, ai-powered, machine-learning, features
**Priority**: 7

Integrate AI-powered features like recommendations, automated insights,
and intelligent data processing to enhance user experience.

## IMPLEMENTATION FRAMEWORK

### Pre-Development Checklist

- [ ] Analyze multi-tenant requirements
- [ ] Define clear tenant isolation strategy
- [ ] Review compliance requirements (GDPR, SOC2)

### During Implementation
- [ ] Update project context after each significant step
- [ ] Test with multiple tenant scenarios
- [ ] Validate billing integration thoroughly
- [ ] Document tenant-specific configurations

### Post-Task Validation
- [ ] Run complete test suite including multi-tenant tests
- [ ] Validate billing workflows end-to-end
- [ ] Test analytics data accuracy
- [ ] Verify AI feature performance
- [ ] Update documentation and compliance records

## QUALITY GATES

Every task must pass these quality gates:

1. **Zero Errors**: No linting, compilation, or build errors
2. **Tenant Isolation**: Complete data separation between tenants
3. **Billing Accuracy**: 100% accurate billing calculations
4. **Performance**: Sub-second response times for all features
5. **Security**: SOC2 and GDPR compliance maintained
6. **Scalability**: Support for 10,000+ concurrent users
```

## Step 3: Project Structure Setup

Following AgentSpec guidelines for SaaS architecture:

```
my-saas-application/
├── .agentspec/                  # AgentSpec configuration
├── project_context.md           # Shared project knowledge
├── saas-spec.md                # Generated specification
├──
├── apps/
│   ├── web/                    # Frontend React application
│   │   ├── src/
│   │   │   ├── components/
│   │   │   ├── pages/
│   │   │   ├── hooks/
│   │   │   ├── contexts/
│   │   │   └── utils/
│   │   ├── package.json
│   │   └── vite.config.ts
│   │
│   ├── api/                    # Backend API service
│   │   ├── src/
│   │   │   ├── controllers/
│   │   │   ├── services/
│   │   │   ├── models/
│   │   │   ├── middleware/
│   │   │   └── utils/
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   └── analytics/              # Analytics service
│       ├── src/
│       ├── package.json
│       └── Dockerfile
├──
├── packages/                   # Shared packages
│   ├── database/              # Database schemas and migrations
│   ├── shared-types/          # TypeScript type definitions
│   ├── ui-components/         # Shared UI components
│   └── utils/                 # Shared utilities
├──
├── infrastructure/            # Infrastructure as code
│   ├── kubernetes/
│   ├── terraform/
│   └── docker/
├──
├── tests/
│   ├── e2e/                  # End-to-end tests
│   ├── integration/          # Integration tests
│   └── load/                 # Load testing
├──
├── docs/
├── docker-compose.yml
└── package.json
```

## Step 4: Development Workflow

### Task 1: Multi-Tenant Database Architecture

#### Task Documentation
```bash

```

#### Task Documentation
```markdown
# Task: Multi-Tenant Database Architecture

## Objective
Implement multi-tenant database architecture with:
- Schema-based tenant isolation
- Tenant-aware database connections
- Automated tenant provisioning
- Data migration strategies

## Context Gathered
- Analyzed tenant isolation requirements
- Chose schema-based approach for balance of isolation and efficiency
- Designed tenant metadata management
- Planned database scaling strategy

## Changes Made
- [Step 1] ✅ Created tenant management schema and models
- [Step 2] ✅ Implemented tenant-aware database middleware
- [Step 3] ✅ Built automated tenant schema provisioning
- [Step 4] ✅ Added tenant context injection for all queries
- [Step 5] ✅ Created tenant data migration utilities
- [Step 6] ✅ Implemented tenant backup and restore
- [Step 7] ✅ Added comprehensive multi-tenant testing

## Issues Encountered
- Schema creation permissions → Updated database user privileges
- Query performance with tenant filtering → Added proper indexes
- Connection pool management → Implemented tenant-aware pooling

## Next Steps
- Implement tenant data archival
- Add cross-tenant analytics capabilities
- Optimize query performance for large tenant counts

## Status
- [x] Implementation completed
- [x] All multi-tenant tests passing
- [x] Performance benchmarks met
- [x] Security audit passed
```

### Task 2: Subscription and Billing System

#### Implementation Context
```markdown
# Implementation: Subscription and Billing System

## Objective
Implement comprehensive billing system with:
- Stripe integration for payment processing
- Multiple subscription plans and tiers
- Usage-based billing capabilities
- Automated invoice generation

## Context Gathered
- Analyzed pricing model requirements
- Designed subscription plan hierarchy
- Planned usage tracking mechanisms
- Reviewed Stripe webhook handling

## Changes Made
- [Step 1] ✅ Integrated Stripe SDK and webhook handling
- [Step 2] ✅ Created subscription plan management
- [Step 3] ✅ Implemented usage tracking and metering
- [Step 4] ✅ Built automated billing and invoicing
- [Step 5] ✅ Added plan upgrade/downgrade workflows
- [Step 6] ✅ Created billing dashboard and analytics
- [Step 7] ✅ Implemented dunning management for failed payments

## Issues Encountered
- Webhook signature verification → Added proper security validation
- Proration calculations → Implemented custom proration logic
- Failed payment handling → Added retry and notification system

## Status
- [x] Implementation completed
- [x] All billing workflows tested
- [x] Stripe integration verified
- [x] Financial reconciliation working
```

### Task 3: User Analytics and Insights

#### Implementation Context
```markdown
# Implementation: User Analytics and Insights

## Objective
Implement comprehensive analytics system with:
- Event tracking and data collection
- Real-time analytics dashboard
- Cohort analysis and retention metrics
- Custom reporting capabilities

## Context Gathered
- Analyzed analytics requirements and KPIs
- Designed event schema and data pipeline
- Chose analytics stack (ClickHouse + Grafana)
- Planned real-time vs batch processing

## Changes Made
- [Step 1] ✅ Set up event tracking infrastructure
- [Step 2] ✅ Implemented real-time analytics pipeline
- [Step 3] ✅ Built analytics dashboard with key metrics
- [Step 4] ✅ Created cohort analysis and retention tracking
- [Step 5] ✅ Added custom report builder
- [Step 6] ✅ Implemented data export capabilities
- [Step 7] ✅ Added privacy-compliant data handling

## Issues Encountered
- Real-time data processing latency → Optimized pipeline architecture
- Dashboard performance with large datasets → Added data aggregation
- GDPR compliance for analytics → Implemented data anonymization

## Status
- [x] Implementation completed
- [x] Real-time analytics working
- [x] Dashboard performance optimized
- [x] Privacy compliance verified
```

### Task 4: AI-Powered Features

#### Implementation Context
```markdown
# Implementation: AI-Powered Features

## Objective
Integrate AI capabilities including:
- Intelligent recommendations engine
- Automated insights and anomaly detection
- Natural language query interface
- Predictive analytics for churn prevention

## Context Gathered
- Analyzed AI feature requirements and use cases
- Designed ML pipeline architecture
- Chose appropriate AI/ML services and models
- Planned model training and deployment strategy

## Changes Made
- [Step 1] ✅ Set up ML pipeline infrastructure
- [Step 2] ✅ Implemented recommendation engine
- [Step 3] ✅ Built anomaly detection system
- [Step 4] ✅ Created natural language query interface
- [Step 5] ✅ Added predictive churn analysis
- [Step 6] ✅ Implemented A/B testing for AI features
- [Step 7] ✅ Added AI feature performance monitoring

## Issues Encountered
- Model inference latency → Implemented model caching and optimization
- Training data quality → Added data validation and cleaning
- AI feature explainability → Added model interpretation tools

## Status
- [x] Implementation completed
- [x] All AI features tested and validated
- [x] Performance benchmarks met
- [x] Model monitoring in place
```

## Step 5: Testing Strategy

Following AgentSpec testing guidelines for SaaS applications:

### Multi-Tenant Testing
```javascript
// tests/multi-tenant/tenant-isolation.test.js
describe('Tenant Isolation', () => {
  let tenant1, tenant2;

  beforeEach(async () => {
    tenant1 = await createTestTenant('tenant1');
    tenant2 = await createTestTenant('tenant2');
  });

  it('should isolate data between tenants', async () => {
    // Create data for tenant1
    const tenant1Data = await createDataForTenant(tenant1.id, {
      name: 'Tenant 1 Data'
    });

    // Create data for tenant2
    const tenant2Data = await createDataForTenant(tenant2.id, {
      name: 'Tenant 2 Data'
    });

    // Verify tenant1 can only see their data
    const tenant1Results = await getDataForTenant(tenant1.id);
    expect(tenant1Results).toHaveLength(1);
    expect(tenant1Results[0].name).toBe('Tenant 1 Data');

    // Verify tenant2 can only see their data
    const tenant2Results = await getDataForTenant(tenant2.id);
    expect(tenant2Results).toHaveLength(1);
    expect(tenant2Results[0].name).toBe('Tenant 2 Data');
  });

  it('should prevent cross-tenant data access', async () => {
    const tenant1Data = await createDataForTenant(tenant1.id, {
      name: 'Secret Data'
    });

    // Attempt to access tenant1 data from tenant2 context
    await expect(
      getSpecificDataForTenant(tenant2.id, tenant1Data.id)
    ).rejects.toThrow('Data not found');
  });
});
```

### Billing Integration Testing
```javascript
// tests/billing/stripe-integration.test.js
describe('Stripe Billing Integration', () => {
  it('should handle subscription creation', async () => {
    const customer = await createTestCustomer();
    const subscription = await createSubscription(customer.id, 'pro-plan');

    expect(subscription.status).toBe('active');
    expect(subscription.plan).toBe('pro-plan');

    // Verify webhook handling
    const webhookEvent = createStripeWebhookEvent('invoice.payment_succeeded', {
      subscription: subscription.id
    });

    const response = await handleStripeWebhook(webhookEvent);
    expect(response.status).toBe(200);
  });

  it('should handle plan upgrades correctly', async () => {
    const customer = await createTestCustomer();
    const subscription = await createSubscription(customer.id, 'basic-plan');

    // Upgrade to pro plan
    const upgradedSubscription = await upgradeSubscription(
      subscription.id,
      'pro-plan'
    );

    expect(upgradedSubscription.plan).toBe('pro-plan');

    // Verify proration calculation
    const invoice = await getLatestInvoice(customer.id);
    expect(invoice.proration_amount).toBeGreaterThan(0);
  });
});
```

### Load Testing for SaaS Scale
```javascript
// tests/load/saas-scale.test.js
import { check } from 'k6';
import http from 'k6/http';

export let options = {
  stages: [
    { duration: '2m', target: 100 },   // Ramp up to 100 users
    { duration: '5m', target: 100 },   // Stay at 100 users
    { duration: '2m', target: 200 },   // Ramp up to 200 users
    { duration: '5m', target: 200 },   // Stay at 200 users
    { duration: '2m', target: 0 },     // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests under 500ms
    http_req_failed: ['rate<0.1'],    // Error rate under 10%
  },
};

export default function() {
  // Simulate multi-tenant load
  const tenantId = Math.floor(Math.random() * 100) + 1;

  const response = http.get(`${__ENV.API_URL}/api/v1/tenants/${tenantId}/data`, {
    headers: {
      'Authorization': `Bearer ${__ENV.TEST_TOKEN}`,
      'X-Tenant-ID': tenantId.toString(),
    },
  });

  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
    'tenant data returned': (r) => JSON.parse(r.body).tenant_id === tenantId,
  });
}
```

## Step 6: Deployment and Infrastructure

### Kubernetes Deployment
```yaml
# infrastructure/kubernetes/saas-app.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: saas-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: saas-api
  template:
    metadata:
      labels:
        app: saas-api
    spec:
      containers:
      - name: api
        image: my-saas-application/api:latest
        ports:
        - containerPort: 3000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-secret
              key: url
        - name: STRIPE_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: stripe-secret
              key: secret-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: saas-api-service
spec:
  selector:
    app: saas-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 3000
  type: LoadBalancer
```

### Monitoring and Observability
```yaml
# infrastructure/monitoring/prometheus-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s

    scrape_configs:
    - job_name: 'saas-api'
      static_configs:
      - targets: ['saas-api-service:80']
      metrics_path: /metrics

    - job_name: 'saas-web'
      static_configs:
      - targets: ['saas-web-service:80']
      metrics_path: /metrics

    rule_files:
    - "saas_alerts.yml"

    alerting:
      alertmanagers:
      - static_configs:
        - targets:
          - alertmanager:9093
```

## Step 7: Validation and Quality Assurance

### Comprehensive Test Suite
```bash
#!/bin/bash
# SaaS platform test suite following AgentSpec guidelines

set -e

echo "🧪 Running SaaS Platform Test Suite..."

# Multi-tenant isolation tests
echo "Testing tenant isolation..."
npm run test:multi-tenant

# Billing integration tests
echo "Testing billing workflows..."
npm run test:billing

# Analytics accuracy tests
echo "Validating analytics data..."
npm run test:analytics

# AI feature tests
echo "Testing AI-powered features..."
npm run test:ai-features

# Load testing
echo "Running load tests..."
npm run test:load

# Security scanning
echo "Running security scans..."
npm run test:security

# End-to-end tests
echo "Running E2E tests..."
npm run test:e2e

# Performance benchmarks
echo "Running performance benchmarks..."
npm run test:performance

echo "✅ All SaaS platform tests passed successfully!"
```

### Project Context Documentation

```markdown
# Project Context - SaaS Platform

## Project Overview
- **Name**: My SaaS Platform
- **Technology Stack**: React, Node.js, PostgreSQL, Stripe, Redis, Kubernetes
- **Last Updated**: 2024-01-15

## Failed Commands & Alternatives
| Failed Command | Error | Working Alternative | Notes |
|----------------|--------|-------------------|-------|
| `kubectl apply -f k8s/` | RBAC permissions | Use `kubectl apply --validate=false` | Need cluster admin |
| `stripe listen --forward-to localhost:3000/webhooks` | Port conflict | Use different port | Multiple services running |
| `docker-compose up` | Memory limits | Increase Docker memory allocation | Large multi-service setup |

## Lessons Learned
- Multi-tenant architecture requires careful planning from day one
- Billing integration testing must include all edge cases
- Analytics data pipeline needs proper error handling and retry logic
- AI features require extensive A/B testing before rollout
- Kubernetes resource limits are crucial for cost management

## Current Issues
- [ ] Optimize database queries for tenants with large datasets
- [ ] Implement automated tenant data archival
- [ ] Add more granular billing usage tracking
- [ ] Improve AI model inference performance

## Performance Metrics
- **Average Response Time**: 120ms
- **Tenant Isolation**: 100% (zero cross-tenant data leaks)
- **Billing Accuracy**: 99.99%
- **Uptime**: 99.9%
- **AI Feature Adoption**: 65%
```

## Results and Benefits

### Metrics After AgentSpec Implementation

- **Development Speed**: 60% faster feature development
- **Tenant Isolation**: 100% data security maintained
- **Billing Accuracy**: 99.99% accuracy achieved
- **Performance**: 120ms average response time
- **Scalability**: Supporting 10,000+ concurrent users
- **AI Feature Adoption**: 65% user engagement

### Key Success Factors

1. **Multi-Tenant Architecture**: Proper isolation prevented security issues
2. **Billing Integration**: Comprehensive testing ensured financial accuracy
3. **Analytics Pipeline**: Real-time insights improved user experience
4. **AI Features**: Intelligent capabilities increased user engagement
5. **Monitoring**: Comprehensive observability prevented downtime

## Environment-Specific Usage

### Amazon Kiro IDE
```bash
# Use the SaaS specification for AI-assisted development
# Reference multi-tenant patterns when building new features
# Follow the billing integration guidelines for payment features
```

### Microsoft SpecKit
```bash
# Import the specification for enterprise project management
# Use the quality gates for automated compliance checking
# Leverage the testing framework for comprehensive validation
```

### VS Code with GitHub Copilot
```bash
# Use the specification as context for SaaS-specific suggestions
# Reference the security guidelines for multi-tenant development
# Follow the performance standards for scalable architecture
```

## Conclusion

AgentSpec transformed our SaaS platform development by:

- Providing clear architectural guidelines for multi-tenant systems
- Enforcing security and compliance standards
- Enabling systematic testing of complex billing workflows
- Facilitating AI feature integration with proper validation
- Maintaining high performance and scalability standards

The specification-driven approach resulted in a production-ready SaaS platform with excellent security, performance, and user experience.

**Next Steps**: Extend AgentSpec usage to mobile applications and international expansion features.
