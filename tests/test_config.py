"""
Тесты для конфигурации MCP Gateway
"""
import pytest
import sys
from pathlib import Path

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Settings


def test_settings_defaults():
    """Проверка дефолтных настроек"""
    settings = Settings(_env_file=None)
    assert settings.mcp_host == "0.0.0.0"
    assert settings.mcp_port == 8000
    assert settings.log_level == "INFO"
    assert settings.fallback_enabled is True
    assert settings.cache_enabled is True


def test_settings_env_vars():
    """Проверка чтения из переменных окружения"""
    import os
    os.environ['GIGACHAT_API_KEY'] = 'test_key_123'
    os.environ['MCP_PORT'] = '9999'
    
    settings = Settings(_env_file=None)
    assert settings.gigachat_api_key == 'test_key_123'
    assert settings.mcp_port == 9999
    
    # Очистка
    del os.environ['GIGACHAT_API_KEY']
    del os.environ['MCP_PORT']


def test_settings_empty_env():
    """Проверка что пустые ключи не требуются"""
    settings = Settings(_env_file=None, gigachat_api_key="", yandexgpt_api_key="")
    assert settings.gigachat_api_key == ""
    assert settings.yandexgpt_api_key == ""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
