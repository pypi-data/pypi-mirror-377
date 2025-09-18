# Example: Microservices Architecture with AgentSpec

This example demonstrates how to use AgentSpec for a distributed microservices architecture with service mesh, API gateway, and comprehensive observability.

## Project Overview

**Technology Stack**: Node.js, Docker, Kubernetes, Istio, PostgreSQL, Redis, RabbitMQ
**Features**: Service mesh, API gateway, distributed tracing, circuit breakers, event-driven architecture

## Step 1: Initialize Project with AgentSpec

```bash
# Create project directory
mkdir microservices-platform
cd microservices-platform

# Generate microservices specification
agentspec generate --template microservice --output microservices-spec.md
```

## Step 2: Review Generated Specification

The generated `microservices-spec.md` includes:

```markdown
# AgentSpec - Project Specification
Generated: 2024-01-15 10:00:00
Template: Microservice (v1.0.0)
Total instructions: 25

## MICROSERVICES GUIDELINES

### 1. Service Boundaries and Design
**Tags**: microservices, architecture, boundaries, domain-driven-design
**Priority**: 10

Design services around business capabilities with clear boundaries.
Follow Domain-Driven Design principles for service decomposition.

### 2. API Gateway Pattern
**Tags**: microservices, api-gateway, routing, security
**Priority**: 9

Implement centralized API gateway for request routing, authentication,
rate limiting, and cross-cutting concerns.

### 3. Service Mesh Implementation
**Tags**: microservices, service-mesh, istio, networking
**Priority**: 8

Use service mesh for service-to-service communication, traffic management,
security policies, and observability.

### 4. Distributed Tracing
**Tags**: microservices, observability, tracing, monitoring
**Priority**: 8

Implement distributed tracing across all services for request flow visibility
and performance analysis.

## IMPLEMENTATION FRAMEWORK

### Pre-Development Checklist

- [ ] Analyze service boundaries and dependencies
- [ ] Define clear service contracts and APIs
- [ ] Review distributed system patterns

### During Implementation
- [ ] Update project context after each significant step
- [ ] Test service interactions thoroughly
- [ ] Validate distributed system behavior
- [ ] Monitor service health and performance

### Post-Task Validation
- [ ] Run complete test suite including integration tests
- [ ] Validate service mesh configuration
- [ ] Test circuit breaker and retry mechanisms
- [ ] Verify distributed tracing coverage
- [ ] Update service documentation

## QUALITY GATES

Every task must pass these quality gates:

1. **Zero Errors**: No service startup or runtime errors
2. **Service Isolation**: Proper fault isolation between services
3. **Performance**: Sub-100ms inter-service communication
4. **Observability**: 100% distributed tracing coverage
5. **Resilience**: Circuit breakers and retry mechanisms working
6. **Security**: mTLS and service-to-service authentication
```

## Step 3: Project Structure Setup

Following AgentSpec guidelines for microservices:

```
microservices-platform/
├── .agentspec/                  # AgentSpec configuration
├── project_context.md           # Shared project knowledge
├── microservices-spec.md        # Generated specification
├──
├── services/
│   ├── api-gateway/            # API Gateway service
│   │   ├── src/
│   │   ├── Dockerfile
│   │   └── package.json
│   │
│   ├── user-service/           # User management service
│   │   ├── src/
│   │   ├── Dockerfile
│   │   └── package.json
│   │
│   ├── order-service/          # Order processing service
│   │   ├── src/
│   │   ├── Dockerfile
│   │   └── package.json
│   │
│   ├── payment-service/        # Payment processing service
│   │   ├── src/
│   │   ├── Dockerfile
│   │   └── package.json
│   │
│   ├── notification-service/   # Notification service
│   │   ├── src/
│   │   ├── Dockerfile
│   │   └── package.json
│   │
│   └── inventory-service/      # Inventory management service
│       ├── src/
│       ├── Dockerfile
│       └── package.json
├──
├── infrastructure/
│   ├── kubernetes/             # K8s manifests
│   │   ├── services/
│   │   ├── deployments/
│   │   ├── configmaps/
│   │   └── secrets/
│   │
│   ├── istio/                  # Service mesh configuration
│   │   ├── gateways/
│   │   ├── virtual-services/
│   │   └── destination-rules/
│   │
│   ├── monitoring/             # Observability stack
│   │   ├── prometheus/
│   │   ├── grafana/
│   │   └── jaeger/
│   │
│   └── terraform/              # Infrastructure as code
├──
├── shared/
│   ├── proto/                  # Protocol buffer definitions
│   ├── events/                 # Event schemas
│   └── libraries/              # Shared libraries
├──
├── tests/
│   ├── integration/            # Cross-service integration tests
│   ├── contract/               # Contract testing
│   └── chaos/                  # Chaos engineering tests
├──
├── scripts/
│   ├── deploy.sh
│   ├── test.sh
│   └── monitoring.sh
├──
└── docker-compose.yml
```

## Step 4: Development Workflow

### Task 1: Service Mesh Setup with Istio

#### Task Documentation
```bash

```

#### Task Documentation
```markdown
# Task: Service Mesh Setup with Istio

## Objective
Implement service mesh infrastructure with:
- Istio installation and configuration
- Automatic sidecar injection
- Traffic management policies
- Security policies with mTLS

## Context Gathered
- Analyzed service communication patterns
- Designed traffic routing strategies
- Planned security policy implementation
- Reviewed Istio best practices

## Changes Made
- [Step 1] ✅ Installed Istio control plane
- [Step 2] ✅ Configured automatic sidecar injection
- [Step 3] ✅ Set up ingress and egress gateways
- [Step 4] ✅ Implemented virtual services for routing
- [Step 5] ✅ Configured destination rules for load balancing
- [Step 6] ✅ Enabled mTLS for service-to-service communication
- [Step 7] ✅ Added traffic policies and circuit breakers

## Issues Encountered
- Sidecar injection conflicts → Updated namespace labels
- mTLS certificate issues → Configured proper CA certificates
- Traffic routing loops → Fixed virtual service configurations

## Next Steps
- Implement advanced traffic splitting for A/B testing
- Add rate limiting policies
- Configure observability add-ons

## Status
- [x] Implementation completed
- [x] All services communicating through mesh
- [x] Security policies active
- [x] Traffic management working
```

### Task 2: API Gateway Implementation

#### Implementation Context
```markdown
# Implementation: API Gateway Implementation

## Objective
Build centralized API gateway with:
- Request routing and load balancing
- Authentication and authorization
- Rate limiting and throttling
- Request/response transformation

## Context Gathered
- Analyzed API routing requirements
- Designed authentication strategy
- Planned rate limiting policies
- Reviewed gateway performance requirements

## Changes Made
- [Step 1] ✅ Built API gateway service with Express.js
- [Step 2] ✅ Implemented JWT-based authentication
- [Step 3] ✅ Added service discovery integration
- [Step 4] ✅ Configured rate limiting with Redis
- [Step 5] ✅ Implemented request/response logging
- [Step 6] ✅ Added health check aggregation
- [Step 7] ✅ Built API documentation portal

## Issues Encountered
- Service discovery latency → Implemented caching layer
- Rate limiting accuracy → Used sliding window algorithm
- Authentication token validation → Added token caching

## Status
- [x] Implementation completed
- [x] All routing rules working
- [x] Authentication integrated
- [x] Performance benchmarks met
```

### Task 3: Event-Driven Architecture

#### Implementation Context
```markdown
# Implementation: Event-Driven Architecture

## Objective
Implement event-driven communication with:
- Message broker setup (RabbitMQ)
- Event schema registry
- Saga pattern for distributed transactions
- Event sourcing for audit trails

## Context Gathered
- Analyzed event flow patterns
- Designed event schemas and contracts
- Planned saga orchestration
- Reviewed event sourcing requirements

## Changes Made
- [Step 1] ✅ Set up RabbitMQ cluster with high availability
- [Step 2] ✅ Created event schema registry
- [Step 3] ✅ Implemented saga orchestrator service
- [Step 4] ✅ Added event sourcing for critical business events
- [Step 5] ✅ Built event replay and recovery mechanisms
- [Step 6] ✅ Implemented dead letter queue handling
- [Step 7] ✅ Added comprehensive event monitoring

## Issues Encountered
- Message ordering guarantees → Implemented partition-based routing
- Saga compensation logic → Added proper rollback mechanisms
- Event schema evolution → Implemented backward compatibility

## Status
- [x] Implementation completed
- [x] All event flows working
- [x] Saga patterns tested
- [x] Event sourcing operational
```

### Task 4: Distributed Observability

#### Implementation Context
```markdown
# Implementation: Distributed Observability

## Objective
Implement comprehensive observability with:
- Distributed tracing with Jaeger
- Metrics collection with Prometheus
- Centralized logging with ELK stack
- Service dependency mapping

## Context Gathered
- Analyzed observability requirements
- Designed tracing strategy across services
- Planned metrics and alerting
- Reviewed logging aggregation needs

## Changes Made
- [Step 1] ✅ Deployed Jaeger for distributed tracing
- [Step 2] ✅ Configured Prometheus metrics collection
- [Step 3] ✅ Set up ELK stack for log aggregation
- [Step 4] ✅ Implemented service dependency visualization
- [Step 5] ✅ Created comprehensive dashboards in Grafana
- [Step 6] ✅ Added alerting rules for critical metrics
- [Step 7] ✅ Implemented SLI/SLO monitoring

## Issues Encountered
- Trace sampling configuration → Optimized for performance vs visibility
- Log volume management → Implemented log level filtering
- Dashboard performance → Added data aggregation

## Status
- [x] Implementation completed
- [x] Full distributed tracing working
- [x] Metrics and alerting active
- [x] Dashboards operational
```

## Step 5: Testing Strategy

Following AgentSpec testing guidelines for microservices:

### Contract Testing
```javascript
// tests/contract/user-service.contract.test.js
const { Pact } = require('@pact-foundation/pact');
const { UserService } = require('../../services/user-service/src/client');

describe('User Service Contract', () => {
  const provider = new Pact({
    consumer: 'order-service',
    provider: 'user-service',
    port: 1234,
    log: path.resolve(process.cwd(), 'logs', 'pact.log'),
    dir: path.resolve(process.cwd(), 'pacts'),
    logLevel: 'INFO',
  });

  beforeAll(() => provider.setup());
  afterAll(() => provider.finalize());

  describe('when requesting user details', () => {
    beforeEach(() => {
      return provider.addInteraction({
        state: 'user exists',
        uponReceiving: 'a request for user details',
        withRequest: {
          method: 'GET',
          path: '/api/users/123',
          headers: {
            'Accept': 'application/json',
            'Authorization': 'Bearer valid-token'
          }
        },
        willRespondWith: {
          status: 200,
          headers: {
            'Content-Type': 'application/json'
          },
          body: {
            id: 123,
            name: 'John Doe',
            email: 'john@example.com'
          }
        }
      });
    });

    it('should return user details', async () => {
      const userService = new UserService('http://localhost:1234');
      const user = await userService.getUser(123, 'valid-token');

      expect(user.id).toBe(123);
      expect(user.name).toBe('John Doe');
      expect(user.email).toBe('john@example.com');
    });
  });
});
```

### Integration Testing
```javascript
// tests/integration/order-flow.test.js
describe('Order Processing Flow', () => {
  let testEnvironment;

  beforeAll(async () => {
    testEnvironment = await setupTestEnvironment();
  });

  afterAll(async () => {
    await teardownTestEnvironment(testEnvironment);
  });

  it('should process complete order flow', async () => {
    // 1. Create user
    const user = await testEnvironment.userService.createUser({
      name: 'Test User',
      email: 'test@example.com'
    });

    // 2. Add items to inventory
    await testEnvironment.inventoryService.addItem({
      id: 'item-123',
      name: 'Test Product',
      quantity: 10,
      price: 29.99
    });

    // 3. Create order
    const order = await testEnvironment.orderService.createOrder({
      userId: user.id,
      items: [{ itemId: 'item-123', quantity: 2 }]
    });

    // 4. Process payment
    const payment = await testEnvironment.paymentService.processPayment({
      orderId: order.id,
      amount: 59.98,
      paymentMethod: 'test-card'
    });

    // 5. Verify order completion
    expect(order.status).toBe('pending');
    expect(payment.status).toBe('completed');

    // Wait for async processing
    await waitForOrderStatus(order.id, 'completed', 30000);

    // 6. Verify inventory update
    const updatedItem = await testEnvironment.inventoryService.getItem('item-123');
    expect(updatedItem.quantity).toBe(8);

    // 7. Verify notification sent
    const notifications = await testEnvironment.notificationService.getNotifications(user.id);
    expect(notifications).toContainEqual(
      expect.objectContaining({
        type: 'order_completed',
        orderId: order.id
      })
    );
  });
});
```

### Chaos Engineering Tests
```javascript
// tests/chaos/service-resilience.test.js
const { ChaosMonkey } = require('../utils/chaos-monkey');

describe('Service Resilience', () => {
  let chaosMonkey;

  beforeEach(() => {
    chaosMonkey = new ChaosMonkey();
  });

  afterEach(async () => {
    await chaosMonkey.restore();
  });

  it('should handle payment service failure gracefully', async () => {
    // Simulate payment service failure
    await chaosMonkey.killService('payment-service');

    // Attempt to create order
    const orderResponse = await request(app)
      .post('/api/orders')
      .send({
        userId: 'user-123',
        items: [{ itemId: 'item-123', quantity: 1 }]
      })
      .expect(202); // Should accept but not complete

    expect(orderResponse.body.status).toBe('pending_payment');

    // Restore payment service
    await chaosMonkey.restoreService('payment-service');

    // Verify order eventually completes
    await waitForOrderStatus(orderResponse.body.id, 'completed', 60000);
  });

  it('should handle network partitions', async () => {
    // Create network partition between order and inventory services
    await chaosMonkey.createNetworkPartition('order-service', 'inventory-service');

    // Order creation should still work with cached inventory data
    const orderResponse = await request(app)
      .post('/api/orders')
      .send({
        userId: 'user-123',
        items: [{ itemId: 'cached-item', quantity: 1 }]
      })
      .expect(201);

    expect(orderResponse.body.status).toBe('pending_inventory_check');

    // Heal partition
    await chaosMonkey.healNetworkPartition('order-service', 'inventory-service');

    // Verify order completes after partition heals
    await waitForOrderStatus(orderResponse.body.id, 'completed', 60000);
  });
});
```

## Step 6: Deployment and Infrastructure

### Kubernetes Deployment with Istio
```yaml
# infrastructure/kubernetes/services/user-service.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
  labels:
    app: user-service
    version: v1
spec:
  replicas: 3
  selector:
    matchLabels:
      app: user-service
      version: v1
  template:
    metadata:
      labels:
        app: user-service
        version: v1
    spec:
      containers:
      - name: user-service
        image: microservices-platform/user-service:latest
        ports:
        - containerPort: 3000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: user-service-secret
              key: database-url
        - name: JAEGER_ENDPOINT
          value: "http://jaeger-collector:14268/api/traces"
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
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
  name: user-service
  labels:
    app: user-service
spec:
  ports:
  - port: 3000
    name: http
  selector:
    app: user-service
```

### Istio Configuration
```yaml
# infrastructure/istio/virtual-services/user-service.yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: user-service
spec:
  hosts:
  - user-service
  http:
  - match:
    - headers:
        canary:
          exact: "true"
    route:
    - destination:
        host: user-service
        subset: v2
      weight: 100
  - route:
    - destination:
        host: user-service
        subset: v1
      weight: 100
---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: user-service
spec:
  host: user-service
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 50
        maxRequestsPerConnection: 10
    circuitBreaker:
      consecutiveErrors: 3
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
```

### Monitoring Configuration
```yaml
# infrastructure/monitoring/prometheus/service-monitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: microservices-monitoring
spec:
  selector:
    matchLabels:
      monitoring: enabled
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
---
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: microservices-alerts
spec:
  groups:
  - name: microservices.rules
    rules:
    - alert: ServiceDown
      expr: up{job=~".*-service"} == 0
      for: 1m
      labels:
        severity: critical
      annotations:
        summary: "Service {{ $labels.job }} is down"
        description: "Service {{ $labels.job }} has been down for more than 1 minute"

    - alert: HighErrorRate
      expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
      for: 2m
      labels:
        severity: warning
      annotations:
        summary: "High error rate on {{ $labels.job }}"
        description: "Error rate is {{ $value }} errors per second"
```

## Step 7: Validation and Quality Assurance

### Comprehensive Test Suite
```bash
#!/bin/bash
# Microservices test suite following AgentSpec guidelines

set -e

echo "🧪 Running Microservices Test Suite..."

# Unit tests for each service
echo "Running unit tests..."
for service in services/*/; do
  echo "Testing $(basename $service)..."
  cd $service && npm test && cd ../..
done

# Contract tests
echo "Running contract tests..."
npm run test:contract

# Integration tests
echo "Running integration tests..."
npm run test:integration

# Chaos engineering tests
echo "Running chaos engineering tests..."
npm run test:chaos

# Performance tests
echo "Running performance tests..."
npm run test:performance

# Security scans
echo "Running security scans..."
npm run test:security

# Service mesh validation
echo "Validating service mesh configuration..."
istioctl analyze

# Distributed tracing validation
echo "Validating distributed tracing..."
npm run test:tracing

echo "✅ All microservices tests passed successfully!"
```

### Project Context Documentation

```markdown
# Project Context - Microservices Platform

## Project Overview
- **Name**: Microservices Platform
- **Technology Stack**: Node.js, Docker, Kubernetes, Istio, PostgreSQL, RabbitMQ
- **Last Updated**: 2024-01-15

## Failed Commands & Alternatives
| Failed Command | Error | Working Alternative | Notes |
|----------------|--------|-------------------|-------|
| `istioctl install` | RBAC permissions | Use `--set values.pilot.env.EXTERNAL_ISTIOD=false` | Cluster config issue |
| `kubectl apply -f istio/` | CRD not found | Install Istio CRDs first | Order dependency |
| `docker-compose up` | Port conflicts | Use different port mappings | Multiple services |

## Lessons Learned
- Service mesh adds complexity but provides essential observability
- Contract testing prevents integration issues between services
- Chaos engineering reveals hidden failure modes
- Distributed tracing is crucial for debugging microservices
- Circuit breakers prevent cascade failures

## Current Issues
- [ ] Optimize service startup times in Kubernetes
- [ ] Implement cross-service transaction patterns
- [ ] Add more sophisticated traffic splitting
- [ ] Improve service discovery performance

## Performance Metrics
- **Inter-service Latency**: 15ms average
- **Service Availability**: 99.95%
- **Request Success Rate**: 99.8%
- **Trace Coverage**: 100%
- **Circuit Breaker Effectiveness**: 95%
```

## Results and Benefits

### Metrics After AgentSpec Implementation

- **Development Speed**: 40% faster service development
- **System Reliability**: 99.95% uptime achieved
- **Observability**: 100% distributed tracing coverage
- **Performance**: 15ms inter-service communication
- **Fault Tolerance**: 95% circuit breaker effectiveness
- **Security**: mTLS enabled for all service communication

### Key Success Factors

1. **Service Mesh**: Istio provided essential traffic management and security
2. **Contract Testing**: Prevented integration issues between services
3. **Chaos Engineering**: Revealed and fixed hidden failure modes
4. **Distributed Tracing**: Enabled effective debugging of complex flows
5. **Event-Driven Architecture**: Improved system resilience and scalability

## Environment-Specific Usage

### Amazon Kiro IDE
```bash
# Use the microservices specification for distributed system development
# Reference the service mesh patterns for inter-service communication
# Follow the observability guidelines for comprehensive monitoring
```

### Microsoft SpecKit
```bash
# Import the specification for enterprise microservices projects
# Use the quality gates for distributed system validation
# Leverage the testing framework for comprehensive service testing
```

### VS Code with GitHub Copilot
```bash
# Use the specification as context for microservices development
# Reference the distributed patterns when building new services
# Follow the resilience guidelines for fault-tolerant systems
```

## Conclusion

AgentSpec transformed our microservices development by:

- Providing clear architectural guidelines for distributed systems
- Enforcing observability and resilience standards
- Enabling systematic testing of complex service interactions
- Facilitating team collaboration on distributed development
- Maintaining high reliability and performance standards

The specification-driven approach resulted in a production-ready microservices platform with excellent observability, resilience, and scalability.

**Next Steps**: Extend AgentSpec usage to serverless architectures and edge computing deployments.
