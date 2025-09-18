"""Utils"""

import re


def ensure_tenant(tenant_id: str) -> str:
    """Validate tenant ID."""
    if not tenant_id:
        raise ValueError("tenant_id is required")
    return tenant_id


def mask_pii(text: str) -> str:
    """Mask personally identifiable information."""
    if not text:
        return text

    # Email masking
    text = re.sub(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[EMAIL]", text
    )

    # Phone number masking (Korean format)
    text = re.sub(r"\b010-?\d{4}-?\d{4}\b", "[PHONE]", text)
    text = re.sub(r"\b01[1-9]-?\d{3,4}-?\d{4}\b", "[PHONE]", text)
    # Generic phone number masking
    text = re.sub(
        r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?|\d{3})[-.\s]?\d{3}[-.\s]?\d{4}\b",
        "[PHONE]",
        text,
    )

    # Resident registration number masking
    text = re.sub(r"\b\d{6}-?[1-4]\d{6}\b", "[RRN]", text)

    # Card number masking
    text = re.sub(r"\b\d{4}(?:[ -]?\d{4}){3}\b", "[CARD]", text)

    # Account number masking (10-20 digits)
    text = re.sub(r"\b\d{10,20}\b", "[ACCOUNT]", text)

    return text
