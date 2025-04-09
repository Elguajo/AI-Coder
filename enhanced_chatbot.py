"""
Расширенная версия чат-бота с дополнительными функциями для кодинга
"""

import os
import sys
import logging
import gradio as gr
from langchain.llms import Ollama
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
import config

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Настройка шаблона подсказки для кодинг-чатбота
CODING_PROMPT_TEMPLATE = """
Ты - полезный ассистент по программированию на основе DeepSeek-coder. 
Ты специализируешься на написании кода, объяснении концепций программирования и решении технических проблем.
Твои ответы должны быть точными, полезными и следовать лучшим практикам программирования.

Текущая дата: {current_date}
Версия Python: {python_version}
Рабочая директория: {working_directory}

История разговора:
{history}

Пользователь: {input}
Ассистент:"""

class EnhancedCodingChatBot:
    def __init__(self):
        """
        Инициализация расширенного чат-бота для кодинга
        """
        logger.info(f"Инициализация чат-бота с моделью {config.MODEL_NAME}")
        
        # Создание экземпляра LLM с использованием Ollama
        self.llm = Ollama(
            model=config.MODEL_NAME,
            temperature=config.TEMPERATURE,
            num_predict=config.MAX_TOKENS
        )
        
        # Добавление контекстной информации в шаблон подсказки
        self.prompt = PromptTemplate(
            input_variables=["history", "input", "current_date", "python_version", "working_directory"],
            template=CODING_PROMPT_TEMPLATE
        )
        
        # Настройка памяти с ограниченным окном
        self.memory = ConversationBufferWindowMemory(
            k=config.MEMORY_SIZE,
            return_messages=True
        )
        
        # Создание цепочки разговора
        self.conversation = ConversationChain(
            llm=self.llm,
            prompt=self.prompt,
            memory=self.memory,
            verbose=config.LOG_LEVEL == "DEBUG"
        )
        
        # Словарь для отслеживания файлов
        self.file_history = {}
        
        logger.info("Чат-бот успешно инициализирован")
    
    def get_context_info(self):
        """
        Получение контекстной информации для шаблона подсказки
        
        Returns:
            dict: Словарь с контекстной информацией
        """
        from datetime import datetime
        
        return {
            "current_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "working_directory": os.getcwd()
        }
    
    def chat(self, message, history):
        """
        Обработка сообщения пользователя и генерация ответа
        
        Args:
            message (str): Сообщение пользователя
            history (list): История диалога
            
        Returns:
            str: Ответ модели
        """
        logger.info(f"Получено сообщение: {message[:50]}{'...' if len(message) > 50 else ''}")
        
        # Получение контекстной информации
        context_info = self.get_context_info()
        
        # Обработка специальных команд
        if message.startswith("/file"):
            parts = message.split(" ", 2)
            if len(parts) < 2:
                return "Ошибка: неверный формат команды. Используйте /file list, /file read <filename> или /file create <filename> <content>"
            
            if parts[1] == "list":
                return self.list_files()
            elif parts[1] == "read" and len(parts) > 2:
                return self.read_file(parts[2])
            elif parts[1] == "create" and len(parts) > 3:
                filename, content = parts[2], parts[3]
                return self.create_file(filename, content)
            else:
                return "Ошибка: неверная команда файла"
        
        # Генерация ответа с использованием LLM
        try:
            response = self.conversation.predict(
                input=message,
                **context_info
            )
            logger.info(f"Сгенерирован ответ длиной {len(response)} символов")
            return response
        except Exception as e:
            logger.error(f"Ошибка при генерации ответа: {str(e)}")
            return f"Произошла ошибка при обработке вашего запроса: {str(e)}"
    
    def create_file(self, filename, content):
        """
        Создание файла с указанным содержимым
        
        Args:
            filename (str): Имя файла
            content (str): Содержимое файла
            
        Returns:
            str: Сообщение о результате операции
        """
        if not filename:
            return "Ошибка: имя файла не указано"
        
        file_path = os.path.join(config.FILES_DIR, filename)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.file_history[filename] = file_path
            logger.info(f"Создан файл: {file_path}")
            return f"Файл {filename} успешно создан в {file_path}"
        except Exception as e:
            logger.error(f"Ошибка при создании файла {filename}: {str(e)}")
            return f"Ошибка при создании файла: {str(e)}"
    
    def read_file(self, filename):
        """
        Чтение содержимого файла
        
        Args:
            filename (str): Имя файла
            
        Returns:
            str: Содержимое файла или сообщение об ошибке
        """
        if not filename:
            return "Ошибка: имя файла не указано"
        
        if filename in self.file_history:
            file_path = self.file_history[filename]
        else:
            file_path = os.path.join(config.FILES_DIR, filename)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.info(f"Прочитан файл: {file_path}")
            return content
        except Exception as e:
            logger.error(f"Ошибка при чтении файла {filename}: {str(e)}")
            return f"Ошибка при чтении файла: {str(e)}"
    
    def list_files(self):
        """
        Получение списка доступных файлов
        
        Returns:
            str: Список файлов
        """
        try:
            files = os.listdir(config.FILES_DIR)
            for f in self.file_history:
                if f not in files:
                    files.append(f)
            
            if not files:
                return "Нет доступных файлов"
            
            logger.info(f"Список файлов: найдено {len(files)} файлов")
            return f"Доступные файлы ({len(files)}):\n" + "\n".join(files)
        except Exception as e:
            logger.error(f"Ошибка при получении списка файлов: {str(e)}")
            return f"Ошибка при получении списка файлов: {str(e)}"
    
    def execute_code(self, code):
        """
        Выполнение Python кода и возврат результата
        
        Args:
            code (str): Python код для выполнения
            
        Returns:
            str: Результат выполнения кода или сообщение об ошибке
        """
        import io
        from contextlib import redirect_stdout, redirect_stderr
        
        output = io.StringIO()
        error = io.StringIO()
        
        try:
            # Настройка безопасного окружения для выполнения кода
            safe_globals = {
                "__builtins__": __builtins__,
                "print": print,
                "range": range,
                "len": len,
                "str": str,
                "int": int,
                "float": float,
                "list": list,
                "dict": dict,
                "tuple": tuple,
                "set": set,
                "bool": bool,
                "sum": sum,
                "max": max,
                "min": min,
            }
            
            # Выполнение кода и перенаправление вывода
            with redirect_stdout(output), redirect_stderr(error):
                exec(code, safe_globals)
            
            stdout = output.getvalue()
            stderr = error.getvalue()
            
            if stderr:
                logger.warning(f"Код выполнен с ошибками: {stderr}")
                return f"Ошибка выполнения:\n{stderr}"
            else:
                logger.info("Код успешно выполнен")
                return f"Результат выполнения:\n{stdout}"
        except Exception as e:
            logger.error(f"Ошибка при выполнении кода: {str(e)}")
            return f"Ошибка при выполнении кода: {str(e)}"

def build_enhanced_interface():
    """
    Создание расширенного веб-интерфейса с использованием Gradio
    
    Returns:
        gr.Blocks: Интерфейс Gradio
    """
    bot = EnhancedCodingChatBot()
    
    with gr.Blocks(title="Расширенный чат-бот для кодинга") as interface:
        gr.Markdown("# 🤖 Расширенный чат-бот для кодинга на основе DeepSeek")
        gr.Markdown("Используйте этого бота для написания кода, решения проблем программирования и работы с файлами.")
        
        with gr.Tab("Чат"):
            chatbot = gr.Chatbot(height=600, elem_id="chatbot")
            with gr.Row():
                msg = gr.Textbox(
                    placeholder="Задайте вопрос или опишите задачу по программированию...",
                    container=False,
                    scale=8
                )
                submit = gr.Button("Отправить", scale=1)
            
            with gr.Row():
                clear = gr.Button("Очистить чат")
                examples = gr.Examples(
                    examples=[
                        "Напиши простой веб-сервер на Flask",
                        "Как реализовать сортировку слиянием в Python?",
                        "Создай класс для работы с базой данных SQLite",
                        "/file list",
                    ],
                    inputs=msg
                )
            
            def user(message, history):
                return "", history + [[message, None]]
            
            def bot_response(history):
                message = history[-1][0]
                response = bot.chat(message, history[:-1])
                history[-1][1] = response
                return history
            
            submit.click(user, [msg, chatbot], [msg, chatbot], queue=False).then(
                bot_response, chatbot, chatbot
            )
            msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
                bot_response, chatbot, chatbot
            )
            clear.click(lambda: None, None, chatbot, queue=False)
        
        with gr.Tab("Файлы"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### Управление файлами")
                    filename_input = gr.Textbox(label="Имя файла")
                    with gr.Row():
                        list_btn = gr.Button("Список файлов")
                        read_btn = gr.Button("Прочитать файл")
                    file_result = gr.Textbox(label="Результат операции", lines=10)
                
                with gr.Column(scale=2):
                    file_content = gr.Code(label="Содержимое файла", language="python", lines=25)
                    save_btn = gr.Button("Сохранить файл")
            
            def list_files_callback():
                return bot.list_files()
            
            def read_file_callback(filename):
                return bot.read_file(filename)
            
            def save_file_callback(filename, content):
                return bot.create_file(filename, content)
            
            list_btn.click(list_files_callback, outputs=[file_result])
            read_btn.click(read_file_callback, inputs=[filename_input], outputs=[file_content])
            save_btn.click(save_file_callback, inputs=[filename_input, file_content], outputs=[file_result])
        
        with gr.Tab("Выполнение кода"):
            with gr.Row():
                with gr.Column():
                    code_input = gr.Code(label="Код Python", language="python", lines=15)
                    run_btn = gr.Button("Выполнить код")
                
                with gr.Column():
                    code_output = gr.Textbox(label="Результат выполнения", lines=15)
            
            def execute_code_callback(code):
                return bot.execute_code(code)
            
            run_btn.click(execute_code_callback, inputs=[code_input], outputs=[code_output])
        
        gr.Markdown("### Информация о системе")
        gr.Markdown(f"* **Модель**: {config.MODEL_NAME}")
        gr.Markdown(f"* **Версия Python**: {sys.version}")
        gr.Markdown(f"* **Директория файлов**: {config.FILES_DIR}")
    
    return interface

if __name__ == "__main__":
    interface = build_enhanced_interface()
    interface.launch(
        server_name=config.SERVER_HOST,
        server_port=config.SERVER_PORT,
        share=config.SHARE,
        auth=config.AUTH
    )
