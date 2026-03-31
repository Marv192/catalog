from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

NAME_MIN_LENGTH = 1
NAME_MAX_LENGTH = 64


class CategoryBase(BaseModel):
    name: str = Field(min_length=NAME_MIN_LENGTH, max_length=NAME_MAX_LENGTH)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=NAME_MIN_LENGTH, max_length=NAME_MAX_LENGTH)


class CategoryDB(CategoryCreate):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
