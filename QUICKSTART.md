# MCP Gateway — Быстрый старт

## Установка зависимостей

```bash
cd ~/Projects/mcp-gateway
source venv/bin/activate

# Установить зависимости (отключаем прокси!)
unset HTTP_PROXY HTTPS_PROXY ALL_PROXY
pip install -r requirements.txt
```

## Настройка API ключей

### GigaChat
1. Перейти на https://developers.sber.ru
2. Создать приложение и получить:
   - Client ID
   - Client Secret
   - Authorization Key (base64 Client ID:Client Secret)
3. Добавить в `.env`:
   ```
   GIGACHAT_API_KEY=Authorization_Key_here
   ```

### YandexGPT (опционально)
1. Перейти на https://console.yandex.cloud
2. Создать API ключ
3. Добавить в `.env`:
   ```
   YANDEXGPT_API_KEY=your_yandex_api_key_here
   ```

## Запуск

```bash
# Демо-режим (без ключей)
python -m src.server

# С API ключами
python -m src.server
```

## Проверка работоспособности

```bash
# Тест конфигурации
python -m pytest tests/ -v

# Запуск сервера
python -m src.server
```

## MCP Tools

| Tool | Описание |
|------|----------|
| **chat** | Вызов LLM с fallback |
| **check_152fz** | Проверка текста на ПД |
| **anonymize_text** | Анонимизация ПД |
| **restore_text** | Восстановление текста |
| **get_models_status** | Статус провайдеров |

## Интеграция с n8n

1. Запустить сервер как MCP endpoint
2. В n8n добавить ноду "AI Agent" → MCP
3. Использовать tools в workflow

## Стоимость LLM

| Провайдер | Цена за 1M токенов | Экономия |
|-----------|-------------------|----------|
| GigaChat | ~200 ₽ | ✅ Базовый |
| YandexGPT | ~1455 ₽ | -86% если использовать GigaChat |
| Ollama | Бесплатно | Fallback |

## Docker

```bash
cd docker
docker-compose up -d
```

## API Endpoints GigaChat

- OAuth: `https://ngw.devices.sberbank.ru:9443/api/v2/oauth`
- Chat: `https://api.giga.chat/v1/chat/completions`
- Models: `https://api.giga.chat/v1/models`
