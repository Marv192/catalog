from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import CATEGORY_LIMIT, CATEGORY_SKIP
from app.crud.base import CRUDBase
from app.models import Product
from app.models.category import Category
from app.routers.validators import validate_category_unique
from app.schemas.categories import CategoryCreate, CategoryUpdate
from app.utils.cache import get_cached, set_cache


class CRUDCategory(CRUDBase[Category, CategoryCreate, CategoryUpdate]):
    async def create(self, db: AsyncSession, *, obj_in: CategoryCreate) -> Category:
        await validate_category_unique(db=db, category_name=obj_in.name)
        return await super().create(db=db, obj_in=obj_in)

    async def get(self, db: AsyncSession, *, category_id: UUID) -> Optional[Category]:
        category_info = await super().get(db=db, obj_id=category_id)

        if not category_info:
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

        await set_cache("categories", categories)

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

        return await super().update(db=db, db_obj=db_obj, obj_in=obj_in)

    async def delete(self, db: AsyncSession, *, category_id: UUID) -> Optional[Category]:
        result = await super().delete(db=db, obj_id=category_id)

        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

        return result


category_crud = CRUDCategory(Category)
