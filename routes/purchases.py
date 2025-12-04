from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import date, datetime
from pydantic import BaseModel
from models.database import get_db
from models.tables import Purchase, PurchaseItem, Product, Supplier, Employee
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
from io import BytesIO
import os

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

@router.get("/{purchase_id}/pdf")
def download_purchase_pdf(purchase_id: int, db: Session = Depends(get_db)):
    purchase = db.query(Purchase).filter(Purchase.purchase_id == purchase_id).first()
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    
    supplier = db.query(Supplier).filter(Supplier.supplier_id == purchase.supplier_id).first()
    employee = db.query(Employee).filter(Employee.employee_id == purchase.employee_id).first()
    items = db.query(PurchaseItem).filter(PurchaseItem.purchase_id == purchase_id).all()
    
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Регистрируем шрифт DejaVu с поддержкой кириллицы
    font_path = "C:/Windows/Fonts/DejaVuSans.ttf"
    font_bold_path = "C:/Windows/Fonts/DejaVuSans-Bold.ttf"
    
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont('DejaVu', font_path))
        pdfmetrics.registerFont(TTFont('DejaVuBold', font_bold_path))
    else:
        # Fallback на Arial если DejaVu не найден
        font_path = "C:/Windows/Fonts/arial.ttf"
        font_bold_path = "C:/Windows/Fonts/arialbd.ttf"
        pdfmetrics.registerFont(TTFont('DejaVu', font_path))
        pdfmetrics.registerFont(TTFont('DejaVuBold', font_bold_path))
    
    # Заголовок
    c.setFillColorRGB(0.42, 0.07, 0.8)
    c.rect(0, height - 120, width, 120, fill=1, stroke=0)
    
    c.setFillColorRGB(1, 1, 1)
    c.setFont("DejaVuBold", 38)
    c.drawString(40, height - 65, "НАКЛАДНАЯ")
    c.setFont("DejaVu", 13)
    c.drawString(40, height - 88, f"№ {purchase.purchase_code}")
    c.drawString(width - 200, height - 88, f"{purchase.purchase_date}")
    
    # Карточка с информацией о закупке
    y = height - 140
    c.setFillColorRGB(0.95, 0.96, 0.98)
    c.roundRect(30, y - 110, width - 60, 105, 15, fill=1, stroke=0)
    c.setStrokeColorRGB(0.42, 0.07, 0.8)
    c.setLineWidth(2)
    c.roundRect(30, y - 110, width - 60, 105, 15, fill=0, stroke=1)
    
    c.setFillColorRGB(0, 0, 0)
    c.setFont("DejaVuBold", 11)
    c.drawString(45, y - 20, "ИНФОРМАЦИЯ О ЗАКУПКЕ")
    
    y -= 45
    c.setFillColorRGB(0, 0, 0)
    c.setFont("DejaVu", 10)
    c.drawString(45, y, f"Дата закупки: {purchase.purchase_date}")
    c.drawString(width - 280, y, f"Статус: {purchase.status}")
    y -= 22
    if purchase.delivery_date:
        c.drawString(45, y, f"Дата доставки: {purchase.delivery_date}")
    if purchase.invoice_number:
        c.drawString(width - 280, y, f"Номер счета: {purchase.invoice_number}")
    y -= 25
    
    # Карточки поставщика и ответственного
    y -= 20
    card_width = (width - 80) / 2
    
    if supplier:
        c.setFillColorRGB(0.95, 0.96, 0.98)
        c.roundRect(30, y - 85, card_width, 80, 12, fill=1, stroke=0)
        c.setStrokeColorRGB(0.42, 0.07, 0.8)
        c.setLineWidth(1.5)
        c.roundRect(30, y - 85, card_width, 80, 12, fill=0, stroke=1)
        
        c.setFillColorRGB(0, 0, 0)
        c.setFont("DejaVuBold", 10)
        c.drawString(45, y - 15, "ПОСТАВЩИК")
        c.setFillColorRGB(0, 0, 0)
        c.setFont("DejaVu", 9)
        c.drawString(45, y - 35, f"{supplier.company_name}")
        if supplier.inn:
            c.drawString(45, y - 50, f"ИНН: {supplier.inn}")
        if supplier.contact_phone:
            c.drawString(45, y - 65, f"Тел: {supplier.contact_phone}")
    
    if employee:
        c.setFillColorRGB(0.95, 0.96, 0.98)
        c.roundRect(width - 30 - card_width, y - 85, card_width, 80, 12, fill=1, stroke=0)
        c.setStrokeColorRGB(0.42, 0.07, 0.8)
        c.setLineWidth(1.5)
        c.roundRect(width - 30 - card_width, y - 85, card_width, 80, 12, fill=0, stroke=1)
        
        c.setFillColorRGB(0, 0, 0)
        c.setFont("DejaVuBold", 10)
        c.drawString(width - 15 - card_width, y - 15, "ОТВЕТСТВЕННЫЙ")
        c.setFillColorRGB(0, 0, 0)
        c.setFont("DejaVu", 9)
        c.drawString(width - 15 - card_width, y - 40, f"{employee.full_name}")
    
    y -= 100
    
    # Таблица товаров
    y -= 30
    c.setFillColorRGB(0, 0, 0)
    c.setFont("DejaVuBold", 12)
    c.drawString(40, y, "ТОВАРЫ")
    y -= 35
    
    table_data = [["№", "Наименование", "Кол-во", "Цена", "Сумма"]]
    for idx, item in enumerate(items, 1):
        product = db.query(Product).filter(Product.product_id == item.product_id).first()
        product_name = product.product_name if product else "—"
        total = item.quantity * float(item.unit_price)
        table_data.append([
            str(idx),
            product_name[:30],
            str(item.quantity),
            f"{float(item.unit_price):.2f} ₽",
            f"{total:.2f} ₽"
        ])
    
    table = Table(table_data, colWidths=[30, 250, 60, 80, 95])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6a11cb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),
        ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'DejaVuBold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTNAME', (0, 1), (-1, -1), 'DejaVu'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
        ('LINEABOVE', (0, 0), (-1, 0), 2, colors.HexColor('#6a11cb')),
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#6a11cb')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('ROUNDEDCORNERS', [15, 15, 15, 15])
    ]))
    
    table.wrapOn(c, width, height)
    table.drawOn(c, 40, y - len(table_data) * 25)
    
    # Итого
    y = y - len(table_data) * 25 - 50
    c.setFillColorRGB(0.42, 0.07, 0.8)
    c.roundRect(width - 300, y - 65, 270, 60, 12, fill=1, stroke=0)
    
    c.setFillColorRGB(1, 1, 1)
    c.setFont("DejaVuBold", 16)
    c.drawString(width - 285, y - 25, "ИТОГО")
    c.setFont("DejaVuBold", 24)
    c.drawString(width - 285, y - 50, f"{float(purchase.total_amount):.2f} ₽")
    
    # Футер
    c.setFillColorRGB(0, 0, 0)
    c.setFont("DejaVuBold", 11)
    c.drawString(40, 40, "Документ сформирован автоматически")
    c.setFillColorRGB(0.3, 0.3, 0.3)
    c.setFont("DejaVu", 8)
    c.drawString(40, 25, f"Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    c.drawString(width - 220, 25, "Система управления складом")
    
    c.save()
    buffer.seek(0)
    
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=purchase_{purchase.purchase_code}.pdf"}
    )
