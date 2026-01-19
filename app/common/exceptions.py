# exceptions.py

class DomainError(Exception):
    """Base class for domain-level errors"""
    pass


class UserNotFound(DomainError):
    pass


class UserAlreadyExists(DomainError):
    pass


class InvalidCredentials(DomainError):
    pass
