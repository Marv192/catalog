import logging
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.constants import CATEGORY_LIMIT, CATEGORY_SKIP
from app.crud.base import CRUDBase
from app.models import Product
from app.models.category import Category
from app.routers.validators import validate_category_unique
from app.schemas.categories import CategoryCreate, CategoryUpdate
from app.utils.cache import get_cached, set_cache, delete_cache

logger = logging.getLogger(__name__)


class CRUDCategory(CRUDBase[Category, CategoryCreate, CategoryUpdate]):
    async def create(self, db: AsyncSession, *, obj_in: CategoryCreate) -> Category:
        await validate_category_unique(db=db, category_name=obj_in.name)
        new_category = await super().create(db=db, obj_in=obj_in)

        await delete_cache('categories')
        logger.info("Category created", extra={
            "category_id": str(new_category.id),
            "category_name": new_category.name
        })
        return new_category

    async def get(self, db: AsyncSession, *, category_id: UUID) -> Optional[Category]:
        category_info = await super().get(db=db, obj_id=category_id)

        if not category_info:
            logger.warning("Category not found", extra={"category_id": str(category_id)})
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

        return category_info

    async def get_all_categories(self, db: AsyncSession, *, skip: int = CATEGORY_SKIP,
                                 limit: int = CATEGORY_LIMIT) -> list[dict]:
        cached = await get_cached('categories')

        if cached:
            return cached

        db_categories = await super().get_multi(db=db, skip=skip, limit=limit)
        categories = [{"id": str(cat.id),
                       "name": cat.name,
                       "created_at": cat.created_at.isoformat()}
                      for cat in db_categories]

        await set_cache("categories", categories, settings.cache_ttl)

        return categories

    async def get_category_products(self, db: AsyncSession, *, category_id: UUID,
                                    skip: int = CATEGORY_SKIP, limit: int = CATEGORY_LIMIT) -> list[Product]:
        await category_crud.get(db=db, category_id=category_id)
        stmt = select(Product).where(Product.category_id == category_id).offset(skip).limit(limit)
        result = await db.execute(stmt)
        products = list(result.scalars().all())
        return products

    async def update(self, db: AsyncSession, *, db_obj: Category, obj_in: CategoryUpdate) -> Category:
        if obj_in.name is not None and obj_in.name != db_obj.name:
            await validate_category_unique(db=db, category_name=obj_in.name)

        updated_category = await super().update(db=db, db_obj=db_obj, obj_in=obj_in)

        await delete_cache('categories')
        logger.info("Category updated", extra={
            "category_id": str(updated_category.id),
            "new_category_name": updated_category.name
        })
        return updated_category

    async def delete(self, db: AsyncSession, *, category_id: UUID) -> Optional[Category]:
        result = await super().delete(db=db, obj_id=category_id)

        if not result:
            logger.warning("Category not found", extra={"category_id": str(category_id)})
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

        await delete_cache('categories')
        logger.info("Category deleted", extra={"category_id": str(category_id)})
        return result


category_crud = CRUDCategory(Category)
