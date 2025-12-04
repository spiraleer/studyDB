# dependencies.py
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.database import get_db
from models.tables import Employee, Permission, RolePermission, Role
from core.permissions import PermissionCode

def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> Employee:
    employee_id = request.cookies.get("employee_id")
    
    if not employee_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не авторизован"
        )
    
    employee = db.scalar(
        select(Employee)
        .where(Employee.employee_id == int(employee_id))
        .where(Employee.is_active == True)
    )
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден"
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