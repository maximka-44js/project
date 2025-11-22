import os
import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
import time

log = logging.getLogger("resume-parser")

FEATURE_PARSE = os.getenv("FEATURE_PARSE", "1") == "1"
MAX_PARSE_SIZE_MB = int(os.getenv("MAX_PARSE_SIZE_MB", "5"))  # не парсим слишком большие файлы

# Ленивая загрузка библиотек
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    import docx
except ImportError:
    docx = None

try:
    import docx2txt
except ImportError:
    docx2txt = None


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
        log.debug(f"Parsing disabled for {path}")
        return None, None

    if not os.path.exists(path):
        log.warning(f"File not found for parsing: {path}")
        return None, "File not found"

    if not _size_ok(path):
        log.debug(f"File too large for parsing: {path}")
        return None, None  # пропускаем без ошибки

    log.info(f"Starting parse for {path} (ext={ext})")
    
    # Use timeout to prevent hanging
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_do_parse, path, ext)
        try:
            result = future.result(timeout=30)  # 30 second timeout
            log.info(f"Parse completed for {path}")
            return result
        except FuturesTimeoutError:
            log.error(f"Parse timeout for {path}")
            return None, "Parse timeout (30s exceeded)"
        except Exception as e:
            log.error(f"Parse executor error for {path}: {e}")
            return None, str(e)


def _do_parse(path: str, ext: str) -> tuple[str | None, str | None]:
    """Actual parsing logic without timeout wrapper"""
    ext = ext.lower()
    try:
        if ext == "pdf":
            if not PdfReader:
                return None, "pypdf not installed"
            try:
                reader = PdfReader(path)
                pages_text = []
                for p in reader.pages:
                    try:
                        pages_text.append(p.extract_text() or "")
                    except Exception as pe:
                        log.debug(f"Page parse error: {pe}")
                        continue
                text = "\n".join(pages_text)
                return text.strip() or None, None
            except Exception as pe:
                return None, f"PDF parse error: {pe}"

        if ext == "docx":
            if not docx:
                return None, "python-docx not installed"
            d = docx.Document(path)
            text = "\n".join(p.text for p in d.paragraphs)
            return text.strip() or None, None

        if ext == "doc":
            if not docx2txt:
                return None, "docx2txt not installed"
            text = docx2txt.process(path)
            return text.strip() or None, None

        if ext == "txt":
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                data = f.read()
            return data.strip() or None, None

        return None, f"Unsupported extension for parsing: {ext}"
    except Exception as e:
        log.warning(f"Parse error for {path}: {e}")
        return None, f"Parse error: {e}"