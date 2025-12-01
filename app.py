# app.py (обновляем health эндпоинт и добавляем импорты)
import os
from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Импортируем функции для работы с БД
from models.database import check_database_connection, get_db

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
        # Проверяем подключение к БД
        db_status = check_database_connection()
        
        # Общий статус приложения
        app_healthy = db_status["connected"]
        
        return {
            "status": "healthy" if app_healthy else "unhealthy",
            "service": "Warehouse Management System",
            "version": "1.0.0",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "database": db_status,
            "timestamp": os.path.getmtime(__file__) if os.path.exists(__file__) else None
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "service": "Warehouse Management System",
                "error": str(e),
                "timestamp": os.path.getmtime(__file__) if os.path.exists(__file__) else None
            }
        )

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
        "token_expire_minutes": os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"),
        "algorithm": os.getenv("ALGORITHM")
    }

# Эндпоинт для проверки только базы данных
@app.get("/api/db-check")
async def db_check():
    """
    Проверка подключения к базе данных.
    """
    return check_database_connection()

# Обработчик 404 ошибки
@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc):
    """
    Обработчик для 404 ошибок.
    """
    return templates.TemplateResponse(
        "404.html", 
        {"request": request, "error": "Страница не найдена"}, 
        status_code=404
    )

# Заглушка для 404 страницы (создадим позже)
@app.get("/404")
async def test_404(request: Request):
    return templates.TemplateResponse(
        "404.html", 
        {"request": request, "error": "Тестовая 404 ошибка"}, 
        status_code=404
    )

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