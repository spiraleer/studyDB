# dependencies.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.database import get_db
from models.tables import Employee

# ВРЕМЕННАЯ заглушка — пока без JWT
def get_current_user(db: Session = Depends(get_db)) -> Employee:
    # Пока просто возвращаем админа (для теста)
    return db.query(Employee).filter(Employee.login == "admin").first()

def require_permission(permission_code: str):
    def dependency(
        user: Employee = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        if not user:
            raise HTTPException(status_code=401, detail="Не авторизован")
        # Проверка права (пока заглушка — всегда True)
        # Потом подключим настоящую проверку через RolePermission
        return user
    return dependency