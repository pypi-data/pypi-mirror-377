from typing import Optional
from pydantic import BaseModel

class ImageFile(BaseModel):
    """
    Represents an image file, including metadata and dimensions.
    """
    href: str
    mime: str
    hash: Optional[str] = None
    filename: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None

class ArchiveFile(BaseModel):
    """
    Represents an archive file, including URL and MIME type.
    """
    href: str
    mime: str

class StatementFile(BaseModel):
    """
    Represents a statement file for a problem, including URL and filename.
    """
    href: str
    mime: str
    filename: str

class SourceCode(BaseModel):
    """
    Represents a source code file for a submission, including filename and encoded source.
    """
    id: str
    submission_id: str
    filename: str
    source: str  # Base64-encoded