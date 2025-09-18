"""Base client for MySingle service integrations."""

from typing import Dict, Optional


class BaseClient:
    """Base client class for MySingle services."""

    def __init__(self, base_url: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _get_headers(
        self, tenant_id: Optional[str] = None, user_id: Optional[str] = None
    ) -> Dict[str, str]:
        """Get standard headers for API requests."""
        headers = {
            "Content-Type": "application/json",
            "X-Internal-Call": "true",
        }

        if tenant_id:
            headers["X-Tenant-Id"] = tenant_id

        if user_id:
            headers["X-User-Id"] = user_id

        return headers
