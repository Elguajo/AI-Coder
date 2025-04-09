"""
Скрипт для быстрой установки и настройки чат-бота
"""

import os
import sys
import subprocess
import argparse

def check_python_version():
    """
    Проверка версии Python
    """
    print("Проверка версии Python...")
    if sys.version_info < (3, 10):
        print("❌ Требуется Python 3.10 или выше")
        sys.exit(1)
    print(f"✅ Используется Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

def check_ollama():
    """
    Проверка установки Ollama
    """
    print("Проверка установки Ollama...")
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama установлена")
            return True
        else:
            print("❌ Ollama не установлена или не запущена")
            return False
    except FileNotFoundError:
        print("❌ Ollama не установлена")
        return False

def install_dependencies():
    """
    Установка зависимостей
    """
    print("Установка зависимостей...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "gradio", "langchain", "langchain-community", 
                        "ollama", "python-dotenv", "chromadb", "pygments"], check=True)
        print("✅ Зависимости установлены")
        return True
    except subprocess.CalledProcessError:
        print("❌ Ошибка при установке зависимостей")
        return False

def create_env_file():
    """
    Создание файла .env
    """
    print("Создание файла .env...")
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write("OLLAMA_BASE_URL=http://localhost:11434\n")
            f.write("MODEL_NAME=deepseek-coder\n")
        print("✅ Файл .env создан")
    else:
        print("✅ Файл .env уже существует")

def create_directories():
    """
    Создание необходимых директорий
    """
    print("Создание директорий...")
    os.makedirs("memory", exist_ok=True)
    os.makedirs("code", exist_ok=True)
    print("✅ Директории созданы")

def pull_model():
    """
    Загрузка модели DeepSeek-coder
    """
    print("Проверка наличия модели DeepSeek-coder...")
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if "deepseek-coder" in result.stdout:
            print("✅ Модель DeepSeek-coder уже загружена")
            return True
        
        print("Загрузка модели DeepSeek-coder (это может занять некоторое время)...")
        subprocess.run(["ollama", "pull", "deepseek-coder"], check=True)
        print("✅ Модель DeepSeek-coder загружена")
        return True
    except subprocess.CalledProcessError:
        print("❌ Ошибка при загрузке модели")
        return False

def main():
    """
    Основная функция
    """
    parser = argparse.ArgumentParser(description="Установка и настройка чат-бота")
    parser.add_argument("--skip-deps", action="store_true", help="Пропустить установку зависимостей")
    parser.add_argument("--skip-model", action="store_true", help="Пропустить загрузку модели")
    args = parser.parse_args()
    
    print("=== Установка и настройка DeepSeek Coder Чат-бота ===")
    
    # Проверка версии Python
    check_python_version()
    
    # Создание директорий
    create_directories()
    
    # Создание файла .env
    create_env_file()
    
    # Установка зависимостей
    if not args.skip_deps:
        install_dependencies()
    else:
        print("Пропуск установки зависимостей")
    
    # Проверка Ollama
    ollama_installed = check_ollama()
    
    # Загрузка модели
    if ollama_installed and not args.skip_model:
        pull_model()
    elif args.skip_model:
        print("Пропуск загрузки модели")
    
    print("\n=== Установка завершена ===")
    print("\nДля запуска чат-бота выполните:")
    print("python app.py")
    
    if not ollama_installed:
        print("\nВНИМАНИЕ: Ollama не установлена или не запущена.")
        print("Установите Ollama с сайта https://ollama.ai/download")
        print("После установки запустите: ollama serve")

if __name__ == "__main__":
    main()
