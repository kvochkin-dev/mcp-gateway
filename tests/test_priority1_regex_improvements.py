#!/usr/bin/env python3
"""
Тесты для Приоритета 1: Улучшение regex patterns
"""
import sys
sys.path.insert(0, '/home/dataguru/Projects/mcp-gateway')

from src.anonymizer import Anonymizer


def test_phone_detection():
    """Тест корректной детекции телефонов"""
    print("\n📋 ТЕСТИРОВАНИЕ TELEPHONE DETECTION")
    print("="*60)
    
    anon = Anonymizer()
    tests = [
        ("+7 (999) 123-45-67", True, "Russian phone with +7"),
        ("8 (900) 123-45-67", True, "Russian phone with 8"),
        ("+799****4567", False, "Phone without separators (should NOT match)"),
        ("1234567890", False, "Random 10 digits (should NOT match)"),
        ("Hello world", False, "No phone here"),
    ]
    
    passed = 0
    for text, should_match, description in tests:
        result = anon.check_compliance(text)
        has_phone = 'phone' in result['entities_found'] and len(result['entities_found']['phone']) > 0
        
        if should_match and has_phone:
            status = "✅"
            passed += 1
        elif not should_match and not has_phone:
            status = "✅"
            passed += 1
        else:
            status = "❌"
        
        print(f"{status} {description}")
        print(f"   Text: '{text}'")
        print(f"   Expected match: {should_match}, Got: {has_phone}")
        if has_phone:
            print(f"   Found: {result['entities_found']['phone']}")
        print()
    
    print(f"Результат: {passed}/{len(tests)} passed")
    return passed == len(tests)


def test_false_positives():
    """Тест на ложные срабатывания - тексты БЕЗ PII должны быть чистыми"""
    print("\n📋 ТЕСТИРОВАНИЕ FALSE POSITIVES")
    print("="*60)
    
    anon = Anonymizer()
    
    # Все эти тексты НЕ содержат PII, поэтому должны быть clean
    tests = [
        ("Это просто текст без PII", True),
        ("HTTP/1.1 200 OK", True),
        ("def hello(): print('world')", True),
        ("https://example.com/page", True),
        ("12345, 67890, 11111", True),
        ("2024-01-01, 2024-12-31", True),
        ("Order #12345 completed", True),
    ]
    
    passed = 0
    for text, should_be_clean in tests:
        result = anon.check_compliance(text)
        is_clean = result['is_compliant']
        
        # Ожидаем что текст БЕЗ PII будет clean (is_compliant=True)
        if should_be_clean and is_clean:
            status = "✅"
            passed += 1
            print(f"{status} '{text[:40]}...' - Clean (correct)")
        elif should_be_clean and not is_clean:
            status = "❌"
            print(f"{status} '{text[:40]}...' - FALSE POSITIVE!")
            print(f"   Entities found: {result['entities_found']}")
        else:
            status = "✅"
            passed += 1
            print(f"{status} '{text[:40]}...' - Detected PII (correct)")
        print()
    
    print(f"Результат: {passed}/{len(tests)} passed")
    return passed == len(tests)


def test_specialized_pii():
    """Тест новых типов PII"""
    print("\n📋 ТЕСТИРОВАНИЕ НОВЫХ ТИПОВ PII")
    print("="*60)
    
    anon = Anonymizer()
    tests = [
        # ИНН - ожидаем обнаружить
        ("ИНН: 7707123456", "inn", True, "INN 10 digits with label"),
        ("ОГРН 1234567890123", "inn", True, "OGRN 13 digits (should detect INN part)"),
        # Паспорт - ожидаем обнаружить
        ("Паспорт 45 01 123456", "passport", True, "Passport series + number"),
        # СНИЛС - ожидаем обнаружить
        ("СНИЛС: 123-456-789 00", "snils", True, "SNILS format"),
        # Адрес - ожидаем обнаружить
        ("г. Москва, ул. Пушкина, д. 10", "address", True, "Full Moscow address"),
    ]
    
    passed = 0
    for text, expected_type, should_detect, description in tests:
        result = anon.check_compliance(text)
        detected = expected_type in result['entities_found'] and len(result['entities_found'][expected_type]) > 0
        
        if should_detect and detected:
            status = "✅"
            passed += 1
            print(f"{status} {description}")
            print(f"   Text: '{text}'")
            print(f"   Detected as: {expected_type}")
            print(f"   Value: {result['entities_found'][expected_type][0]}")
        elif not should_detect and not detected:
            status = "✅"
            passed += 1
            print(f"{status} {description} - correctly not detected")
        else:
            status = "❌"
            print(f"{status} {description}: {'NOT DETECTED' if should_detect else 'INCORRECTLY DETECTED'}")
            print(f"   Text: '{text}'")
            if detected:
                print(f"   Found types: {list(result['entities_found'].keys())}")
        print()
    
    print(f"Результат: {passed}/{len(tests)} passed")
    return passed == len(tests)


def main():
    print("="*60)
    print("🧪 ПРИОРИТЕТ 1: УЛУЧШЕНИЕ REGEX PATTERNS")
    print("="*60)
    
    results = {
        'phone_detection': test_phone_detection(),
        'false_positives': test_false_positives(),
        'specialized_pii': test_specialized_pii(),
    }
    
    print("\n" + "="*60)
    print("📊 ИТОГОВЫЙ ОТЧЁТ")
    print("="*60)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\nВсего тестов: {total}")
    print(f"Пройдено: {passed}")
    print(f"Успешность: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n✅ ПРИОРИТЕТ 1 ЗАВЕРШЕН УСПЕШНО!")
        return True
    else:
        print("\n❌ Есть неудачи, требуется доработка")
        return False


if __name__ == '__main__':
    main()