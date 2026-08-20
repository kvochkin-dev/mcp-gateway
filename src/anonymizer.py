"""
Модуль для обезличивания ПД по 152-ФЗ
Улучшенные regex patterns с улучшенной точностью
"""
import re
from typing import Dict, Any, List
from datetime import datetime


class Anonymizer:
    """Анонимизатор персональных данных для соответствия 152-ФЗ"""
    
    # УЛУЧШЕННЫЕ ПАТТЕРНЫ
    PATTERNS = {
        # Email: строгий формат
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        
        # Телефон: только +7 или 8 с 10 цифрами после
        "phone": r'(?:\+7|8)\s*[\(]?\d{3}[\)]?\s*[\-]?\d{3}[\-]?\d{2}[\-]?\d{2}',
        
        # ФИО: 2-3 слова с заглавными буквами
        "name": r'\b([А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)?)\b',
        
        # Адрес РФ: расширенный паттерн
        "address": r'г\.?\s*[А-ЯЁa-yo]+\s*,\s*(?:ул\.?\s*[А-ЯЁa-yo]+\s*,\s*)?д\.?\s*\d+',
        
        # ИНН: 10, 12 или 13 цифр (OGRN)
        "inn": r'\b\d{10,13}\b',
        
        # Паспорт: 4 цифры пробел 4-6 цифр (поддерживает разные форматы)
        "passport": r'\b\d{2,4}\s\d{2,4}\s?\d{4,6}\b',
        
        # СНИЛС: 123-456-789 00
        "snils": r'\b\d{3}-\d{3}-\d{3}\s\d{2}\b',
    }
    
    def __init__(self):
        self._replacements: Dict[str, str] = {}
        self._counter = 0
        self._compiled_patterns = self._compile_all()
    
    def _compile_all(self) -> Dict[str, re.Pattern]:
        """Компилируем все паттерны"""
        compiled = {}
        for name, pattern in self.PATTERNS.items():
            try:
                flags = re.IGNORECASE if name in ['inn', 'address'] else 0
                compiled[name] = re.compile(pattern, flags)
            except re.error as e:
                print(f"⚠️  Error compiling '{name}': {e}")
        return compiled
    
    def _is_likely_pii(self, text: str, entity_type: str, match_start: int, match_end: int) -> bool:
        """Проверяет, является ли совпадение скорее всего ПИД"""
        matched_text = text[match_start:match_end]
        
        # Для phone: проверяем длину
        if entity_type == 'phone':
            digits_only = re.sub(r'\D', '', matched_text)
            return len(digits_only) >= 10
        
        # Для inn/odrn: проверяем контекст
        if entity_type == 'inn':
            before = text[max(0, match_start-50):match_start]
            after = text[match_end:min(len(text), match_end+50)]
            context = before + ' ' + after
            
            # Если рядом есть "ИНН", "OGRN", "number", "#" - точно ПИД
            if re.search(r'(?i)(инн|ogrн|number|#|№|\b INN\b|\b OGRN\b)', context):
                return True
            
            # Иначе проверяем длину
            digits_count = len(re.findall(r'\d', matched_text))
            return digits_count >= 10
        
        # Для name: минимум 2 слова с заглавными
        if entity_type == 'name':
            words = matched_text.split()
            return len(words) >= 2 and all(w[0].isupper() for w in words)
        
        return True  # Для остальных типов допускаем всё
    
    def anonymize(self, text: str) -> Dict[str, Any]:
        """Анонимизация текста"""
        found_entities: List[Dict[str, Any]] = []
        anonymized = text
        
        # Приоритетный порядок обработки
        priority_order = ['snils', 'passport', 'inn', 'address', 'phone', 'email', 'name']
        
        for entity_type in priority_order:
            if entity_type not in self._compiled_patterns:
                continue
                
            pattern = self._compiled_patterns[entity_type]
            
            matches_to_process = []
            for match in pattern.finditer(anonymized):
                if self._is_likely_pii(anonymized, entity_type, match.start(), match.end()):
                    matches_to_process.append(match)
            
            for match in reversed(matches_to_process):
                original = match.group(0)
                replacement = f"[{entity_type}_{self._counter}]"
                
                self._replacements[replacement] = original
                found_entities.append({
                    "type": entity_type,
                    "original": original,
                    "placeholder": replacement
                })
                
                anonymized = anonymized[:match.start()] + replacement + anonymized[match.end():]
                self._counter += 1
        
        return {
            "anonymized_text": anonymized,
            "found_entities": found_entities,
            "mapping": self._replacements,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def restore(self, text: str) -> str:
        """Обратная анонимизация"""
        result = text
        for placeholder, original in reversed(list(self._replacements.items())):
            result = result.replace(placeholder, original)
        return result
    
    def check_compliance(self, text: str) -> Dict[str, Any]:
        """Проверка на соответствие 152-ФЗ"""
        found: Dict[str, List[str]] = {}
        
        for entity_type, pattern in self._compiled_patterns.items():
            matches = []
            for match in pattern.finditer(text):
                if self._is_likely_pii(text, entity_type, match.start(), match.end()):
                    matches.append(match.group(0))
            
            if matches:
                found[entity_type] = matches
        
        return {
            "is_compliant": len(found) == 0,
            "entities_found": found,
            "timestamp": datetime.utcnow().isoformat()
        }


if __name__ == "__main__":
    anon = Anonymizer()
    
    tests = [
        "Иванов Иван Иванович проживает по адресу: г. Москва, ул. Ленина, д. 1",
        "Контакт: +7 (999) 123-45-67, email: test@example.com",
        "ИНН: 7707123456, СНИЛС: 123-456-789 00",
        "Это просто текст без ПД",
    ]
    
    for text in tests:
        print(f"\nOriginal: {text}")
        result = anon.anonymize(text)
        print(f"Anonymized: {result['anonymized_text']}")
        print(f"Entities: {[e['type'] for e in result['found_entities']]}")
        restored = anon.restore(result['anonymized_text'])
        print(f"Restored: {restored}")
        print(f"Match: {text == restored}")
