#!/bin/bash
# Мониторинг и автоматический рестарт MCP серверов

LOG_FILE="$HOME/.hermes/logs/mcp-monitor.log"
CHECK_INTERVAL=60  # Проверка каждый минут

while true; do
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Проверка n8n-mcp
    HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/health 2>/dev/null)
    if [ "$HEALTH" != "200" ]; then
        echo "[$TIMESTAMP] n8n-mcp health check FAILED (HTTP $HEALTH)" | tee -a "$LOG_FILE"
        sudo docker restart lotus-n8n-mcp 2>/dev/null && \
            echo "[$TIMESTAMP] n8n-mcp container restarted" | tee -a "$LOG_FILE" || \
            echo "[$TIMESTAMP] Failed to restart n8n-mcp" | tee -a "$LOG_FILE"
    else
        echo "[$TIMESTAMP] n8n-mcp: OK" >> "$LOG_FILE"
    fi
    
    # Проверка Hermes gateway
    if ! systemctl is-active --quiet mcp-gateway 2>/dev/null; then
        echo "[$TIMESTAMP] mcp-gateway service DOWN" | tee -a "$LOG_FILE"
        sudo systemctl restart mcp-gateway 2>/dev/null
    fi
    
    sleep $CHECK_INTERVAL
done
