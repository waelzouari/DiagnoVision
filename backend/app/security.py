import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from argon2 import PasswordHasher
from fastapi import Cookie, Depends, Header, HTTPException, Request, status
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.orm import Session
from .config import get_settings
from .database import get_db
from .models import Doctor

hasher = PasswordHasher()
settings = get_settings()


def hash_password(value: str) -> str:
    return hasher.hash(value)


def verify_password(value: str, hashed: str) -> bool:
    try:
        return hasher.verify(hashed, value)
    except Exception:
        return False


def create_token(doctor_id: str, kind: str, expires: timedelta) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode({"sub": doctor_id, "type": kind, "iat": now, "exp": now + expires, "jti": secrets.token_urlsafe(12)}, settings.jwt_secret, algorithm="HS256")


def decode_token(value: str, kind: str) -> str:
    try:
        payload = jwt.decode(value, settings.jwt_secret, algorithms=["HS256"])
        if payload.get("type") != kind:
            raise ValueError
        return str(payload["sub"])
    except (JWTError, KeyError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired") from exc


def get_current_doctor(access_token: str | None = Cookie(default=None), db: Session = Depends(get_db)) -> Doctor:
    if not access_token:
        raise HTTPException(status_code=401, detail="Authentication required")
    doctor = db.get(Doctor, decode_token(access_token, "access"))
    if not doctor or not doctor.active:
        raise HTTPException(status_code=401, detail="Authentication required")
    return doctor


def enforce_csrf(request: Request, csrf_token: str | None = Cookie(default=None), x_csrf_token: str | None = Header(default=None)) -> None:
    if request.method in {"GET", "HEAD", "OPTIONS"}:
        return
    if not csrf_token or not x_csrf_token or not secrets.compare_digest(csrf_token, x_csrf_token):
        raise HTTPException(status_code=403, detail="CSRF validation failed")
    origin = request.headers.get("origin")
    if origin and origin not in settings.origins:
        raise HTTPException(status_code=403, detail="Origin is not allowed")


def new_csrf() -> str:
    return secrets.token_urlsafe(32)

