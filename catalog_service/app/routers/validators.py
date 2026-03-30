from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Category


async def validate_category_exists(db: AsyncSession, category_id: UUID):
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Category {category_id} does not exist")

async def validate_category_unique(db: AsyncSession, category_name: str):
    result = await db.execute(select(Category).where(Category.name == category_name))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Category {category_name} already exists")

