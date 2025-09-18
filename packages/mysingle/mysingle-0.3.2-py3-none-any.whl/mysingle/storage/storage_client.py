"""Storage client for MySingle Object Storage Service integration."""

from typing import Dict, List, Optional
from urllib.parse import urljoin

import httpx

from ..base.client import BaseClient
from ..config import settings
from .schemas import FileInfo, UploadResult


class StorageClient(BaseClient):
    """Client for Object Storage Service."""

    def __init__(
        self,
        base_url: str = settings.OBJECT_STORAGE_SERVICE_URL,
        timeout: float = 30.0,
    ):
        super().__init__(base_url, timeout)

    async def upload_file(
        self,
        tenant_id: str,
        file_data: bytes,
        filename: str,
        content_type: str,
        category: str = "documents",
        visibility: str = "private",
        tags: Optional[List[str]] = None,
        display_name: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> UploadResult:
        """
        Upload a file to object storage.

        Args:
            tenant_id: Tenant identifier
            file_data: File content as bytes
            filename: Original filename
            content_type: MIME content type
            category: File category (documents, images, etc.)
            visibility: File visibility (public, private)
            tags: Optional file tags
            display_name: Optional display name
            user_id: User performing the upload

        Returns:
            UploadResult with file information
        """
        files = {"file": (filename, file_data, content_type)}
        data = {
            "category": category,
            "visibility": visibility,
            "tags": tags or [],
            "display_name": display_name,
        }

        headers = self._get_headers(tenant_id, user_id)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                urljoin(self.base_url, "/api/v1/files/upload"),
                files=files,
                data=data,
                headers=headers,
            )
            response.raise_for_status()
            return UploadResult(**response.json())

    async def get_file_info(
        self,
        file_id: str,
        tenant_id: str,
        user_id: Optional[str] = None,
        include_download_url: bool = False,
    ) -> FileInfo:
        """
        Get file information.

        Args:
            file_id: File identifier
            tenant_id: Tenant identifier
            user_id: User requesting the file
            include_download_url: Whether to include download URL

        Returns:
            FileInfo with file details
        """
        headers = self._get_headers(tenant_id, user_id)
        params = {"include_download_url": include_download_url}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                urljoin(self.base_url, f"/api/v1/files/{file_id}"),
                headers=headers,
                params=params,
            )
            response.raise_for_status()
            return FileInfo(**response.json())

    async def get_download_url(
        self,
        file_id: str,
        tenant_id: str,
        user_id: Optional[str] = None,
        expires_in: int = 3600,
    ) -> str:
        """
        Get a temporary download URL for a file.

        Args:
            file_id: File identifier
            tenant_id: Tenant identifier
            user_id: User requesting the URL
            expires_in: URL expiration time in seconds

        Returns:
            Temporary download URL
        """
        headers = self._get_headers(tenant_id, user_id)
        params = {"expires_in": expires_in}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                urljoin(
                    self.base_url, f"/api/v1/files/{file_id}/download-url"
                ),
                headers=headers,
                params=params,
            )
            response.raise_for_status()
            result = response.json()
            if isinstance(result, dict) and "download_url" in result:
                download_url = result["download_url"]
                if isinstance(download_url, str):
                    return download_url
            raise ValueError(
                f"Invalid response from storage service: {result}"
            )

    async def get_image_url(
        self,
        file_id: str,
        tenant_id: str,
        processing_type: str = "original",  # original, thumbnail, resize
        size: Optional[str] = None,  # small, medium, large for thumbnails
        width: Optional[int] = None,
        height: Optional[int] = None,
        format: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> str:
        """
        Get URL for processed image.

        Args:
            file_id: File identifier
            tenant_id: Tenant identifier
            processing_type: Type of processing (original, thumbnail, resize)
            size: Thumbnail size (small, medium, large)
            width: Target width for resize
            height: Target height for resize
            format: Output format
            user_id: User requesting the image

        Returns:
            Image URL
        """
        headers = self._get_headers(tenant_id, user_id)

        if processing_type == "thumbnail":
            endpoint = f"/api/v1/images/{file_id}/thumbnail"
            params = {
                "size": str(size) if size is not None else None,
                "format": format,
            }
        elif processing_type == "resize":
            endpoint = f"/api/v1/images/{file_id}/resize"
            params = {
                "width": str(width) if width is not None else None,
                "height": str(height) if height is not None else None,
                "format": format,
            }
        else:
            endpoint = f"/api/v1/files/{file_id}/download-url"
            params = {}

        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                urljoin(self.base_url, endpoint),
                headers=headers,
                params=params,
            )
            response.raise_for_status()
            result = response.json()
            if isinstance(result, dict) and "url" in result:
                url = result["url"]
                if isinstance(url, str):
                    return url
            raise ValueError(
                f"Invalid response from storage service: {result}"
            )

    async def list_files(
        self,
        tenant_id: str,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        visibility: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        user_id: Optional[str] = None,
    ) -> Dict:
        """
        List files for a tenant.

        Args:
            tenant_id: Tenant identifier
            category: Filter by category
            tags: Filter by tags
            visibility: Filter by visibility
            limit: Maximum number of results
            offset: Result offset for pagination
            user_id: User requesting the list

        Returns:
            List of files with pagination info
        """
        headers = self._get_headers(tenant_id, user_id)
        params = {
            "category": category,
            "tags": tags,
            "visibility": visibility,
            "limit": limit,
            "offset": offset,
        }
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                urljoin(self.base_url, "/api/v1/files/"),
                headers=headers,
                params=params,
            )
            response.raise_for_status()
            result = response.json()
            if isinstance(result, dict):
                return result
            raise ValueError(
                f"Invalid response from storage service: {result}"
            )

    async def update_file(
        self,
        file_id: str,
        tenant_id: str,
        display_name: Optional[str] = None,
        tags: Optional[List[str]] = None,
        visibility: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> FileInfo:
        """
        Update file metadata.

        Args:
            file_id: File identifier
            tenant_id: Tenant identifier
            display_name: New display name
            tags: New tags
            visibility: New visibility
            user_id: User performing the update

        Returns:
            Updated FileInfo
        """
        headers = self._get_headers(tenant_id, user_id)
        data = {
            "display_name": display_name,
            "tags": tags,
            "visibility": visibility,
        }
        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.put(
                urljoin(self.base_url, f"/api/v1/files/{file_id}"),
                headers=headers,
                json=data,
            )
            response.raise_for_status()
            return FileInfo(**response.json())

    async def delete_file(
        self,
        file_id: str,
        tenant_id: str,
        user_id: Optional[str] = None,
        permanent: bool = False,
    ) -> bool:
        """
        Delete a file.

        Args:
            file_id: File identifier
            tenant_id: Tenant identifier
            user_id: User performing the deletion
            permanent: Whether to permanently delete (vs soft delete)

        Returns:
            True if successful
        """
        headers = self._get_headers(tenant_id, user_id)
        params = {"permanent": permanent}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.delete(
                urljoin(self.base_url, f"/api/v1/files/{file_id}"),
                headers=headers,
                params=params,
            )
            response.raise_for_status()
            return True
