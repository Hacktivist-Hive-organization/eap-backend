# app/common/exception_handlers.py
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.common.exceptions import BusinessException


def business_exception_handler(request, exc: BusinessException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


def validation_exception_handler(request, exc: RequestValidationError):
    """
    Convert Pydantic validation errors to a simple message
    """

    first_error = exc.errors()[0]
    # loc example: ('description', 'String should have at least 20 characters')
    field_name = first_error["loc"][-1]
    message = first_error["msg"]

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": f"{field_name}: {message}"},
    )
