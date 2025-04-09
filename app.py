import gradio as gr
from langchain_community.chat_models import ChatOllama
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain.chains import LLMChain
import os
import time # Для имитации "печати"

# --- 1. Настройка LangChain ---

# Убедитесь, что Ollama запущена с моделью deepseek-coder
# Замените 'deepseek-coder' на имя вашей модели, если оно другое
LLM_MODEL = "deepseek-coder"
try:
    llm = ChatOllama(model=LLM_MODEL)
    # Пробный вызов для проверки доступности модели
    llm.invoke("Hello!")
    print(f"Модель '{LLM_MODEL}' успешно загружена через Ollama.")
except Exception as e:
    print(f"Ошибка при инициализации модели Ollama ('{LLM_MODEL}'): {e}")
    print("Пожалуйста, убедитесь, что Ollama запущена и модель '{LLM_MODEL}' доступна.")
    # Можно завершить выполнение или использовать заглушку
    llm = None # Указываем, что LLM недоступна

# Память для хранения истории диалога (последние K=5 пар сообщений)
memory = ConversationBufferWindowMemory(
    k=5,                # Количество запоминаемых пар сообщений (вопрос-ответ)
    return_messages=True, # Возвращать историю как список сообщений
    memory_key="history"  # Ключ для использования в промпте
)

# Промпт-шаблон: Инструкции для LLM
system_message = """You are a helpful AI coding assistant powered by DeepSeek-coder, named Elcoder.
Your goal is to assist users with programming tasks.
You can write code, explain code snippets, find bugs, refactor code, and discuss programming concepts.
If the user provides content from a file, use that content as context for their request.
Format code blocks clearly using Markdown (e.g., ```python ... ```).
Be concise and accurate in your responses."""

prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(system_message), # Системное сообщение (инструкция)
    MessagesPlaceholder(variable_name="history"),              # Место для вставки истории диалога
    HumanMessagePromptTemplate.from_template("{input}")        # Место для вставки текущего запроса пользователя (+ контент файла)
])

# Цепочка LangChain: Связывает LLM, Промпт и Память
if llm: # Создаем цепочку только если LLM доступна
    chain = LLMChain(
        llm=llm,
        prompt=prompt,
        memory=memory,
        verbose=True # Выводить подробную информацию о работе цепочки в консоль (полезно для отладки)
    )
else:
    chain = None # Цепочка недоступна, если LLM не загрузилась

# --- 2. Глобальные переменные для управления состоянием файла ---
# В простом локальном приложении это допустимо.
latest_file_content = None
latest_file_name = None

# --- 3. Функции для Gradio ---

def handle_file_upload(file_obj):
    """
    Обрабатывает загрузку файла пользователем.
    Читает содержимое файла и сохраняет его в глобальные переменные.
    Возвращает статусное сообщение для отображения пользователю.
    """
    global latest_file_content, latest_file_name
    if file_obj is not None:
        try:
            # file_obj в Gradio - это временный файл. Используем его имя.
            filepath = file_obj.name
            filename = os.path.basename(filepath) # Получаем только имя файла

            # Читаем содержимое файла
            with open(filepath, 'r', encoding='utf-8') as f:
                latest_file_content = f.read()
            latest_file_name = filename

            print(f"Файл '{latest_file_name}' успешно загружен. Размер: {len(latest_file_content)} байт.")
            # Предупреждение о размере файла (токены LLM ограничены)
            if len(latest_file_content) > 10000: # Примерный порог
                 return f"⚠️ Файл '{latest_file_name}' загружен, но он очень большой. Модель может не обработать весь контент."
            return f"✅ Файл '{latest_file_name}' загружен. Теперь вы можете задавать вопросы по его содержимому."

        except Exception as e:
            print(f"Ошибка чтения файла '{filepath}': {e}")
            latest_file_content = None
            latest_file_name = None
            return f"❌ Ошибка при чтении файла: {e}"
    else:
        # Если пользователь отменил выбор файла
        latest_file_content = None
        latest_file_name = None
        return "Файл не выбран или очищен."


def chat_logic(message, chat_history):
    """
    Основная логика чата. Вызывается при отправке сообщения пользователем.
    Формирует вход для LangChain, вызывает цепочку и возвращает ответ.
    """
    global latest_file_content, latest_file_name

    print(f"\n--- Новый запрос ---")
    print(f"Пользователь: {message}")
    # print(f"История до запроса: {chat_history}") # История передается Gradio

    # Проверяем, доступна ли LLM
    if not chain:
        return "Ошибка: Модель LLM не инициализирована. Проверьте запуск Ollama и доступность модели."

    input_for_chain = message

    # Если есть контент загруженного файла, добавляем его в начало запроса
    if latest_file_content:
        print(f"Добавляем контекст из файла: {latest_file_name}")
        file_context = f"Context from file '{latest_file_name}':\n```\n{latest_file_content}\n```\n\n"
        input_for_chain = file_context + f"User query: {message}"
        # Важно: Решите, нужно ли очищать файл после каждого использования.
        # Если оставить, он будет добавляться ко всем последующим запросам, пока не будет загружен новый файл или не нажата кнопка "Очистить".
        # Если раскомментировать строки ниже, файл будет использоваться только один раз:
        # latest_file_content = None
        # latest_file_name = None
        # print("Контекст файла использован и очищен для следующего запроса.")

    print(f"Полный вход для LLMChain:\n{input_for_chain[:500]}...") # Показываем начало входа для отладки

    try:
        # Вызываем цепочку LangChain (которая включает LLM и память)
        # .invoke ожидает словарь и возвращает словарь
        response = chain.invoke({"input": input_for_chain})
        bot_response = response['text'] # Извлекаем текст ответа
        print(f"Ответ LLM: {bot_response}")

    except Exception as e:
        print(f"Ошибка при вызове LLMChain: {e}")
        bot_response = f"Произошла ошибка при обработке вашего запроса: {e}"

    # Добавляем пару (запрос, ответ) в историю Gradio
    # chat_history.append((message, bot_response)) # Gradio сделает это автоматически

    # Имитация "печати" для лучшего UX (опционально)
    # full_response = ""
    # for chunk in bot_response:
    #     full_response += chunk
    #     time.sleep(0.01)
    #     yield full_response

    return bot_response # Возвращаем только ответ бота


def clear_chat_and_memory():
    """
    Очищает историю чата в Gradio, память LangChain и сбрасывает загруженный файл.
    """
    global latest_file_content, latest_file_name

    # Очистка памяти LangChain
    if memory:
        memory.clear()

    # Сброс глобальных переменных файла
    latest_file_content = None
    latest_file_name = None

    print("История чата, память LangChain и контекст файла очищены.")
    # Возвращаем пустую историю для Chatbot и пустую строку для Textbox + статус
    return [], "", "История и память очищены."

# --- 4. Создание интерфейса Gradio ---

with gr.Blocks(theme=gr.themes.Soft()) as demo: # Используем тему для лучшего вида
    gr.Markdown(
        f"""
        # 🤖 Elcoder: Ваш Локальный Помощник по Коду ({LLM_MODEL} + Ollama)
        Задавайте вопросы по программированию, вставляйте код или загружайте файлы для анализа.
        """
    )

    # Основной компонент чата
    chatbot = gr.Chatbot(
        label="Диалог с Elcoder",
        bubble_full_width=False, # Пузыри сообщений не на всю ширину
        height=500 # Высота области чата
        )

    with gr.Row(): # Располагаем элементы в ряд
        # Поле для ввода текста пользователя
        msg_textbox = gr.Textbox(
            label="Ваш запрос к Elcoder:",
            placeholder="Напишите ваш вопрос или вставьте код здесь...",
            lines=3, # Несколько строк для удобства ввода кода
            scale=7 # Занимает большую часть ряда
            )
        # Компонент для загрузки файла
        file_upload_button = gr.UploadButton(
                "📁 Загрузить файл",
                file_types=['.py', '.txt', '.md', '.json', '.csv', '.html', '.css', '.js', '.java', '.c', '.cpp', '.h', '.hpp', '.rs', '.go', '.php'], # Укажите нужные типы
                scale=1 # Занимает меньшую часть ряда
            )

    # Кнопка "Очистить диалог"
    clear_button = gr.Button("🧹 Очистить диалог и память")

    # Статусная строка для сообщений (например, об успешной загрузке файла)
    status_display = gr.Markdown("") # Используем Markdown для возможного форматирования

    # --- Связывание компонентов ---

    # 1. Обработка отправки сообщения (нажатие Enter в Textbox или клик по невидимой кнопке отправки)
    # Используем streaming для имитации печати (если раскомментировать yield в chat_logic)
    msg_textbox.submit(
        chat_logic,                 # Функция-обработчик
        [msg_textbox, chatbot],     # Входные данные: текущее сообщение и история чата
        [chatbot]                   # Выходные данные: обновленная история чата (постепенно, если yield)
    ).then(lambda: "", None, [msg_textbox], queue=False) # Очищаем текстовое поле после отправки

    # 2. Обработка загрузки файла
    file_upload_button.upload(
        handle_file_upload,         # Функция-обработчик
        [file_upload_button],       # Входные данные: объект загруженного файла
        [status_display],           # Выходные данные: сообщение о статусе загрузки
        queue=False
    )

    # 3. Обработка нажатия кнопки "Очистить"
    clear_button.click(
        clear_chat_and_memory,      # Функция-обработчик
        [],                         # Нет входных данных
        [chatbot, msg_textbox, status_display], # Выходные данные: очищенный чат, пустое поле ввода, сообщение о статусе
        queue=False
    )

# --- 5. Запуск приложения ---
if __name__ == "__main__":
    print("Запуск Gradio приложения Elcoder...")
    if not llm or not chain:
         print("\n*** ПРЕДУПРЕЖДЕНИЕ: LLM или LangChain не инициализированы! Функциональность будет ограничена. ***\n")

    # Запуск веб-сервера Gradio
    demo.launch(server_name="0.0.0.0") # Доступно в локальной сети, используйте "127.0.0.1" только для локального доступа
    # demo.launch() # Только локальный доступ по умолчанию
