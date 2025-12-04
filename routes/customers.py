# routes/customers.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.database import get_db
from models.tables import Customer
from dependencies import require_permission
from core.permissions import PermissionCode

router = APIRouter(prefix="/api/customers", tags=["Клиенты"])

@router.get("/")
async def get_customers(
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(PermissionCode.CUSTOMERS_VIEW))
):
    customers = db.scalars(select(Customer)).all()
    return customers

@router.get("/{customer_id}")
async def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(PermissionCode.CUSTOMERS_VIEW))
):
    customer = db.scalar(select(Customer).where(Customer.customer_id == customer_id))
    if not customer:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    return customer

@router.post("/")
async def create_customer(
    customer_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(PermissionCode.CUSTOMERS_MANAGE))
):
    customer = Customer(
        customer_name=customer_data["customer_name"],
        phone=customer_data["phone"],
        email=customer_data.get("email"),
        loyalty_card_number=customer_data.get("loyalty_card_number"),
        notes=customer_data.get("notes"),
        created_by_employee_id=current_user.employee_id
    )
    
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer

@router.put("/{customer_id}")
async def update_customer(
    customer_id: int,
    customer_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(PermissionCode.CUSTOMERS_MANAGE))
):
    customer = db.scalar(select(Customer).where(Customer.customer_id == customer_id))
    if not customer:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    
    for key, value in customer_data.items():
        if hasattr(customer, key):
            setattr(customer, key, value)
    
    db.commit()
    return customer

@router.delete("/{customer_id}")
async def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(PermissionCode.CUSTOMERS_MANAGE))
):
    customer = db.scalar(select(Customer).where(Customer.customer_id == customer_id))
    if not customer:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    
    db.delete(customer)
    db.commit()
    return {"message": "Клиент удален"}