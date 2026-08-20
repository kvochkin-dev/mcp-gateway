"""
Приоритет 3: Контекстная проверка и improved accuracy
"""
import sys
sys.path.insert(0, '/home/dataguru/Projects/mcp-gateway')

from src.anonymizer import Anonymizer


def test_contextual_accuracy():
    """Тест повышения точности через контекст"""
    print("\n📋 ТЕСТИРОВАНИЕ КОНТЕКСТНОЙ ТОЧНОСТИ")
    print("="*60)
    
    anon = Anonymizer()
    
    # Тесты, которые НЕ должны детектировать ПИД
    false_positive_tests = [
        ("12345", False, "Random 5-digit number"),
        ("Order 12345 completed", False, "Order number in context"),
        ("HTTP/1.1 200 OK", False, "HTTP version"),
        ("Python 3.11 released", False, "Version number"),
    ]
    
    # Тесты, которые ДОЛЖНЫ детектировать ПИД
    true_positive_tests = [
        ("Меня зовут Иванов Иван Иванович", True, "Name with context"),
        ("Телефон: +7 (999) 123-45-67", True, "Phone with label"),
        ("Email: test@example.com", True, "Email with label"),
    ]
    
    all_passed = True
    
    print("\n--- FALSE POSITIVE TESTS ---")
    for text, should_detect, description in false_positive_tests:
        result = anon.check_compliance(text)
        has_pii = not result['is_compliant']
        
        if not should_detect and not has_pii:
            status = "✅"
        elif should_detect and has_pii:
            status = "✅"
        else:
            status = "❌"
            all_passed = False
        
        print(f"{status} {description}: '{text[:40]}'")
        if has_pii:
            print(f"   Found: {result['entities_found']}")
    
    print("\n--- TRUE POSITIVE TESTS ---")
    for text, should_detect, description in true_positive_tests:
        result = anon.check_compliance(text)
        has_pii = not result['is_compliant']
        
        if should_detect and has_pii:
            status = "✅"
        else:
            status = "❌"
            all_passed = False
        
        print(f"{status} {description}: '{text[:40]}'")
    
    print(f"\n{'✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!' if all_passed else '❌ ЕСТЬ ОШИБКИ'}")
    return all_passed


def test_edge_cases():
    """Тест краевых случаев"""
    print("\n📋 ТЕСТИРОВАНИЕ КРАЕВЫХ СЛУЧАЕВ")
    print("="*60)
    
    anon = Anonymizer()
    
    edge_cases = [
        ("", True, "Empty string"),
        (" ", True, "Single space"),
        ("X" * 10000, True, "Very long text"),
        ("Привет мир! Это тест.", True, "Simple Russian text"),
        ("Hello world! This is a test.", True, "Simple English text"),
    ]
    
    all_passed = True
    for text, should_be_clean, description in edge_cases:
        result = anon.check_compliance(text)
        is_clean = result['is_compliant']
        
        if should_be_clean and is_clean:
            status = "✅"
        else:
            status = "❌"
            all_passed = False
        
        print(f"{status} {description}")
        if not is_clean:
            print(f"   Found: {result['entities_found']}")
    
    return all_passed


def main():
    results = {
        'contextual_accuracy': test_contextual_accuracy(),
        'edge_cases': test_edge_cases(),
    }
    
    print("\n" + "="*60)
    print("📊 ИТОГОВЫЙ ОТЧЁТ ПРИОРИТЕТ 2+3")
    print("="*60)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\nВсего тестов: {total}")
    print(f"Пройдено: {passed}")
    print(f"Успешность: {passed/total*100:.1f}%")
    
    return all(results.values())


if __name__ == '__main__':
    main()
