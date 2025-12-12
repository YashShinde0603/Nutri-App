# app/utils/security.py
from passlib.context import CryptContext
from typing import Optional
from datetime import datetime, timedelta

from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.db.session import SessionLocal
from app.models.user import User

# -------------------------
# Password & hashing
# -------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    Truncate to 72 bytes to avoid bcrypt errors on long passwords.
    """
    max_bytes = 72
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > max_bytes:
        password_bytes = password_bytes[:max_bytes]
        password = password_bytes.decode("utf-8", errors="ignore")
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# -------------------------
# JWT helpers
# -------------------------
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None


# -------------------------
# Database helpers
# -------------------------
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------
# FastAPI dependency
# -------------------------
def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Validate token, return User model instance or raise HTTPException.
    Token payload must contain "sub" with user's email (string).
    """
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    finally:
        db.close()
