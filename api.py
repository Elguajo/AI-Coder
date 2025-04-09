"""
API для интеграции Elcoder с внешними фронтендами
"""

from fastapi import FastAPI, HTTPException, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
import uvicorn
import logging
import os
import sys

# Добавляем текущую директорию в PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Импортируем наши модули
from enhanced_chatbot import EnhancedCodingChatBot
import config

# Настраиваем логгирование
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Создаем экземпляр FastAPI
app = FastAPI(
    title="Elcoder API",
    description="API для Elcoder - локального чат-бота для кодинга на основе DeepSeek-coder",
    version="1.0.0"
)

# Настраиваем CORS для доступа с фронтендов
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене лучше указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Создаем глобальный экземпляр чат-бота
bot = EnhancedCodingChatBot()

# Определяем модели данных
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[List[Optional[str]]]] = []

class ChatResponse(BaseModel):
    response: str

class FileRequest(BaseModel):
    filename: str
    content: Optional[str] = None

class FileResponse(BaseModel):
    filename: str
    content: str

class FileListResponse(BaseModel):
    files: List[str]

class ExecuteCodeRequest(BaseModel):
    code: str

class ExecuteCodeResponse(BaseModel):
    result: str

class StatusResponse(BaseModel):
    status: str
    model: str
    version: str

# Маршруты API
@app.get("/", response_model=StatusResponse)
async def root():
    """Получить статус API"""
    return {
        "status": "ok",
        "model": config.MODEL_NAME,
        "version": "1.0.0"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Отправить сообщение в чат и получить ответ Elcoder
    """
    try:
        logger.info(f"Получен запрос чата: {request.message[:50]}...")
        response = bot.chat(request.message, request.history)
        return {"response": response}
    except Exception as e:
        logger.error(f"Ошибка при обработке запроса чата: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files", response_model=FileListResponse)
async def list_files():
    """
    Получить список доступных файлов
    """
    try:
        files_str = bot.list_files()
        # Извлекаем только имена файлов из строки
        if "Нет доступных файлов" in files_str:
            files = []
        else:
            files_part = files_str.split(":\n")
            if len(files_part) > 1:
                files = files_part[1].split("\n")
            else:
                files = []
        
        return {"files": files}
    except Exception as e:
        logger.error(f"Ошибка при получении списка файлов: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files/{filename}", response_model=FileResponse)
async def read_file(filename: str):
    """
    Прочитать содержимое файла
    """
    try:
        content = bot.read_file(filename)
        if "Ошибка при чтении файла" in content:
            raise HTTPException(status_code=404, detail=f"Файл не найден: {filename}")
        return {"filename": filename, "content": content}
    except Exception as e:
        logger.error(f"Ошибка при чтении файла {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/files", status_code=201)
async def create_file(request: FileRequest):
    """
    Создать новый файл
    """
    try:
        if not request.filename:
            raise HTTPException(status_code=400, detail="Имя файла не указано")
        
        if request.content is None:
            raise HTTPException(status_code=400, detail="Содержимое файла не указано")
        
        result = bot.create_file(request.filename, request.content)
        if "Ошибка при создании файла" in result:
            raise HTTPException(status_code=500, detail=result)
        
        return {"result": result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при создании файла {request.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/execute", response_model=ExecuteCodeResponse)
async def execute_code(request: ExecuteCodeRequest):
    """
    Выполнить код Python
    """
    try:
        if not request.code:
            raise HTTPException(status_code=400, detail="Код не указан")
        
        result = bot.execute_code(request.code)
        return {"result": result}
    except Exception as e:
        logger.error(f"Ошибка при выполнении кода: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/export", status_code=200)
async def export_session(format: str = "markdown"):
    """
    Экспортировать текущую сессию
    """
    try:
        file_path = bot.export_session(format)
        return {"file_path": file_path}
    except Exception as e:
        logger.error(f"Ошибка при экспорте сессии: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """
    Проверка работоспособности API
    """
    return {"status": "healthy"}

@app.get("/config")
async def get_config():
    """
    Получить текущую конфигурацию
    """
    return {
        "model": config.MODEL_NAME,
        "temperature": config.TEMPERATURE,
        "max_tokens": config.MAX_TOKENS,
        "memory_size": config.MEMORY_SIZE
    }

def start_api(host: str = "127.0.0.1", port: int = 8000):
    """
    Запустить API сервер
    """
    logger.info(f"Запуск API сервера Elcoder на {host}:{port}")
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    print("""
    ███████╗██╗      ██████╗ ██████╗ ██████╗ ███████╗██████╗     █████╗ ██████╗ ██╗
    ██╔════╝██║     ██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔══██╗   ██╔══██╗██╔══██╗██║
    █████╗  ██║     ██║     ██║   ██║██║  ██║█████╗  ██████╔╝   ███████║██████╔╝██║
    ██╔══╝  ██║     ██║     ██║   ██║██║  ██║██╔══╝  ██╔══██╗   ██╔══██║██╔═══╝ ██║
    ███████╗███████╗╚██████╗╚██████╔╝██████╔╝███████╗██║  ██║██╗██║  ██║██║     ██║
    ╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝╚═╝     ╚═╝
    
    API сервер для Elcoder
    """)
    # Запуск API сервера
    start_api(host=config.SERVER_HOST, port=8000)
