# routes/categories.py
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

from models.database import get_db
from models.tables import Category, Product
from dependencies import require_permission, get_current_user
from core.permissions import PermissionCode
from schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/categories", tags=["Категории"])


@router.get("/", response_model=List[CategoryResponse])
async def get_categories(
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(PermissionCode.PRODUCTS_VIEW))
):
    """Получить список всех категорий"""
    categories = db.scalars(
        select(Category).order_by(Category.category_name)
    ).all()
    return categories


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(PermissionCode.PRODUCTS_VIEW))
):
    category = db.scalar(select(Category).where(Category.category_id == category_id))
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Категория не найдена")
    return category


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Создать новую категорию"""
    try:
        logger.info(f"Creating category: {category_data.category_name}")
        
        # Проверяем уникальность имени
        existing = db.scalar(select(Category).where(Category.category_name == category_data.category_name))
        if existing:
            logger.warning(f"Category already exists: {category_data.category_name}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Категория с таким названием уже существует")

        # Create the category with current user
        new_cat = Category(
            category_name=category_data.category_name,
            description=category_data.description,
            created_by_employee_id=current_user.employee_id
        )
        db.add(new_cat)
        db.commit()
        db.refresh(new_cat)
        
        logger.info(f"Category created successfully: {new_cat.category_id}")
        return new_cat
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating category: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ошибка при создании категории: {str(e)}")


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Обновить категорию"""
    try:
        category = db.scalar(select(Category).where(Category.category_id == category_id))
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Категория не найдена")

        update_data = category_data.model_dump(exclude_unset=True)
        for k, v in update_data.items():
            setattr(category, k, v)
        category.updated_by_employee_id = current_user.employee_id
        db.commit()
        db.refresh(category)
        return category
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating category {category_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ошибка при обновлении категории: {str(e)}")


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    hard: bool = Query(False, description="Если true — удалить строку из БД; иначе выполнить мягкое удаление"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Удалить категорию.

    При `hard=true` выполняется полноценное удаление (если нет активных товаров).
    При `hard=false` — мягкое удаление: если у модели есть `is_active`, он будет выставлен в False,
    иначе к имени будет добавлен уникальный суффикс "(удалено-<ts>)".
    """
    category = db.scalar(select(Category).where(Category.category_id == category_id))
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Категория не найдена")

    if hard:
        # hard deletion path: block if any active products reference it
        product_exists = db.scalar(
            select(Product.product_id)
            .where(Product.category_id == category_id)
            .where(Product.is_active == True)
            .limit(1)
        )
        if product_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя удалить категорию: к ней привязаны активные товары. Удалите или переназначьте товары сначала."
            )

        try:
            db.delete(category)
            db.commit()
            logger.info(f"Category {category_id} removed from database")
            return
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting category {category_id}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ошибка при удалении категории: {str(e)}")

    # soft-delete path
    try:
        if hasattr(category, 'is_active'):
            setattr(category, 'is_active', False)
            category.updated_by_employee_id = current_user.employee_id
        else:
            import time
            suffix = int(time.time())
            category.category_name = f"{category.category_name} (удалено-{suffix})"
        db.commit()
        logger.info(f"Category {category_id} soft-deleted")
    except Exception as e:
        db.rollback()
        logger.error(f"Error soft-deleting category {category_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ошибка при удалении категории: {str(e)}")