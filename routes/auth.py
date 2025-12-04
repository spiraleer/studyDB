# routes/auth.py
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import select
from pydantic import BaseModel

from models.database import get_db
from models.tables import Employee, UserSession
from core.sessions import generate_session_token
from core.security import verify_password, get_password_hash
from dependencies import require_permission
from core.permissions import PermissionCode
from datetime import datetime

templates = Jinja2Templates(directory="templates")

class ChangePasswordRequest(BaseModel):
    employee_id: int
    current_password: str
    new_password: str

# Инициализируем роутер
router = APIRouter(
    prefix="/api/auth",
    tags=["Аутентификация"],
)

@router.post("/token") 
async def login_for_access(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Принимает логин и пароль, ищет сотрудника и проверяет их.
    Пароль проверяется безопасно через bcrypt хеширование.
    """
    
    # 1. Поиск сотрудника по логину
    employee = db.scalar(select(Employee).filter(
        Employee.login == form_data.username,
        Employee.is_active == True
    ))
    
    # 2. Проверяем пароль
    if not employee or not verify_password(form_data.password, employee.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    

    
    # 3. Генерируем токен для сессии (но не создаем запись в БД)
    session_token = generate_session_token()
    
    # Возвращаем статус успеха с токеном сессии
    return {
        "status": "success",
        "employee_id": employee.employee_id,
        "login": employee.login,
        "session_token": session_token
    }


@router.post("/logout")
async def logout(
    data: dict,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Создает запись о выходе из системы.
    
    Args:
        data: JSON с session_token и employee_id
    """
    session_token = data.get("session_token")
    employee_id = data.get("employee_id")
    
    if not session_token or not employee_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="session_token и employee_id требуются"
        )
    
    # Создаем запись о сессии с временем выхода
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent", None)
    
    session = UserSession(
        employee_id=employee_id,
        session_token=session_token,
        login_time=datetime.now(),  # Примерное время входа
        logout_time=datetime.now(),  # Время выхода
        ip_address=ip_address,
        user_agent=user_agent,
        is_active=True
    )
    
    db.add(session)
    db.commit()
    
    return {
        "status": "success",
        "message": "Сессия завершена"
    }

@router.delete("/sessions")
async def clear_all_sessions(
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(PermissionCode.EMPLOYEES_DELETE))
):
    """Очистить все сессии (только администратор)"""
    db.query(UserSession).delete()
    db.commit()
    return {"message": "Все сессии удалены"}

@router.post("/change-password")
async def change_password(request: ChangePasswordRequest, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.employee_id == request.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    if not verify_password(request.current_password, employee.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect current password")
    
    employee.password_hash = get_password_hash(request.new_password)
    db.commit()
    return {"message": "Password changed successfully"}