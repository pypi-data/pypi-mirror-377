"""IAM Service HTTP client utilities."""

from __future__ import annotations

from typing import Any, Dict, Optional

import httpx


def _get_settings():
    """지연 import로 순환 import 방지"""
    from .config import settings

    return settings


class IAMClient:
    """Client for communicating with the IAM Service."""

    def __init__(self, base_url: Optional[str] = None) -> None:
        self.base_url = base_url or _get_settings().IAM_SERVICE_URL
        self._client = httpx.AsyncClient(base_url=self.base_url)

    async def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify *token* with IAM service."""
        response = await self._client.post(
            "/api/v1/auth/verify",
            headers={"Authorization": f"Bearer {token}"},
            json={"token": token},
        )
        response.raise_for_status()
        result = response.json()
        if isinstance(result, dict):
            return result
        raise ValueError(f"Unexpected response type from IAM: {type(result)}")

    async def create_user(
        self, email: str, name: str, password: str, tenant_id: str
    ) -> Dict[str, Any]:
        """Create a new user in IAM service."""
        response = await self._client.post(
            "/api/v1/users",
            json={
                "email": email,
                "name": name,
                "password": password,
                "tenant_id": tenant_id,
            },
        )
        response.raise_for_status()
        result = response.json()
        if isinstance(result, dict):
            return result
        raise ValueError(f"Unexpected response type from IAM: {type(result)}")

    async def get_user(self, user_id: str, token: str) -> Dict[str, Any]:
        """Retrieve user information by *user_id*."""
        response = await self._client.get(
            f"/api/v1/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        result = response.json()
        if isinstance(result, dict):
            return result
        raise ValueError(f"Unexpected response type from IAM: {type(result)}")

    async def authorize(self, token: str, permission: str) -> bool:
        """Check whether *token* is authorized for *permission*."""
        response = await self._client.post(
            "/api/v1/authorize",
            headers={"Authorization": f"Bearer {token}"},
            json={"permission": permission},
        )
        response.raise_for_status()
        data = response.json()
        return bool(data.get("allowed"))

    async def get_role(
        self, role_id: str, token: str | None = None
    ) -> Dict[str, Any]:
        """Retrieve role information by *role_id*."""
        headers = {"Authorization": f"Bearer {token}"} if token else None
        response = await self._client.get(
            f"/api/v1/roles/{role_id}", headers=headers
        )
        response.raise_for_status()
        result = response.json()
        if isinstance(result, dict):
            return result
        raise ValueError(f"Unexpected response type from IAM: {type(result)}")

    async def list_roles(
        self, token: str | None = None
    ) -> list[Dict[str, Any]]:
        """List all roles."""
        headers = {"Authorization": f"Bearer {token}"} if token else None
        response = await self._client.get("/api/v1/roles", headers=headers)
        response.raise_for_status()
        result = response.json()
        if isinstance(result, list):
            return result
        raise ValueError(f"Unexpected response type from IAM: {type(result)}")

    async def get_role_by_name(
        self, name: str, token: str | None = None
    ) -> Dict[str, Any] | None:
        """Retrieve a role by *name*.

        This helper performs a client-side search until the IAM service provides
        a dedicated lookup endpoint. Returns ``None`` when the role is not
        found.
        """
        roles = await self.list_roles(token=token)
        for role in roles:
            if role.get("name") == name:
                return role
        return None

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()


iam_client = IAMClient()
