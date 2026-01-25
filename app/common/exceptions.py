# exceptions.py


class DomainError(Exception):
    pass


class UserNotFound(DomainError):
    pass


class UserAlreadyExists(DomainError):
    pass


class InvalidCredentials(DomainError):
    pass


class InvalidPassword(DomainError):
    pass


class TokenExpired(DomainError):
    pass


class TokenInvalid(DomainError):
    pass


class PermissionDenied(DomainError):
    pass


class ResourceLocked(DomainError):
    pass
