#!/usr/bin/env python3
"""
Главный скрипт для запуска Elcoder с выбором интерфейса
"""

import os
import sys
import argparse
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """
    Проверка наличия необходимых зависимостей
    """
    try:
        import gradio
        import langchain
        logger.info("Основные зависимости установлены")
        return True
    except ImportError as e:
        logger.error(f"Отсутствуют необходимые зависимости: {str(e)}")
        logger.info("Установите зависимости с помощью команды: pip install -r requirements.txt")
        return False

def check_ollama():
    """
    Проверка доступности Ollama
    """
    import subprocess
    import platform
    
    system = platform.system()
    
    try:
        if system == "Windows":
            process = subprocess.Popen(
                ["powershell", "-Command", "Get-Process ollama -ErrorAction SilentlyContinue"], 
                stdout=subprocess.PIPE
            )
            output, _ = process.communicate()
            return "ollama" in output.decode().lower()
        else:  # Linux/Mac
            process = subprocess.Popen(
                ["pgrep", "ollama"], 
                stdout=subprocess.PIPE
            )
            output, _ = process.communicate()
            return output.strip() != b''
    except Exception as e:
        logger.warning(f"Не удалось проверить статус Ollama: {str(e)}")
        return False

def check_model(model_name):
    """
    Проверка наличия выбранной модели в Ollama
    """
    import subprocess
    import json
    
    try:
        process = subprocess.Popen(
            ["ollama", "list", "--json"], 
            stdout=subprocess.PIPE
        )
        output, _ = process.communicate()
        models = json.loads(output.decode())
        
        for model in models:
            if model.get("name") == model_name:
                return True
        
        return False
    except Exception as e:
        logger.warning(f"Не удалось проверить наличие модели: {str(e)}")
        return False

def main():
    """
    Основная функция для запуска Elcoder
    """
    parser = argparse.ArgumentParser(description="Elcoder - Локальный чат-бот для кодинга")
    parser.add_argument(
        "--ui", 
        choices=["basic", "enhanced", "custom"], 
        default="custom", 
        help="Тип интерфейса (basic, enhanced, custom)"
    )
    parser.add_argument(
        "--host", 
        type=str, 
        help="Хост для запуска сервера"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        help="Порт для запуска сервера"
    )
    parser.add_argument(
        "--share", 
        action="store_true", 
        help="Создать публичную ссылку"
    )
    parser.add_argument(
        "--model", 
        type=str, 
        help="Название модели для использования с Ollama"
    )
    
    args = parser.parse_args()
    
    # Проверка зависимостей
    if not check_dependencies():
        sys.exit(1)
    
    # Проверка Ollama
    if not check_ollama():
        logger.error("Ollama не запущен. Пожалуйста, запустите Ollama перед запуском Elcoder.")
        logger.info("Инструкции по установке Ollama: https://github.com/ollama/ollama")
        sys.exit(1)
    
    # Обновление конфигурации
    import config
    
    if args.host:
        config.SERVER_HOST = args.host
    
    if args.port:
        config.SERVER_PORT = args.port
    
    if args.share:
        config.SHARE = True
    
    if args.model:
        config.MODEL_NAME = args.model
    
    # Проверка наличия модели
    if not check_model(config.MODEL_NAME):
        logger.warning(f"Модель {config.MODEL_NAME} не найдена. Попытка загрузки...")
        import subprocess
        try:
            subprocess.run(["ollama", "pull", config.MODEL_NAME], check=True)
            logger.info(f"Модель {config.MODEL_NAME} успешно загружена")
        except subprocess.CalledProcessError:
            logger.error(f"Не удалось загрузить модель {config.MODEL_NAME}")
            sys.exit(1)
    
    # Запуск выбранного интерфейса
    logger.info(f"Запуск интерфейса типа: {args.ui}")
    
    if args.ui == "basic":
        from main import build_interface
        interface = build_interface()
    elif args.ui == "enhanced":
        from enhanced_chatbot import build_enhanced_interface
        interface = build_enhanced_interface()
    else:  # custom
        from custom_ui import build_custom_interface
        interface = build_custom_interface()
    
    # Запуск интерфейса
    interface.launch(
        server_name=config.SERVER_HOST,
        server_port=config.SERVER_PORT,
        share=config.SHARE,
        auth=config.AUTH
    )

if __name__ == "__main__":
    print("""
    ███████╗██╗      ██████╗ ██████╗ ██████╗ ███████╗██████╗ 
    ██╔════╝██║     ██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔══██╗
    █████╗  ██║     ██║     ██║   ██║██║  ██║█████╗  ██████╔╝
    ██╔══╝  ██║     ██║     ██║   ██║██║  ██║██╔══╝  ██╔══██╗
    ███████╗███████╗╚██████╗╚██████╔╝██████╔╝███████╗██║  ██║
    ╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝
    
    Локальный ассистент для программирования
    """)
    main()
