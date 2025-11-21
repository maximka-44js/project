import uuid
import enum
from sqlalchemy import Column, String, DateTime, Text, Enum, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from shared.database import Base

class ResumeStatus(str, enum.Enum):
    uploaded = "uploaded"
    parsed = "parsed"
    queued = "queued"
    analyzing = "analyzing"
    done = "done"
    error = "error"

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    original_filename = Column(String(255), nullable=False)
    stored_path = Column(String(512), nullable=False)

    mime_type = Column(String(120), nullable=True)
    size_bytes = Column(Integer, nullable=True)

    content_text = Column(Text, nullable=True)
    status = Column(Enum(ResumeStatus), default=ResumeStatus.uploaded, nullable=False)
    error_message = Column(String(512), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())