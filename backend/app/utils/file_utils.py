import os
from typing import Optional
from fastapi import HTTPException, status

def get_file_extension(filename: str) -> str:
    """Get the file extension from a filename."""
    return os.path.splitext(filename)[1].lower()

def validate_file_size(file_size: int, max_size: int) -> None:
    """Validate if file size is within the allowed limit."""
    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum limit of {max_size/1024/1024}MB"
        )

def get_mime_type(file_path: str) -> str:
    """Get the MIME type of a file."""
    import magic
    mime = magic.Magic(mime=True)
    return mime.from_file(file_path)

def ensure_directory_exists(directory: str) -> None:
    """Ensure that a directory exists, create it if it doesn't."""
    os.makedirs(directory, exist_ok=True)

def get_unique_filename(directory: str, filename: str) -> str:
    """Generate a unique filename in the given directory."""
    base, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    
    while os.path.exists(os.path.join(directory, new_filename)):
        new_filename = f"{base}_{counter}{ext}"
        counter += 1
    
    return new_filename 