# MCP Gateway

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/Docker-ready-2496ED?style=flat-square&logo=docker" alt="Docker">
  <img src="https://img.shields.io/badge/Tests-13%2F13%20passed-brightgreen?style=flat-square" alt="Tests">
  <img src="https://img.shields.io/badge/152--ФЗ-compliant-red?style=flat-square" alt="152-FZ">
  <img src="https://img.shields.io/badge/Экономия-86%25-yellowgreen?style=flat-square" alt="Savings">
</p>

---

**MCP Gateway** — production-ready шлюз Model Context Protocol для российских LLM: единый интерфейс к GigaChat и YandexGPT с автоматическим fallback, анонимизацией ПД по 152-ФЗ и экономией 86% на токенах.

Подключите любой MCP-клиент (Hermes Agent, Claude Code, Cursor, n8n) — и получите доступ к российским моделям через один endpoint. Стек: FastAPI, MCP SDK, GigaChat API, YandexGPT API.

---

## ✨ Возможности

| Функция | Описание |
|---------|----------|
| **🔀 Мультипровайдерность** | GigaChat (основной) + YandexGPT (fallback) + Ollama (локальный) |
| **🛡️ 152-ФЗ** | Встроенная детекция и анонимизация ПД: телефон, ИНН, паспорт, СНИЛС, адрес |
| **💰 Экономия 86%** | GigaChat ~200₽/M токенов против YandexGPT ~1 455₽/M токенов |
| **🔄 Авто-fallback** | Бесшовное переключение провайдеров при ошибках и rate-limit (429) |
| **🐳 Docker Ready** | Полный Docker Compose для развёртывания одной командой |
| **💚 Health Checks** | Эндпоинты мониторинга и systemd-сервис с автозапуском |

---

## 🏗️ Архитектура

```mermaid
flowchart TB
    classDef client fill:#eef2f7,stroke:#4a5568,stroke-width:1.5px
    classDef gateway fill:#edf2f7,stroke:#4a5568,stroke-width:1.5px
    classDef llm fill:#e2e8f0,stroke:#4a5568,stroke-width:1.5px

    subgraph Client["👤 Клиент"]
        Agent["🤖 MCP-клиент<br>Hermes Agent / Claude Code / n8n"]
    end
    class Client client

    subgraph Gateway["⚙️ MCP Gateway (FastAPI, port 8000)"]
        MCP["MCP Server<br>5 tools"]
        Anon["🛡️ Анонимизатор ПД<br>152-ФЗ"]
        Fallback["🔀 Fallback-оркестратор"]
        MCP --> Anon --> Fallback
    end
    class Gateway gateway

    subgraph Providers["🧠 LLM-провайдеры"]
        Giga["GigaChat<br>~200₽/M токенов"]
        Yandex["YandexGPT<br>~1 455₽/M токенов"]
        Ollama["Ollama<br>локально, 0₽"]
    end
    class Providers llm

    Agent --> MCP
    Fallback -->|"основной"| Giga
    Fallback -.->|"fallback"| Yandex
    Fallback -.->|"fallback"| Ollama
```

---

## 🚀 Быстрый старт

```bash
# Клонирование
git clone https://github.com/kvochkin-dev/mcp-gateway.git
cd mcp-gateway

# Настройка окружения
cp .env.example .env
# Впишите свои API-ключи в .env

# Запуск через Docker
docker-compose up -d

# Или напрямую
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python app.py
```

---

## 📋 API Endpoints

| Метод | Путь | Описание |
|-------|------|----------|
| `GET` | `/health` | Статус сервиса и провайдеров |
| `GET` | `/docs` | Swagger UI |
| `POST` | `/mcp` | MCP-интерфейс (tools) |

### Health Check

```bash
curl http://localhost:8000/health
```

```json
{
  "status": "healthy",
  "gigachat": "connected",
  "yandexgpt": "connected",
  "anonymizer": "ready"
}
```

---

## 🔐 Конфигурация

Все секреты хранятся в `.env` (файл исключён из git):

```env
GIGACHAT_CLIENT_ID=***
GIGACHAT_CLIENT_SECRET=***
YANDEXGPT_API_KEY=***
YANDEXGPT_FOLDER_ID=***
```

---

## 🧪 Тесты

```bash
pytest tests/ -v
```

**13/13 тестов passed** — клиенты провайдеров, fallback-логика, анонимизатор ПД.

---

## 📁 Структура проекта

```
mcp-gateway/
├── app.py                  # FastAPI + MCP сервер
├── src/
│   ├── clients/            # GigaChat, YandexGPT клиенты
│   └── anonymizer/         # 152-ФЗ анонимизация ПД
├── scripts/
│   └── mcp-monitor.sh      # Мониторинг сервисов
├── docs/                   # Отчёты и документация
├── tests/                  # 13 тестов
└── docker-compose.yml      # Docker-развёртывание
```

---

## 📄 Лицензия

MIT — используйте свободно.

---

<p align="center">
  Сделано в opencode, работает в проде. 🧿
</p>
