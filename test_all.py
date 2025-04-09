"""
Модуль для тестирования всех компонентов чат-бота
"""

import os
import sys
import time
import subprocess
import importlib.util
from pathlib import Path

def print_header(text):
    """Печать заголовка теста"""
    print("\n" + "=" * 60)
    print(f" {text} ".center(60, "="))
    print("=" * 60)

def print_result(name, success):
    """Печать результата теста"""
    status = "✅ УСПЕШНО" if success else "❌ ОШИБКА"
    print(f"{name}: {status}")

def check_file_exists(file_path):
    """Проверка существования файла"""
    exists = os.path.exists(file_path)
    print_result(f"Проверка файла {file_path}", exists)
    return exists

def check_directory_exists(dir_path):
    """Проверка существования директории"""
    exists = os.path.exists(dir_path) and os.path.isdir(dir_path)
    print_result(f"Проверка директории {dir_path}", exists)
    return exists

def check_module_imports(module_name):
    """Проверка импорта модуля"""
    try:
        importlib.import_module(module_name)
        print_result(f"Импорт модуля {module_name}", True)
        return True
    except ImportError as e:
        print_result(f"Импорт модуля {module_name}", False)
        print(f"  Ошибка: {str(e)}")
        return False

def check_ollama_running():
    """Проверка запуска Ollama"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags")
        success = response.status_code == 200
        print_result("Проверка запуска Ollama", success)
        return success
    except Exception as e:
        print_result("Проверка запуска Ollama", False)
        print(f"  Ошибка: {str(e)}")
        return False

def test_ollama_client():
    """Тестирование клиента Ollama"""
    print_header("Тестирование клиента Ollama")
    
    try:
        from ollama_client import OllamaClient
        
        # Создаем клиент
        client = OllamaClient()
        
        # Проверяем список моделей
        models = client.list_models()
        print(f"Доступные модели: {len(models)}")
        for model in models:
            print(f"  - {model['name']}")
        
        # Проверяем доступность модели deepseek-coder
        model_available = any(model['name'] == 'deepseek-coder' for model in models)
        print_result("Проверка доступности модели deepseek-coder", model_available)
        
        if model_available:
            # Тестируем генерацию
            print("Тестирование генерации...")
            response = client.generate(
                prompt="Напиши простую функцию на Python для вычисления факториала числа.",
                temperature=0.7,
                max_tokens=500
            )
            
            success = len(response) > 0 and "def" in response
            print_result("Генерация кода", success)
            
            if success:
                print("\nПример сгенерированного кода:")
                print("-" * 40)
                print(response[:500] + ("..." if len(response) > 500 else ""))
                print("-" * 40)
        
        return model_available
    except Exception as e:
        print_result("Тестирование клиента Ollama", False)
        print(f"  Ошибка: {str(e)}")
        return False

def test_memory_manager():
    """Тестирование менеджера памяти"""
    print_header("Тестирование менеджера памяти")
    
    try:
        from memory_manager import ChatMemory
        
        # Создаем менеджер памяти
        memory = ChatMemory()
        
        # Проверяем добавление сообщений
        print("Добавление тестовых сообщений...")
        memory.add_message("user", "Как написать функцию для сортировки списка?")
        memory.add_message("assistant", "Вот пример функции для сортировки списка: def sort_list(lst): return sorted(lst)")
        
        # Проверяем поиск сообщений
        print("Поиск сообщений...")
        results = memory.search_similar("сортировка списка", k=1)
        
        success = len(results) > 0
        print_result("Поиск сообщений", success)
        
        if success:
            print("\nНайденное сообщение:")
            print("-" * 40)
            print(f"Роль: {results[0].metadata.get('role', 'unknown')}")
            print(f"Содержание: {results[0].page_content[:100]}...")
            print("-" * 40)
        
        # Очищаем память
        print("Очистка памяти...")
        memory.clear()
        
        return success
    except Exception as e:
        print_result("Тестирование менеджера памяти", False)
        print(f"  Ошибка: {str(e)}")
        return False

def test_code_manager():
    """Тестирование менеджера кода"""
    print_header("Тестирование менеджера кода")
    
    try:
        from code_manager import CodeFileManager
        
        # Создаем менеджер кода
        code_manager = CodeFileManager()
        
        # Тестовый код
        test_code = """def factorial(n):
    \"\"\"Calculate factorial of n.\"\"\"
    if n == 0 or n == 1:
        return 1
    else:
        return n * factorial(n-1)

# Test the function
print(factorial(5))"""
        
        # Сохраняем код в файл
        print("Сохранение кода в файл...")
        file_path = code_manager.save_code_to_file(test_code, "test_factorial.py")
        
        # Проверяем чтение кода из файла
        print("Чтение кода из файла...")
        read_code = code_manager.read_code_from_file("test_factorial.py")
        
        read_success = read_code == test_code
        print_result("Чтение кода из файла", read_success)
        
        # Проверяем подсветку кода
        print("Подсветка кода...")
        highlighted_code = code_manager.highlight_code(test_code, "python")
        
        highlight_success = "<pre>" in highlighted_code and "factorial" in highlighted_code
        print_result("Подсветка кода", highlight_success)
        
        # Проверяем выполнение кода
        print("Выполнение кода...")
        execution_result = code_manager.execute_code(test_code, "python")
        
        execution_success = "120" in execution_result  # 5! = 120
        print_result("Выполнение кода", execution_success)
        
        if execution_success:
            print("\nРезультат выполнения:")
            print("-" * 40)
            print(execution_result)
            print("-" * 40)
        
        # Проверяем список файлов
        print("Получение списка файлов...")
        files = code_manager.list_code_files()
        
        files_success = "test_factorial.py" in files
        print_result("Получение списка файлов", files_success)
        
        if files_success:
            print("\nСписок файлов:")
            for file in files:
                print(f"  - {file}")
        
        # Удаляем тестовый файл
        print("Удаление файла...")
        delete_success = code_manager.delete_code_file("test_factorial.py")
        print_result("Удаление файла", delete_success)
        
        return read_success and highlight_success and execution_success and files_success and delete_success
    except Exception as e:
        print_result("Тестирование менеджера кода", False)
        print(f"  Ошибка: {str(e)}")
        return False

def test_chatbot():
    """Тестирование основного класса чат-бота"""
    print_header("Тестирование основного класса чат-бота")
    
    try:
        from code_enabled_chatbot import CodeEnabledChatBot
        
        # Создаем чат-бот
        print("Инициализация чат-бота...")
        chatbot = CodeEnabledChatBot()
        
        # Тестируем простой запрос
        print("Тестирование простого запроса...")
        response = chatbot.get_chat_response("Привет! Расскажи о себе.")
        
        simple_success = len(response) > 0 and "DeepSeek" in response
        print_result("Простой запрос", simple_success)
        
        if simple_success:
            print("\nОтвет на простой запрос:")
            print("-" * 40)
            print(response[:300] + ("..." if len(response) > 300 else ""))
            print("-" * 40)
        
        # Тестируем запрос на генерацию кода
        print("Тестирование запроса на генерацию кода...")
        code_response = chatbot.get_chat_response("Напиши функцию для проверки, является ли строка палиндромом.")
        
        code_success = len(code_response) > 0 and "def" in code_response and "palindrom" in code_response.lower()
        print_result("Запрос на генерацию кода", code_success)
        
        if code_success:
            print("\nОтвет на запрос о генерации кода:")
            print("-" * 40)
            print(code_response[:300] + ("..." if len(code_response) > 300 else ""))
            print("-" * 40)
        
        return simple_success and code_success
    except Exception as e:
        print_result("Тестирование основного класса чат-бота", False)
        print(f"  Ошибка: {str(e)}")
        return False

def test_gradio_interface():
    """Тестирование Gradio интерфейса"""
    print_header("Тестирование Gradio интерфейса")
    
    try:
        # Проверяем наличие файла app.py
        app_exists = check_file_exists("app.py")
        
        if not app_exists:
            return False
        
        # Импортируем класс интерфейса
        from app import ChatBotInterface
        
        # Проверяем создание интерфейса
        print("Создание интерфейса...")
        interface = ChatBotInterface()
        
        interface_success = hasattr(interface, 'interface') and hasattr(interface, 'chatbot')
        print_result("Создание интерфейса", interface_success)
        
        return interface_success
    except Exception as e:
        print_result("Тестирование Gradio интерфейса", False)
        print(f"  Ошибка: {str(e)}")
        return False

def run_all_tests():
    """Запуск всех тестов"""
    print_header("ТЕСТИРОВАНИЕ ЧАТБОТА")
    
    # Проверка файлов и директорий
    files_to_check = [
        "config.py", 
        "memory_manager.py", 
        "ollama_client.py", 
        "chatbot.py", 
        "deepseek_model.py", 
        "enhanced_chatbot.py", 
        "code_manager.py", 
        "code_enabled_chatbot.py", 
        "app.py", 
        "ollama_integration.py", 
        "memory_test.py",
        "setup.py",
        "README.md",
        "docs/README.md"
    ]
    
    dirs_to_check = ["memory", "code", "docs"]
    
    print_header("Проверка файлов и директорий")
    
    files_success = all(check_file_exists(file) for file in files_to_check)
    dirs_success = all(check_directory_exists(dir_path) for dir_path in dirs_to_check)
    
    # Проверка импортов
    print_header("Проверка импортов")
    
    imports_to_check = ["gradio", "langchain", "langchain_community", "ollama", "chromadb", "pygments"]
    imports_success = all(check_module_imports(module) for module in imports_to_check)
    
    # Проверка запуска Ollama
    ollama_success = check_ollama_running()
    
    # Запуск функциональных тестов
    if ollama_success:
        ollama_client_success = test_ollama_client()
        memory_success = test_memory_manager()
        code_success = test_code_manager()
        chatbot_success = test_chatbot()
        gradio_success = test_gradio_interface()
    else:
        print("\n⚠️ Ollama не запущена, пропуск функциональных тестов")
        ollama_client_success = memory_success = code_success = chatbot_success = gradio_success = False
    
    # Итоговый результат
    print_header("ИТОГОВЫЙ РЕЗУЛЬТАТ")
    
    print_result("Проверка файлов", files_success)
    print_result("Проверка директорий", dirs_success)
    print_result("Проверка импортов", imports_success)
    print_result("Проверка Ollama", ollama_success)
    
    if ollama_success:
        print_result("Тестирование клиента Ollama", ollama_client_success)
        print_result("Тестирование менеджера памяти", memory_success)
        print_result("Тестирование менеджера кода", code_success)
        print_result("Тестирование чат-бота", chatbot_success)
        print_result("Тестирование Gradio интерфейса", gradio_success)
    
    all_success = files_success and dirs_success and imports_success
    if ollama_success:
        all_success = all_success and ollama_client_success and memory_success and code_success and chatbot_success and gradio_success
    
    print("\n" + "=" * 60)
    if all_success:
        print("✅ ВСЕ ТЕСТЫ УСПЕШНО ПРОЙДЕНЫ")
        print("Чат-бот готов к использованию!")
        print("Для запуска выполните: python app.py")
    else:
        print("⚠️ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
        print("Проверьте ошибки и исправьте их перед использованием чат-бота")
    print("=" * 60)
    
    return all_success

if __name__ == "__main__":
    run_all_tests()
