"""
Комплексное тестирование 152-FZ compliance
Расширенные тесты на защиту персональных данных
"""
import sys
import os
import time
import re
from typing import List, Dict, Any, Tuple
sys.path.insert(0, '/home/dataguru/Projects/mcp-gateway')

from dotenv import load_dotenv
load_dotenv('.env')

from src.anonymizer import Anonymizer


class PIITester:
    """Тестер для обнаружения PII в различных форматах"""
    
    # Типы PII для тестирования
    PII_TYPES = {
        'ФИО': ['Иванов Иван Иванович', 'Петрова Анна Сергеевна', 'Сидоров Алексей Петрович'],
        'Email': ['user@example.com', 'test.mail@gmail.com', 'name.surname@company.ru'],
        'Телефон': ['+7 (999) 123-45-67', '8 (900) 123-45-67', '+1 (555) 123-4567'],
        'Адрес РФ': ['г. Москва, ул. Ленина, д. 1, кв. 10', 
                    'г. Санкт-Петербург, Невский пр., д. 100'],
        'ИНН': ['1234567890', '9876543210'],
        'Паспорт': ['45 XX XXXXXX'],
        'Серия/номер билета': ['AA 1234567'],
        'Номер карты': ['****1234'],
        'СНИЛС': ['123-456-789 00'],
    }
    
    def __init__(self):
        self.anonymizer = Anonymizer()
        self.results = []
        
    def test_basic_pii_types(self):
        """Базовые типы PII"""
        print("\n📋 БАЗОВЫЕ ТЕСТЫ PII")
        print("="*60)
        
        results = []
        
        for pii_type, test_cases in self.PII_TYPES.items():
            for test_case in test_cases:
                print(f"\nТест: {pii_type} - '{test_case}'")
                
                # Check compliance (sync function)
                compliance = self.anonymizer.check_compliance(test_case)
                print(f"  Compliance: {compliance['is_compliant']}")
                print(f"  Entities found: {len(compliance['entities_found'])}")
                
                if not compliance['is_compliant']:
                    for entity_type, entities in compliance['entities_found'].items():
                        for entity in entities[:3]:
                            print(f"    - {entity_type}: '{entity[:30]}...'")
                
                results.append({
                    'type': pii_type,
                    'input': test_case,
                    'is_compliant': compliance['is_compliant'],
                    'entities_found': len(str(compliance['entities_found']))
                })
        
        return results
    
    def test_mixed_content(self):
        """Смешанный контент (текст + PII)"""
        print("\n📋 ТЕСТЫ СМЕШАННОГО КОНТЕНТА")
        print("="*60)
        
        mixed_cases = [
            "Здравствуйте! Меня зовут Иванов Иван Иванович, и я обращаюсь по поводу заказа №12345",
            "Контактный email: support@example.com для связи по вопросам доставки",
            "Мой телефон: +7 (999) 123-45-67, адрес: Москва, ул. Пушкина, д. 10",
            "ИНН организации: 7707123456, адрес: 123456, г. Москва",
            "Паспорт серии 45 12 123456 выдан 01.01.2020, СНИЛС: 123-456-789 00",
        ]
        
        results = []
        for text in mixed_cases:
            print(f"\nТест: '{text[:50]}...'")
            
            # Check compliance
            compliance = self.anonymizer.check_compliance(text)
            print(f"  Compliance: {compliance['is_compliant']}")
            print(f"  Entities: {len(str(compliance['entities_found']))}")
            
            for entity_type, entities in compliance['entities_found'].items():
                for entity in entities:
                    print(f"    - {entity_type}: '{entity[:30]}'")
            
            results.append({
                'input': text[:50] + '...',
                'is_compliant': compliance['is_compliant'],
                'entities_count': len(str(compliance['entities_found']))
            })
        
        return results
    
    def test_anonymization_restoration(self):
        """Тест анонимизации и восстановления"""
        print("\n📋 ТЕСТЫ АНОНИМИЗАЦИИ И ВОССТАНОВЛЕНИЯ")
        print("="*60)
        
        test_texts = [
            "Иванов Иван Иванович проживает по адресу: Москва, ул. Ленина, д. 1",
            "Свяжитесь со мной: email test@example.com или тел. +7 (999) 123-45-67",
            "ИНН: 7707123456, ОГРН: 1234567890123",
            "Паспорт: 45 01 123456, выдан 01.01.2020, серия 45 номер 123456",
        ]
        
        results = []
        for original in test_texts:
            print(f"\nИсходный текст: '{original}'")
            
            # Anonymize
            anon_result = self.anonymizer.anonymize(original)
            anonymized = anon_result['anonymized_text']
            print(f"Анонимизирован: '{anonymized[:50]}...'")
            print(f"  Found entities: {len(anon_result['found_entities'])}")
            
            # Restore
            restored = self.anonymizer.restore(anonymized)
            print(f"Восстановлен:   '{restored[:50]}...'")
            
            # Check restoration quality
            match = original == restored
            print(f"Совпадение: {match}")
            
            results.append({
                'original': original,
                'anonymized': anonymized,
                'restored': restored,
                'restoration_match': match
            })
        
        return results
    
    def test_performance_under_load(self):
        """Производительность под нагрузкой"""
        print("\n📋 ТЕСТЫ ПРОИЗВОДИТЕЛЬНОСТИ")
        print("="*60)
        
        # Generate large text with many PII entities
        large_text = " ".join([
            f"Контакт: Иван{i} Иван{i}ович, email: user{i}@example.com, "
            f"тел: +7 (99{i}) 123-45-6{i}"
            for i in range(50)
        ])
        
        print(f"\nТест: 50 ПИД в одном тексте ({len(large_text)} символов)")
        
        start = time.perf_counter()
        compliance = self.anonymizer.check_compliance(large_text)
        check_time = time.perf_counter() - start
        
        print(f"Время проверки: {check_time*1000:.2f}ms")
        print(f"PII найдено: {len(str(compliance['entities_found']))}")
        
        start = time.perf_counter()
        anon_result = self.anonymizer.anonymize(large_text)
        anon_time = time.perf_counter() - start
        
        print(f"Время анонимизации: {anon_time*1000:.2f}ms")
        
        # Test concurrent requests (simulate)
        print("\nТест: 10 последовательных запросов...")
        start = time.perf_counter()
        
        for _ in range(10):
            self.anonymizer.check_compliance(large_text)
        
        sequential_time = time.perf_counter() - start
        print(f"Время 10 запросов: {sequential_time*1000:.2f}ms")
        print(f"Среднее время на запрос: {sequential_time*1000/10:.2f}ms")
        
        return {
            'large_text_checks': len(str(compliance['entities_found'])),
            'check_time_ms': check_time * 1000,
            'anon_time_ms': anon_time * 1000,
            'sequential_10_time_ms': sequential_time * 1000,
            'avg_sequential_time_ms': sequential_time * 1000 / 10
        }
    
    def test_edge_cases(self):
        """Краевые случаи"""
        print("\n📋 КРАЕВЫЕ СЛУЧАИ")
        print("="*60)
        
        edge_cases = [
            ("Пустая строка", ""),
            ("Только пробелы", "   "),
            ("Очень длинный текст", "X" * 10000),
            ("Спецсимволы", "!@#$%^&*()_+-=[]{}|;':\",./<>?"),
            ("Unicode русский", "Привет мир! Это тест на кириллицу."),
            ("Mixed scripts", "Hello Привет 123 456"),
            ("Encoded PII", "Иванов%20Иван%20Иванович"),
            ("Partial matches", "Иванов (без имени)"),
            ("Numbers only", "1234567890"),
            ("Dates", "01.01.2020, 31.12.2025"),
        ]
        
        results = []
        for name, text in edge_cases:
            print(f"\nТест: {name}")
            print(f"  Input: '{text[:50]}{'...' if len(text) > 50 else ''}'")
            
            start = time.perf_counter()
            compliance = self.anonymizer.check_compliance(text)
            elapsed = time.perf_counter() - start
            
            print(f"  Compliance: {compliance['is_compliant']}")
            print(f"  Entities: {len(str(compliance['entities_found']))}")
            print(f"  Time: {elapsed*1000:.2f}ms")
            
            results.append({
                'name': name,
                'input_len': len(text),
                'is_compliant': compliance['is_compliant'],
                'entities_count': len(str(compliance['entities_found'])),
                'time_ms': elapsed * 1000
            })
        
        return results
    
    def test_false_positives(self):
        """Тест ложных срабатываний"""
        print("\n📋 ТЕСТ ЛОЖНЫХ СРАБАТЫВАНИЙ")
        print("="*60)
        
        false_positive_cases = [
            ("Обычный текст без PII", "Это просто тестовый текст без каких-либо персональных данных"),
            ("Технические данные", "HTTP/1.1 200 OK, Content-Type: application/json"),
            ("Код", "def hello(): print('world')"),
            ("URL без PII", "https://example.com/page"),
            ("Числа", "12345, 67890, 11111"),
            ("Даты в коде", "2024-01-01, 2024-12-31"),
        ]
        
        results = []
        for name, text in false_positive_cases:
            print(f"\nТест: {name}")
            print(f"  Input: '{text[:50]}'")
            
            compliance = self.anonymizer.check_compliance(text)
            print(f"  Compliance: {compliance['is_compliant']}")
            print(f"  Entities found: {len(str(compliance['entities_found']))}")
            
            if len(str(compliance['entities_found'])) > 0:
                print(f"  ⚠️  POSSIBLE FALSE POSITIVE!")
                for entity_type, entities in compliance['entities_found'].items():
                    for entity in entities:
                        print(f"     - {entity_type}: '{entity}'")
            
            results.append({
                'name': name,
                'is_compliant': compliance['is_compliant'],
                'entities_count': len(str(compliance['entities_found'])),
                'has_false_positive': len(str(compliance['entities_found'])) > 0 and not compliance['is_compliant']
            })
        
        return results
    
    def run_all_tests(self):
        """Запуск всех тестов"""
        print("="*60)
        print("🧪 КОМПЛЕКСНОЕ ТЕСТИРОВАНИЕ 152-FZ COMPLIANCE")
        print(f"Дата: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        all_results = {}
        
        # Run all test categories
        all_results['basic_pii'] = self.test_basic_pii_types()
        all_results['mixed_content'] = self.test_mixed_content()
        all_results['anonymization'] = self.test_anonymization_restoration()
        all_results['performance'] = self.test_performance_under_load()
        all_results['edge_cases'] = self.test_edge_cases()
        all_results['false_positives'] = self.test_false_positives()
        
        # Summary
        print("\n" + "="*60)
        print("📊 ИТОГОВЫЙ ОТЧЁТ")
        print("="*60)
        
        total_tests = sum(len(v) for v in all_results.values())
        passed_tests = 0
        
        for category, tests in all_results.items():
            for test in tests:
                if test.get('is_compliant', True) or test.get('restoration_match', True):
                    passed_tests += 1
        
        print(f"\nВсего тестов: {total_tests}")
        print(f"Пройдено: {passed_tests}")
        print(f"Успешность: {passed_tests/total_tests*100:.1f}%")
        
        return all_results


def main():
    tester = PIITester()
    results = tester.run_all_tests()
    
    # Save results
    output_file = '/home/dataguru/Projects/mcp-gateway/tests/PII_TEST_RESULTS.md'
    with open(output_file, 'w') as f:
        f.write("# Результаты тестирования 152-FZ PII Protection\n\n")
        f.write(f"**Дата:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for category, tests in results.items():
            f.write(f"## {category}\n\n")
            f.write("| Тест | Статус | PII найдено | Время | Примечания |\n")
            f.write("|------|--------|-------------|-------|------------|\n")
            
            for test in tests:
                status = "✅" if test.get('is_compliant', True) else "❌"
                pii_count = test.get('entities_count', test.get('entities_found', 0))
                time_ms = test.get('time_ms', 0)
                notes = test.get('notes', '')
                
                f.write(f"| {test.get('name', test.get('input', 'N/A'))} | {status} | {pii_count} | {time_ms:.2f}ms | {notes} |\n")
            
            f.write("\n")
    
    print(f"\n💾 Результаты сохранены: {output_file}")


if __name__ == '__main__':
    main()