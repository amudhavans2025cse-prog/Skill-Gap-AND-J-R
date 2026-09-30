import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .database import get_db

bearer = HTTPBearer(auto_error=False)
ALGORITHM = "HS256"


def _secret():
    secret = os.getenv("JWT_SECRET_KEY")
    if not secret:
        raise HTTPException(503, "Authentication is not configured")
    return secret


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_access_token(email: str, role: str) -> str:
    expires = datetime.now(timezone.utc) + timedelta(hours=12)
    return jwt.encode({"sub": email, "role": role, "exp": expires}, _secret(), algorithm=ALGORITHM)


def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)):
    if credentials is None:
        raise HTTPException(401, "Sign in to continue", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(credentials.credentials, _secret(), algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise ValueError("Missing subject")
    except (jwt.PyJWTError, ValueError, TypeError, HTTPException) as exc:
        raise HTTPException(401, "Invalid or expired access token", headers={"WWW-Authenticate": "Bearer"}) from exc
    try:
        user = get_db().users.find_one({"email": email}, {"password_hash": 0})
    except Exception as exc:
        raise HTTPException(503, "User database is unavailable") from exc
    if not user:
        raise HTTPException(401, "Invalid or expired access token", headers={"WWW-Authenticate": "Bearer"})
    return user


def admin_user(user=Depends(current_user)):
    if user.get("role") != "admin":
        raise HTTPException(403, "Administrator access required")
    return user