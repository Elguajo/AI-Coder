"""
Модуль для создания кастомного UI для Elcoder с помощью Gradio
"""

import gradio as gr
import os
import sys
from pathlib import Path
from enhanced_chatbot import EnhancedCodingChatBot
import config

# Создание директории для CSS и JavaScript файлов
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

# Путь к файлу CSS
CSS_FILE = os.path.join(ASSETS_DIR, "custom.css")

def create_custom_css():
    """Создает файл с кастомными CSS стилями"""
    if not os.path.exists(CSS_FILE):
        with open(CSS_FILE, "w", encoding="utf-8") as f:
            f.write("""
/* Кастомные стили для Elcoder */
:root {
    --primary-color: #8b5cf6;   /* Фиолетовый */
    --secondary-color: #7c3aed;
    --background-color: #f8fafc;
    --text-color: #1e293b;
    --border-color: #e2e8f0;
    --success-color: #10b981;
    --error-color: #ef4444;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    background-color: var(--background-color);
    color: var(--text-color);
}

.gradio-container {
    max-width: 1200px;
    margin: 0 auto;
}

.main-header {
    background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
    color: white;
    padding: 1.5rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.footer {
    text-align: center;
    margin-top: 2rem;
    padding: 1rem 0;
    border-top: 1px solid var(--border-color);
    font-size: 0.875rem;
    color: #64748b;
}

/* Стили для чата */
.chatbot-container {
    border: 1px solid var(--border-color);
    border-radius: 0.5rem;
    overflow: hidden;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
}

.user-message {
    background-color: #ede9fe;
    border-radius: 0.5rem 0.5rem 0 0.5rem;
    padding: 0.75rem 1rem;
    margin: 0.5rem 0;
    border-left: 3px solid var(--primary-color);
}

.bot-message {
    background-color: #f1f5f9;
    border-radius: 0.5rem 0.5rem 0.5rem 0;
    padding: 0.75rem 1rem;
    margin: 0.5rem 0;
    border-left: 3px solid var(--secondary-color);
}

/* Стили для кнопок */
button.primary {
    background-color: var(--primary-color) !important;
    color: white !important;
    border: none !important;
    padding: 0.5rem 1rem !
