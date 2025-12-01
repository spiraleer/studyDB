# app.py
import os
from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os

# Загружаем переменные окружения из .env файла
load_dotenv()

# Создаем экземпляр FastAPI
app = FastAPI(
    title="Warehouse Management System",
    description="Система управления складом и продажами",
    version="1.0.0",
    docs_url="/api/docs" if os.getenv("DEBUG", "False").lower() == "true" else None,
    redoc_url="/api/redoc" if os.getenv("DEBUG", "False").lower() == "true" else None
)

# Настройка CORS (если нужно)
if os.getenv("DEBUG", "False").lower() == "true":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Создаем папки если их нет
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)

# Настройка шаблонов
templates = Jinja2Templates(directory="templates")

# Подключаем статические файлы (если будут CSS/JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Импортируем модели и зависимости (позже добавим)
# from models.database import get_db
# from models.tables import ...

# Главная страница
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Главная страница приложения.
    """
    return templates.TemplateResponse("index.html", {"request": request})

# Эндпоинт для проверки здоровья приложения
@app.get("/health")
async def health_check():
    """
    Проверка состояния приложения и подключения к БД.
    """
    try:
        # Здесь позже добавим проверку подключения к БД
        return {
            "status": "healthy",
            "service": "Warehouse Management System",
            "version": "1.0.0",
            "environment": os.getenv("ENVIRONMENT", "development")
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

# Эндпоинт для информации о конфигурации (только для разработки)
@app.get("/api/config")
async def get_config():
    """
    Возвращает текущую конфигурацию приложения (без паролей).
    Только для режима разработки!
    """
    if os.getenv("ENVIRONMENT") != "development":
        return {"error": "Not available in production"}
    
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        # Безопасно показываем только первые 20 символов
        masked_url = database_url[:20] + "..."
    else:
        masked_url = None
    
    return {
        "environment": os.getenv("ENVIRONMENT"),
        "debug": os.getenv("DEBUG"),
        "database_url": masked_url,
        "token_expire_minutes": os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    }

# Импортируем маршруты (позже добавим)
# from routes.auth import router as auth_router
# from routes.dashboard import router as dashboard_router

# Подключаем маршруты
# app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
# app.include_router(dashboard_router, prefix="/api/dashboard", tags=["dashboard"])

# Обработчик 404 ошибки
@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc):
    """
    Обработчик для 404 ошибок.
    """
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

if __name__ == "__main__":
    import uvicorn
    
    # Запуск сервера
    host = "0.0.0.0"
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=os.getenv("DEBUG", "False").lower() == "true",
        log_level="info"
    )