"""
Security, password hashing, and JWT token handling for AgentCare.

DISCLAIMER: AgentCare does not diagnose Type-2 Diabetes or prescribe treatment.
It assists clinicians and patients only.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Union
from jose import jwt, JWTError
from passlib.hash import pbkdf2_sha256
from app.core.config import settings

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain text password against a stored hash."""
    return pbkdf2_sha256.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generates a PBKDF2 SHA256 password hash."""
    return pbkdf2_sha256.hash(password)


def create_access_token(subject: Union[str, Any], role: str, expires_delta: Optional[timedelta] = None) -> str:
    """Creates a signed JWT access token containing subject (username/user_id) and user role."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "role": role,
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decodes and validates a JWT access token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
