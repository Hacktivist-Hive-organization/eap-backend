# app/common/utils.py

import re

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
