"""
Модуль для создания кастомного UI с помощью Gradio
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

# Создание CSS файла, если он не существует
def create_custom_css():
    """Создает файл с кастомными CSS стилями"""
    if not os.path.exists(CSS_FILE):
        with open(CSS_FILE, "w", encoding="utf-8") as f:
            f.write("""
/* Кастомные стили для чат-бота */
:root {
    --primary-color: #2563eb;
    --secondary-color: #1e40af;
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
    background-color: #e9f5ff;
    border-radius: 0.5rem 0.5rem 0 0.5rem;
    padding: 0.75rem 1rem;
    margin: 0.5rem 0;
}

.bot-message {
    background-color: #f1f5f9;
    border-radius: 0.5rem 0.5rem 0.5rem 0;
    padding: 0.75rem 1rem;
    margin: 0.5rem 0;
}

/* Стили для кнопок */
button.primary {
    background-color: var(--primary-color) !important;
    color: white !important;
    border: none !important;
    padding: 0.5rem 1rem !important;
    border-radius: 0.375rem !important;
    font-weight: 500 !important;
    cursor: pointer !important;
    transition: background-color 0.2s !important;
}

button.primary:hover {
    background-color: var(--secondary-color) !important;
}

button.secondary {
    background-color: white !important;
    color: var(--primary-color) !important;
    border: 1px solid var(--border-color) !important;
    padding: 0.5rem 1rem !important;
    border-radius: 0.375rem !important;
    font-weight: 500 !important;
    cursor: pointer !important;
    transition: background-color 0.2s !important;
}

button.secondary:hover {
    background-color: #f1f5f9 !important;
}

/* Стили для вкладок */
.tab-nav {
    border-bottom: 1px solid var(--border-color);
    margin-bottom: 1rem;
}

.tab-nav button {
    padding: 0.75rem 1.5rem !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    background-color: transparent !important;
    font-weight: 500 !important;
    color: #64748b !important;
    transition: all 0.2s !important;
}

.tab-nav button.selected {
    color: var(--primary-color) !important;
    border-bottom: 2px solid var(--primary-color) !important;
}

/* Стили для кода */
.code-editor {
    font-family: 'Fira Code', 'Courier New', monospace;
    border-radius: 0.375rem;
    overflow: hidden;
}

.code-editor pre {
    padding: 1rem !important;
}

/* Стили для результатов файловых операций */
.file-result {
    background-color: #f1f5f9;
    border-radius: 0.375rem;
    padding: 0.75rem 1rem;
    font-family: 'Fira Code', 'Courier New', monospace;
    font-size: 0.875rem;
    white-space: pre-wrap;
}

/* Темная тема */
@media (prefers-color-scheme: dark) {
    :root {
        --background-color: #0f172a;
        --text-color: #e2e8f0;
        --border-color: #334155;
    }
    
    .user-message {
        background-color: #1e3a8a;
        color: white;
    }
    
    .bot-message {
        background-color: #1f2937;
        color: white;
    }
    
    .file-result {
        background-color: #1f2937;
        color: white;
    }
    
    button.secondary {
        background-color: #1f2937 !important;
        color: #e2e8f0 !important;
    }
    
    button.secondary:hover {
        background-color: #334155 !important;
    }
}
""")

def build_custom_interface():
    """
    Создание кастомного веб-интерфейса с использованием Gradio
    и применением пользовательских стилей
    
    Returns:
        gr.Blocks: Интерфейс Gradio с кастомным UI
    """
    # Создание CSS файла
    create_custom_css()
    
    # Инициализация чат-бота
    bot = EnhancedCodingChatBot()
    
    # Создание интерфейса
    with gr.Blocks(css=CSS_FILE, title="Чат-бот для кодинга") as interface:
        # Шапка
        with gr.Box(elem_classes="main-header"):
            gr.Markdown("# 🤖 Чат-бот для кодинга на основе DeepSeek")
            gr.Markdown("Локальный ассистент для программирования с использованием DeepSeek Coder, Ollama и LangChain")
        
        # Основное содержимое
        with gr.Tabs(elem_classes="tab-nav") as tabs:
            
            # Вкладка чата
            with gr.TabItem("💬 Чат", id="chat"):
                chatbot = gr.Chatbot(elem_id="chatbot", elem_classes="chatbot-container", height=500)
                
                with gr.Row():
                    msg = gr.Textbox(
                        placeholder="Задайте вопрос или опишите задачу по программированию...",
                        container=False,
                        scale=7
                    )
                    submit = gr.Button("Отправить", elem_classes="primary", scale=1)
                
                with gr.Row():
                    clear = gr.Button("Очистить чат", elem_classes="secondary")
                    
                with gr.Accordion("Примеры запросов", open=False):
                    gr.Examples(
                        examples=[
                            "Напиши простой веб-сервер на Flask",
                            "Как реализовать сортировку слиянием в Python?",
                            "Создай класс для работы с базой данных SQLite",
                            "Напиши функцию для анализа CSV файла с помощью pandas",
                            "Объясни концепцию замыканий в Python",
                            "/file list"
                        ],
                        inputs=msg
                    )
            
            # Вкладка для работы с файлами
            with gr.TabItem("📁 Файлы", id="files"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 📋 Управление файлами")
                        filename_input = gr.Textbox(label="Имя файла")
                        
                        with gr.Row():
                            list_btn = gr.Button("Список файлов", elem_classes="secondary")
                            read_btn = gr.Button("Прочитать", elem_classes="secondary")
                        
                        file_result = gr.Textbox(
                            label="Результат операции", 
                            lines=10,
                            elem_classes="file-result"
                        )
                    
                    with gr.Column(scale=2):
                        file_content = gr.Code(
                            label="Содержимое файла", 
                            language="python", 
                            lines=25,
                            elem_classes="code-editor"
                        )
                        save_btn = gr.Button("Сохранить файл", elem_classes="primary")
            
            # Вкладка для запуска кода
            with gr.TabItem("🚀 Запуск кода", id="execute"):
                with gr.Row():
                    with gr.Column():
                        code_input = gr.Code(
                            label="Код Python", 
                            language="python", 
                            lines=15,
                            elem_classes="code-editor"
                        )
                        run_btn = gr.Button("Выполнить код", elem_classes="primary")
                    
                    with gr.Column():
                        code_output = gr.Textbox(
                            label="Результат выполнения", 
                            lines=15,
                            elem_classes="file-result"
                        )
            
            # Вкладка настроек
            with gr.TabItem("⚙️ Настройки", id="settings"):
                gr.Markdown("### ⚙️ Настройки системы")
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("#### Модель")
                        model_info = gr.Markdown(f"**Текущая модель**: {config.MODEL_NAME}")
                        model_temp = gr.Slider(
                            label="Температура", 
                            minimum=0.0, 
                            maximum=1.0, 
                            step=0.1, 
                            value=config.TEMPERATURE
                        )
                        
                        def update_temp(temp):
                            config.TEMPERATURE = temp
                            return f"Температура установлена на {temp}"
                        
                        model_temp.change(update_temp, inputs=[model_temp], outputs=[model_info])
                    
                    with gr.Column():
                        gr.Markdown("#### Информация о системе")
                        gr.Markdown(f"* **Версия Python**: {sys.version.split()[0]}")
                        gr.Markdown(f"* **Директория файлов**: {config.FILES_DIR}")
                        gr.Markdown(f"* **Хост/порт**: {config.SERVER_HOST}:{config.SERVER_PORT}")
        
        # Подвал
        with gr.Box(elem_classes="footer"):
            gr.Markdown("Локальный чат-бот для кодинга | Использует DeepSeek-coder через Ollama")
        
        # Функции для работы с интерфейсом
        def user(message, history):
            return "", history + [[message, None]]
        
        def bot_response(history):
            message = history[-1][0]
            response = bot.chat(message, history[:-1])
            history[-1][1] = response
            return history
        
        # Обработчики событий
        submit.click(user, [msg, chatbot], [msg, chatbot], queue=False).then(
            bot_response, chatbot, chatbot
        )
        
        msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
            bot_response, chatbot, chatbot
        )
        
        clear.click(lambda: None, None, chatbot, queue=False)
        
        # Обработчики для файлов
        def list_files_callback():
            return bot.list_files()
        
        def read_file_callback(filename):
            return bot.read_file(filename)
        
        def save_file_callback(filename, content):
            return bot.create_file(filename, content)
        
        list_btn.click(list_files_callback, outputs=[file_result])
        read_btn.click(read_file_callback, inputs=[filename_input], outputs=[file_content])
        save_btn.click(save_file_callback, inputs=[filename_input, file_content], outputs=[file_result])
        
        # Обработчики для запуска кода
        def execute_code_callback(code):
            return bot.execute_code(code)
        
        run_btn.click(execute_code_callback, inputs=[code_input], outputs=[code_output])
    
    return interface

if __name__ == "__main__":
    # Запуск кастомного интерфейса
    interface = build_custom_interface()
    interface.launch(
        server_name=config.SERVER_HOST,
        server_port=config.SERVER_PORT,
        share=config.SHARE,
        auth=config.AUTH
    )
