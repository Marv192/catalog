from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from app.constants import PRODUCT_NAME_MIN_LENGTH, PRODUCT_NAME_MAX_LENGTH, PRODUCT_DESCRIPTION_MIN_LENGTH, \
    PRODUCT_DESCRIPTION_MAX_LENGTH, PRODUCT_PRICE_MIN_VALUE, PRODUCT_PRICE_DECIMAL_PLACES, PRODUCT_PRICE_MAX_DIGITS


class ProductBase(BaseModel):
    name: str = Field(min_length=PRODUCT_NAME_MIN_LENGTH, max_length=PRODUCT_NAME_MAX_LENGTH)
    description: str = Field(min_length=PRODUCT_DESCRIPTION_MIN_LENGTH, max_length=PRODUCT_DESCRIPTION_MAX_LENGTH)
    price: Decimal = Field(gt=PRODUCT_PRICE_MIN_VALUE, decimal_places=PRODUCT_PRICE_DECIMAL_PLACES,
                           max_digits=PRODUCT_PRICE_MAX_DIGITS)
    category_id: UUID


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=PRODUCT_NAME_MIN_LENGTH, max_length=PRODUCT_NAME_MAX_LENGTH)
    description: Optional[str] = Field(default=None, min_length=PRODUCT_DESCRIPTION_MIN_LENGTH,
                                       max_length=PRODUCT_DESCRIPTION_MAX_LENGTH)
    price: Optional[Decimal] = Field(default=None, gt=PRODUCT_PRICE_MIN_VALUE,
                                     decimal_places=PRODUCT_PRICE_DECIMAL_PLACES,
                                     max_digits=PRODUCT_PRICE_MAX_DIGITS)
    category_id: Optional[UUID] = None


class ProductInfo(ProductCreate):
    category_id: UUID | None


class ProductDB(ProductCreate):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
