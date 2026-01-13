from pydantic import BaseModel
from enum import Enum
from typing import Optional

class SupportedFormat(str, Enum):
    TXT = "txt"
    EPUB = "epub"
    PDF = "pdf"

class ConversionRequest(BaseModel):
    source_format: SupportedFormat
    target_format: SupportedFormat
    title: Optional[str] = "转换的电子书"
    author: Optional[str] = "未知作者"

class ConversionResponse(BaseModel):
    success: bool
    message: str
    download_url: Optional[str] = None
    file_size: Optional[int] = None
    original_filename: Optional[str] = None
    title: Optional[str] = None