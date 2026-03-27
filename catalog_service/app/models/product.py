import uuid
from datetime import datetime

from sqlalchemy import Column, UUID, String, DECIMAL, ForeignKey, DateTime

from app.models.db import Base


class Product(Base):
    __tablename__ = 'products'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey('categories.id', ondelete='SET NULL'), nullable=True)
    created_at = Column(DateTime, default=datetime.now)