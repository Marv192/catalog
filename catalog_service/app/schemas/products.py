from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    description: str = Field(min_length=1, max_length=1000)
    price: Decimal = Field(gt=0, decimal_places=2, max_digits=10)
    category_id: UUID

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=64)
    description: Optional[str] = Field(default=None, min_length=1, max_length=1000)
    price: Optional[Decimal] = Field(default=None, gt=0, decimal_places=2, max_digits=10)
    category_id: Optional[UUID] = None

class ProductInfo(ProductCreate):
    category_id: UUID | None

class ProductDB(ProductCreate):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)