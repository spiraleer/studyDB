from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

from models.database import get_db
from models.tables import StockMovement, Employee
from dependencies import require_permission, get_current_user
from core.permissions import PermissionCode

router = APIRouter(
    prefix="/api/stock-movements",
    tags=["Движение товаров"]
)

templates = Jinja2Templates(directory="templates")

@router.get("/", response_model=List[dict])
async def get_stock_movements(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission(PermissionCode.PRODUCTS_VIEW))
):
    """Получить список движений товаров"""
    query = select(StockMovement).offset(skip).limit(limit).order_by(StockMovement.movement_date.desc())
    movements = db.scalars(query).all()
    
    return [
        {
            "movement_id": m.movement_id,
            "product_id": m.product_id,
            "movement_type": m.movement_type,
            "quantity": m.quantity,
            "movement_date": m.movement_date.isoformat() if m.movement_date else None,
            "reference_id": m.reference_id,
            "reference_type": m.reference_type,
            "employee_id": m.employee_id,
            "notes": m.notes
        }
        for m in movements
    ]
