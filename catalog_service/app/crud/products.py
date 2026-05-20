import logging
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import PRODUCT_SKIP, PRODUCT_LIMIT
from app.crud.base import CRUDBase
from app.kafka.events import send_product_updated_event
from app.models.product import Product
from app.routers.validators import validate_category_exists
from app.schemas.products import ProductCreate, ProductUpdate

logger = logging.getLogger(__name__)


class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    async def create(self, db: AsyncSession, *, obj_in: ProductCreate) -> Product:
        await validate_category_exists(db=db, category_id=obj_in.category_id)
        result = await super().create(db=db, obj_in=obj_in)

        logger.info("Product created", extra={"product_id": str(result.product_id)})
        return result

    async def get(self, db: AsyncSession, *, product_id: UUID) -> Product:
        product_info = await super().get(db=db, obj_id=product_id)

        if not product_info:
            logger.warning("Product not found", extra={"product_id": str(product_id)})
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product not found")

        return product_info

    async def get_all_products(self, db: AsyncSession, *, skip: int = PRODUCT_SKIP,
                               limit: int = PRODUCT_LIMIT) -> list[Product]:
        return await super().get_multi(db=db, skip=skip, limit=limit)

    async def update(self, db: AsyncSession, *, db_obj: Product, obj_in: ProductUpdate) -> Product:
        if obj_in.category_id is not None and obj_in.category_id != db_obj.category_id:
            await validate_category_exists(db=db, category_id=obj_in.category_id)

        new_values = obj_in.model_dump(exclude_unset=True)
        old_values = {key: getattr(db_obj, key) for key in new_values.keys()}

        result = await super().update(db=db, db_obj=db_obj, obj_in=obj_in)

        send_product_updated_event(product_id=db_obj.id, old_values=old_values, new_values=new_values)
        logger.info("Product updated", extra={
            "product_id": str(result.product_id),
            "new_values": new_values,
        })

        return result

    async def delete(self, db: AsyncSession, *, product_id: UUID) -> Optional[Product]:
        result = await super().delete(db=db, obj_id=product_id)

        if not result:
            logger.warning("Product not found", extra={"product_id": str(product_id)})
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product not found")

        logger.info("Product deleted", extra={"product_id": str(product_id)})
        return result


product_crud = CRUDProduct(Product)
