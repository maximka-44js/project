import uuid
import enum
from sqlalchemy import Column, String, DateTime, Text, Enum, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from shared.database import Base


class AnalysisStatus(str, enum.Enum):
    processing = "processing"
    completed = "completed"
    error = "error"


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    upload_id = Column(UUID(as_uuid=True), nullable=False)  # Ссылка на resume upload
    user_id = Column(UUID(as_uuid=True), nullable=True)  # Опциональный user
    email = Column(String(254), nullable=True)  # Email для отправки результатов

    status = Column(Enum(AnalysisStatus), default=AnalysisStatus.processing, nullable=False)
    results = Column(JSONB, nullable=True)  # JSON с position_levels, market_data, recommendations
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)