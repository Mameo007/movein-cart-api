import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# How long an admin stays logged in before having to sign in again
TOKEN_TTL_HOURS = 8
ALGORITHM = "HS256"

# Reads the Authorization: Bearer <token> header off the request
bearer_scheme = HTTPBearer(auto_error=False)


def get_admin_password():
    """The single shared admin password, from the environment."""
    password = os.getenv("ADMIN_PASSWORD")
    if not password:
        raise HTTPException(status_code=500, detail="ADMIN_PASSWORD is not configured")
    return password


def get_jwt_secret():
    """The key used to sign and verify admin tokens."""
    secret = os.getenv("ADMIN_JWT_SECRET")
    if not secret:
        raise HTTPException(status_code=500, detail="ADMIN_JWT_SECRET is not configured")
    return secret


def verify_password(submitted: str):
    """True if the submitted password matches. compare_digest is constant-time,
    so an attacker can't guess the password one character at a time by timing us."""
    return secrets.compare_digest(submitted, get_admin_password())


def create_access_token():
    """Mints a signed token that expires on its own."""
    expires_at = datetime.now(timezone.utc) + timedelta(hours=TOKEN_TTL_HOURS)
    payload = {"sub": "admin", "exp": expires_at}
    return jwt.encode(payload, get_jwt_secret(), algorithm=ALGORITHM)


def require_admin(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    """Dependency that rejects any request without a valid, unexpired admin token."""
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(credentials.credentials, get_jwt_secret(), algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    if payload.get("sub") != "admin":
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return payload
