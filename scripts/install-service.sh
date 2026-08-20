#!/bin/bash
# Install MCP Gateway as systemd service for production

set -e

SERVICE_FILE="$HOME/Projects/mcp-gateway/scripts/mcp-gateway.service"
SYSTEMD_SERVICE="/etc/systemd/system/mcp-gateway.service"

echo "🚀 Installing MCP Gateway as systemd service..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run with sudo: sudo $0"
    exit 1
fi

# Copy service file
cp "$SERVICE_FILE" "$SYSTEMD_SERVICE"
echo "✅ Service file installed to $SYSTEMD_SERVICE"

# Reload systemd
systemctl daemon-reload
echo "✅ Systemd reloaded"

# Enable and start service
systemctl enable mcp-gateway
systemctl start mcp-gateway

echo ""
echo "🎉 MCP Gateway is now running as a systemd service!"
echo ""
echo "Commands:"
echo "  systemctl status mcp-gateway    # Check status"
echo "  systemctl stop mcp-gateway      # Stop service"
echo "  systemctl restart mcp-gateway   # Restart service"
echo "  journalctl -u mcp-gateway -f   # View logs"
echo ""
echo "Health check: http://localhost:8000/health"
