# app/common/security.py

from datetime import datetime, timedelta, timezone

from fastapi import status
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext

from app.common.exceptions import BusinessException
from app.core.config import settings

pwd_context = CryptContext(
    schemes=["bcrypt_sha256", "bcrypt"],
    deprecated="auto",
)
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def create_access_token(
    data: dict, expires_minutes: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES
) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        raise BusinessException(
            message="Token expired",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    except JWTError:
        raise BusinessException(
            message="Invalid token",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


def validate_token_payload(payload: dict) -> int:
    user_id = payload.get("sub")
    if not user_id:
        raise BusinessException(
            message="Invalid token payload",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    return int(user_id)
