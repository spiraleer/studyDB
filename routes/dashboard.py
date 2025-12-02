# routes/dashboard.py (Реальный вывод данных таблицы)
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session
from models.database import engine, get_db
# Импортируем все модели из tables.py для динамического доступа
import models.tables as tables 
from models.tables import Base # Нужна для динамического доступа к моделям

templates = Jinja2Templates(directory="templates")

router = APIRouter(
    tags=["Панель управления"],
)

def get_all_model_tables():
    """Возвращает список всех таблиц, определенных в схеме."""
    inspector = inspect(engine)
    # Получаем имена всех существующих таблиц в БД
    return inspector.get_table_names()

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
    tables = get_all_model_tables()
    
    return templates.TemplateResponse(
        "dashboard.html", 
        {
            "request": request,
            "tables": tables,
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

    if ModelClass is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Таблица '{table_name}' не найдена или не имеет соответствующей ORM-модели."
        )

    # 1. Получаем столбцы (заголовки)
    # Используем названия атрибутов модели
    column_names = [column.key for column in inspect(ModelClass).mapper.columns]
    
    # 2. Получаем данные
    try:
        # Выполняем простой запрос SELECT *
        # Ограничиваем 50 строками, чтобы не нагружать браузер и БД
        query = db.query(ModelClass).limit(50)
        records = query.all()
        
        # Преобразуем записи в список словарей для удобной передачи в шаблон
        data = []
        for record in records:
            row = {}
            for col_name in column_names:
                # Получаем значение атрибута. Для дат, JSON и т.д. может потребоваться форматирование,
                # но пока оставляем как есть.
                value = getattr(record, col_name)
                # Преобразуем None в строку 'NULL' для отображения
                row[col_name] = value if value is not None else 'NULL' 
            data.append(row)
            
        total_rows = db.query(ModelClass).count() # Подсчитываем общее количество строк

    except Exception as e:
        # Если что-то пошло не так (например, таблица пуста или ошибка SQL)
        print(f"Ошибка при запросе данных таблицы {table_name}: {e}")
        column_names = ["Ошибка"]
        data = [[f"Не удалось загрузить данные: {str(e)}"]]
        total_rows = 0

    # 3. Рендерим шаблон
    return templates.TemplateResponse(
        "table_view.html", 
        {
            "request": request,
            "table_name": table_name,
            "column_names": column_names, # Заголовки
            "data": data,                 # Данные
            "total_rows": total_rows,     # Общее количество
        }
    )