from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from app.constants import CATEGORY_NAME_MIN_LENGTH, CATEGORY_NAME_MAX_LENGTH


class CategoryBase(BaseModel):
    name: str = Field(min_length=CATEGORY_NAME_MIN_LENGTH, max_length=CATEGORY_NAME_MAX_LENGTH)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=CATEGORY_NAME_MIN_LENGTH, max_length=CATEGORY_NAME_MAX_LENGTH)


class CategoryDB(CategoryCreate):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
