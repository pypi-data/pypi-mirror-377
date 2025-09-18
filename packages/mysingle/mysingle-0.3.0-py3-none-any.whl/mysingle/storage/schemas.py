"""Supplemental schemas for py_common."""

from typing import Dict, Optional

from pydantic import BaseModel


class S3Config(BaseModel):
    """S3/MinIO configuration."""

    access_key: str
    secret_key: str
    bucket: str
    region: str
    endpoint_url: str


class FileInfo(BaseModel):
    """File information response."""

    file_id: str
    original_name: str
    display_name: Optional[str]
    content_type: str
    file_size: int
    category: str
    visibility: str
    download_url: Optional[str] = None
    thumbnail_urls: Optional[Dict[str, str]] = None


class UploadResult(BaseModel):
    """File upload result."""

    file_id: str
    original_name: str
    file_size: int
    content_type: str
    storage_path: str
    upload_url: Optional[str] = None
