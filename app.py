# app.py (обновляем health эндпоинт и добавляем импорты)
import os
from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from sqlalchemy import inspect
from routes import dashboard
from routes import dashboard, auth
from routes import categories
from routes import products
from routes import orders
from routes import customers
from routes import suppliers
from routes import employees
from routes import purchases
from routes import audit
from routes import payments
from routes import price_history
from routes import stock_movements

# Импортируем функции для работы с БД
from models.database import check_database_connection, get_db, create_tables, engine
from models.tables import Base

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

app.include_router(dashboard.router)
app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(customers.router)
app.include_router(suppliers.router)
app.include_router(employees.router)
app.include_router(purchases.router)
app.include_router(audit.router)
app.include_router(payments.router)
app.include_router(price_history.router)
app.include_router(stock_movements.router)

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

# Эндпоинт для создания таблиц (ТОЛЬКО ДЛЯ РАЗРАБОТКИ!)
@app.get("/api/init-db")
async def init_database():
    """
    Создает таблицы в базе данных.
    ВНИМАНИЕ: Использовать только при первом запуске или в разработке!
    """
    if os.getenv("ENVIRONMENT") != "development":
        return {"error": "Эта функция доступна только в режиме разработки"}
    
    result = create_tables()
    return result

# Эндпоинт для проверки существования таблиц
@app.get("/api/check-tables")
async def check_tables():
    """
    Проверяет какие таблицы существуют в базе данных.
    """
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    # Проверяем наличие основных таблиц
    expected_tables = [
        'role', 'employee', 'permission', 'role_permission',
        'category', 'customer', 'supplier', 'product',
        'orders', 'orders_item', 'payment', 'purchase',
        'purchase_item', 'price_history', 'stock_movement',
        'audit_log', 'user_session'
    ]
    
    missing_tables = [table for table in expected_tables if table not in tables]
    
    return {
        "total_tables": len(tables),
        "existing_tables": tables,
        "missing_tables": missing_tables,
        "all_tables_exist": len(missing_tables) == 0
    }

# Страница входа в систему
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """
    Страница авторизации пользователей.
    """
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    return templates.TemplateResponse("settings.html", {"request": request})

@app.get("/audit", response_class=HTMLResponse)
async def audit_page(request: Request):
    return templates.TemplateResponse("audit.html", {"request": request})

@app.get("/docs", response_class=HTMLResponse)
async def api_docs_page(request: Request):
    return templates.TemplateResponse("api_docs.html", {"request": request})

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