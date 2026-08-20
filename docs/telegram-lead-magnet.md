# 🎁 БОНУСНЫЕ МАТЕРИАЛЫ к статье «MCP Gateway»

*Только для подписчиков Lotus Digital Agents*

---

## 📦 Что внутри

### 1. Полный docker-compose.yml (production-ready)

```yaml
version: "3.9"

services:
  mcp-gateway:
    build: .
    ports:
      - "8000:8000"
    env_file: .env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 60s
      timeout: 10s
      retries: 3
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

### 2. Шаблон .env (заполни своими ключами)

```bash
# GigaChat
GIGACHAT_CLIENT_ID=ваш_client_id
GIGACHAT_CLIENT_SECRET=***
GIGACHAT_SCOPE=GIGACHAT_API_PERS

# YandexGPT
YANDEXGPT_API_KEY=***
YANDEXGPT_FOLDER_ID=ваш_folder_id

# Ollama (опционально)
OLLAMA_BASE_URL=http://localhost:11434

# Gateway
GATEWAY_HOST=0.0.0.0
GATEWAY_PORT=8000
LOG_LEVEL=info
```

### 3. Шпаргалка: где взять API-ключи

**GigaChat:**
1. Иди на https://developers.sber.ru/studio/workspace
2. Создай проект → получи Client ID и Secret
3. Scope: `GIGACHAT_API_PERS` (для физлиц) или `GIGACHAT_API_CORP` (для юрлиц)
4. ⚠️ OAuth-токен живёт 30 минут — обновляй автоматически

**YandexGPT:**
1. Иди в Yandex Cloud → AI Studio
2. Создай API-ключ для сервисного аккаунта
3. Folder ID — в консоли проекта
4. ⚠️ Грант 4000₽ на 60 дней для новых аккаунтов

**Ollama:**
1. `curl -fsSL https://ollama.com/install.sh | sh`
2. `ollama pull llama3.1`
3. Готово. Бесплатно. Навсегда.

### 4. Скрипт мониторинга (будит в Telegram)

```bash
#!/bin/bash
# mcp-monitor.sh — проверяет все сервисы каждые 5 минут

GATEWAY_URL="http://localhost:8000/health"
N8N_MCP_URL="http://localhost:3000/health"
TG_BOT_TOKEN="***"
TG_CHAT_ID="ваш_chat_id"

check() {
    local name=$1 url=$2
    if ! curl -sf "$url" > /dev/null 2>&1; then
        curl -s "https://api.telegram.org/bot$TG_BOT_TOKEN/sendMessage" \
            -d chat_id="$TG_CHAT_ID" \
            -d text="🚨 $name упал! $(date '+%H:%M')" > /dev/null
    fi
}

check "MCP Gateway" "$GATEWAY_URL"
check "N8N MCP" "$N8N_MCP_URL"
```

### 5. Подключение к n8n за 3 шага

1. В n8n добавь ноду **AI Agent** → **MCP Client Tool**
2. URL: `http://localhost:8000/mcp` (или IP сервера)
3. Используй tools: `chat`, `check_152fz`, `anonymize_text`, `restore_text`, `get_models_status`

Пример workflow:
```
[Webhook] → [anonymize_text] → [chat] → [restore_text] → [Response]
```

### 6. Шаблоны промптов для n8n

**Промпт для чат-бота с 152-ФЗ:**
```
Ты — ассистент компании. Отвечай на вопросы клиентов.
Если в запросе есть персональные данные — они уже анонимизированы.
Не пытайся угадать исходные данные. Отвечай по сути вопроса.
```

**Промпт для проверки compliance:**
```
Проверь текст на наличие персональных данных по 152-ФЗ.
Верни JSON: {"has_pii": bool, "types": [...], "risk_level": "low|medium|high"}
```

---

## 🔜 Что будет дальше

- **Статья 2:** SSL, OAuth и 429 — как мы падали и вставали
- **Статья 3:** 152-ФЗ без боли — анонимизация в проде
- **Статья 4:** Ночь, когда Лила замолчала (23:59)
- **Статья 5:** 13/13 и 86% — как мы поняли, что мы кентавры

Подпишись, чтобы не пропустить. Код — открытый. Ошибки — наши. Победы — общие.

---

*Lotus Digital Agents* 🧿
*Собрал сам — даю другим. Сделано в opencode, работает в проде.*
