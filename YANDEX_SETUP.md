# Где получить API ключ YandexGPT

## Шаг 1: Создать Service Account с доступом

1. Перейти: https://console.yandex.cloud/iam/service-accounts
2. Нажать "Создать сервисный аккаунт"
3. Назвать (например: `mcp-gateway`)
4. Скопировать ID аккаунта

## Шаг 2: Выдать роль "AI Language User"

1. Открыть создан Service Account
2. Вкладка "Доступ" → "Добавить привязку"
3. Роль: **AI Language User** (или **Member of AI users group**)
4. Сохранить

## Шаг 3: Создать API ключ

1. В том же Service Account → вкладка "Ключи доступа"
2. Нажать "Создать ключ"
3. Скопировать ключ (длинная строка вида `AIoa...`)

## Альтернатива: Personal API Key

Можно получить в настройках профиля:
https://console.yandex.cloud/oversight/user-settings

## Шаг 4: Настроить в проекте

Добавить в `.env`:
```
YANDEXGPT_API_KEY=AIoaXXXXXXXXXXXXXXXXXXXX
```

## Проверка

```bash
cd ~/Projects/mcp-gateway
source venv/bin/activate
unset HTTP_PROXY HTTPS_PROXY ALL_PROXY
python -c "
from src.clients.yandexgpt import YandexGPTClient
import asyncio

async def test():
    client = YandexGPTClient('YOUR_KEY_HERE')
    result = await client.health_check()
    print(f'Health check: {result}')

asyncio.run(test())
"
```

---

## Стоимость YandexGPT (примерно)

| Модель | Цена за 1M токенов |
|--------|-------------------|
| YandexGPT Lite | ~500 ₽ |
| YandexGPT Pro | ~1455 ₽ |
| GigaChat | ~200 ₽ ← выгоднее |

**Рекомендация:** Использовать GigaChat как primary, YandexGPT как fallback на случай недоступности GigaChat.
