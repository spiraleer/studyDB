# routes/employees.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from models.database import get_db
from models.tables import Employee, Role
from dependencies import require_permission
from core.permissions import PermissionCode
from core.security import get_password_hash
from datetime import date
from decimal import Decimal

router = APIRouter(prefix="/api/employees", tags=["Сотрудники"])

@router.get("/count")
async def get_employees_count(
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(PermissionCode.EMPLOYEES_VIEW))
):
    count = db.scalar(select(func.count(Employee.employee_id)))
    return {"count": count}

@router.get("/")
async def get_employees(
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(PermissionCode.EMPLOYEES_VIEW))
):
    employees = db.scalars(select(Employee)).all()
    return employees

@router.get("/{employee_id}")
async def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(PermissionCode.EMPLOYEES_VIEW))
):
    employee = db.scalar(select(Employee).where(Employee.employee_id == employee_id))
    if not employee:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    return employee

@router.post("/")
async def create_employee(
    employee_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(PermissionCode.EMPLOYEES_CREATE))
):
    # Проверка уникальности логина
    existing = db.scalar(select(Employee).where(Employee.login == employee_data["login"]))
    if existing:
        raise HTTPException(status_code=400, detail="Логин уже используется")
    
    new_employee = Employee(
        full_name=employee_data["full_name"],
        position=employee_data["position"],
        role_id=employee_data["role_id"],
        hire_date=employee_data["hire_date"],
        salary=Decimal(str(employee_data.get("salary", 0))) if employee_data.get("salary") else None,
        login=employee_data["login"],
        password_hash=get_password_hash(employee_data["password"]),
        is_active=employee_data.get("is_active", True)
    )
    
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return new_employee

@router.put("/{employee_id}")
async def update_employee(
    employee_id: int,
    employee_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(PermissionCode.EMPLOYEES_EDIT))
):
    employee = db.scalar(select(Employee).where(Employee.employee_id == employee_id))
    if not employee:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    
    # Проверка уникальности логина при изменении
    if "login" in employee_data and employee_data["login"] != employee.login:
        existing = db.scalar(select(Employee).where(Employee.login == employee_data["login"]))
        if existing:
            raise HTTPException(status_code=400, detail="Логин уже используется")
    
    if "full_name" in employee_data:
        employee.full_name = employee_data["full_name"]
    if "position" in employee_data:
        employee.position = employee_data["position"]
    if "role_id" in employee_data:
        employee.role_id = employee_data["role_id"]
    if "hire_date" in employee_data:
        employee.hire_date = employee_data["hire_date"]
    if "salary" in employee_data:
        employee.salary = Decimal(str(employee_data["salary"])) if employee_data["salary"] else None
    if "login" in employee_data:
        employee.login = employee_data["login"]
    if "password" in employee_data and employee_data["password"]:
        employee.password_hash = get_password_hash(employee_data["password"])
    if "is_active" in employee_data:
        employee.is_active = employee_data["is_active"]
    
    db.commit()
    db.refresh(employee)
    return employee

@router.delete("/{employee_id}")
async def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(PermissionCode.EMPLOYEES_DELETE))
):
    if employee_id == current_user.employee_id:
        raise HTTPException(status_code=400, detail="Нельзя удалить самого себя")
    
    employee = db.scalar(select(Employee).where(Employee.employee_id == employee_id))
    if not employee:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    
    # Мягкое удаление
    employee.is_active = False
    db.commit()
    return {"message": "Сотрудник деактивирован"}

@router.get("/roles/list")
async def get_roles(
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(PermissionCode.EMPLOYEES_VIEW))
):
    roles = db.scalars(select(Role)).all()
    return [{"role_id": r.role_id, "role_name": r.role_name} for r in roles]