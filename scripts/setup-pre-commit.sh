#!/bin/bash

set -e

echo "🔧 Setting up pre-commit hooks..."

# Check if pre-commit is installed
if ! command -v pre-commit &> /dev/null; then
    echo "📦 Installing pre-commit..."
    pip3 install pre-commit
else
    echo "✅ pre-commit is already installed"
fi

# Ensure containers are running for pre-commit hooks
echo "🐳 Starting containers for pre-commit hooks..."
docker compose up -d frontend backend

# Wait for containers to be ready
echo "⏳ Waiting for containers to be ready..."
sleep 10

# Install the pre-commit hooks
echo "🔗 Installing pre-commit hooks..."
pre-commit install

# Run pre-commit on all files to ensure everything is formatted
echo "🎨 Running pre-commit on all files..."
pre-commit run --all-files

echo "✅ Pre-commit setup complete!"
echo ""
echo "📝 Usage:"
echo "  - Hooks will run automatically on commit"
echo "  - Run manually: pre-commit run --all-files"
echo "  - Skip hooks: git commit --no-verify"
echo "  - Update hooks: pre-commit autoupdate"
echo ""
echo "🐳 Note: Frontend and backend containers must be running for hooks to work"
echo "  - Start: docker compose up -d frontend backend"
echo "  - Stop: docker compose down"
