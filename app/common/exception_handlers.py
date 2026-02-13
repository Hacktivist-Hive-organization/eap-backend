# app/common/exception_handlers.py
import json

import structlog
from fastapi import status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.common.exceptions import BusinessException

logger = structlog.get_logger()


def business_exception_handler(request, exc: BusinessException):
    """
    Handles BusinessException globally.
    Logs the exception with correlation ID and client info.
    """

    logger.warning(
        "business_exception",
        path=request.url.path,
        detail=json.dumps(str(exc), ensure_ascii=False),
        client=request.client.host if request.client else None,
        correlation_id=getattr(request.state, "correlation_id", None),
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


def validation_exception_handler(request, exc: RequestValidationError):
    """
    Handles FastAPI request validation errors.
    Logs the first validation error with correlation ID and client info.
    """
    first_error = exc.errors()[0]
    field_name = first_error["loc"][-1]
    message = first_error["msg"]

    logger.warning(
        "validation_exception",
        path=request.url.path,
        field=field_name,
        detail=json.dumps(message, ensure_ascii=False),
        client=request.client.host if request.client else None,
        correlation_id=getattr(request.state, "correlation_id", None),
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": f"{field_name}: {message}"},
    )
