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
