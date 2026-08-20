# MCP Gateway — Fix N8N MCP

**Дата:** 2026-08-20  
**Статус:** ✅ **ИСПРАВЛЕНО**

---

## Проблема

MCP сервер `n8n-mcp` падал с ошибкой:
```
[n8n-mcp] [WARN] Authentication failed: Invalid token
[n8n-mcp] [WARN] Authentication failed: no_auth_header
```

Hermis логи показывали:
```
MCP server 'n8n-mcp' failed initial connection after 3 attempts
(state: connecting → parked)
```

---

## Причина

Несоответствие токенов авторизации:

| Источник | Токен | Длина |
|----------|-------|-------|
| **Контейнер (старый)** | `EU0E1z6tRzuZrNlWrHnuVd9SUcJcLzZA/BLqhRehM80=` | 43 символа |
| **База данных n8n** | `eyJhbGci...sp5w` | 272 символа (JWT) |

Контейнер использовал устаревший `AUTH_TOKEN`, а n8n ожидал актуальный JWT-токен из БД.

---

## Решение

### 1. Получение актуального токена из БД

```bash
sudo docker exec lotus-postgres psql -U n8n -d n8n -t -A \
  -c "SELECT \"apiKey\" FROM user_api_keys WHERE audience='mcp-server-api' LIMIT 1;"
```

**Результат:** 272-символьный JWT токен

### 2. Пересоздание контейнера с правильным токеном

```bash
# Остановка и удаление старого контейнера
sudo docker stop lotus-n8n-mcp
sudo docker rm lotus-n8n-mcp

# Создание env файла
cat > /tmp/n8n-mcp.env << EOF
AUTH_TOKEN=<272-символьный_JWT_токен>
N8N_API_URL=http://host.docker.internal:5678
IS_DOCKER=true
NODE_ENV=production
MCP_MODE=http
EOF

# Запуск нового контейнера
sudo docker run -d \
  --name lotus-n8n-mcp \
  --network host \
  --env-file /tmp/n8n-mcp.env \
  ghcr.io/czlonkowski/n8n-mcp:latest
```

### 3. Обновление конфига Hermes

Изменён порт в `~/.hermes/config.yaml`:
```yaml
mcp_servers:
  n8n-mcp:
    url: http://localhost:3000/mcp  # Было: 3001
    headers:
      Authorization: Bearer ${MCP_N8N_API_KEY}
```

---

## Результат

✅ Контейнер запускается успешно  
✅ Health check проходит: `curl http://localhost:3000/health` → `{"status":"ok"}`  
✅ Подключение к n8n API установлено  
✅ 2414 нод загружено в базу  
✅ Hermes видит MCP сервер  

---

## Мониторинг

Создан скрипт мониторинга: `scripts/mcp-monitor.sh`

```bash
# Установка как systemd сервиса
sudo cp scripts/mcp-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable mcp-monitor
sudo systemctl start mcp-monitor

# Проверка статуса
sudo systemctl status mcp-monitor

# Просмотр логов
tail -f ~/.hermes/logs/mcp-monitor.log
```

---

## Важные замечания

1. **Токен нужно обновлять** при его ротации в n8n
2. **Порт 3000** — стандартный порт n8n-mcp, не 3001
3. **host.docker.internal** — корректный адрес для доступа к n8n из контейнера

---

**Статус:** ✅ Исправлено и работает
