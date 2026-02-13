# app/common/enums.py

from enum import Enum


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Status(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"


class UserRole(str, Enum):
    ADMIN = "admin"
    APPROVER = "approver"
    REQUESTER = "requester"
