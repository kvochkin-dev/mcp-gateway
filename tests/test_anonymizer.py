"""
Тесты для модуля анонимизатора
"""
import pytest
import sys
from pathlib import Path

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.anonymizer import Anonymizer


class TestAnonymizer:
    def setup_method(self):
        self.anonymizer = Anonymizer()
    
    def test_anonymize_name(self):
        text = "Контакт: Иван Иванов, телефон: 8-900-123-45-67"
        result = self.anonymizer.anonymize(text)
        
        assert "[name_0]" in result["anonymized_text"]
        assert len(result["found_entities"]) >= 1
    
    def test_check_compliance_clean(self):
        text = "Это безопасный текст без персональных данных"
        result = self.anonymizer.check_compliance(text)
        
        assert result["is_compliant"] is True
        assert result["entities_found"] == {}
    
    def test_check_compliance_dirty(self):
        text = "Письмо от Петр Петров, email: test@example.com"
        result = self.anonymizer.check_compliance(text)
        
        assert result["is_compliant"] is False
        assert "name" in result["entities_found"]
        assert "email" in result["entities_found"]
    
    def test_restore(self):
        original = "Иван Петров"
        result = self.anonymizer.anonymize(f"Текст: {original}")
        restored = self.anonymizer.restore(result["anonymized_text"])
        
        assert original in restored


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
