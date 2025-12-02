# routes/dashboard.py (С русскими названиями)
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import inspect
from sqlalchemy.orm import Session
from models.database import engine, get_db
import models.tables as tables
from models.tables import Base
from core.mapping import get_russian_name # <--- ИМПОРТ ФУНКЦИИ ПЕРЕВОДА

templates = Jinja2Templates(directory="templates")

router = APIRouter(
    tags=["Панель управления"],
)

def get_all_model_tables():
    """Возвращает список всех таблиц, определенных в схеме, с русскими названиями."""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    # Переводим технические имена в русские
    translated_tables = [
        {"technical_name": name, "russian_name": get_russian_name(name, 'table')}
        for name in existing_tables
    ]
    return translated_tables

def get_model_class_by_table_name(table_name: str):
    """Динамически находит класс модели SQLAlchemy по имени таблицы."""
    for mapper in Base.registry.mappers:
        cls = mapper.class_
        if hasattr(cls, '__tablename__') and cls.__tablename__ == table_name:
            return cls
    return None

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    """
    Основная страница панели управления, отображающая список таблиц БД.
    """
    tables_list = get_all_model_tables() # <--- Используем список с русскими названиями
    
    return templates.TemplateResponse(
        "dashboard.html", 
        {
            "request": request,
            "tables": tables_list,
            "employee_login": "admin"
        }
    )

# Роут для просмотра содержимого таблицы
@router.get("/dashboard/table/{table_name}", response_class=HTMLResponse)
async def table_view(
    table_name: str, 
    request: Request, 
    db: Session = Depends(get_db)
):
    """
    Роут для отображения содержимого конкретной таблицы.
    """
    
    ModelClass = get_model_class_by_table_name(table_name)
    russian_table_name = get_russian_name(table_name, 'table') # <--- Получаем русское название таблицы

    if ModelClass is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Таблица '{table_name}' не найдена или не имеет соответствующей ORM-модели."
        )

    # 1. Получаем столбцы и переводим их
    column_names = []
    # Названия, которые будут отображаться пользователю
    display_column_names = [] 
    
    for column in inspect(ModelClass).mapper.columns:
        technical_name = column.key
        column_names.append(technical_name)
        # 💡 Переводим техническое имя столбца в русское
        display_column_names.append(get_russian_name(technical_name, 'column')) 
    
    # 2. Получаем данные (логика запроса остается прежней)
    try:
        query = db.query(ModelClass).limit(50)
        records = query.all()
        
        data = []
        for record in records:
            row = {}
            for col_name in column_names:
                value = getattr(record, col_name)
                # Преобразуем None в строку 'NULL' для отображения
                row[col_name] = value if value is not None else 'NULL' 
            data.append(row)
            
        total_rows = db.query(ModelClass).count() 

    except Exception as e:
        print(f"Ошибка при запросе данных таблицы {table_name}: {e}")
        display_column_names = ["Ошибка"]
        data = []
        total_rows = 0

    # 3. Рендерим шаблон
    return templates.TemplateResponse(
        "table_view.html", 
        {
            "request": request,
            "table_name": table_name,
            "russian_table_name": russian_table_name, # Передаем русское название таблицы
            "column_names": column_names, # Технические имена (нужны для доступа к данным в строке)
            "display_column_names": display_column_names, # Имена для отображения в заголовке
            "data": data,                 
            "total_rows": total_rows,     
        }
    )