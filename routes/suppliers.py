# routes/suppliers.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.database import get_db
from models.tables import Supplier
from dependencies import require_permission
from core.permissions import PermissionCode

router = APIRouter(prefix="/api/suppliers", tags=["Поставщики"])

@router.get("/")
async def get_suppliers(
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(PermissionCode.SUPPLIERS_VIEW))
):
    suppliers = db.scalars(select(Supplier)).all()
    return suppliers

@router.get("/{supplier_id}")
async def get_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(PermissionCode.SUPPLIERS_VIEW))
):
    supplier = db.scalar(select(Supplier).where(Supplier.supplier_id == supplier_id))
    if not supplier:
        raise HTTPException(status_code=404, detail="Поставщик не найден")
    return supplier

@router.post("/")
async def create_supplier(
    supplier_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(PermissionCode.SUPPLIERS_MANAGE))
):
    supplier = Supplier(
        company_name=supplier_data["company_name"],
        inn=supplier_data.get("inn"),
        kpp=supplier_data.get("kpp"),
        address=supplier_data.get("address"),
        contact_phone=supplier_data.get("contact_phone"),
        contact_email=supplier_data.get("contact_email"),
        is_active=supplier_data.get("is_active", True),
        created_by_employee_id=current_user.employee_id
    )
    
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier

@router.put("/{supplier_id}")
async def update_supplier(
    supplier_id: int,
    supplier_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(PermissionCode.SUPPLIERS_MANAGE))
):
    supplier = db.scalar(select(Supplier).where(Supplier.supplier_id == supplier_id))
    if not supplier:
        raise HTTPException(status_code=404, detail="Поставщик не найден")
    
    for key, value in supplier_data.items():
        if hasattr(supplier, key):
            setattr(supplier, key, value)
    
    db.commit()
    return supplier

@router.delete("/{supplier_id}")
async def delete_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(PermissionCode.SUPPLIERS_MANAGE))
):
    supplier = db.scalar(select(Supplier).where(Supplier.supplier_id == supplier_id))
    if not supplier:
        raise HTTPException(status_code=404, detail="Поставщик не найден")
    
    db.delete(supplier)
    db.commit()
    return {"message": "Поставщик удален"}