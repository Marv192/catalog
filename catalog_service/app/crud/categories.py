from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Product
from app.models.category import Category
from app.schemas.categories import CategoryCreate, CategoryUpdate
from app.utils.cache import get_cached, set_cache


class CRUDCategory(CRUDBase[Category, CategoryCreate, CategoryUpdate]):
    async def create(self, db: AsyncSession, *, obj_in: CategoryCreate) -> Category:
        try:
            category = await super().create(db=db, obj_in=obj_in)
            await db.commit()
            await db.refresh(category)
            return category

        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"Category with name {obj_in.name} already exists")

    async def get(self, db: AsyncSession, *, category_id: UUID) -> Optional[Category]:
        category_info = await super().get(db=db, obj_id=category_id)

        if not category_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

        return category_info

    async def get_all_categories(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> list[dict]:
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
                                            skip: int = 0, limit: int = 100) -> list[Product]:
        await category_crud.get(db=db, category_id=category_id)
        stmt = select(Product).where(Product.category_id == category_id).offset(skip).limit(limit)
        result = await db.execute(stmt)
        products = list(result.scalars().all())
        return products

    async def update(self, db: AsyncSession, *, db_obj: Category, obj_in: CategoryUpdate) -> Category:
        try:
            category = await super().update(db=db, db_obj=db_obj, obj_in=obj_in)
            await db.commit()
            await db.refresh(category)
            return category

        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"Category with name {obj_in.name} already exists")

    async def delete(self, db: AsyncSession, *, category_id: UUID) -> Optional[Category]:
        try:
            result = await super().delete(db=db, obj_id=category_id)

            if not result:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

            await db.commit()
            return result

        except HTTPException:
            await db.rollback()
            raise

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

category_crud = CRUDCategory(Category)