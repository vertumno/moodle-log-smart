"""API authentication middleware."""

import os
import hashlib
from typing import Optional
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
import logging

logger = logging.getLogger(__name__)

# Load API keys from environment
API_KEYS_STR = os.getenv("API_KEYS", "")
API_KEYS = [key.strip() for key in API_KEYS_STR.split(",") if key.strip()]

# Validate configuration on module import
if not API_KEYS:
    logger.warning(
        "⚠️ No API keys configured! Set API_KEYS environment variable. "
        "Generate with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
    )
    # For development, allow empty keys (will fail on first request)
    # For production, should fail at startup
    if os.getenv("ENVIRONMENT") == "production":
        raise RuntimeError("API_KEYS environment variable must be set in production")

# Security scheme
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    """Verify API key and return hashed key ID for ownership tracking.

    Args:
        api_key: API key from X-API-Key header

    Returns:
        Hashed API key ID (first 16 chars of SHA256) for job ownership

    Raises:
        HTTPException: 401 if key missing or invalid
    """
    if not api_key:
        logger.warning("API request without API key")
        raise HTTPException(
            status_code=401,
            detail="Missing API key. Provide via X-API-Key header",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if api_key not in API_KEYS:
        logger.warning(f"Invalid API key attempt: {api_key[:8]}...")
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # Return hashed key for ownership tracking (not the key itself)
    hashed = hashlib.sha256(api_key.encode()).hexdigest()[:16]
    logger.debug(f"API key verified: {hashed}")
    return hashed


def get_api_key_hash(api_key: str) -> str:
    """Get hash of API key for ownership comparison.

    Args:
        api_key: Raw API key

    Returns:
        First 16 chars of SHA256 hash
    """
    return hashlib.sha256(api_key.encode()).hexdigest()[:16]
