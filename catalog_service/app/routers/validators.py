import logging
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Category

logger = logging.getLogger(__name__)


async def validate_category_exists(db: AsyncSession, category_id: UUID):
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()

    if not category:
        logger.warning("Validate category exists error: category does not exist", extra={"category_id": str(category_id)})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Category {category_id} does not exist")


async def validate_category_unique(db: AsyncSession, category_name: str):
    result = await db.execute(select(Category).where(Category.name == category_name))
    if result.scalar_one_or_none():
        logger.warning("Validate category unique error: category exists", extra={"category_name": category_name})
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Category {category_name} already exists")
