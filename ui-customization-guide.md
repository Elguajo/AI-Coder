# Руководство по кастомизации UI чат-бота

В этом руководстве описаны лучшие способы изменения интерфейса (frontend) чат-бота, с сохранением всей функциональности бэкенда. Рассмотрим несколько подходов от простых до более сложных.

## Содержание

1. [Изменение стилей CSS](#изменение-стилей-css)
2. [Модификация Gradio-интерфейса](#модификация-gradio-интерфейса)
3. [Полное разделение frontend и backend](#полное-разделение-frontend-и-backend)
4. [Рекомендуемые подходы](#рекомендуемые-подходы)
5. [Примеры кастомизации](#примеры-кастомизации)

## Изменение стилей CSS

Самый простой способ изменить внешний вид — это модифицировать CSS стили. В нашем проекте уже есть поддержка кастомных стилей.

### Редактирование существующих стилей

1. Откройте файл `assets/custom.css` (он создается при первом запуске)
2. Измените стили по вашему желанию
3. Перезапустите приложение, чтобы увидеть изменения

Пример изменения цветовой схемы:

```css
:root {
    --primary-color: #3b82f6;  /* Изменение на синий */
    --secondary-color: #1d4ed8;
    --background-color: #f8fafc;
    --text-color: #1e293b;
}

/* Изменение стиля заголовка */
.main-header {
    background: linear-gradient(90deg, #3b82f6, #1d4ed8);
    padding: 2rem;
}
```

### Добавление новых стилей

Вы можете добавить новые стили для элементов интерфейса:

```css
/* Анимация кнопок */
button.primary {
    transition: transform 0.2s, box-shadow 0.2s !important;
}

button.primary:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
}

/* Стилизация сообщений в чате */
.user-message {
    border-left: 4px solid var(--primary-color) !important;
}

.bot-message {
    border-left: 4px solid var(--secondary-color) !important;
}
```

## Модификация Gradio-интерфейса

Для более глубоких изменений UI, вы можете модифицировать сам интерфейс Gradio.

### Изменение структуры интерфейса

1. Откройте файл `custom_ui.py`
2. Измените структуру интерфейса по вашему желанию

Пример добавления нового компонента:

```python
# В функции build_custom_interface
with gr.Tabs(elem_classes="tab-nav") as tabs:
    # Существующие вкладки...
    
    # Добавляем новую вкладку
    with gr.TabItem("📊 Статистика", id="stats"):
        with gr.Row():
            gr.Markdown("### Статистика использования")
            stats_refresh = gr.Button("Обновить")
        
        with gr.Row():
            stats_output = gr.JSON(label="Данные")
            
        def get_stats():
            # Логика получения статистики
            return {"total_messages": 100, "files_created": 25}
            
        stats_refresh.click(get_stats, outputs=[stats_output])
```

### Изменение компонентов

Вы можете настроить внешний вид и поведение существующих компонентов:

```python
# Изменение chatbot компонента
chatbot = gr.Chatbot(
    elem_id="chatbot",
    elem_classes="chatbot-container",
    height=600,  # Увеличение высоты
    avatar_images=["assets/user.png", "assets/bot.png"],  # Добавление аватаров
    bubble_full_width=False,  # Отключение полной ширины пузырьков
)

# Изменение кнопок
submit = gr.Button(
    "Отправить",
    elem_classes="primary",
    scale=1,
    variant="primary",  # Использование встроенного варианта
    size="lg"  # Увеличение размера
)
```

## Полное разделение frontend и backend

Для максимальной гибкости можно полностью разделить frontend и backend. Это наиболее сложный, но и самый гибкий вариант.

### 1. Создание API

Сначала нужно обернуть логику бота в API:

```python
# api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from enhanced_chatbot import EnhancedCodingChatBot
import uvicorn

app = FastAPI()
bot = EnhancedCodingChatBot()

class ChatRequest(BaseModel):
    message: str
    history: list = []

class FileRequest(BaseModel):
    filename: str
    content: str = None

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        response = bot.chat(request.message, request.history)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files")
async def list_files():
    return {"files": bot.list_files()}

@app.get("/files/{filename}")
async def read_file(filename: str):
    content = bot.read_file(filename)
    return {"filename": filename, "content": content}

@app.post("/files")
async def create_file(request: FileRequest):
    result = bot.create_file(request.filename, request.content)
    return {"result": result}

@app.post("/execute")
async def execute_code(code: str):
    result = bot.execute_code(code)
    return {"result": result}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
```

### 2. Создание фронтенда

Теперь вы можете создать отдельный фронтенд, используя любую технологию (React, Vue, Angular и т.д.), который будет взаимодействовать с этим API.

Пример на React:

```jsx
// Упрощенный компонент чата
function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;
    
    const userMessage = { role: "user", content: input };
    setMessages([...messages, userMessage]);
    setInput("");
    setLoading(true);
    
    try {
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          message: input,
          history: messages.map(m => [m.content, m.response || null])
        })
      });
      
      const data = await response.json();
      setMessages(messages => [...messages, { 
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
    <div className="chat-container">
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
          placeholder="Ask something..."
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
}
```

## Рекомендуемые подходы

В зависимости от ваших потребностей, вот рекомендуемые подходы:

1. **Для небольших изменений внешнего вида**:
   - Используйте CSS-кастомизацию
   - Плюсы: простота, быстрое внедрение
   - Минусы: ограниченные возможности

2. **Для средних изменений структуры и функциональности**:
   - Модифицируйте Gradio-интерфейс
   - Плюсы: сохранение всей функциональности, достаточная гибкость
   - Минусы: ограничения экосистемы Gradio

3. **Для полной переработки UI**:
   - Разделите frontend и backend с помощью API
   - Плюсы: максимальная гибкость, возможность использовать любые технологии
   - Минусы: сложность разработки и поддержки, требуется больше времени

## Примеры кастомизации

### Пример 1: Темная тема

```python
# Создание нового файла dark_theme.py
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
        
        .chatbot-container {
            background-color: #1f2937;
            border-color: #374151;
        }
        
        .user-message {
            background-color: #3730a3;
            color: white;
        }
        
        .bot-message {
            background-color: #1f2937;
            color: white;
            border-left: 3px solid var(--primary-color);
        }
        
        /* И другие стили... */
        """)
    
    return css_file

# Модифицированная функция для построения интерфейса
def build_dark_theme_interface():
    # Использование вашего кастомного CSS
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

### Пример 2: Мобильная версия

```python
def build_mobile_interface():
    bot = EnhancedCodingChatBot()
    
    with gr.Blocks(title="Мобильный чат-бот для кодинга") as interface:
        gr.Markdown("# 📱 Чат-бот для кодинга")
        
        with gr.Accordion("ℹ️ Информация", open=False):
            gr.Markdown("Мобильная версия чат-бота на основе DeepSeek-coder")
        
        chatbot = gr.Chatbot(height=400)
        
        with gr.Row():
            msg = gr.Textbox(
                placeholder="Задайте вопрос...",
                container=False,
                scale=4
            )
            submit = gr.Button("➤", scale=1)
        
        with gr.Accordion("🔧 Файлы и код", open=False):
            with gr.Tabs():
                with gr.TabItem("📁 Файлы"):
                    filename_input = gr.Textbox(label="Имя файла")
                    with gr.Row():
                        list_btn = gr.Button("📋 Список")
                        read_btn = gr.Button("📖 Читать")
                        
                    file_content = gr.Code(language="python", lines=10)
                    save_btn = gr.Button("💾 Сохранить")
                    file_result = gr.Textbox(lines=3)
                
                with gr.TabItem("▶️ Код"):
                    code_input = gr.Code(language="python", lines=10)
                    run_btn = gr.Button("▶️ Запустить")
                    code_output = gr.Textbox(lines=5)
        
        # Вся функциональность связывания как в стандартном интерфейсе
        # ...
    
    return interface
```

Эти примеры показывают, как можно модифицировать интерфейс, сохраняя при этом всю логику бэкенда без необходимости повторной реализации функциональности бота.
