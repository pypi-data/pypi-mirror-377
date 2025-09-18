# Example: React Frontend Application with AgentSpec

This example demonstrates how to use AgentSpec for a modern React frontend application with TypeScript, testing, and accessibility features.

## Project Overview

**Technology Stack**: React, TypeScript, Vite, Jest, React Testing Library, Tailwind CSS
**Features**: Component library, state management, routing, accessibility compliance

## Step 1: Initialize Project with AgentSpec

```bash
# Create project directory
mkdir my-react-frontend
cd my-react-frontend

# Generate React-specific specification
agentspec generate --template react_app --output react-spec.md
```

## Step 2: Review Generated Specification

The generated `react-spec.md` includes:

```markdown
# AgentSpec - Project Specification
Generated: 2024-12-15 10:00:00
Template: React Web Application (v1.0.0)
Total instructions: 15

## FRONTEND GUIDELINES

### 1. React Component Architecture
**Tags**: react, components, architecture
**Priority**: 9

Implement a modular component architecture using React functional components with hooks.
Create reusable components with clear props interfaces and proper TypeScript definitions.

### 2. TypeScript Configuration
**Tags**: typescript, type-safety, frontend
**Priority**: 8

Configure strict TypeScript settings with proper type definitions for all components,
hooks, and utilities. Never use 'any' types.

### 3. Accessibility Compliance
**Tags**: accessibility, frontend, ui, compliance
**Priority**: 8

Ensure WCAG 2.1 AA compliance with proper ARIA labels, keyboard navigation,
color contrast ratios, and screen reader compatibility.

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
- [ ] Run complete test suite (`npm test`)
- [ ] Check for linting/build errors (`npm run lint`)
- [ ] Validate browser functionality
- [ ] Update documentation
- [ ] Update project context with lessons learned

## QUALITY GATES

Every task must pass these quality gates:

1. **Zero Errors**: No linting, compilation, or build errors
2. **Test Coverage**: All new code covered by tests
3. **Documentation**: Public APIs documented
4. **Security**: Security best practices followed
5. **Performance**: No performance regressions
6. **Accessibility**: WCAG 2.1 AA compliance maintained
```

## Step 3: Project Structure Setup

Following AgentSpec guidelines, create the project structure:

```
my-react-frontend/
├── .agentspec/                  # AgentSpec configuration

├── project_context.md           # Shared project knowledge
├── react-spec.md               # Generated specification
├──
├── src/
│   ├── components/             # Reusable components
│   │   ├── ui/                # Base UI components
│   │   └── features/          # Feature-specific components
│   ├── hooks/                 # Custom React hooks
│   ├── utils/                 # Utility functions
│   ├── types/                 # TypeScript type definitions
│   ├── styles/                # Global styles and themes
│   └── __tests__/             # Test files
├──
├── public/
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
└── jest.config.js
```

## Step 4: Development Workflow

### Task 1: Component Library Setup

#### Task Documentation
```markdown
# Task: Component Library Setup

## Objective
Create a foundational component library with:
- Base UI components (Button, Input, Card, etc.)
- TypeScript interfaces for all props
- Comprehensive test coverage
- Storybook documentation
- Accessibility compliance

## Context Gathered
- Reviewed design system requirements
- Analyzed existing component patterns
- Chose Tailwind CSS for styling
- Selected React Testing Library for testing
- Planned component hierarchy and API design

## Changes Made
- [Step 1] ✅ Set up base Button component with variants
- [Step 2] ✅ Created Input component with validation states
- [Step 3] ✅ Built Card component with flexible content areas
- [Step 4] ✅ Added comprehensive TypeScript interfaces
- [Step 5] ✅ Implemented accessibility features (ARIA labels, keyboard nav)
- [Step 6] ✅ Created test suites for all components
- [Step 7] ✅ Set up Storybook documentation

## Issues Encountered
- Tailwind CSS purging unused styles → Updated purge configuration
- TypeScript strict mode errors → Fixed all type definitions
- Accessibility testing challenges → Added jest-axe for automated a11y testing

## Next Steps
- Add more complex components (Modal, Dropdown, etc.)
- Implement theming system
- Add animation utilities

## Status
- [x] Implementation completed
- [x] All tests passing (100% coverage)
- [x] Accessibility audit passed
- [x] Documentation complete
- [x] Code review approved
```

### Task 2: State Management Implementation

#### Implementation Context
```markdown
# Implementation: State Management Implementation

## Objective
Implement state management using React Context and useReducer for:
- User authentication state
- Application theme preferences
- Form state management
- API data caching

## Context Gathered
- Analyzed state requirements across components
- Chose Context + useReducer over external libraries for simplicity
- Designed state structure and action types
- Planned provider hierarchy and context splitting

## Changes Made
- [Step 1] ✅ Created AuthContext with login/logout actions
- [Step 2] ✅ Built ThemeContext for dark/light mode
- [Step 3] ✅ Implemented FormContext for complex forms
- [Step 4] ✅ Added ApiContext for data fetching and caching
- [Step 5] ✅ Created custom hooks for each context
- [Step 6] ✅ Added TypeScript interfaces for all state shapes
- [Step 7] ✅ Implemented comprehensive testing

## Issues Encountered
- Context re-rendering performance → Split contexts by concern
- TypeScript inference issues → Added explicit type parameters
- Testing context providers → Created test utilities for context wrapping

## Status
- [x] Implementation completed
- [x] Performance optimized
- [x] All tests passing
- [x] Documentation updated
```

### Task 3: Routing and Navigation

#### Implementation Context
```markdown
# Implementation: Routing and Navigation

## Objective
Implement client-side routing with:
- React Router v6 integration
- Protected routes for authenticated users
- Breadcrumb navigation
- Route-based code splitting

## Context Gathered
- Analyzed application page structure
- Designed route hierarchy and nesting
- Planned authentication guards
- Identified code splitting opportunities

## Changes Made
- [Step 1] ✅ Set up React Router with nested routes
- [Step 2] ✅ Created ProtectedRoute component
- [Step 3] ✅ Built breadcrumb navigation system
- [Step 4] ✅ Implemented lazy loading for route components
- [Step 5] ✅ Added route transition animations
- [Step 6] ✅ Created navigation menu with active states
- [Step 7] ✅ Added comprehensive route testing

## Issues Encountered
- Route parameter TypeScript typing → Created route parameter interfaces
- Lazy loading error boundaries → Added proper error handling
- Navigation state persistence → Implemented route state management

## Status
- [x] Implementation completed
- [x] All routes tested
- [x] Performance optimized
- [x] Accessibility verified
```

## Step 5: Testing Strategy

Following AgentSpec testing guidelines:

### Test Structure
```
src/__tests__/
├── components/           # Component tests
├── hooks/               # Custom hook tests
├── utils/               # Utility function tests
├── integration/         # Integration tests
└── e2e/                # End-to-end tests
```

### Test Implementation
```javascript
// Example component test following AgentSpec guidelines
import { render, screen, fireEvent } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { Button } from '../components/ui/Button';

expect.extend(toHaveNoViolations);

describe('Button Component', () => {
  it('renders with correct text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button')).toHaveTextContent('Click me');
  });

  it('handles click events', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);

    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('meets accessibility standards', async () => {
    const { container } = render(<Button>Accessible button</Button>);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('supports keyboard navigation', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);

    const button = screen.getByRole('button');
    button.focus();
    fireEvent.keyDown(button, { key: 'Enter' });
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

## Step 6: Validation and Quality Assurance

### Comprehensive Test Suite
```bash
#!/bin/bash
# test script following AgentSpec guidelines

set -e

echo "🧪 Running React Frontend Test Suite..."

# Type checking
echo "Checking TypeScript..."
npx tsc --noEmit

# Linting
echo "Running ESLint..."
npx eslint src/ --ext .ts,.tsx

# Unit and integration tests
echo "Running Jest tests..."
npm test -- --coverage --watchAll=false

# Accessibility tests
echo "Running accessibility tests..."
npm run test:a11y

# Build verification
echo "Testing production build..."
npm run build

# Bundle analysis
echo "Analyzing bundle size..."
npm run analyze

echo "✅ All tests passed successfully!"
```

### Project Context Documentation

```markdown
# Project Context - React Frontend App

## Project Overview
- **Name**: My React App
- **Technology Stack**: React 18, TypeScript, Vite, Tailwind CSS, Jest
- **Last Updated**: 2024-01-15

## Failed Commands & Alternatives
| Failed Command | Error | Working Alternative | Notes |
|----------------|--------|-------------------|-------|
| `npm test -- --coverage` | Jest config issue | `npm test -- --coverage --watchAll=false` | CI mode needed |
| `npm run build` | TypeScript errors | Fix types first, then build | Strict mode enabled |

## Lessons Learned
- TypeScript strict mode catches many runtime errors early
- Accessibility testing should be automated with jest-axe
- Component testing requires proper context providers
- Bundle size monitoring prevents performance regressions
- Tailwind CSS purging needs careful configuration

## Current Issues
- [ ] Bundle size optimization for production
- [ ] Implement service worker for offline functionality
- [ ] Add internationalization support
- [ ] Optimize image loading and caching

## Performance Metrics
- **Bundle Size**: 145KB gzipped
- **First Contentful Paint**: 1.2s
- **Largest Contentful Paint**: 2.1s
- **Cumulative Layout Shift**: 0.05
- **Test Coverage**: 95%
```

## Results and Benefits

### Metrics After AgentSpec Implementation

- **Development Speed**: 35% faster component development
- **Code Quality**: 98% test coverage maintained
- **Accessibility**: 100% WCAG 2.1 AA compliance
- **Performance**: Lighthouse score 95+
- **Type Safety**: Zero TypeScript errors in production
- **Bundle Size**: Optimized to 145KB gzipped

### Key Success Factors

1. **Component-First Architecture**: Reusable components reduced code duplication
2. **TypeScript Integration**: Caught 40+ potential runtime errors during development
3. **Accessibility Focus**: Built-in a11y testing prevented compliance issues
4. **Testing Strategy**: Comprehensive testing caught regressions early
5. **Performance Monitoring**: Bundle analysis prevented size bloat

## Environment-Specific Usage

### Amazon Kiro IDE
```bash
# In Kiro IDE, use the generated spec as a project guide
# The specification provides context for AI-assisted development
# Reference project contexts when resuming work sessions
```

### Microsoft SpecKit
```bash
# Import the generated specification into SpecKit
# Use the quality gates as automated checks
# Leverage the implementation framework for project planning
```

### VS Code with GitHub Copilot
```bash
# Use the specification as context for Copilot suggestions
# Reference the coding standards when accepting AI suggestions
# Follow the validation framework for quality assurance
```

## Conclusion

AgentSpec transformed our React frontend development by:

- Providing clear architectural guidelines for component design
- Enforcing accessibility and performance standards
- Enabling systematic testing and quality assurance
- Facilitating team collaboration through shared specifications
- Maintaining high code quality throughout development

The specification-driven approach resulted in a production-ready React application with excellent performance, accessibility, and maintainability.

**Next Steps**: Extend AgentSpec usage to backend API development and mobile applications.
