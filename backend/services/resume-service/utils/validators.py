ALLOWED_EXT = {"pdf", "doc", "docx", "txt"}
ALLOWED_MIME = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
}

import os
MAX_SIZE_MB = int(os.getenv("MAX_RESUME_SIZE_MB", "10"))

def validate_extension(filename: str):
    if "." not in filename:
        raise ValueError("No extension")
    ext = filename.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXT:
        raise ValueError(f"Unsupported extension: {ext}")
    return ext

def validate_size(upload_file):
    upload_file.file.seek(0, 2)
    size = upload_file.file.tell()
    upload_file.file.seek(0)
    if size == 0:
        raise ValueError("Empty file")
    if size > MAX_SIZE_MB * 1024 * 1024:
        raise ValueError(f"File too large (> {MAX_SIZE_MB}MB)")
    return size

def validate_mime(mime: str | None):
    if mime and mime not in ALLOWED_MIME:
        raise ValueError(f"Unsupported MIME: {mime}")
    return mime