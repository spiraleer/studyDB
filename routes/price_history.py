from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.database import get_db
from models.tables import PriceHistory, Product, Employee

router = APIRouter(prefix="/api/price-history", tags=["price_history"])

@router.get("/")
def get_price_history(db: Session = Depends(get_db)):
    history = db.query(PriceHistory).order_by(PriceHistory.change_date.desc()).all()
    result = []
    for h in history:
        product = db.query(Product).filter(Product.product_id == h.product_id).first()
        employee = db.query(Employee).filter(Employee.employee_id == h.changed_by_employee_id).first()
        result.append({
            "price_history_id": h.price_history_id,
            "product_id": h.product_id,
            "product_name": product.product_name if product else None,
            "old_price": float(h.old_price) if h.old_price else None,
            "new_price": float(h.new_price),
            "change_date": h.change_date,
            "changed_by_employee_id": h.changed_by_employee_id,
            "employee_name": employee.full_name if employee else None,
            "reason": h.reason
        })
    return result
