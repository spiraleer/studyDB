# routes/dashboard.py — ИСПРАВЛЕННАЯ ВЕРСИЯ
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import inspect
from sqlalchemy.orm import Session
from models.database import engine, get_db
from core.mapping import get_russian_name
from dependencies import require_permission
from core.permissions import PermissionCode

templates = Jinja2Templates(directory="templates")
router = APIRouter(tags=["Панель управления"])

# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ (оставь как было)
def get_all_model_tables():
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    return [
        {"technical_name": name, "russian_name": get_russian_name(name, 'table')}
        for name in existing_tables
    ]

def get_model_class_by_table_name(table_name: str):
    from models.tables import Base
    for mapper in Base.registry.mappers:
        cls = mapper.class_
        if hasattr(cls, '__tablename__') and cls.__tablename__ == table_name:
            return cls
    return None


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(PermissionCode.VIEW_DASHBOARD))  # ← ИСПРАВЛЕНО!
):
    tables_list = get_all_model_tables()
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "tables": tables_list,
            "employee_login": current_user.login  # теперь реальный пользователь
        }
    )


@router.get("/dashboard/table/{table_name}", response_class=HTMLResponse)
async def table_view(
    table_name: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(PermissionCode.VIEW_DASHBOARD))  # можно своё разрешение
):
    ModelClass = get_model_class_by_table_name(table_name)
    russian_table_name = get_russian_name(table_name, 'table')

    if ModelClass is None:
        raise HTTPException(status_code=404, detail="Таблица не найдена")

    column_names = [col.key for col in inspect(ModelClass).mapper.columns]
    display_column_names = [get_russian_name(col, 'column') for col in column_names]

    records = db.query(ModelClass).limit(50).all()
    data = [
        {col_name: getattr(record, col_name) if getattr(record, col_name) is not None else 'NULL'
         for col_name in column_names}
        for record in records
    ]
    total_rows = db.query(ModelClass).count()

    return templates.TemplateResponse(
        "table_view.html",
        {
            "request": request,
            "table_name": table_name,
            "russian_table_name": russian_table_name,
            "column_names": column_names,
            "display_column_names": display_column_names,
            "data": data,
            "total_rows": total_rows,
        }
    )