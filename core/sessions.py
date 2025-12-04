# core/sessions.py — Управление сессиями пользователей
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, update
from models.tables import UserSession
import secrets


def generate_session_token() -> str:
    """
    Генерирует уникальный токен сессии.
    """
    return secrets.token_urlsafe(32)


def create_session(
    db: Session,
    employee_id: int,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> UserSession:
    """
    Создаёт новую сессию пользователя и сохраняет в БД.
    
    Args:
        db: Сессия БД
        employee_id: ID сотрудника
        ip_address: IP-адрес клиента
        user_agent: User-Agent браузера
    
    Returns:
        Объект UserSession
    """
    session_token = generate_session_token()
    
    session = UserSession(
        employee_id=employee_id,
        session_token=session_token,
        ip_address=ip_address,
        user_agent=user_agent,
        is_active=True
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return session


def end_session(
    db: Session,
    session_id: int
) -> bool:
    """
    Завершает сессию (устанавливает logout_time и is_active=False).
    
    Args:
        db: Сессия БД
        session_id: ID сессии
    
    Returns:
        True если успешно, False если сессия не найдена
    """
    session = db.scalar(select(UserSession).where(UserSession.session_id == session_id))
    
    if not session:
        return False
    
    session.logout_time = datetime.now()
    session.is_active = False
    db.commit()
    
    return True


def end_session_by_token(
    db: Session,
    session_token: str
) -> bool:
    """
    Завершает сессию по токену.
    
    Args:
        db: Сессия БД
        session_token: Токен сессии
    
    Returns:
        True если успешно, False если сессия не найдена
    """
    session = db.scalar(select(UserSession).where(UserSession.session_token == session_token))
    
    if not session:
        return False
    
    session.logout_time = datetime.now()
    session.is_active = False
    db.commit()
    
    return True


def get_active_session(
    db: Session,
    session_token: str
) -> Optional[UserSession]:
    """
    Получает активную сессию по токену.
    
    Args:
        db: Сессия БД
        session_token: Токен сессии
    
    Returns:
        Объект UserSession или None
    """
    return db.scalar(
        select(UserSession).where(
            UserSession.session_token == session_token,
            UserSession.is_active == True
        )
    )


def get_employee_active_sessions(
    db: Session,
    employee_id: int
) -> list[UserSession]:
    """
    Получает все активные сессии сотрудника.
    
    Args:
        db: Сессия БД
        employee_id: ID сотрудника
    
    Returns:
        Список активных сессий
    """
    return db.scalars(
        select(UserSession).where(
            UserSession.employee_id == employee_id,
            UserSession.is_active == True
        )
    ).all()
