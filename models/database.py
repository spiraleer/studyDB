# models/database.py
import os
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Получаем URL базы данных из переменных окружения
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # fallback для тестирования
    DATABASE_URL = "postgresql://test:test@localhost:5432/test_db"
    print(f"⚠️ DATABASE_URL не установлен, используем: {DATABASE_URL[:30]}...")

# Для psycopg3 нужно изменить URL
if DATABASE_URL.startswith("postgresql://"):
    # Заменяем postgresql:// на postgresql+psycopg:// для psycopg3
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

print(f"🔗 Используем DSN: {DATABASE_URL[:50]}...")

# Создаем движок SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Проверяет соединение перед использованием
    pool_recycle=300,    # Переподключается каждые 300 секунд
    echo=os.getenv("DEBUG", "False").lower() == "true"  # Логирование SQL запросов в debug режиме
)

# Создаем фабрику сессий
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Базовый класс для моделей
Base = declarative_base()

# Зависимость для получения сессии БД
def get_db() -> Generator[Session, None, None]:
    """
    Возвращает сессию базы данных.
    Используется как зависимость в эндпоинтах FastAPI.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Функция для проверки подключения к БД
def check_database_connection() -> dict:
    """
    Проверяет подключение к базе данных.
    Возвращает словарь с результатом проверки.
    """
    try:
        # Пытаемся подключиться к БД
        with engine.connect() as connection:
            # Выполняем простой запрос с text()
            result = connection.execute(text("SELECT version()")).fetchone()
            
            # Получаем версию PostgreSQL
            postgres_version = result[0] if result else "Неизвестно"
            
            return {
                "connected": True,
                "status": "connected",
                "database_version": postgres_version,
                "message": "Подключение к базе данных успешно установлено",
                "driver": "psycopg3"
            }
            
    except Exception as e:
        return {
            "connected": False,
            "status": "disconnected",
            "database_version": None,
            "message": f"Ошибка подключения к базе данных: {str(e)}",
            "error_details": str(e),
            "driver": "psycopg3"
        }

# Функция для создания таблиц (используется при первом запуске)
def create_tables():
    """
    Создает все таблицы в базе данных на основе моделей.
    Внимание: Используйте аккуратно в production!
    """
    try:
        Base.metadata.create_all(bind=engine)
        return {"success": True, "message": "Таблицы успешно созданы"}
    except Exception as e:
        return {"success": False, "message": f"Ошибка создания таблиц: {str(e)}"}