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


class InvalidPassword(DomainError):
    """
    Raised when a password does not meet security requirements.
    E.g., less than 8 characters, missing uppercase, number, or special character.
    """
    pass
