# routes/auth.py
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import select # <--- Важно: используем select

from models.database import get_db
from models.tables import Employee

# Инициализируем роутер
router = APIRouter(
    prefix="/api/auth",
    tags=["Аутентификация"],
)

@router.post("/token") 
async def login_for_access(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
    db: Session = Depends(get_db)
):
    """
    Принимает логин и пароль, ищет сотрудника и проверяет их.
    ВНИМАНИЕ: Пароль сравнивается в чистом виде!
    """
    
    # 1. Поиск сотрудника
    # Ищем сотрудника с заданным логином И паролем (в чистом виде)
    employee = db.scalar(select(Employee).filter(
        Employee.login == form_data.username, 
        # Пароль сравнивается с password_hash, где лежит чистый пароль
        Employee.password_hash == form_data.password, 
        Employee.is_active == True
    ))
    
    # 2. ❌ ИСПРАВЛЕНИЕ: Используем явное сравнение "is None"
    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. ❌ УДАЛЕНО: Мы полностью убрали операцию employee.last_login = func.now(), 
    # так как она вызывала ошибку типизации и усложняла код.
    
    # db.commit()
    
    # Возвращаем простой статус успеха
    return {"status": "success", "employee_id": employee.employee_id, "login": employee.login}