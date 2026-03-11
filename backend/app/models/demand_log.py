from sqlalchemy import Column, Date, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base


class DemandLog(Base):
    __tablename__ = "demand_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    query = Column(String, nullable=False)
    topic_key = Column(String, nullable=False)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    search_date = Column(Date, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "topic_key",
            "search_date",
            name="unique_user_topic_day"
        ),
    )