import shutil

import docx
from fastapi import HTTPException, UploadFile, status
from pdfminer.high_level import extract_text as pdf_extract_text

from app.core.config import settings


def validate_file(file: UploadFile, allowed_extensions: set):
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No filename provided.")
    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported file type: .{ext}"
        )
    content = file.file.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")

    # Rewind file after reading
    file.file.seek(0)


def save_upload_file(upload_file: UploadFile, dest_path: str):
    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    upload_file.file.close()


def extract_text_from_pdf(path: str) -> str:
    return pdf_extract_text(path)


def extract_text_from_docx(path: str) -> str:
    doc = docx.Document(path)
    return "\n".join([p.text for p in doc.paragraphs])
