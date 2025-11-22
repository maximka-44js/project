from fastapi import APIRouter, UploadFile, HTTPException, Depends, Form, status
import logging
import threading
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
log = logging.getLogger("resumes-upload")

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

@router.get("/")
def list_resumes(db: Session = Depends(get_db)):
    """List all resumes with basic info"""
    resumes = db.query(Resume).order_by(Resume.created_at.desc()).limit(50).all()
    return {
        "data": [
            {
                "id": str(r.id),
                "filename": r.original_filename,
                "status": r.status,
                "size_bytes": r.size_bytes,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in resumes
        ],
        "success": True,
    }

@router.post("/upload")
async def upload_resume(
    resume: UploadFile,
    email: Optional[str] = Form(default=None),
    db: Session = Depends(get_db),
    user = Depends(get_current_user_optional),
):
    log.info(f"Upload start: filename={resume.filename} size_header={resume.size if hasattr(resume,'size') else 'n/a'} content_type={resume.content_type}")
    try:
        ext = validate_extension(resume.filename)
        size = validate_size(resume)
        validate_mime(resume.content_type)
    except ValueError as e:
        log.warning(f"Validation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    stored_path, _ = save_file(resume)
    log.info(f"File saved to {stored_path}")

    # Create record with uploaded status first (non-blocking parsing will update later)
    record = Resume(
        user_id=getattr(user, "id", None),
        original_filename=resume.filename,
        stored_path=stored_path,
        mime_type=resume.content_type,
        size_bytes=size,
        status=ResumeStatus.uploaded,
    )
    try:
        db.add(record)
        db.commit()
        db.refresh(record)
    except Exception:
        log.error("DB commit failed during upload")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="database_unavailable")

    def _parse_and_update(resume_id: str, path: str, ext_local: str, mime_local: str | None):
        log.info(f"Background parse start id={resume_id}")
        text, parse_error = parse_text(path, ext_local, mime_local)
        try:
            sess = _db_manager.get_session()
            rec = sess.query(Resume).filter(Resume.id == resume_id).first()
            if rec:
                if text:
                    rec.content_text = text
                    rec.status = ResumeStatus.parsed
                if parse_error and not text:
                    rec.error_message = parse_error
                sess.commit()
                log.info(f"Background parse done id={resume_id} status={rec.status} error={rec.error_message}")
            sess.close()
        except Exception as e:
            log.error(f"Background parse failed id={resume_id}: {e}")

    threading.Thread(target=_parse_and_update, args=(str(record.id), stored_path, ext, resume.content_type), daemon=True).start()
    publish_resume(str(record.id))  # заглушка (очередь анализа)

    return {
        "data": {
            "upload_id": str(record.id),
            "file_name": record.original_filename,
            "file_size": record.size_bytes,
            "status": record.status,
            "analysis_id": None,
            "email_bound": email is not None,
            "has_text": False,
            "parse_error": None,
            "processing": True,
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