from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CategoryBase(BaseModel):
    category_name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    category_name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None

class CategoryResponse(CategoryBase):
    category_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    created_by_employee_id: Optional[int]
    updated_by_employee_id: Optional[int]

    class Config:
        from_attributes = True
