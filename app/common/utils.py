# app/common/utils.py

import re

from app.common.security import create_token
from app.core.config import settings

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_required_fields_filled(**fields) -> bool:
    return all(value and str(value).strip() for value in fields.values())


def is_email_valid(email: str) -> bool:
    return bool(email and EMAIL_REGEX.match(email))


def is_password_strong(password: str) -> bool:
    if not password or len(password) < 8:
        return False
    if password.islower() or password.isupper() or password.isalnum():
        return False
    return True


def normalize_email(email: str) -> str:
    return email.strip().lower()


def create_jwt_token(sub: str, token_type: str = "access") -> str:
    """
    token_type: 'access', 'email_verification', 'password_reset'
    """
    if token_type == "access":
        expires_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    elif token_type == "email_verification":
        expires_minutes = settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES
    elif token_type == "password_reset":
        expires_minutes = settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
    else:
        raise ValueError(f"Unknown token type: {token_type}")

    payload = {"sub": str(sub), "type": token_type}
    return create_token(payload, expires_minutes=expires_minutes)
