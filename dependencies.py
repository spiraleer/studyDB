# dependencies.py - ИСПРАВЛЕННАЯ ВЕРСИЯ
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.database import get_db
from models.tables import Employee, Permission, RolePermission, Role
from core.permissions import PermissionCode
from typing import Optional

# Временная заглушка для токена - будем передавать через куки или headers
def get_current_user(
    # В будущем добавим: token: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Employee:
    """
    Получить текущего пользователя.
    Временная реализация - возвращает первого активного сотрудника.
    TODO: Заменить на JWT проверку
    """
    # TODO: Реализовать проверку JWT токена
    # if token:
    #     # Декодируем JWT токен и получаем employee_id
    #     # user_id = decode_jwt_token(token)
    #     # employee = db.scalar(select(Employee).where(Employee.employee_id == user_id))
    #     pass
    
    # Временная реализация для тестирования
    # Возвращаем администратора или первого активного сотрудника
    employee = db.scalar(
        select(Employee)
        .where(Employee.login == "admin")
        .where(Employee.is_active == True)
    )
    
    if not employee:
        # Если админ не найден, берем первого активного сотрудника
        employee = db.scalar(
            select(Employee)
            .where(Employee.is_active == True)
            .limit(1)
        )
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден или не авторизован"
        )
    
    return employee

def require_permission(permission_code: PermissionCode):
    def dependency(
        current_user: Employee = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> Employee:
        """
        Проверяет наличие разрешения у текущего пользователя.
        """
        # Администратор имеет все права
        # Получаем значение атрибута, а не объект Column
        if hasattr(current_user, 'login') and str(current_user.login) == "admin":
            return current_user
        
        # Проверяем, есть ли у роли пользователя нужное разрешение
        permission_exists = db.scalar(
            select(Permission.permission_id)
            .join(RolePermission, RolePermission.permission_id == Permission.permission_id)
            .join(Role, Role.role_id == RolePermission.role_id)
            .where(Permission.permission_code == permission_code.value)
            .where(Role.role_id == current_user.role_id)
        )
        
        if not permission_exists:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Недостаточно прав. Требуется разрешение: {permission_code.value}"
            )
        
        return current_user
    
    return dependency