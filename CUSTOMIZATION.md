# Руководство по кастомизации Elcoder

В этом руководстве описаны способы изменения интерфейса Elcoder, с сохранением функциональности бэкенда.

## Содержание

1. [Изменение стилей CSS](#изменение-стилей-css)
2. [Модификация Gradio-интерфейса](#модификация-gradio-интерфейса)
3. [Полное разделение frontend и backend](#полное-разделение-frontend-и-backend)
4. [Замена модели](#замена-модели)
5. [Настройка системного промпта](#настройка-системного-промпта)
6. [Примеры кастомизации](#примеры-кастомизации)

## Изменение стилей CSS

Самый простой способ изменить внешний вид Elcoder — это модифицировать CSS стили.

### Редактирование файла CSS

1. Запустите Elcoder хотя бы один раз с кастомным интерфейсом:
   ```bash
   python run.py --ui custom
   ```
   
2. Найдите и отредактируйте файл `assets/custom.css`

3. Примеры изменений:

   ```css
   /* Изменение цветовой схемы */
   :root {
       --primary-color: #8b5cf6;    /* Фиолетовый вместо синего */
       --secondary-color: #7c3aed;
       --background-color: #f8fafc;
       --text-color: #1e293b;
   }

   /* Изменение заголовка */
   .main-header {
       background: linear-gradient(90deg, #8b5cf6, #7c3aed);
       padding: 2rem;
       border-radius: 1rem;
   }

   /* Изменение стиля сообщений */
   .user-message {
       background-color: #ddd6fe;
       border-left: 4px solid var(--primary-color);
   }

   .bot-message {
       background-color: #f1f5f9;
       border-left: 4px solid var(--secondary-color);
   }
   ```

4. Перезапустите Elcoder, чтобы применить изменения

## Модификация Gradio-интерфейса

Для более глубоких изменений UI, вы можете модифицировать интерфейс в файле `custom_ui.py`.

### Изменение структуры интерфейса

Пример добавления новой вкладки:

```python
# В функции build_custom_interface
with gr.Tabs(elem_classes="tab-nav") as tabs:
    # Существующие вкладки
    with gr.TabItem("💬 Чат", id="chat"):
        # Содержимое вкладки чата
    
    # Новая вкладка для статистики
    with gr.TabItem("📊 Статистика", id="stats"):
        with gr.Row():
            gr.Markdown("### Статистика использования")
            stats_refresh = gr.Button("Обновить")
        
        with gr.Row():
            stats_output = gr.JSON(label="Данные")
            
        def get_stats():
            # Логика получения статистики
            return {"сообщений": 100, "файлов_создано": 25}
            
        stats_refresh.click(get_stats, outputs=[stats_output])
```

### Изменение компонентов

```python
# Изменение стиля для компонента чата
chatbot = gr.Chatbot(
    elem_id="chatbot",
    elem_classes="chatbot-container elcoder-chat",
    height=600,  # Увеличение высоты
    avatar_images=["assets/user.png", "assets/elcoder.png"],  # Добавление аватаров
    bubble_full_width=False,  # Отключение полной ширины пузырьков
)

# Изменение кнопок
submit = gr.Button(
    "Отправить",
    elem_classes="primary elcoder-button",
    scale=1,
    variant="primary",
    size="lg"  # Увеличение размера
)
```

## Полное разделение frontend и backend

Для максимальной гибкости можно использовать API-интерфейс и создать полностью отдельный фронтенд.

### 1. Запуск API-сервера

```bash
python api.py
```

API будет доступен по адресу `http://localhost:8000`.

### 2. Создание frontend на React/Vue/Angular

Пример компонента на React:

```jsx
import React, { useState, useEffect } from 'react';
import './ElcoderChat.css';

const API_URL = 'http://localhost:8000';

function ElcoderChat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  
  const sendMessage = async () => {
    if (!input.trim()) return;
    
    const userMessage = { role: 'user', content: input };
    setMessages([...messages, userMessage]);
    setInput('');
    setLoading(true);
    
    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: input,
          history: messages.map(m => [m.content, m.response || null])
        })
      });
      
      const data = await response.json();
      setMessages(messages => [...messages.slice(0, -1), { 
        ...userMessage, 
        response: data.response 
      }]);
    } catch (error) {
      console.error("Error:", error);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="elcoder-chat">
      <div className="messages">
        {messages.map((msg, i) => (
          <div key={i}>
            <div className="user-message">{msg.content}</div>
            {msg.response && <div className="bot-message">{msg.response}</div>}
          </div>
        ))}
        {loading && <div className="loading">Thinking...</div>}
      </div>
      
      <div className="input-area">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyPress={e => e.key === "Enter" && sendMessage()}
          placeholder="Задайте вопрос по программированию..."
        />
        <button onClick={sendMessage}>Отправить</button>
      </div>
    </div>
  );
}

export default ElcoderChat;
```

## Замена модели

Вы можете заменить используемую модель для Elcoder:

1. Загрузите новую модель через Ollama:
   ```bash
   ollama pull codellama:7b-instruct-q4_K_M
   ```

2. Укажите модель при запуске:
   ```bash
   python run.py --model codellama:7b-instruct-q4_K_M
   ```

3. Или измените параметр в `config.py`:
   ```python
   MODEL_NAME = "codellama:7b-instruct-q4_K_M"
   ```

## Настройка системного промпта

Для изменения поведения Elcoder вы можете настроить системный промпт в файле `enhanced_chatbot.py`:

```python
CODING_PROMPT_TEMPLATE = """
Ты - Elcoder, полезный ассистент по программированию на основе DeepSeek-coder. 
Твоя цель - помогать пользователю решать задачи программирования, объяснять концепции кода и предлагать оптимальные решения.
Твой ответ должен быть точным, полезным и следовать лучшим практикам программирования.

Когда пользователь просит написать код:
1. Пиши чистый, понятный и хорошо организованный код
2. Добавляй комментарии к сложным участкам
3. Объясняй принципы работы кода

История разговора:
{history}

Пользователь: {input}
Elcoder:"""
```

## Примеры кастомизации

### Пример 1: Темная тема

Создайте файл `dark_theme.py`:

```python
import gradio as gr
import os
from custom_ui import build_custom_interface, create_custom_css

# Переопределение функции создания CSS
def create_dark_theme_css():
    css_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "dark_theme.css")
    
    with open(css_file, "w", encoding="utf-8") as f:
        f.write("""
        :root {
            --primary-color: #8b5cf6;
            --secondary-color: #7c3aed;
            --background-color: #111827;
            --text-color: #e5e7eb;
            --border-color: #374151;
            --success-color: #10b981;
            --error-color: #ef4444;
        }
        
        body {
            background-color: var(--background-color);
            color: var(--text-color);
        }
        
        .main-header {
            background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        }
        
        /* Дополнительные стили... */
        """)
    
    return css_file

def build_dark_theme_interface():
    css_file = create_dark_theme_css()
    
    # Возьмем оригинальную реализацию интерфейса
    interface = build_custom_interface()
    
    # Заменим CSS файл
    interface.css_path = css_file
    
    return interface

if __name__ == "__main__":
    interface = build_dark_theme_interface()
    interface.launch()
```

### Пример 2: Добавление экспорта сессии

Добавление новой функции в `enhanced_chatbot.py`:

```python
def export_session(self, format="markdown"):
    """
    Экспорт текущей сессии в файл
    
    Args:
        format (str): Формат экспорта ('markdown', 'html', 'txt')
        
    Returns:
        str: Путь к созданному файлу
    """
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"elcoder_session_{timestamp}.{format}"
    file_path = os.path.join(config.FILES_DIR, filename)
    
    # Получение сообщений из памяти
    messages = self.memory.chat_memory.messages
    
    with open(file_path, 'w', encoding='utf-8') as f:
        if format == "markdown":
            f.write("# Elcoder Session Export\n\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for msg in messages:
                if msg.type == "human":
                    f.write(f"## User\n\n{msg.content}\n\n")
                else:
                    f.write(f"## Elcoder\n\n{msg.content}\n\n")
                    
        elif format == "html":
            # HTML экспорт
            # ...
        else:
            # Текстовый экспорт
            # ...
    
    return file_path
```

Добавление кнопки экспорта в `custom_ui.py`:

```python
with gr.Row():
    clear = gr.Button("Очистить чат", elem_classes="secondary")
    export_btn = gr.Button("Экспорт сессии", elem_classes="secondary")
    
def export_session_callback():
    file_path = bot.export_session()
    return f"Сессия экспортирована в {file_path}"

export_btn.click(export_session_callback, outputs=[gr.Textbox(label="Результат")])
```

Эти примеры показывают, как можно расширять и изменять функциональность Elcoder, добавляя новые возможности и изменяя интерфейс пользователя.
