# app/models/context.py

from dataclasses import dataclass

from app.common.enums import UserRole


@dataclass
class CurrentUser:
    id: int
    role: UserRole
