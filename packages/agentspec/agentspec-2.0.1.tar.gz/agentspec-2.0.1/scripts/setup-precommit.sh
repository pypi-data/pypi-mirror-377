#!/bin/bash
# Setup script for pre-commit hooks with error handling

set -e

echo "🔧 Setting up pre-commit hooks for AgentSpec..."

# Check if pre-commit is installed
if ! command -v pre-commit &> /dev/null; then
    echo "❌ pre-commit is not installed. Please install it first:"
    echo "   pip install pre-commit"
    exit 1
fi

# Clean any existing pre-commit cache
echo "🧹 Cleaning pre-commit cache..."
pre-commit clean || true

# Install pre-commit hooks
echo "📦 Installing pre-commit hooks..."
if pre-commit install; then
    echo "✅ Pre-commit hooks installed successfully!"
else
    echo "⚠️  Pre-commit installation failed. This is a known issue with some environments."
    echo "   You can still commit using --no-verify flag if needed."
    echo "   The CI pipeline will catch any formatting issues."
fi

# Test the hooks
echo "🧪 Testing pre-commit hooks..."
if pre-commit run --all-files; then
    echo "✅ All pre-commit checks passed!"
else
    echo "⚠️  Some pre-commit checks failed. Please review the output above."
    echo "   You can run individual tools manually:"
    echo "   - black agentspec/ tests/"
    echo "   - isort agentspec/ tests/"
fi

echo "🎉 Pre-commit setup complete!"
