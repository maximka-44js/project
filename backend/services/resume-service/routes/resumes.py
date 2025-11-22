import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi import Depends
from sqlalchemy.orm import Session
from shared.database import DatabaseManager
from models.resume import ResumeFile
from utils.validators import validate_extension, parse_file, ALLOWED_FORMATS
from shared.auth import get_current_user_optional

SERVICE_NAME = "resumes"
router = APIRouter()

db_manager = DatabaseManager(SERVICE_NAME)


def get_db():
	db = db_manager.get_session()
	try:
		yield db
	finally:
		db.close()


STORAGE_ROOT = os.getenv("RESUME_STORAGE_PATH", "storage/resumes")
ORIGINAL_DIR = os.path.join(STORAGE_ROOT, "original")
PROCESSED_DIR = os.path.join(STORAGE_ROOT, "processed")
os.makedirs(ORIGINAL_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

FEATURE_PARSE = os.getenv("FEATURE_PARSE", "1") == "1"


@router.get("/supported-formats")
def supported_formats():
	return {"formats": ALLOWED_FORMATS}


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user_optional),
):
	try:
		ext = validate_extension(file.filename)
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))

	resume_id = uuid.uuid4()
	stored_filename = f"{resume_id}.{ext}"
	stored_path = os.path.join(ORIGINAL_DIR, stored_filename)

	contents = await file.read()
	with open(stored_path, 'wb') as f:
		f.write(contents)

	text_content = None
	if FEATURE_PARSE:
		text_content = parse_file(stored_path, ext)
		if text_content:
			processed_path = os.path.join(PROCESSED_DIR, f"{resume_id}.txt")
			with open(processed_path, 'w', encoding='utf-8') as out:
				out.write(text_content)

	resume_row = ResumeFile(
		uid=int(user.id) if user else None,
		id=resume_id,
		original_filename=file.filename,
		stored_path=stored_path,
		file_type=ext,
		text_content=text_content,
	)
	db.add(resume_row)
	db.commit()
	db.refresh(resume_row)

	return {"id": str(resume_row.id), "parsed": text_content is not None}


@router.get("/{resume_id}/content")
def get_content(resume_id: uuid.UUID, db: Session = Depends(get_db)):
	resume = db.query(ResumeFile).filter(ResumeFile.id == resume_id).first()
	if not resume:
		raise HTTPException(status_code=404, detail="Resume not found")
	return {
		"id": str(resume.id),
		"filename": resume.original_filename,
		"file_type": resume.file_type,
		"uploaded_at": resume.uploaded_at.isoformat(),
		"text": resume.text_content,
	}
