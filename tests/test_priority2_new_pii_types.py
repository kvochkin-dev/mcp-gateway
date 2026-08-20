"""
Приоритет 2: Добавление новых типов PII
"""
import sys
sys.path.insert(0, '/home/dataguru/Projects/mcp-gateway')

from src.anonymizer import Anonymizer


def test_new_pii_types():
    """Тест новых типов PII"""
    print("\n📋 ТЕСТИРОВАНИЕ НОВЫХ ТИПОВ PII")
    print("="*60)
    
    anon = Anonymizer()
    tests = [
        # ИНН
        ("ИНН: 7707123456", "inn", True, "INN 10 digits with label"),
        ("ОГРН 1234567890123", "inn", True, "OGRN 13 digits (should detect INN part)"),
        # Паспорт
        ("Паспорт 45 01 123456", "passport", True, "Passport series + number"),
        # СНИЛС
        ("СНИЛС: 123-456-789 00", "snils", True, "SNILS format"),
        # Адрес
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
    success = test_new_pii_types()
    
    print("\n" + "="*60)
    if success:
        print("✅ ПРИОРИТЕТ 2 ЗАВЕРШЕН УСПЕШНО!")
    else:
        print("❌ ПРИОРИТЕТ 2 ТРЕБУЕТ ДОРАБОТКИ")
    print("="*60)
    
    return success


if __name__ == '__main__':
    main()