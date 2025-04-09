"""
Файл конфигурации для Elcoder - локального чат-бота для кодинга
"""

# Настройки модели
MODEL_NAME = "deepseek-coder:6.7b-instruct-q4_K_M"  # Название модели для Ollama
TEMPERATURE = 0.7  # Температура генерации (0.0 - 1.0)
MAX_TOKENS = 2048  # Максимальное количество токенов в ответе

# Настройки веб-интерфейса
SERVER_HOST = "127.0.0.1"  # Хост для запуска сервера
SERVER_PORT = 7860  # Порт для запуска сервера
SHARE = False  # Создать публичную ссылку (Gradio share link)
AUTH = None  # Авторизация в формате ("username", "password")

# Настройки системы
MEMORY_SIZE = 10  # Количество сообщений, хранящихся в памяти
LOG_LEVEL = "INFO"  # Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)

# Путь к директории для хранения файлов
# По умолчанию создает директорию 'files' в текущей директории
import os
FILES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "files")
os.makedirs(FILES_DIR, exist_ok=True)
