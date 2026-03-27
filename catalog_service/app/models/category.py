import uuid
from datetime import datetime

from sqlalchemy import Column, UUID, String, DateTime

from app.models.db import Base


class Category(Base):
    __tablename__ = "categories"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.now)