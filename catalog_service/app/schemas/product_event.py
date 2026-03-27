import uuid
from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class ProductUpdateField(str, Enum):
    NAME = "name"
    DESCRIPTION = "description"
    PRICE = "price"
    CATEGORY_ID = "category_id"

class EventMetadata(BaseModel):
    event_id: UUID = Field(default_factory=uuid.uuid4)
    event_type: str = Field(default="product.updated")
    timestamp: datetime = Field(default_factory=datetime.now)

class ProductUpdatedData(BaseModel):
    product_id: UUID
    old_values: dict
    new_values: dict
    updated_at: datetime = Field(default_factory=datetime.now)

class ProductUpdatedEvent(BaseModel):
    metadata: EventMetadata = Field(default_factory=EventMetadata)
    data: ProductUpdatedData
