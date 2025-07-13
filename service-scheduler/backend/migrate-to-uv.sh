#!/bin/bash

# Migration script from pip to uv
# This script helps existing developers migrate from pip to uv

echo "🔄 Migrating from pip to uv..."

# Check if we're in the backend directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Please run this script from the backend directory"
    exit 1
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
    echo "✅ uv installed successfully"
else
    echo "✅ uv is already installed"
fi

# Remove old virtual environment if it exists
if [ -d "venv" ]; then
    echo "🗑️  Removing old virtual environment..."
    rm -rf venv/
    echo "✅ Old virtual environment removed"
fi

# Install dependencies with uv
echo "📦 Installing dependencies with uv..."
uv sync

echo ""
echo "🎉 Migration complete!"
echo ""
echo "To run the application now, use:"
echo "  uv run uvicorn main:app --reload"
echo ""
echo "Common uv commands:"
echo "  uv sync         - Install all dependencies"
echo "  uv add <pkg>    - Add a new dependency"
echo "  uv remove <pkg> - Remove a dependency"
echo "  uv run <cmd>    - Run a command in the project environment"
echo "  uv lock         - Update the lock file"
