from sqlalchemy import Column, ForeignKey, DateTime, Enum, UniqueConstraint, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum

from app.db.base import Base


class SubmissionStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ChallengeSubmission(Base):
    __tablename__ = "challenge_submissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    challenge_id = Column(UUID(as_uuid=True), ForeignKey("challenges.id"))
    note_id = Column(UUID(as_uuid=True), ForeignKey("notes.id"))

    user_id = Column(Integer, ForeignKey("users.id"))  # FIXED

    status = Column(Enum(SubmissionStatus), default=SubmissionStatus.PENDING)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint(
            "challenge_id",
            "note_id",
            name="unique_note_challenge_submission"
        ),
    )