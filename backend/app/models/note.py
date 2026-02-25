import uuid

from sqlalchemy import Column, String, Integer, DateTime, Boolean, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from app.db.base import Base


class Note(Base):
    __tablename__ = "notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    title = Column(String(255), nullable=False)

    subject = Column(String(30), nullable=False)

    file_type = Column(String, nullable=False)

    file_path = Column(String, nullable=False)

    file_size = Column(Integer)

    page_count = Column(Integer)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    upvotes = Column(Integer, default=0)

    download_count = Column(Integer, default=0)

    view_count = Column(Integer, default=0)

    comment_count = Column(Integer, default=0)

    average_rating = Column(Float, default=0.0)

    is_private = Column(Boolean, default=True)

    embedding = Column(Vector(384))