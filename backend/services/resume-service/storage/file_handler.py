import os
import uuid
from utils.validators import validate_extension

STORAGE_ROOT = os.getenv("RESUME_STORAGE_ROOT", "/data/resumes")


def ensure_storage_root():
    """Создать директорию для хранения файлов."""
    os.makedirs(STORAGE_ROOT, exist_ok=True)


def save_file(upload_file) -> tuple[str, str]:
    """Сохранить файл на диск. Возвращает (stored_path, stored_name)."""
    ensure_storage_root()
    ext = validate_extension(upload_file.filename)
    uid = str(uuid.uuid4())
    stored_name = f"{uid}.{ext}"
    path = os.path.join(STORAGE_ROOT, stored_name)
    
    with open(path, "wb") as f:
        f.write(upload_file.file.read())
    upload_file.file.seek(0)  # reset для повторного чтения если нужно
    
    return path, stored_name
