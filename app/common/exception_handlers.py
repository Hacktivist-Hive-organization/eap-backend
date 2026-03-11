# app/common/exception_handlers.py

import json

import structlog
from fastapi import Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.common.exceptions import (
    BusinessException,
    ConfigurationException,
    ExternalServiceException,
)

logger = structlog.get_logger()


def business_exception_handler(request, exc: BusinessException) -> JSONResponse:
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


def configuration_exception_handler(
    request: Request, exc: ConfigurationException
) -> JSONResponse:
    logger.error(
        "configuration_exception",
        path=request.url.path,
        detail=json.dumps(str(exc), ensure_ascii=False),
        client=request.client.host if request.client else None,
        correlation_id=getattr(request.state, "correlation_id", None),
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


def external_service_exception_handler(
    request: Request, exc: ExternalServiceException
) -> JSONResponse:
    logger.error(
        "external_service_exception",
        path=request.url.path,
        detail=json.dumps(str(exc), ensure_ascii=False),
        client=request.client.host if request.client else None,
        correlation_id=getattr(request.state, "correlation_id", None),
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
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
