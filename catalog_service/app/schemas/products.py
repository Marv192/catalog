from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

NAME_MIN_LENGTH = 1
NAME_MAX_LENGTH = 64
DESCRIPTION_MIN_LENGTH = 1
DESCRIPTION_MAX_LENGTH = 1000
PRICE_MAX_DIGITS = 10
PRICE_MIN_VALUE = 0
PRICE_DECIMAL_PLACES = 2


class ProductBase(BaseModel):
    name: str = Field(min_length=NAME_MIN_LENGTH, max_length=NAME_MAX_LENGTH)
    description: str = Field(min_length=DESCRIPTION_MIN_LENGTH, max_length=DESCRIPTION_MAX_LENGTH)
    price: Decimal = Field(gt=PRICE_MIN_VALUE, decimal_places=PRICE_DECIMAL_PLACES, max_digits=PRICE_MAX_DIGITS)
    category_id: UUID


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=NAME_MIN_LENGTH, max_length=NAME_MAX_LENGTH)
    description: Optional[str] = Field(default=None, min_length=DESCRIPTION_MIN_LENGTH,
                                       max_length=DESCRIPTION_MAX_LENGTH)
    price: Optional[Decimal] = Field(default=None, gt=PRICE_MIN_VALUE, decimal_places=PRICE_DECIMAL_PLACES,
                                     max_digits=PRICE_MAX_DIGITS)
    category_id: Optional[UUID] = None


class ProductInfo(ProductCreate):
    category_id: UUID | None


class ProductDB(ProductCreate):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
