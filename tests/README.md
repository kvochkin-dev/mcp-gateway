# Tests for MCP Gateway

## Запуск тестов

```bash
# Через venv
source venv/bin/activate
pip install pytest
pytest -v

# Или напрямую
python -m pytest tests/ -v
```

## Что тестируется

- `test_gigachat.py` — клиент GigaChat API
- `test_yandexgpt.py` — клиент YandexGPT API  
- `test_fallback.py` — логика fallback между моделями
- `test_anonymizer.py` — анонимизация ПД по 152-ФЗ
- `test_cache.py` — кеширование ответов

## Покрытие

Цель: ≥80% покрытие кода тестами.
