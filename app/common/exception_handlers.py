# exception_handlers.py

from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.common.exceptions import (
    InvalidCredentials,
    InvalidPassword,
    PermissionDenied,
    ResourceLocked,
    TokenExpired,
    TokenInvalid,
    UserAlreadyExists,
    UserNotFound,
)


async def user_not_found_handler(request: Request, exc: UserNotFound):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "User not found"},
    )


async def user_already_exists_handler(request: Request, exc: UserAlreadyExists):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "User already exists"},
    )


async def invalid_credentials_handler(request: Request, exc: InvalidCredentials):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Invalid email or password"},
    )


async def invalid_password_handler(request: Request, exc: InvalidPassword):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Password does not meet security requirements"},
    )


async def token_expired_handler(request: Request, exc: TokenExpired):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Token has expired"},
    )


async def token_invalid_handler(request: Request, exc: TokenInvalid):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Token is invalid"},
    )


async def permission_denied_handler(request: Request, exc: PermissionDenied):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": "Permission denied"},
    )


async def resource_locked_handler(request: Request, exc: ResourceLocked):
    return JSONResponse(
        status_code=status.HTTP_423_LOCKED,
        content={"detail": "Resource is locked"},
    )


def register_exception_handlers(app):
    """Register all domain exception handlers to FastAPI app."""
    app.add_exception_handler(UserNotFound, user_not_found_handler)
    app.add_exception_handler(UserAlreadyExists, user_already_exists_handler)
    app.add_exception_handler(InvalidCredentials, invalid_credentials_handler)
    app.add_exception_handler(InvalidPassword, invalid_password_handler)
    app.add_exception_handler(TokenExpired, token_expired_handler)
    app.add_exception_handler(TokenInvalid, token_invalid_handler)
    app.add_exception_handler(PermissionDenied, permission_denied_handler)
    app.add_exception_handler(ResourceLocked, resource_locked_handler)
