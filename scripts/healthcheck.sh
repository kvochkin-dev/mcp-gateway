#!/bin/bash
# Health check script for MCP Gateway

set -e

echo "🏥 Checking MCP Gateway health..."

# Check if server is running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ MCP Gateway is healthy"
    exit 0
else
    echo "❌ MCP Gateway is not responding"
    exit 1
fi
