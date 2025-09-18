"""JWT utility functions."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, cast

import jwt

from mysingle.config import settings


def encode_token(
    data: Dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    """Encode a JWT access token.

    Args:
        data: The payload data to encode.
        expires_delta: Optional timedelta for token expiry.

    Returns:
        Encoded JWT token string.
    """
    payload = data.copy()
    expire_in = expires_delta or timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    expire = datetime.now(timezone.utc) + expire_in
    payload.update({"exp": expire, "type": "access"})
    return jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def decode_token(token: str) -> Dict[str, Any]:
    """Decode a JWT token and return its payload."""
    payload = jwt.decode(
        token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
    )
    return cast(Dict[str, Any], payload)


def create_refresh_token(
    data: Dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    """Create a refresh JWT token."""
    payload = data.copy()
    expire_in = expires_delta or timedelta(
        minutes=settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES
    )
    expire = datetime.now(timezone.utc) + expire_in
    payload.update({"exp": expire, "type": "refresh"})
    return jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
