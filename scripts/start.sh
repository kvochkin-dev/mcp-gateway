#!/bin/bash
# Start MCP Gateway server

set -e

echo "🚀 Starting MCP Gateway..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "✅ Please edit .env and add your API keys"
    exit 1
fi

# Validate configuration
echo "🔍 Validating configuration..."
python -c "from src.config import validate_keys; validate_keys()" || exit 1
echo "✅ Configuration valid"

# Start server
echo "🌐 Starting MCP server on port 8000..."
python -m src.server
