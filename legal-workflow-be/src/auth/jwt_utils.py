"""JWT encode/decode utilities."""

import jwt
import time
from src.config.settings import settings


def encode_jwt(payload: dict) -> str:
    """Encode a payload into a JWT token."""
    if "exp" not in payload:
        payload["exp"] = int(time.time()) + (settings.JWT_EXPIRATION_MINUTES * 60)
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_jwt(token: str) -> dict:
    """Decode and verify a JWT token. Raises jwt.exceptions on failure."""
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
