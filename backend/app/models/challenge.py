from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db.base import Base


class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    topic_key = Column(String, unique=True, nullable=False)

    reward_credits = Column(Integer, default=50)

    demand_count = Column(Integer, default=1)

    days_active = Column(Integer, default=1)

    is_active = Column(Boolean, default=True)