# app/common/security_models.py

from dataclasses import dataclass

from app.common.enums import UserRole


@dataclass
class CurrentUser:
    id: int
    role: UserRole
