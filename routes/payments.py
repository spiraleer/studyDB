from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from models.database import get_db
from models.tables import Payment, Orders, Employee, Customer, OrderItem, Product
from dependencies import require_permission
from core.permissions import PermissionCode
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
import os

router = APIRouter(prefix="/api/payments", tags=["payments"])

class PaymentCreate(BaseModel):
    order_id: int
    amount: float
    payment_type: str
    payment_status: str = "Оплачено"
    employee_id: int
    receipt_number: str = None
    notes: str = None

class PaymentUpdate(BaseModel):
    amount: float = None
    payment_type: str = None
    payment_status: str = None
    receipt_number: str = None
    notes: str = None

@router.get("/")
def get_payments(
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(PermissionCode.ORDERS_VIEW))
):
    payments = db.query(Payment).all()
    result = []
    for p in payments:
        order = db.query(Orders).filter(Orders.order_id == p.order_id).first()
        employee = db.query(Employee).filter(Employee.employee_id == p.employee_id).first()
        result.append({
            "payment_id": p.payment_id,
            "payment_code": p.payment_code,
            "payment_date": p.payment_date,
            "order_id": p.order_id,
            "order_code": order.order_code if order else None,
            "amount": float(p.amount),
            "payment_type": p.payment_type,
            "payment_status": p.payment_status,
            "employee_id": p.employee_id,
            "employee_name": employee.full_name if employee else None,
            "receipt_number": p.receipt_number,
            "notes": p.notes,
            "created_at": p.created_at
        })
    return result

@router.get("/{payment_id}")
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(PermissionCode.ORDERS_VIEW))
):
    payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return {
        "payment_id": payment.payment_id,
        "payment_code": payment.payment_code,
        "payment_date": payment.payment_date,
        "order_id": payment.order_id,
        "amount": float(payment.amount),
        "payment_type": payment.payment_type,
        "payment_status": payment.payment_status,
        "employee_id": payment.employee_id,
        "receipt_number": payment.receipt_number,
        "notes": payment.notes
    }

@router.post("/")
def create_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(PermissionCode.ORDERS_CREATE))
):
    new_payment = Payment(
        order_id=payment.order_id,
        amount=payment.amount,
        payment_type=payment.payment_type,
        payment_status=payment.payment_status,
        employee_id=payment.employee_id,
        receipt_number=payment.receipt_number,
        notes=payment.notes
    )
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    return {"payment_id": new_payment.payment_id}

@router.put("/{payment_id}")
def update_payment(
    payment_id: int,
    payment: PaymentUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(PermissionCode.ORDERS_EDIT))
):
    db_payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
    if not db_payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    if payment.amount is not None:
        db_payment.amount = payment.amount
    if payment.payment_type:
        db_payment.payment_type = payment.payment_type
    if payment.payment_status:
        db_payment.payment_status = payment.payment_status
    if payment.receipt_number is not None:
        db_payment.receipt_number = payment.receipt_number
    if payment.notes is not None:
        db_payment.notes = payment.notes
    
    db.commit()
    return {"message": "Payment updated"}

@router.delete("/{payment_id}")
def delete_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(PermissionCode.ORDERS_EDIT))
):
    payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    db.delete(payment)
    db.commit()
    return {"message": "Payment deleted"}

@router.get("/orders/list")
def get_orders(
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(PermissionCode.ORDERS_VIEW))
):
    orders = db.query(Orders).all()
    return [{"order_id": o.order_id, "order_code": o.order_code, "total_amount": float(o.total_amount)} for o in orders]

@router.get("/{payment_id}/pdf")
def download_payment_pdf(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(PermissionCode.ORDERS_VIEW))
):
    payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    order = db.query(Orders).filter(Orders.order_id == payment.order_id).first()
    customer = db.query(Customer).filter(Customer.customer_id == order.customer_id).first() if order else None
    employee = db.query(Employee).filter(Employee.employee_id == payment.employee_id).first()
    items = db.query(OrderItem).filter(OrderItem.order_id == payment.order_id).all() if order else []
    
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    font_path = "C:/Windows/Fonts/DejaVuSans.ttf"
    font_bold_path = "C:/Windows/Fonts/DejaVuSans-Bold.ttf"
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont('DejaVu', font_path))
        pdfmetrics.registerFont(TTFont('DejaVuBold', font_bold_path))
    else:
        pdfmetrics.registerFont(TTFont('DejaVu', "C:/Windows/Fonts/arial.ttf"))
        pdfmetrics.registerFont(TTFont('DejaVuBold', "C:/Windows/Fonts/arialbd.ttf"))
    
    c.setFillColorRGB(0.42, 0.07, 0.8)
    c.rect(0, height - 100, width, 100, fill=1, stroke=0)
    
    c.setFillColorRGB(1, 1, 1)
    c.setFont("DejaVuBold", 42)
    c.drawString(40, height - 60, "ЧЕК")
    c.setFont("DejaVu", 13)
    c.drawString(40, height - 82, f"№ {payment.payment_code or payment.payment_id}")
    c.drawString(width - 200, height - 82, f"{payment.payment_date.strftime('%d.%m.%Y %H:%M')}")
    
    y = height - 120
    
    c.setFillColorRGB(0.95, 0.96, 0.98)
    c.roundRect(30, y - 100, width - 60, 95, 15, fill=1, stroke=0)
    c.setStrokeColorRGB(0.42, 0.07, 0.8)
    c.setLineWidth(2)
    c.roundRect(30, y - 100, width - 60, 95, 15, fill=0, stroke=1)
    
    c.setFillColorRGB(0, 0, 0)
    c.setFont("DejaVuBold", 11)
    c.drawString(45, y - 20, "ИНФОРМАЦИЯ О ПЛАТЕЖЕ")
    
    y -= 40
    c.setFillColorRGB(0, 0, 0)
    c.setFont("DejaVu", 10)
    c.drawString(45, y, f"Заказ: {order.order_code if order else '—'}")
    c.drawString(width - 250, y, f"Тип оплаты: {payment.payment_type}")
    y -= 20
    c.drawString(45, y, f"Статус: {payment.payment_status}")
    if payment.receipt_number:
        c.drawString(width - 250, y, f"Номер чека: {payment.receipt_number}")
    y -= 25
    
    if customer or employee:
        y -= 15
        card_width = (width - 80) / 2
        
        if customer:
            c.setFillColorRGB(0.95, 0.96, 0.98)
            c.roundRect(30, y - 70, card_width, 65, 12, fill=1, stroke=0)
            c.setStrokeColorRGB(0.42, 0.07, 0.8)
            c.setLineWidth(1.5)
            c.roundRect(30, y - 70, card_width, 65, 12, fill=0, stroke=1)
            
            c.setFillColorRGB(0, 0, 0)
            c.setFont("DejaVuBold", 10)
            c.drawString(45, y - 15, "КЛИЕНТ")
            c.setFont("DejaVu", 9)
            c.drawString(45, y - 35, f"{customer.customer_name}")
            if customer.phone:
                c.drawString(45, y - 50, f"Тел: {customer.phone}")
        
        if employee:
            c.setFillColorRGB(0.95, 0.96, 0.98)
            c.roundRect(width - 30 - card_width, y - 70, card_width, 65, 12, fill=1, stroke=0)
            c.setStrokeColorRGB(0.42, 0.07, 0.8)
            c.setLineWidth(1.5)
            c.roundRect(width - 30 - card_width, y - 70, card_width, 65, 12, fill=0, stroke=1)
            
            c.setFillColorRGB(0, 0, 0)
            c.setFont("DejaVuBold", 10)
            c.drawString(width - 15 - card_width, y - 15, "КАССИР")
            c.setFont("DejaVu", 9)
            c.drawString(width - 15 - card_width, y - 35, f"{employee.full_name}")
        
        y -= 85
    
    if items:
        y -= 25
        c.setFillColorRGB(0, 0, 0)
        c.setFont("DejaVuBold", 12)
        c.drawString(40, y, "ТОВАРЫ")
        y -= 30
        
        table_data = [["№", "Наименование", "Кол-во", "Цена", "Сумма"]]
        for idx, item in enumerate(items, 1):
            product = db.query(Product).filter(Product.product_id == item.product_id).first()
            product_name = product.product_name if product else "—"
            total = item.quantity * float(item.item_price) * (1 - float(item.item_discount) / 100)
            table_data.append([
                str(idx),
                product_name[:30],
                str(item.quantity),
                f"{float(item.item_price):.2f} ₽",
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
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
        ]))
        table.wrapOn(c, width, height)
        table.drawOn(c, 40, y - len(table_data) * 25)
        y = y - len(table_data) * 25 - 40
    
    c.setFillColorRGB(0.42, 0.07, 0.8)
    c.roundRect(width - 280, y - 55, 250, 50, 10, fill=1, stroke=0)
    
    c.setFillColorRGB(1, 1, 1)
    c.setFont("DejaVuBold", 18)
    c.drawString(width - 265, y - 25, "ОПЛАЧЕНО")
    c.setFont("DejaVuBold", 22)
    c.drawString(width - 265, y - 45, f"{float(payment.amount):.2f} ₽")
    
    c.setFillColorRGB(0, 0, 0)
    c.setFont("DejaVuBold", 11)
    c.drawString(40, 35, "Спасибо за покупку!")
    c.setFillColorRGB(0.3, 0.3, 0.3)
    c.setFont("DejaVu", 8)
    c.drawString(40, 20, f"Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    c.drawString(width - 220, 20, "Система управления складом")
    
    c.save()
    buffer.seek(0)
    
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=receipt_{payment.payment_code or payment.payment_id}.pdf"}
    )
