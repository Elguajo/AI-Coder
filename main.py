import os
import gradio as gr
from langchain.llms import Ollama
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
import tempfile

# Настройка директории для временных файлов
TEMP_DIR = os.path.join(tempfile.gettempdir(), "elcoder_files")
os.makedirs(TEMP_DIR, exist_ok=True)

# Настройка шаблона подсказки для Elcoder
PROMPT_TEMPLATE = """
Ты - Elcoder, полезный ассистент по программированию на основе DeepSeek-coder. Ты помогаешь пользователям писать код, объяснять концепции программирования и решать технические проблемы.

История разговора:
{history}

Пользователь: {input}
Elcoder:"""

class CodingChatBot:
    def __init__(self, model_name="deepseek-coder:6.7b-instruct-q4_K_M"):
        """
        Инициализация Elcoder - чат-бота для кодинга
        
        Args:
            model_name (str): Название модели для использования с Ollama
        """
        self.model_name = model_name
        self.llm = Ollama(model=model_name)
        self.prompt = PromptTemplate(
            input_variables=["history", "input"],
            template=PROMPT_TEMPLATE
        )
        self.memory = ConversationBufferMemory(return_messages=True)
        self.conversation = ConversationChain(
            llm=self.llm,
            prompt=self.prompt,
            memory=self.memory,
            verbose=True
        )
        self.file_history = {}
    
    def chat(self, message, history):
        """
        Обработка сообщения пользователя и генерация ответа
        
        Args:
            message (str): Сообщение пользователя
            history (list): История диалога
            
        Returns:
            str: Ответ модели
        """
        response = self.conversation.predict(input=message)
        return response
    
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
        
        file_path = os.path.join(TEMP_DIR, filename)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.file_history[filename] = file_path
            return f"Файл {filename} успешно создан в {file_path}"
        except Exception as e:
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
            file_path = os.path.join(TEMP_DIR, filename)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            return f"Ошибка при чтении файла: {str(e)}"
    
    def list_files(self):
        """
        Получение списка доступных файлов
        
        Returns:
            str: Список файлов
        """
        files = list(self.file_history.keys())
        if not files:
            return "Нет созданных файлов"
        
        return "Созданные файлы:\n" + "\n".join(files)

def build_interface():
    """
    Создание веб-интерфейса с использованием Gradio
    
    Returns:
        gr.Blocks: Интерфейс Gradio
    """
    bot = CodingChatBot()
    
    with gr.Blocks(title="Elcoder - Базовый режим") as interface:
        gr.Markdown("# 🤖 Elcoder - Локальный чат-бот для кодинга")
        gr.Markdown("Используйте Elcoder для написания кода, решения проблем программирования и работы с файлами.")
        
        with gr.Tab("Чат"):
            chatbot = gr.Chatbot(height=500)
            msg = gr.Textbox(
                placeholder="Задайте вопрос или опишите задачу по программированию...",
                container=False,
                scale=8
            )
            clear = gr.Button("Очистить")
            
            def user(message, history):
                return "", history + [[message, None]]
            
            def bot_response(history):
                message = history[-1][0]
                response = bot.chat(message, history[:-1])
                history[-1][1] = response
                return history
            
            msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
                bot_response, chatbot, chatbot
            )
            clear.click(lambda: None, None, chatbot, queue=False)
        
        with gr.Tab("Файлы"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### Управление файлами")
                    filename_input = gr.Textbox(label="Имя файла")
                    list_btn = gr.Button("Список файлов")
                    read_btn = gr.Button("Прочитать файл")
                    file_result = gr.Textbox(label="Результат операции", lines=10)
                
                with gr.Column(scale=2):
                    file_content = gr.Code(language="python", label="Содержимое файла", lines=25)
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
    
    return interface

if __name__ == "__main__":
    interface = build_interface()
    interface.launch()
