# routes/products.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional

from models.database import get_db
from models.tables import Product, Category, Supplier, Employee
from dependencies import require_permission, get_current_user
from core.permissions import PermissionCode

# Импортируем схемы ТОЛЬКО из schemas.product
from schemas.product import ProductCreate, ProductUpdate, ProductResponse

router = APIRouter(
    prefix="/api/products",
    tags=["Товары"]
)

@router.get("/", response_model=List[ProductResponse])
async def get_products(
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None,
    supplier_id: Optional[int] = None,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission(PermissionCode.PRODUCTS_VIEW))
):
    """
    Получить список товаров с фильтрацией
    """
    query = select(Product)
    
    # active_only controls filtering explicitly:
    # - True  => only active products
    # - False => only inactive products
    # - None  => no filter (all products)
    if active_only is True:
        query = query.where(Product.is_active == True)
    elif active_only is False:
        query = query.where(Product.is_active == False)
    
    if category_id:
        query = query.where(Product.category_id == category_id)
    
    if supplier_id:
        query = query.where(Product.supplier_id == supplier_id)
    
    query = query.offset(skip).limit(limit)
    
    products = db.scalars(query).all()
    return products

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission(PermissionCode.PRODUCTS_VIEW))
):
    """
    Получить информацию о конкретном товаре
    """
    product = db.scalar(select(Product).where(Product.product_id == product_id))
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар не найден"
        )
    
    return product

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission(PermissionCode.PRODUCTS_CREATE))
):
    """
    Создать новый товар
    """
    # Проверяем существование категории
    category = db.scalar(
        select(Category).where(Category.category_id == product_data.category_id)
    )
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Указанная категория не существует"
        )
    
    # Проверяем существование поставщика (если указан)
    if product_data.supplier_id:
        supplier = db.scalar(
            select(Supplier).where(Supplier.supplier_id == product_data.supplier_id)
        )
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Указанный поставщик не существует"
            )
    
    # Проверяем уникальность баркода (если указан)
    if product_data.barcode:
        existing_product = db.scalar(
            select(Product).where(Product.barcode == product_data.barcode)
        )
        if existing_product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Товар с таким штрихкодом уже существует"
            )
    
    # Подготавливаем данные для создания
    product_dict = product_data.model_dump()
    
    # Создаем новый товар
    new_product = Product(
        **product_dict,
        created_by_employee_id=current_user.employee_id
    )
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    return new_product

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission(PermissionCode.PRODUCTS_EDIT))
):
    """
    Обновить информацию о товаре
    """
    product = db.scalar(select(Product).where(Product.product_id == product_id))
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар не найден"
        )
    
    # Проверяем уникальность нового баркода (если меняется)
    if product_data.barcode and product_data.barcode != product.barcode:
        existing_product = db.scalar(
            select(Product).where(
                Product.barcode == product_data.barcode,
                Product.product_id != product_id
            )
        )
        if existing_product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Товар с таким штрихкодом уже существует"
            )
    
    # Обновляем поля (с преобразованием float -> Decimal для price и weight)
    from decimal import Decimal
    update_data = product_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:  # Проверяем, что значение не None
            # Для полей price и weight применяем преобразование float -> Decimal
            if field in ('price', 'weight') and isinstance(value, (int, float)):
                value = Decimal(str(value))
            setattr(product, field, value)
    
    # Обновляем ID сотрудника, который внес изменения
    product.updated_by_employee_id = current_user.employee_id
    
    db.commit()
    db.refresh(product)
    
    return product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    hard: bool = Query(False, description="Если true — выполнится жёсткое удаление из БД; иначе — мягкое (is_active=False)"),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission(PermissionCode.PRODUCTS_DELETE))
):
    """
    Удалить товар.

    Если `hard=true` — попробуем удалить запись из БД (будет отказано при наличии ссылок).
    Если `hard=false` — выполним мягкое удаление: установим `is_active=False`.
    """
    product = db.scalar(select(Product).where(Product.product_id == product_id))

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар не найден"
        )

    if not hard:
        # soft-delete
        try:
            setattr(product, 'is_active', False)
            setattr(product, 'updated_by_employee_id', current_user.employee_id)
            db.commit()
            return
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ошибка при деактивации товара: {str(e)}")

    # hard delete path
    from models.tables import OrderItem, PurchaseItem

    referenced = db.scalar(select(OrderItem.order_item_id).where(OrderItem.product_id == product_id).limit(1))
    if referenced:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Товар используется в заказах и не может быть удалён")

    referenced = db.scalar(select(PurchaseItem.purchase_item_id).where(PurchaseItem.product_id == product_id).limit(1))
    if referenced:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Товар используется в поступлениях и не может быть удалён")

    try:
        db.delete(product)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ошибка при удалении товара: {str(e)}")