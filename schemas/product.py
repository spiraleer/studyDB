# schemas/product.py - ПРАВИЛЬНАЯ ВЕРСИЯ
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from decimal import Decimal

class ProductBase(BaseModel):
    product_name: str = Field(..., min_length=1, max_length=100, description="Название товара")
    description: Optional[str] = Field(None, description="Описание товара")
    unit: str = Field(..., max_length=20, description="Единица измерения (шт, кг, л и т.д.)")
    category_id: int = Field(..., description="ID категории")
    price: float = Field(..., gt=0, description="Цена товара")
    stock_quantity: int = Field(default=0, ge=0, description="Количество на складе")
    barcode: Optional[str] = Field(None, max_length=50, description="Штрихкод")
    supplier_id: Optional[int] = Field(None, description="ID поставщика")
    weight: Optional[float] = Field(None, ge=0, description="Вес (кг)")
    is_active: bool = Field(default=True, description="Активен ли товар")
    
    @validator('price')
    def validate_price(cls, v):
        """Преобразуем float в Decimal для SQLAlchemy"""
        if v is not None:
            return Decimal(str(v))
        return v
    
    @validator('weight')
    def validate_weight(cls, v):
        """Преобразуем float в Decimal для SQLAlchemy"""
        if v is not None:
            return Decimal(str(v))
        return v

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    product_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    unit: Optional[str] = Field(None, max_length=20)
    category_id: Optional[int] = None
    price: Optional[float] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    barcode: Optional[str] = Field(None, max_length=50)
    supplier_id: Optional[int] = None
    weight: Optional[float] = Field(None, ge=0)
    is_active: Optional[bool] = None
    
    @validator('price')
    def validate_price(cls, v):
        if v is not None:
            return Decimal(str(v))
        return v
    
    @validator('weight')
    def validate_weight(cls, v):
        if v is not None:
            return Decimal(str(v))
        return v

class ProductResponse(ProductBase):
    product_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    created_by_employee_id: Optional[int]
    updated_by_employee_id: Optional[int]
    
    class Config:
        from_attributes = True