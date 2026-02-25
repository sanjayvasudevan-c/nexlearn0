import uuid
from sqlalchemy import Column, String, Integer, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.base import Base


class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    topic_key = Column(String, nullable=False, unique=True)

    reward_credits = Column(Integer, default=50)

    demand_count = Column(Integer, default=0)

    is_active = Column(Boolean, default=True)

    winner_note_id = Column(UUID(as_uuid=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())