import os
import logging

log = logging.getLogger("resume-parser")

FEATURE_PARSE = os.getenv("FEATURE_PARSE", "1") == "1"
MAX_PARSE_SIZE_MB = int(os.getenv("MAX_PARSE_SIZE_MB", "5"))  # не парсим слишком большие файлы

# Ленивая загрузка библиотек
try:
    import pdfminer as pdfminer
except ImportError:
    pdfminer_high_level = None

try:
    import docx
except ImportError:
    docx = None

try:
    import textract
except ImportError:
    textract = None


def _size_ok(path: str) -> bool:
    try:
        return os.path.getsize(path) <= MAX_PARSE_SIZE_MB * 1024 * 1024
    except OSError:
        return False


def extract_text(path: str, ext: str, mime: str | None) -> tuple[str | None, str | None]:
    """
    Возвращает (text, error_message).
    Если парсинг отключён или слишком большой файл — text=None, error_message=None.
    """
    if not FEATURE_PARSE:
        return None, None

    if not _size_ok(path):
        return None, None  # пропускаем без ошибки

    ext = ext.lower()
    try:
        if ext == "pdf":
            if not pdfminer_high_level:
                return None, "pdfminer.six not installed"
            text = pdfminer_high_level.extract_text(path)
            return text.strip() or None, None

        if ext == "docx":
            if not docx:
                return None, "python-docx not installed"
            d = docx.Document(path)
            text = "\n".join(p.text for p in d.paragraphs)
            return text.strip() or None, None

        if ext == "doc":
            if not textract:
                return None, "textract not installed"
            raw = textract.process(path)
            return raw.decode("utf-8", errors="ignore").strip() or None, None

        if ext == "txt":
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                data = f.read()
            return data.strip() or None, None

        return None, f"Unsupported extension for parsing: {ext}"
    except Exception as e:
        log.warning(f"Parse error for {path}: {e}")
        return None, f"Parse error: {e}"