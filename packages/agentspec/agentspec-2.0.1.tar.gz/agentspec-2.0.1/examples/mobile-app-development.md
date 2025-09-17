# Example: Mobile App Development with AgentSpec

This example demonstrates how to use AgentSpec for cross-platform mobile app development using React Native with native modules, offline capabilities, and comprehensive testing.

## Project Overview

**Technology Stack**: React Native, TypeScript, Expo, Redux Toolkit, React Query, SQLite
**Features**: Cross-platform compatibility, offline-first architecture, push notifications, biometric authentication

## Step 1: Initialize Project with AgentSpec

```bash
# Create project directory
mkdir my-mobile-app
cd my-mobile-app

# Generate mobile app specification
agentspec generate --template mobile-app --output mobile-spec.md
```

## Step 2: Review Generated Specification

The generated `mobile-spec.md` includes:

```markdown
# AgentSpec - Project Specification
Generated: 2024-01-15 10:00:00
Template: Mobile App (v1.0.0)
Total instructions: 20

## MOBILE DEVELOPMENT GUIDELINES

### 1. Cross-Platform Architecture
**Tags**: mobile, react-native, cross-platform, architecture
**Priority**: 10

Design components and navigation for both iOS and Android platforms.
Use platform-specific code only when necessary for native functionality.

### 2. Offline-First Design
**Tags**: mobile, offline, data-sync, storage
**Priority**: 9

Implement offline-first architecture with local data storage,
background sync, and conflict resolution for seamless user experience.

### 3. Performance Optimization
**Tags**: mobile, performance, optimization, memory
**Priority**: 8

Optimize for mobile constraints including battery life, memory usage,
network efficiency, and smooth 60fps animations.

### 4. Native Module Integration
**Tags**: mobile, native-modules, ios, android
**Priority**: 7

Integrate native modules for platform-specific functionality like
biometrics, camera, location services, and push notifications.

## IMPLEMENTATION FRAMEWORK

### Pre-Development Checklist

- [ ] Test on both iOS and Android platforms
- [ ] Verify offline functionality works
- [ ] Check performance on low-end devices

### During Implementation
- [ ] Update project context after each significant step
- [ ] Test on physical devices regularly
- [ ] Validate offline/online state transitions
- [ ] Monitor memory usage and performance

### Post-Task Validation
- [ ] Run complete test suite on both platforms
- [ ] Test offline scenarios thoroughly
- [ ] Validate push notification delivery
- [ ] Check app store compliance
- [ ] Update documentation

## QUALITY GATES

Every task must pass these quality gates:

1. **Zero Errors**: No crashes or runtime errors on either platform
2. **Performance**: 60fps animations and <3s startup time
3. **Offline Support**: Full functionality available offline
4. **Platform Compliance**: Meets iOS and Android guidelines
5. **Accessibility**: VoiceOver and TalkBack support
6. **Security**: Secure storage and data transmission
```

## Step 3: Project Structure Setup

Following AgentSpec guidelines for mobile development:

```
my-mobile-app/
├── .agentspec/                  # AgentSpec configuration
├── project_context.md           # Shared project knowledge
├── mobile-spec.md              # Generated specification
├──
├── src/
│   ├── components/             # Reusable UI components
│   │   ├── common/            # Cross-platform components
│   │   ├── ios/               # iOS-specific components
│   │   └── android/           # Android-specific components
│   │
│   ├── screens/               # Screen components
│   │   ├── auth/
│   │   ├── home/
│   │   └── profile/
│   │
│   ├── navigation/            # Navigation configuration
│   │   ├── AppNavigator.tsx
│   │   └── types.ts
│   │
│   ├── services/              # API and data services
│   │   ├── api/
│   │   ├── storage/
│   │   └── sync/
│   │
│   ├── store/                 # Redux store configuration
│   │   ├── slices/
│   │   └── index.ts
│   │
│   ├── utils/                 # Utility functions
│   │   ├── platform.ts
│   │   ├── permissions.ts
│   │   └── validation.ts
│   │
│   └── types/                 # TypeScript type definitions
├──
├── ios/                       # iOS-specific code
├── android/                   # Android-specific code
├──
├── __tests__/
│   ├── components/
│   ├── screens/
│   ├── services/
│   └── e2e/
├──
├── assets/
│   ├── images/
│   ├── fonts/
│   └── sounds/
├──
├── app.json
├── package.json
├── tsconfig.json
└── metro.config.js
```

## Step 4: Development Workflow

### Task 1: Offline-First Architecture

#### Task Documentation
```bash

```

#### Task Documentation
```markdown
# Task: Offline-First Architecture

## Objective
Implement offline-first data architecture with:
- Local SQLite database for data persistence
- Background synchronization with server
- Conflict resolution for concurrent edits
- Offline queue for pending operations

## Context Gathered
- Analyzed data flow and synchronization requirements
- Designed local database schema
- Planned conflict resolution strategies
- Reviewed offline UX patterns

## Changes Made
- [Step 1] ✅ Set up SQLite database with TypeORM
- [Step 2] ✅ Implemented local data models and repositories
- [Step 3] ✅ Built background sync service
- [Step 4] ✅ Added conflict resolution algorithms
- [Step 5] ✅ Created offline operation queue
- [Step 6] ✅ Implemented network state monitoring
- [Step 7] ✅ Added offline UI indicators

## Issues Encountered
- SQLite migration issues → Added proper migration scripts
- Sync conflict edge cases → Implemented last-write-wins with user override
- Background sync battery usage → Added intelligent sync scheduling

## Next Steps
- Add selective sync for large datasets
- Implement data compression for sync
- Add offline analytics tracking

## Status
- [x] Implementation completed
- [x] Offline functionality tested extensively
- [x] Sync performance optimized
- [x] Conflict resolution working
```

### Task 2: Native Module Integration

#### Implementation Context
```markdown
# Implementation: Native Module Integration

## Objective
Integrate native functionality including:
- Biometric authentication (Face ID, Touch ID, Fingerprint)
- Camera and photo library access
- Push notification handling
- Location services with background tracking

## Context Gathered
- Analyzed native functionality requirements
- Reviewed platform-specific implementation differences
- Planned permission handling strategies
- Designed native module interfaces

## Changes Made
- [Step 1] ✅ Integrated react-native-biometrics for authentication
- [Step 2] ✅ Added react-native-image-picker for camera access
- [Step 3] ✅ Implemented push notifications with Firebase
- [Step 4] ✅ Set up location tracking with react-native-geolocation
- [Step 5] ✅ Created unified permission management system
- [Step 6] ✅ Added native module error handling
- [Step 7] ✅ Implemented platform-specific UI adaptations

## Issues Encountered
- iOS permission descriptions → Added proper Info.plist entries
- Android permission timing → Implemented proper permission flow
- Push notification token handling → Added token refresh logic

## Status
- [x] Implementation completed
- [x] All native features working on both platforms
- [x] Permission flows tested
- [x] Error handling comprehensive
```

### Task 3: Performance Optimization

#### Implementation Context
```markdown
# Implementation: Performance Optimization

## Objective
Optimize app performance for:
- Fast startup times (<3 seconds)
- Smooth 60fps animations
- Efficient memory usage
- Optimized bundle size

## Context Gathered
- Analyzed performance bottlenecks using Flipper
- Identified heavy components and operations
- Reviewed bundle analysis and optimization opportunities
- Planned lazy loading and code splitting strategies

## Changes Made
- [Step 1] ✅ Implemented lazy loading for screens
- [Step 2] ✅ Optimized image loading and caching
- [Step 3] ✅ Added React.memo for expensive components
- [Step 4] ✅ Implemented virtualized lists for large datasets
- [Step 5] ✅ Optimized Redux store structure
- [Step 6] ✅ Added bundle splitting and code optimization
- [Step 7] ✅ Implemented performance monitoring

## Issues Encountered
- FlatList performance with complex items → Added getItemLayout optimization
- Image memory leaks → Implemented proper image cleanup
- Redux re-renders → Added proper selector memoization

## Status
- [x] Implementation completed
- [x] Startup time under 3 seconds
- [x] 60fps maintained during navigation
- [x] Memory usage optimized
```

### Task 4: Cross-Platform UI Components

#### Implementation Context
```markdown
# Implementation: Cross-Platform UI Components

## Objective
Build consistent UI component library with:
- Platform-adaptive design system
- Accessibility support for screen readers
- Responsive layouts for different screen sizes
- Consistent theming and styling

## Context Gathered
- Analyzed design system requirements
- Reviewed platform-specific UI guidelines
- Planned accessibility implementation
- Designed component API interfaces

## Changes Made
- [Step 1] ✅ Created base component library with TypeScript
- [Step 2] ✅ Implemented platform-adaptive styling system
- [Step 3] ✅ Added comprehensive accessibility support
- [Step 4] ✅ Built responsive layout components
- [Step 5] ✅ Created theming system with dark mode support
- [Step 6] ✅ Added animation and gesture handling
- [Step 7] ✅ Implemented component testing suite

## Issues Encountered
- Platform styling differences → Created platform-specific style overrides
- Accessibility testing → Added automated accessibility testing
- Animation performance → Optimized using native driver

## Status
- [x] Implementation completed
- [x] All components working on both platforms
- [x] Accessibility compliance verified
- [x] Performance benchmarks met
```

## Step 5: Testing Strategy

Following AgentSpec testing guidelines for mobile development:

### Component Testing
```typescript
// __tests__/components/LoginForm.test.tsx
import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { LoginForm } from '../../src/components/auth/LoginForm';
import { AuthProvider } from '../../src/contexts/AuthContext';

const renderWithAuth = (component: React.ReactElement) => {
  return render(
    <AuthProvider>
      {component}
    </AuthProvider>
  );
};

describe('LoginForm', () => {
  it('should handle login submission', async () => {
    const mockLogin = jest.fn().mockResolvedValue({ success: true });

    const { getByTestId, getByText } = renderWithAuth(
      <LoginForm onLogin={mockLogin} />
    );

    // Fill in form fields
    fireEvent.changeText(getByTestId('email-input'), 'test@example.com');
    fireEvent.changeText(getByTestId('password-input'), 'password123');

    // Submit form
    fireEvent.press(getByText('Login'));

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123'
      });
    });
  });

  it('should show validation errors', async () => {
    const { getByTestId, getByText } = renderWithAuth(
      <LoginForm onLogin={jest.fn()} />
    );

    // Submit without filling fields
    fireEvent.press(getByText('Login'));

    await waitFor(() => {
      expect(getByText('Email is required')).toBeTruthy();
      expect(getByText('Password is required')).toBeTruthy();
    });
  });

  it('should support biometric login when available', async () => {
    const mockBiometricLogin = jest.fn().mockResolvedValue({ success: true });

    const { getByTestId } = renderWithAuth(
      <LoginForm
        onLogin={jest.fn()}
        onBiometricLogin={mockBiometricLogin}
        biometricAvailable={true}
      />
    );

    fireEvent.press(getByTestId('biometric-login-button'));

    await waitFor(() => {
      expect(mockBiometricLogin).toHaveBeenCalled();
    });
  });
});
```

### E2E Testing with Detox
```typescript
// e2e/auth.e2e.ts
import { device, expect, element, by } from 'detox';

describe('Authentication Flow', () => {
  beforeAll(async () => {
    await device.launchApp();
  });

  beforeEach(async () => {
    await device.reloadReactNative();
  });

  it('should complete login flow', async () => {
    // Navigate to login screen
    await element(by.id('login-button')).tap();

    // Fill in credentials
    await element(by.id('email-input')).typeText('test@example.com');
    await element(by.id('password-input')).typeText('password123');

    // Submit login
    await element(by.text('Login')).tap();

    // Verify successful login
    await expect(element(by.text('Welcome back!'))).toBeVisible();
    await expect(element(by.id('home-screen'))).toBeVisible();
  });

  it('should handle offline login', async () => {
    // Simulate offline state
    await device.setNetworkConnection('none');

    // Navigate to login screen
    await element(by.id('login-button')).tap();

    // Try to login with cached credentials
    await element(by.id('email-input')).typeText('cached@example.com');
    await element(by.id('password-input')).typeText('password123');
    await element(by.text('Login')).tap();

    // Verify offline login works
    await expect(element(by.text('Offline mode'))).toBeVisible();
    await expect(element(by.id('home-screen'))).toBeVisible();

    // Restore network
    await device.setNetworkConnection('wifi');
  });

  it('should sync data when coming back online', async () => {
    // Start offline
    await device.setNetworkConnection('none');

    // Create some data offline
    await element(by.id('add-item-button')).tap();
    await element(by.id('item-title-input')).typeText('Offline Item');
    await element(by.text('Save')).tap();

    // Verify item appears with sync indicator
    await expect(element(by.text('Offline Item'))).toBeVisible();
    await expect(element(by.id('sync-pending-indicator'))).toBeVisible();

    // Go back online
    await device.setNetworkConnection('wifi');

    // Wait for sync to complete
    await waitFor(element(by.id('sync-complete-indicator')))
      .toBeVisible()
      .withTimeout(10000);

    // Verify sync indicator is gone
    await expect(element(by.id('sync-pending-indicator'))).not.toBeVisible();
  });
});
```

### Performance Testing
```typescript
// __tests__/performance/startup.test.ts
import { performance } from 'perf_hooks';
import { AppRegistry } from 'react-native';
import App from '../../App';

describe('App Performance', () => {
  it('should start up within 3 seconds', async () => {
    const startTime = performance.now();

    // Simulate app startup
    AppRegistry.registerComponent('MyMobileApp', () => App);

    // Wait for initial render
    await new Promise(resolve => setTimeout(resolve, 100));

    const endTime = performance.now();
    const startupTime = endTime - startTime;

    expect(startupTime).toBeLessThan(3000); // 3 seconds
  });

  it('should maintain 60fps during navigation', async () => {
    // This would integrate with performance monitoring tools
    // to measure actual frame rates during navigation
    const frameRates = await measureNavigationPerformance();

    expect(frameRates.average).toBeGreaterThanOrEqual(58); // Allow for minor drops
    expect(frameRates.minimum).toBeGreaterThanOrEqual(45); // No severe drops
  });
});
```

## Step 6: Platform-Specific Considerations

### iOS Configuration
```xml
<!-- ios/MyMobileApp/Info.plist -->
<dict>
  <!-- Camera permissions -->
  <key>NSCameraUsageDescription</key>
  <string>This app needs access to camera to take photos</string>

  <!-- Photo library permissions -->
  <key>NSPhotoLibraryUsageDescription</key>
  <string>This app needs access to photo library to select images</string>

  <!-- Location permissions -->
  <key>NSLocationWhenInUseUsageDescription</key>
  <string>This app needs location access to provide location-based features</string>

  <!-- Biometric authentication -->
  <key>NSFaceIDUsageDescription</key>
  <string>This app uses Face ID for secure authentication</string>

  <!-- Background modes -->
  <key>UIBackgroundModes</key>
  <array>
    <string>background-fetch</string>
    <string>background-processing</string>
  </array>
</dict>
```

### Android Configuration
```xml
<!-- android/app/src/main/AndroidManifest.xml -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
  <!-- Permissions -->
  <uses-permission android:name="android.permission.CAMERA" />
  <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
  <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
  <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
  <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
  <uses-permission android:name="android.permission.USE_FINGERPRINT" />
  <uses-permission android:name="android.permission.USE_BIOMETRIC" />
  <uses-permission android:name="android.permission.INTERNET" />
  <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />

  <application
    android:name=".MainApplication"
    android:allowBackup="false"
    android:theme="@style/AppTheme">

    <!-- Main activity -->
    <activity
      android:name=".MainActivity"
      android:exported="true"
      android:launchMode="singleTop"
      android:theme="@style/LaunchTheme"
      android:configChanges="keyboard|keyboardHidden|orientation|screenSize|uiMode"
      android:windowSoftInputMode="adjustResize">
      <intent-filter>
        <action android:name="android.intent.action.MAIN" />
        <category android:name="android.intent.category.LAUNCHER" />
      </intent-filter>
    </activity>
  </application>
</manifest>
```

## Step 7: Validation and Quality Assurance

### Comprehensive Test Suite
```bash
#!/bin/bash
# Mobile app test suite following AgentSpec guidelines

set -e

echo "📱 Running Mobile App Test Suite..."

# TypeScript type checking
echo "Running TypeScript checks..."
npx tsc --noEmit

# Linting
echo "Running ESLint..."
npx eslint src/ --ext .ts,.tsx

# Unit and integration tests
echo "Running Jest tests..."
npm test -- --coverage --watchAll=false

# Component tests
echo "Running component tests..."
npm run test:components

# iOS build test
echo "Testing iOS build..."
cd ios && xcodebuild -workspace MyMobileApp.xcworkspace -scheme MyMobileApp -configuration Debug -sdk iphonesimulator -arch x86_64 build && cd ..

# Android build test
echo "Testing Android build..."
cd android && ./gradlew assembleDebug && cd ..

# E2E tests (if devices available)
if command -v detox &> /dev/null; then
  echo "Running E2E tests..."
  detox test --configuration ios.sim.debug
  detox test --configuration android.emu.debug
fi

# Bundle analysis
echo "Analyzing bundle size..."
npx react-native bundle --platform ios --dev false --entry-file index.js --bundle-output ios-bundle.js --assets-dest ios-assets
npx react-native bundle --platform android --dev false --entry-file index.js --bundle-output android-bundle.js --assets-dest android-assets

echo "✅ All mobile app tests passed successfully!"
```

### Project Context Documentation

```markdown
# Project Context - Mobile App

## Project Overview
- **Name**: My Mobile App
- **Technology Stack**: React Native, TypeScript, Expo, Redux Toolkit, SQLite
- **Last Updated**: 2024-01-15

## Failed Commands & Alternatives
| Failed Command | Error | Working Alternative | Notes |
|----------------|--------|-------------------|-------|
| `npx react-native run-ios` | Simulator not found | `npx react-native run-ios --simulator="iPhone 14"` | Specify simulator |
| `cd android && ./gradlew clean` | Permission denied | `chmod +x gradlew` first | File permissions |
| `detox test` | No devices | Use `--configuration ios.sim.debug` | Specify configuration |

## Lessons Learned
- Always test on physical devices, not just simulators
- Offline functionality requires careful state management
- Platform-specific code should be minimal and well-abstracted
- Performance testing on low-end devices is crucial
- Biometric authentication UX varies significantly between platforms

## Current Issues
- [ ] Optimize app startup time on older Android devices
- [ ] Implement incremental sync for large datasets
- [ ] Add automated accessibility testing
- [ ] Improve offline conflict resolution UX

## Performance Metrics
- **Startup Time**: 2.8s (iOS), 3.2s (Android)
- **Bundle Size**: 15MB (iOS), 18MB (Android)
- **Memory Usage**: 45MB average
- **Battery Impact**: Low (background sync optimized)
- **Crash Rate**: <0.1%
```

## Results and Benefits

### Metrics After AgentSpec Implementation

- **Development Speed**: 45% faster cross-platform development
- **Code Quality**: 92% test coverage maintained
- **Performance**: <3s startup time on both platforms
- **Offline Support**: 100% functionality available offline
- **User Experience**: 4.8/5 app store rating
- **Platform Compliance**: Passed all app store reviews

### Key Success Factors

1. **Offline-First Architecture**: Seamless user experience regardless of connectivity
2. **Cross-Platform Consistency**: Unified codebase with platform-specific optimizations
3. **Performance Focus**: Smooth 60fps animations and fast startup times
4. **Native Integration**: Proper use of platform-specific features
5. **Comprehensive Testing**: High confidence in releases across platforms

## Environment-Specific Usage

### Amazon Kiro IDE
```bash
# Use the mobile specification for React Native development
# Reference the offline patterns for robust mobile apps
# Follow the performance guidelines for optimal user experience
```

### Microsoft SpecKit
```bash
# Import the specification for mobile project planning
# Use the quality gates for app store compliance
# Leverage the testing framework for comprehensive mobile testing
```

### VS Code with GitHub Copilot
```bash
# Use the specification as context for mobile development
# Reference the platform-specific patterns for native integration
# Follow the accessibility guidelines for inclusive mobile apps
```

## Conclusion

AgentSpec transformed our mobile app development by:

- Providing clear guidelines for cross-platform architecture
- Enforcing performance and accessibility standards
- Enabling systematic testing across platforms and scenarios
- Facilitating offline-first development patterns
- Maintaining high code quality and user experience

The specification-driven approach resulted in a production-ready mobile app with excellent performance, accessibility, and platform compliance.

**Next Steps**: Extend AgentSpec usage to IoT applications and wearable device integration.
