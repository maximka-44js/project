from fastapi import APIRouter, UploadFile, HTTPException, Depends, Form
from sqlalchemy.orm import Session
from typing import Optional

from shared.database import DatabaseManager
from shared.auth import get_current_user_optional
from models.resume import Resume, ResumeStatus
from utils.validators import validate_extension, validate_size, validate_mime, ALLOWED_EXT
from storage.storage_adapter import save_file
from storage.parser import extract_text as parse_text
from utils.publisher import publish_resume

_db_manager = DatabaseManager("resumes")

def get_db():
    db = _db_manager.get_session()
    try:
        yield db
    finally:
        db.close()

router = APIRouter(tags=["resumes"])

@router.get("/supported-formats")
def supported_formats():
    return {"data": [f".{ext}" for ext in sorted(ALLOWED_EXT)], "success": True}

@router.post("/upload")
async def upload_resume(
    resume: UploadFile,
    email: Optional[str] = Form(default=None),
    db: Session = Depends(get_db),
    user = Depends(get_current_user_optional),
):
    try:
        ext = validate_extension(resume.filename)
        size = validate_size(resume)
        validate_mime(resume.content_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    stored_path, _ = save_file(resume)

    # Парсим на основе сохранённого пути (локально) или пропускаем если S3 (текст уже в памяти)
    text, parse_error = parse_text(stored_path, ext, resume.content_type)
    status = ResumeStatus.parsed if text else ResumeStatus.uploaded
    if parse_error and not text:
        status = ResumeStatus.uploaded  # парсинг не критичен на этапе загрузки

    record = Resume(
        user_id=getattr(user, "id", None),
        original_filename=resume.filename,
        stored_path=stored_path,
        mime_type=resume.content_type,
        size_bytes=size,
        status=status,
        content_text=text,
        error_message=parse_error,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    publish_resume(str(record.id))  # заглушка

    return {
        "data": {
            "upload_id": str(record.id),
            "file_name": record.original_filename,
            "file_size": record.size_bytes,
            "status": record.status,
            "analysis_id": None,
            "email_bound": email is not None,
            "has_text": bool(record.content_text),
            "parse_error": record.error_message,
        },
        "success": True,
    }

@router.get("/{resume_id}/content")
def get_content(resume_id: str, db: Session = Depends(get_db)):
    rec = db.query(Resume).filter(Resume.id == resume_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Not found")
    return {
        "data": {
            "resume_id": str(rec.id),
            "status": rec.status,
            "text": rec.content_text,
            "error": rec.error_message,
        },
        "success": True,
    }

@router.get("/{resume_id}/status")
def get_status(resume_id: str, db: Session = Depends(get_db)):
    rec = db.query(Resume).filter(Resume.id == resume_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Not found")
    return {"data": {"resume_id": str(rec.id), "status": rec.status}, "success": True}