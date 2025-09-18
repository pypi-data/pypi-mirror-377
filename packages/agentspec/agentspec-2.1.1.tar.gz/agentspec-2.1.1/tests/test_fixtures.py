"""
Additional test fixtures and utilities.
"""

import json
from pathlib import Path
from unittest.mock import Mock

import pytest


@pytest.fixture
def sample_instruction_data():
    """Sample instruction data for testing."""
    return {
        "id": "test_instruction_comprehensive",
        "version": "1.2.0",
        "tags": ["testing", "quality", "comprehensive"],
        "content": "This is a comprehensive test instruction with detailed content for validation.",
        "conditions": [
            {"type": "project_type", "value": "web_frontend", "operator": "equals"}
        ],
        "parameters": [
            {
                "name": "test_framework",
                "type": "string",
                "default": "jest",
                "description": "Testing framework to use",
                "required": False,
            }
        ],
        "dependencies": ["base_quality_instruction"],
        "metadata": {
            "category": "testing",
            "priority": 8,
            "author": "test_author",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-06-01T00:00:00Z",
            "default_language": "en",
        },
        "language_variants": {
            "es": {
                "content": "Esta es una instrucción de prueba integral con contenido detallado para validación.",
                "parameters": [
                    {
                        "name": "test_framework",
                        "type": "string",
                        "default": "jest",
                        "description": "Marco de pruebas a utilizar",
                        "required": False,
                    }
                ],
            }
        },
    }


@pytest.fixture
def sample_template_data():
    """Sample template data for testing."""
    return {
        "id": "comprehensive_react_app",
        "name": "Comprehensive React Application",
        "description": "A comprehensive template for React applications with testing, linting, and deployment setup.",
        "version": "2.1.0",
        "project_type": "web_frontend",
        "technology_stack": ["react", "javascript", "typescript", "webpack"],
        "default_tags": ["frontend", "react", "testing", "quality", "deployment"],
        "required_instructions": ["react_setup", "testing_setup", "quality_gates"],
        "optional_instructions": ["typescript_config", "deployment_config"],
        "excluded_instructions": ["vue_specific", "angular_specific"],
        "parameters": {
            "project_name": {
                "type": "string",
                "default": "my-react-app",
                "description": "Name of the React project",
                "required": True,
            },
            "use_typescript": {
                "type": "boolean",
                "default": True,
                "description": "Whether to use TypeScript",
                "required": False,
            },
            "testing_framework": {
                "type": "string",
                "default": "jest",
                "description": "Testing framework to use",
                "required": False,
                "options": ["jest", "vitest", "mocha"],
            },
        },
        "conditions": [
            {
                "type": "file_exists",
                "value": "package.json",
                "operator": "exists",
                "weight": 0.9,
            },
            {
                "type": "dependency_exists",
                "value": "react",
                "operator": "exists",
                "weight": 0.8,
            },
        ],
        "metadata": {
            "category": "web",
            "complexity": "intermediate",
            "author": "template_author",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-06-01T00:00:00Z",
            "tags": ["popular", "maintained", "production-ready"],
        },
    }


@pytest.fixture
def comprehensive_project_structure(temp_dir):
    """Create a comprehensive project structure for testing."""
    project_dir = temp_dir / "comprehensive_project"
    project_dir.mkdir()

    # Package.json with comprehensive dependencies
    package_json = {
        "name": "comprehensive-react-app",
        "version": "1.0.0",
        "description": "A comprehensive React application",
        "main": "src/index.js",
        "scripts": {
            "start": "react-scripts start",
            "build": "react-scripts build",
            "test": "react-scripts test",
            "eject": "react-scripts eject",
            "lint": "eslint src/",
            "type-check": "tsc --noEmit",
        },
        "dependencies": {
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
            "react-router-dom": "^6.8.0",
            "axios": "^1.3.0",
            "styled-components": "^5.3.6",
        },
        "devDependencies": {
            "react-scripts": "5.0.1",
            "@testing-library/react": "^13.4.0",
            "@testing-library/jest-dom": "^5.16.5",
            "@testing-library/user-event": "^14.4.3",
            "@types/react": "^18.0.27",
            "@types/react-dom": "^18.0.10",
            "typescript": "^4.9.4",
            "eslint": "^8.34.0",
            "prettier": "^2.8.4",
        },
        "browserslist": {
            "production": [">0.2%", "not dead", "not op_mini all"],
            "development": [
                "last 1 chrome version",
                "last 1 firefox version",
                "last 1 safari version",
            ],
        },
    }

    with open(project_dir / "package.json", "w") as f:
        json.dump(package_json, f, indent=2)

    # TypeScript config
    tsconfig = {
        "compilerOptions": {
            "target": "es5",
            "lib": ["dom", "dom.iterable", "es6"],
            "allowJs": True,
            "skipLibCheck": True,
            "esModuleInterop": True,
            "allowSyntheticDefaultImports": True,
            "strict": True,
            "forceConsistentCasingInFileNames": True,
            "noFallthroughCasesInSwitch": True,
            "module": "esnext",
            "moduleResolution": "node",
            "resolveJsonModule": True,
            "isolatedModules": True,
            "noEmit": True,
            "jsx": "react-jsx",
        },
        "include": ["src"],
        "exclude": ["node_modules"],
    }

    with open(project_dir / "tsconfig.json", "w") as f:
        json.dump(tsconfig, f, indent=2)

    # Create source structure
    src_dir = project_dir / "src"
    src_dir.mkdir()

    # Main App component
    (src_dir / "App.tsx").write_text(
        """
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import styled from 'styled-components';
import Home from './components/Home';
import About from './components/About';

const AppContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
`;

function App() {
  return (
    <Router>
      <AppContainer>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </AppContainer>
    </Router>
  );
}

export default App;
    """
    )

    # Index file
    (src_dir / "index.tsx").write_text(
        """
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
    """
    )

    # Components directory
    components_dir = src_dir / "components"
    components_dir.mkdir()

    (components_dir / "Home.tsx").write_text(
        """
import React from 'react';

const Home: React.FC = () => {
  return (
    <div>
      <h1>Welcome Home</h1>
      <p>This is the home page of our comprehensive React app.</p>
    </div>
  );
};

export default Home;
    """
    )

    (components_dir / "About.tsx").write_text(
        """
import React from 'react';

const About: React.FC = () => {
  return (
    <div>
      <h1>About Us</h1>
      <p>Learn more about our comprehensive React application.</p>
    </div>
  );
};

export default About;
    """
    )

    # Test files
    tests_dir = src_dir / "__tests__"
    tests_dir.mkdir()

    (tests_dir / "App.test.tsx").write_text(
        """
import React from 'react';
import { render, screen } from '@testing-library/react';
import App from '../App';

test('renders app without crashing', () => {
  render(<App />);
  expect(screen.getByText(/welcome home/i)).toBeInTheDocument();
});
    """
    )

    (tests_dir / "Home.test.tsx").write_text(
        """
import React from 'react';
import { render, screen } from '@testing-library/react';
import Home from '../components/Home';

test('renders home component', () => {
  render(<Home />);
  expect(screen.getByText(/welcome home/i)).toBeInTheDocument();
});
    """
    )

    # Styles
    (src_dir / "index.css").write_text(
        """
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}
    """
    )

    # Public directory
    public_dir = project_dir / "public"
    public_dir.mkdir()

    (public_dir / "index.html").write_text(
        """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="Comprehensive React application" />
    <title>Comprehensive React App</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
    """
    )

    # Configuration files
    (project_dir / ".eslintrc.json").write_text(
        """
{
  "extends": [
    "react-app",
    "react-app/jest"
  ],
  "rules": {
    "no-console": "warn",
    "no-unused-vars": "error"
  }
}
    """
    )

    (project_dir / ".prettierrc").write_text(
        """
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2
}
    """
    )

    (project_dir / "README.md").write_text(
        """
# Comprehensive React App

This is a comprehensive React application with TypeScript, testing, and modern tooling.

## Features

- React 18 with TypeScript
- React Router for navigation
- Styled Components for styling
- Jest and React Testing Library for testing
- ESLint and Prettier for code quality

## Getting Started

1. Install dependencies: `npm install`
2. Start development server: `npm start`
3. Run tests: `npm test`
4. Build for production: `npm run build`

## Project Structure

- `src/` - Source code
- `src/components/` - React components
- `src/__tests__/` - Test files
- `public/` - Static assets
    """
    )

    return project_dir


@pytest.fixture
def mock_validation_errors():
    """Mock validation errors for testing."""
    return [
        "Missing required section: ## IMPLEMENTATION FRAMEWORK",
        "Missing required section: ## QUALITY GATES",
        "Instruction content too short",
        "Invalid version format: must be semantic versioning",
    ]


@pytest.fixture
def mock_validation_warnings():
    """Mock validation warnings for testing."""
    return [
        "Potential instruction conflict detected",
        "Template parameter not used: unused_param",
        "Low confidence project type detection",
    ]


@pytest.fixture
def performance_test_data():
    """Large dataset for performance testing."""
    instructions = []
    for i in range(100):
        instructions.append(
            {
                "id": f"perf_instruction_{i}",
                "version": "1.0.0",
                "tags": [f"tag-{i % 10}", f"category-{i % 5}"],
                "content": f"Performance test instruction {i} with detailed content for testing large datasets.",
                "metadata": {"category": f"category-{i % 5}", "priority": i % 10 + 1},
            }
        )

    return {"instructions": instructions}


@pytest.fixture
def mock_git_repository(temp_dir):
    """Create a mock git repository for testing."""
    repo_dir = temp_dir / "git_repo"
    repo_dir.mkdir()

    # Create .git directory
    git_dir = repo_dir / ".git"
    git_dir.mkdir()

    # Create basic git files
    (git_dir / "HEAD").write_text("ref: refs/heads/main\n")

    refs_dir = git_dir / "refs" / "heads"
    refs_dir.mkdir(parents=True)
    (refs_dir / "main").write_text("abc123def456\n")

    # Create config file
    (git_dir / "config").write_text(
        """
[core]
    repositoryformatversion = 0
    filemode = true
    bare = false
    logallrefupdates = true
[remote "origin"]
    url = https://github.com/user/repo.git
    fetch = +refs/heads/*:refs/remotes/origin/*
[branch "main"]
    remote = origin
    merge = refs/heads/main
    """
    )

    return repo_dir


@pytest.fixture
def mock_network_responses():
    """Mock network responses for testing."""
    return {
        "github_api": {
            "status_code": 200,
            "json": {
                "name": "test-repo",
                "description": "Test repository",
                "language": "JavaScript",
                "stargazers_count": 42,
            },
        },
        "npm_registry": {
            "status_code": 200,
            "json": {
                "name": "test-package",
                "version": "1.0.0",
                "description": "Test package",
            },
        },
    }


def create_mock_logger():
    """Create a mock logger for testing."""
    logger = Mock()
    logger.debug = Mock()
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    logger.critical = Mock()
    return logger


def assert_file_contains(file_path: Path, expected_content: str):
    """Assert that a file contains expected content."""
    assert file_path.exists(), f"File {file_path} does not exist"
    content = file_path.read_text()
    assert expected_content in content, f"Expected content not found in {file_path}"


def assert_json_file_valid(file_path: Path):
    """Assert that a JSON file is valid."""
    assert file_path.exists(), f"JSON file {file_path} does not exist"
    try:
        with open(file_path) as f:
            json.load(f)
    except json.JSONDecodeError as e:
        pytest.fail(f"Invalid JSON in {file_path}: {e}")


def create_temp_config_file(temp_dir: Path, config_data: dict) -> Path:
    """Create a temporary configuration file."""
    config_file = temp_dir / "test_config.yaml"

    import yaml

    with open(config_file, "w") as f:
        yaml.dump(config_data, f)

    return config_file
