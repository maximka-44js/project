import os
from typing import List

ALLOWED_FORMATS: List[str] = ["pdf", "doc", "docx", "txt"]


def get_extension(filename: str) -> str:
	return filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''


def validate_extension(filename: str) -> str:
	ext = get_extension(filename)
	if ext not in ALLOWED_FORMATS:
		raise ValueError(f"Unsupported file format: {ext}")
	return ext


def parse_file(path: str, ext: str) -> str | None:
	"""Return extracted text or None if unsupported/failed."""
	if not os.path.exists(path):
		return None

	try:
		if ext == "txt":
			with open(path, 'r', encoding='utf-8', errors='ignore') as f:
				return f.read()
		if ext == "pdf":
			from pypdf import PdfReader
			text_parts = []
			reader = PdfReader(path)
			for page in reader.pages:
				page_text = page.extract_text() or ""
				text_parts.append(page_text)
			return "\n".join(text_parts).strip() or None
		if ext == "docx":
			try:
				import docx2txt
				extracted = docx2txt.process(path)
				return extracted.strip() if extracted else None
			except Exception:
				from docx import Document
				doc = Document(path)
				return "\n".join(p.text for p in doc.paragraphs).strip() or None
		return None
	except Exception:
		return None
