from fastapi import APIRouter, UploadFile, HTTPException, Depends, Form, status
import logging
import threading
from sqlalchemy.orm import Session
from typing import Optional

from shared.database import DatabaseManager
from shared.auth import get_current_user
from models.resume import Resume, ResumeStatus
from utils.validators import validate_extension, validate_size, validate_mime, ALLOWED_EXT
from storage.storage_adapter import save_file
from storage.parser import extract_text as parse_text
from utils.publisher import publish_resume


import boto3
from botocore.exceptions import NoCredentialsError

_db_manager = DatabaseManager("resumes")
log = logging.getLogger("resumes-upload")



# Конфигурация S3
S3_ENDPOINT = "https://s3.twcstorage.ru"
S3_ACCESS_KEY = "XV7MOPOCDX3RZCA5ZSFM"
S3_SECRET_KEY = "KDirXBA2Icff7CU9NZJQ2YM8BlZBPeftmlT0eI8Z"
BUCKET_NAME = "2640e22d-9ef3465a-250f-4a31-b297-d4f9faf5d7c3"

# Инициализация клиента S3
s3 = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
)


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
    user = Depends(get_current_user),
):
    log.info(f"got file from user: {user}")
    log.info(f"Upload start: filename={resume.filename} size_header={resume.size if hasattr(resume,'size') else 'n/a'} content_type={resume.content_type}")
    try:
        ext = validate_extension(resume.filename)
        size = validate_size(resume)
        validate_mime(resume.content_type)
    except ValueError as e:
        log.warning(f"Validation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    try:
        # Загрузка файла на S3 в папку с user_id
        user_id = getattr(user, "id", "anonymous")
        object_name = f"uploads/{user_id}/{resume.filename}"
        s3.upload_fileobj(resume.file, BUCKET_NAME, object_name)
        log.info(f"File uploaded to S3: {object_name}")
    except NoCredentialsError:
        log.error("S3 upload failed: No credentials provided")
        raise HTTPException(status_code=500, detail="S3 upload failed: No credentials provided")
    except Exception as e:
        log.error(f"S3 upload failed: {e}")
        raise HTTPException(status_code=500, detail="S3 upload failed")

    return {
        "data": {
            "file_name": resume.filename,
            "file_size": size,
            "status": "uploaded",
            "s3_path": object_name,
            "email_bound": email is not None,
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