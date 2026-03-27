from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.kafka.events import send_product_updated_event
from app.models.product import Product
from app.schemas.products import ProductCreate, ProductUpdate


class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    async def create(self, db: AsyncSession, *, obj_in: ProductCreate) -> Product:
        try:
            product = await super().create(db=db, obj_in=obj_in)
            await db.commit()
            await db.refresh(product)
            return product

        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Category with id {obj_in.category_id} does not exist")


    async def get(self, db: AsyncSession, *, product_id: UUID) -> Product:
        product_info = await super().get(db=db, obj_id=product_id)

        if not product_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product not found")

        return product_info

    async def get_all_products(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> list[Product]:
        return await super().get_multi(db=db, skip=skip, limit=limit)

    async def update(self, db: AsyncSession, *, db_obj: Product, obj_in: ProductUpdate) -> Product:
        try:
            new_values = obj_in.model_dump(exclude_unset=True)
            old_values = {key: getattr(db_obj, key) for key in new_values.keys()}

            await super().update(db=db, db_obj=db_obj, obj_in=obj_in)
            await db.commit()
            await db.refresh(db_obj)

            send_product_updated_event(product_id=db_obj.id, old_values=old_values, new_values=new_values)

            return db_obj

        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Invalid category_id: category does not exist")

    async def delete(self, db: AsyncSession, *, product_id: UUID) -> Optional[Product]:
        try:
            result = await super().delete(db=db, obj_id=product_id)

            if not result:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product not found")

            await db.commit()
            return result

        except HTTPException:
            await db.rollback()
            raise

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


product_crud = CRUDProduct(Product)