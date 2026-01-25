# exception_handlers.py

from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.common.exceptions import (
    InvalidCredentials,
    InvalidPassword,
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


def register_exception_handlers(app):
    """Register all domain exception handlers to FastAPI app."""
    app.add_exception_handler(UserNotFound, user_not_found_handler)
    app.add_exception_handler(UserAlreadyExists, user_already_exists_handler)
    app.add_exception_handler(InvalidCredentials, invalid_credentials_handler)
    app.add_exception_handler(InvalidPassword, invalid_password_handler)
