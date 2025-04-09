"""
Веб-интерфейс для чат-бота на базе Gradio
"""

import os
import re
import gradio as gr
from code_enabled_chatbot import CodeEnabledChatBot
import config

class ChatBotInterface:
    """
    Класс для создания веб-интерфейса чат-бота с использованием Gradio
    """
    
    def __init__(self):
        """
        Инициализация интерфейса чат-бота
        """
        # Инициализация чат-бота
        self.chatbot = CodeEnabledChatBot()
        
        # Флаг для отслеживания статуса инициализации Ollama
        self.ollama_initialized = False
        
        # Создаем интерфейс
        self.create_interface()
    
    def create_interface(self):
        """
        Создание веб-интерфейса с использованием Gradio
        """
        # Создаем тему
        theme = gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="indigo",
        )
        
        # Создаем интерфейс
        with gr.Blocks(title=config.GRADIO_TITLE, theme=theme) as self.interface:
            # Заголовок
            gr.Markdown(f"# {config.GRADIO_TITLE}")
            gr.Markdown(config.GRADIO_DESCRIPTION)
            
            # Статус Ollama
            with gr.Row():
                self.status_box = gr.Textbox(
                    label="Статус",
                    value="Инициализация...",
                    interactive=False
                )
                check_button = gr.Button("Проверить статус Ollama")
            
            # Чат
            with gr.Row():
                with gr.Column(scale=4):
                    self.chatbot_ui = gr.Chatbot(
                        label="Диалог",
                        height=500,
                        show_copy_button=True,
                        show_share_button=False,
                        avatar_images=("👤", "🤖")
                    )
                    
                    with gr.Row():
                        self.msg_box = gr.Textbox(
                            label="Сообщение",
                            placeholder="Введите ваш запрос здесь...",
                            lines=3,
                            max_lines=10,
                            show_copy_button=True,
                            container=False
                        )
                        self.submit_btn = gr.Button("Отправить", variant="primary")
                    
                    with gr.Row():
                        clear_btn = gr.Button("Очистить чат")
                        memory_clear_btn = gr.Button("Очистить память")
                
                # Панель файлов и кода
                with gr.Column(scale=2):
                    gr.Markdown("### Файлы с кодом")
                    self.files_dropdown = gr.Dropdown(
                        label="Выберите файл",
                        choices=self.get_code_files(),
                        interactive=True
                    )
                    
                    with gr.Row():
                        view_file_btn = gr.Button("Просмотреть")
                        run_file_btn = gr.Button("Выполнить")
                        delete_file_btn = gr.Button("Удалить")
                    
                    self.code_display = gr.Code(
                        label="Код",
                        language="python",
                        value="# Здесь будет отображаться код",
                        interactive=True,
                        height=350
                    )
                    
                    save_code_btn = gr.Button("Сохранить изменения")
                    
                    self.code_output = gr.Textbox(
                        label="Результат выполнения",
                        placeholder="Здесь будет отображаться результат выполнения кода",
                        lines=5,
                        max_lines=10,
                        interactive=False
                    )
            
            # Настройки модели
            with gr.Accordion("Настройки модели", open=False):
                with gr.Row():
                    model_name = gr.Textbox(
                        label="Название модели",
                        value=config.MODEL_NAME,
                        interactive=True
                    )
                    temperature_slider = gr.Slider(
                        label="Температура",
                        minimum=0.1,
                        maximum=1.0,
                        value=0.7,
                        step=0.1
                    )
                
                update_settings_btn = gr.Button("Обновить настройки")
            
            # Обработчики событий
            
            # Проверка статуса Ollama
            check_button.click(
                fn=self.check_ollama_status,
                outputs=[self.status_box]
            )
            
            # Отправка сообщения
            self.submit_btn.click(
                fn=self.chat,
                inputs=[self.msg_box],
                outputs=[self.chatbot_ui, self.msg_box, self.files_dropdown]
            )
            
            # Отправка сообщения по нажатию Enter (с Shift+Enter для новой строки)
            self.msg_box.submit(
                fn=self.chat,
                inputs=[self.msg_box],
                outputs=[self.chatbot_ui, self.msg_box, self.files_dropdown]
            )
            
            # Очистка чата
            clear_btn.click(
                fn=self.clear_chat,
                outputs=[self.chatbot_ui]
            )
            
            # Очистка памяти
            memory_clear_btn.click(
                fn=self.clear_memory,
                outputs=[self.status_box]
            )
            
            # Обновление списка файлов
            self.files_dropdown.change(
                fn=lambda x: x,
                inputs=[self.files_dropdown],
                outputs=[self.files_dropdown]
            )
            
            # Просмотр файла
            view_file_btn.click(
                fn=self.view_file,
                inputs=[self.files_dropdown],
                outputs=[self.code_display]
            )
            
            # Выполнение файла
            run_file_btn.click(
                fn=self.run_file,
                inputs=[self.files_dropdown],
                outputs=[self.code_output]
            )
            
            # Удаление файла
            delete_file_btn.click(
                fn=self.delete_file,
                inputs=[self.files_dropdown],
                outputs=[self.files_dropdown, self.status_box]
            )
            
            # Сохранение изменений в коде
            save_code_btn.click(
                fn=self.save_code,
                inputs=[self.files_dropdown, self.code_display],
                outputs=[self.status_box]
            )
            
            # Обновление настроек модели
            update_settings_btn.click(
                fn=self.update_settings,
                inputs=[model_name, temperature_slider],
                outputs=[self.status_box]
            )
            
            # Инициализация при запуске
            self.interface.load(
                fn=self.initialize,
                outputs=[self.status_box]
            )
    
    def initialize(self):
        """
        Инициализация чат-бота при запуске интерфейса
        
        Returns:
            str: Статус инициализации
        """
        try:
            # Проверяем доступность Ollama
            if self.chatbot.ollama_client.check_model_availability():
                self.ollama_initialized = True
                return "✅ Ollama запущена, модель готова к использованию"
            else:
                return "⚠️ Ollama запущена, но модель не найдена. Используйте 'Проверить статус Ollama' для загрузки модели."
        except Exception as e:
            return f"❌ Ошибка при инициализации: {str(e)}"
    
    def check_ollama_status(self):
        """
        Проверка статуса Ollama и модели
        
        Returns:
            str: Статус Ollama и модели
        """
        try:
            # Проверяем доступность Ollama
            models = self.chatbot.ollama_client.list_models()
            
            # Проверяем наличие нужной модели
            model_available = any(model['name'] == config.MODEL_NAME for model in models)
            
            if model_available:
                self.ollama_initialized = True
                return f"✅ Ollama запущена, модель {config.MODEL_NAME} готова к использованию"
            else:
                # Предлагаем загрузить модель
                try:
                    self.chatbot.ollama_client.pull_model()
                    self.ollama_initialized = True
                    return f"✅ Модель {config.MODEL_NAME} успешно загружена и готова к использованию"
                except Exception as e:
                    return f"⚠️ Не удалось загрузить модель: {str(e)}"
        except Exception as e:
            return f"❌ Ошибка при проверке статуса Ollama: {str(e)}"
    
    def chat(self, message):
        """
        Обработка сообщения пользователя
        
        Args:
            message: Сообщение пользователя
            
        Returns:
            tuple: (обновленный чат, пустое поле ввода, обновленный список файлов)
        """
        # Проверяем, что сообщение не пустое
        if not message or message.strip() == "":
            return self.chatbot_ui, "", self.get_code_files()
        
        # Проверяем инициализацию Ollama
        if not self.ollama_initialized:
            status = self.check_ollama_status()
            if not self.ollama_initialized:
                self.chatbot_ui.append((message, f"⚠️ Ollama не инициализирована. {status}"))
                return self.chatbot_ui, "", self.get_code_files()
        
        # Получаем ответ от чат-бота
        try:
            response = self.chatbot.get_chat_response(message)
            
            # Добавляем сообщение и ответ в интерфейс
            self.chatbot_ui.append((message, response))
            
            # Обновляем список файлов
            files = self.get_code_files()
            
            return self.chatbot_ui, "", files
        except Exception as e:
            error_message = f"❌ Произошла ошибка: {str(e)}"
            self.chatbot_ui.append((message, error_message))
            return self.chatbot_ui, "", self.get_code_files()
    
    def clear_chat(self):
        """
        Очистка чата
        
        Returns:
            list: Пустой список сообщений
        """
        return []
    
    def clear_memory(self):
        """
        Очистка памяти чат-бота
        
        Returns:
            str: Статус операции
        """
        try:
            self.chatbot.clear_memory()
            return "✅ Память успешно очищена"
        except Exception as e:
            return f"❌ Ошибка при очистке памяти: {str(e)}"
    
    def get_code_files(self):
        """
        Получение списка файлов с кодом
        
        Returns:
            list: Список имен файлов
        """
        try:
            return self.chatbot.code_manager.list_code_files()
        except Exception:
            return []
    
    def view_file(self, file_name):
        """
        Просмотр содержимого файла
        
        Args:
            file_name: Имя файла
            
        Returns:
            str: Содержимое файла
        """
        if not file_name:
            return "# Выберите файл для просмотра"
        
        try:
            content = self.chatbot.code_manager.read_code_from_file(file_name)
            return content
        except Exception as e:
            return f"# Ошибка при чтении файла: {str(e)}"
    
    def run_file(self, file_name):
        """
        Выполнение кода из файла
        
        Args:
            file_name: Имя файла
            
        Returns:
            str: Результат выполнения
        """
        if not file_name:
            return "Выберите файл для выполнения"
        
        try:
            # Определяем язык по расширению файла
            language = file_name.split('.')[-1] if '.' in file_name else "python"
            
            # Читаем код из файла
            code = self.chatbot.code_manager.read_code_from_file(file_name)
            
            # Выполняем код
            result = self.chatbot.code_manager.execute_code(code, language)
            
            return result
        except Exception as e:
            return f"Ошибка при выполнении файла: {str(e)}"
    
    def delete_file(self, file_name):
        """
        Удаление файла
        
        Args:
            file_name: Имя файла
            
        Returns:
            tuple: (обновленный список файлов, статус операции)
        """
        if not file_name:
            return self.get_code_files(), "Выберите файл для удаления"
        
        try:
            success = self.chatbot.code_manager.delete_code_file(file_name)
            
            if success:
                return self.get_code_files(), f"✅ Файл {file_name} успешно удален"
            else:
                return self.get_code_files(), f"❌ Файл {file_name} не найден"
        except Exception as e:
            return self.get_code_files(), f"❌ Ошибка при удалении файла: {str(e)}"
    
    def save_code(self, file_name, code):
        """
        Сохранение изменений в коде
        
        Args:
            file_name: Имя файла
            code: Новое содержимое файла
            
        Returns:
            str: Статус операции
        """
        if not file_name:
            return "Выберите файл для сохранения"
        
        try:
            self.chatbot.code_manager.save_code_to_file(code, file_name)
            return f"✅ Файл {file_name} успешно сохранен"
        except Exception as e:
            return f"❌ Ошибка при сохранении файла: {str(e)}"
    
    def update_settings(self, model_name, temperature):
        """
        Обновление настроек модели
        
        Args:
            model_name: Название модели
            temperature: Температура генерации
            
        Returns:
            str: Статус операции
        """
        try:
            # Обновляем название модели
            if model_name != config.MODEL_NAME:
                config.MODEL_NAME = model_name
                self.chatbot.ollama_client.model_name = model_name
                self.ollama_initialized = False  # Требуется повторная инициализация
            
            # Обновляем температуру (для будущих запросов)
            # Здесь можно добавить сохранение температуры в конфигурацию
            
            return f"✅ Настройки обновлены: модель={model_name}, температура={temperature}"
        except Exception as e:
            return f"❌ Ошибка при обновлении настроек: {str(e)}"
    
    def launch(self, share=False):
        """
        Запуск веб-интерфейса
        
        Args:
            share: Флаг для создания публичной ссылки
        """
        self.interface.launch(share=share)


if __name__ == "__main__":
    # Создаем и запускаем интерфейс
    interface = ChatBotInterface()
    interface.launch()
