from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class CategoryBase(BaseModel):
    name: str = Field(min_length=1, max_length=64)

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=64)

class CategoryDB(CategoryCreate):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)