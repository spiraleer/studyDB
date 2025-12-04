from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from pydantic import BaseModel
from models.database import get_db
from models.tables import Purchase, PurchaseItem, Product, Supplier, Employee

router = APIRouter(prefix="/api/purchases", tags=["purchases"])

class PurchaseItemCreate(BaseModel):
    product_id: int
    quantity: int
    unit_price: float

class PurchaseCreate(BaseModel):
    purchase_date: str
    supplier_id: int
    employee_id: int
    delivery_date: str = None
    status: str = "ordered"
    invoice_number: str = None
    notes: str = None
    items: List[PurchaseItemCreate]

class PurchaseUpdate(BaseModel):
    purchase_date: str = None
    supplier_id: int = None
    delivery_date: str = None
    status: str = None
    invoice_number: str = None
    notes: str = None

@router.get("/")
def get_purchases(db: Session = Depends(get_db)):
    purchases = db.query(Purchase).all()
    result = []
    for p in purchases:
        supplier = db.query(Supplier).filter(Supplier.supplier_id == p.supplier_id).first()
        employee = db.query(Employee).filter(Employee.employee_id == p.employee_id).first()
        result.append({
            "purchase_id": p.purchase_id,
            "purchase_code": p.purchase_code,
            "purchase_date": p.purchase_date,
            "supplier_id": p.supplier_id,
            "supplier_name": supplier.company_name if supplier else None,
            "total_amount": float(p.total_amount) if p.total_amount else 0,
            "delivery_date": p.delivery_date,
            "employee_id": p.employee_id,
            "employee_name": employee.full_name if employee else None,
            "status": p.status,
            "invoice_number": p.invoice_number,
            "notes": p.notes,
            "created_at": p.created_at
        })
    return result

@router.get("/{purchase_id}")
def get_purchase(purchase_id: int, db: Session = Depends(get_db)):
    purchase = db.query(Purchase).filter(Purchase.purchase_id == purchase_id).first()
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    
    items = db.query(PurchaseItem).filter(PurchaseItem.purchase_id == purchase_id).all()
    items_data = []
    for item in items:
        product = db.query(Product).filter(Product.product_id == item.product_id).first()
        items_data.append({
            "purchase_item_id": item.purchase_item_id,
            "product_id": item.product_id,
            "product_name": product.product_name if product else None,
            "quantity": item.quantity,
            "unit_price": float(item.unit_price)
        })
    
    return {
        "purchase": {
            "purchase_id": purchase.purchase_id,
            "purchase_code": purchase.purchase_code,
            "purchase_date": purchase.purchase_date,
            "supplier_id": purchase.supplier_id,
            "total_amount": float(purchase.total_amount) if purchase.total_amount else 0,
            "delivery_date": purchase.delivery_date,
            "employee_id": purchase.employee_id,
            "status": purchase.status,
            "invoice_number": purchase.invoice_number,
            "notes": purchase.notes
        },
        "items": items_data
    }

@router.post("/")
def create_purchase(purchase: PurchaseCreate, db: Session = Depends(get_db)):
    total = sum(item.quantity * item.unit_price for item in purchase.items)
    
    new_purchase = Purchase(
        purchase_date=purchase.purchase_date,
        supplier_id=purchase.supplier_id,
        employee_id=purchase.employee_id,
        total_amount=total,
        delivery_date=purchase.delivery_date,
        status=purchase.status,
        invoice_number=purchase.invoice_number,
        notes=purchase.notes
    )
    db.add(new_purchase)
    db.flush()
    
    for item in purchase.items:
        new_item = PurchaseItem(
            purchase_id=new_purchase.purchase_id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price
        )
        db.add(new_item)
    
    db.commit()
    db.refresh(new_purchase)
    return {"purchase_id": new_purchase.purchase_id}

@router.put("/{purchase_id}")
def update_purchase(purchase_id: int, purchase: PurchaseUpdate, db: Session = Depends(get_db)):
    db_purchase = db.query(Purchase).filter(Purchase.purchase_id == purchase_id).first()
    if not db_purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    
    old_status = db_purchase.status
    
    if purchase.purchase_date:
        db_purchase.purchase_date = purchase.purchase_date
    if purchase.supplier_id:
        db_purchase.supplier_id = purchase.supplier_id
    if purchase.delivery_date:
        db_purchase.delivery_date = purchase.delivery_date
    if purchase.status:
        db_purchase.status = purchase.status
    if purchase.invoice_number:
        db_purchase.invoice_number = purchase.invoice_number
    if purchase.notes is not None:
        db_purchase.notes = purchase.notes
    
    # Увеличиваем остатки при смене статуса на "delivered"
    if purchase.status == "delivered" and old_status != "delivered":
        items = db.query(PurchaseItem).filter(PurchaseItem.purchase_id == purchase_id).all()
        for item in items:
            product = db.query(Product).filter(Product.product_id == item.product_id).first()
            if product:
                product.stock_quantity += item.quantity
    
    db.commit()
    return {"message": "Purchase updated"}

@router.delete("/{purchase_id}")
def delete_purchase(purchase_id: int, db: Session = Depends(get_db)):
    purchase = db.query(Purchase).filter(Purchase.purchase_id == purchase_id).first()
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    
    db.query(PurchaseItem).filter(PurchaseItem.purchase_id == purchase_id).delete()
    db.delete(purchase)
    db.commit()
    return {"message": "Purchase deleted"}

@router.get("/suppliers/list")
def get_suppliers(db: Session = Depends(get_db)):
    suppliers = db.query(Supplier).filter(Supplier.is_active == True).all()
    return [{"supplier_id": s.supplier_id, "company_name": s.company_name} for s in suppliers]

@router.get("/products/list")
def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).filter(Product.is_active == True).all()
    return [{"product_id": p.product_id, "product_name": p.product_name, "price": float(p.price)} for p in products]
