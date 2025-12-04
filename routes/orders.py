# routes/orders.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.database import get_db
from models.tables import Orders, OrderItem, Product, Customer, StockMovement
from dependencies import require_permission
from core.permissions import PermissionCode
from datetime import datetime
from decimal import Decimal

router = APIRouter(prefix="/api/orders", tags=["Заказы"])

@router.get("/")
async def get_orders(
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(PermissionCode.ORDERS_VIEW))
):
    orders = db.scalars(select(Orders)).all()
    return orders

@router.post("/")
async def create_order(
    order_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(PermissionCode.ORDERS_CREATE))
):
    # Создаем заказ
    order = Orders(
        customer_id=order_data.get("customer_id"),
        total_amount=Decimal(str(order_data.get("total_amount", 0))),
        status=order_data.get("status", "Принят"),
        employee_id=current_user.employee_id,
        discount_percent=Decimal(str(order_data.get("discount_percent", 0))),
        payment_type=order_data.get("payment_type"),
        notes=order_data.get("notes")
    )
    
    db.add(order)
    db.flush()  # Получаем ID заказа
    
    # Добавляем позиции заказа
    for item in order_data.get("items", []):
        order_item = OrderItem(
            order_id=order.order_id,
            product_id=item["product_id"],
            quantity=item["quantity"],
            item_price=Decimal(str(item["item_price"])),
            item_discount=Decimal(str(item.get("item_discount", 0)))
        )
        db.add(order_item)
        
        # Создаём запись о движении (триггер БД автоматически обновит stock_quantity)
        movement = StockMovement(
            product_id=item["product_id"],
            movement_type="outgoing",
            quantity=item["quantity"],
            reference_id=order.order_id,
            reference_type="order",
            employee_id=current_user.employee_id,
            notes=f"Заказ #{order.order_id}"
        )
        db.add(movement)
    
    db.commit()
    return {"message": "Заказ создан", "order_id": order.order_id}

@router.get("/customers")
async def get_customers(
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(PermissionCode.CUSTOMERS_VIEW))
):
    customers = db.scalars(select(Customer)).all()
    return customers

@router.get("/products")
async def get_products_for_order(
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(PermissionCode.PRODUCTS_VIEW))
):
    products = db.scalars(select(Product).where(Product.is_active == True)).all()
    return products

@router.get("/{order_id}")
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(PermissionCode.ORDERS_VIEW))
):
    order = db.scalar(select(Orders).where(Orders.order_id == order_id))
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    
    # Получаем позиции заказа
    items = db.scalars(select(OrderItem).where(OrderItem.order_id == order_id)).all()
    
    return {
        "order": order,
        "items": items
    }

@router.put("/{order_id}")
async def update_order(
    order_id: int,
    order_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(PermissionCode.ORDERS_EDIT))
):
    order = db.scalar(select(Orders).where(Orders.order_id == order_id))
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    
    # Обновляем основные поля заказа
    if "customer_id" in order_data:
        order.customer_id = order_data["customer_id"]
    if "status" in order_data:
        order.status = order_data["status"]
    if "payment_type" in order_data:
        order.payment_type = order_data["payment_type"]
    if "discount_percent" in order_data:
        order.discount_percent = Decimal(str(order_data["discount_percent"]))
    if "notes" in order_data:
        order.notes = order_data["notes"]
    if "total_amount" in order_data:
        order.total_amount = Decimal(str(order_data["total_amount"]))
    
    # Обновляем позиции заказа
    if "items" in order_data:
        # Удаляем старые позиции
        db.query(OrderItem).filter(OrderItem.order_id == order_id).delete()
        
        # Добавляем новые позиции
        for item in order_data["items"]:
            order_item = OrderItem(
                order_id=order_id,
                product_id=item["product_id"],
                quantity=item["quantity"],
                item_price=Decimal(str(item["item_price"])),
                item_discount=Decimal(str(item.get("item_discount", 0)))
            )
            db.add(order_item)
    
    db.commit()
    return {"message": "Заказ обновлен"}