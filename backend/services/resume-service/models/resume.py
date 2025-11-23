import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from shared.database import Base
from sqlalchemy.inspection import inspect

class ResumeFile(Base):
    __tablename__ = "resumes"
    uid = Column(Integer, nullable=True, index=True)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_filename = Column(String(255), nullable=False)
    stored_path = Column(String(512), nullable=False)
    file_type = Column(String(16), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    text_content = Column(Text, nullable=True)

    def as_dict(self):
        data = {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}
        data["id"] = str(data["id"])
        data["has_text"] = self.text_content is not None
        return data

    def to_dict(self):
        return {
            "id": str(self.id),
            "uid": self.uid,
            "original_filename": self.original_filename,
            "file_type": self.file_type,
            "uploaded_at": self.uploaded_at.isoformat(),
            "has_text": self.text_content is not None,
        }