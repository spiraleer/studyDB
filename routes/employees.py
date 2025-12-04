# routes/employees.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from models.database import get_db
from models.tables import Employee
from dependencies import require_permission
from core.permissions import PermissionCode

router = APIRouter(prefix="/api/employees", tags=["Сотрудники"])

@router.get("/count")
async def get_employees_count(
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(PermissionCode.EMPLOYEES_VIEW))
):
    count = db.scalar(select(func.count(Employee.employee_id)))
    return {"count": count}