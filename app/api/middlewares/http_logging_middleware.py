# app/api/middlewares/http_logging_middleware.py

import json
import time
import uuid
from typing import Any

import structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

CORRELATION_HEADER = "X-Request-ID"
SERVICE_NAME = "eap-backend"

SENSITIVE_FIELDS = {"email", "password", "token", "access_token", "refresh_token"}

MAX_BODY_SIZE = 5000  # 5 KB

logger = structlog.get_logger()


def mask_sensitive_data(data: Any) -> Any:
    """
    Recursively mask sensitive fields in JSON body.
    """
    if isinstance(data, dict):
        return {
            key: (
                "***" if key.lower() in SENSITIVE_FIELDS else mask_sensitive_data(value)
            )
            for key, value in data.items()
        }
    elif isinstance(data, list):
        return [mask_sensitive_data(item) for item in data]
    return data


class HttpLoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs:
    - Correlation ID
    - Method
    - Path
    - Status code
    - Duration
    - Client IP
    - Safe request body (JSON only)
    - Service name
    """

    async def dispatch(self, request: Request, call_next):
        #  Create or reuse correlation ID
        correlation_id = request.headers.get(CORRELATION_HEADER) or str(uuid.uuid4())
        request.state.correlation_id = correlation_id

        structlog.contextvars.bind_contextvars(correlation_id=correlation_id)

        start_time = time.time()

        # -------- SAFE BODY READ --------
        body_content = None
        if request.method in {"POST", "PUT", "PATCH"}:
            try:
                if "/auth/login" in request.url.path:
                    body_content = "Login attempt"
                elif "/auth/register" in request.url.path:
                    body_content = "Register attempt"
                else:
                    body_bytes = await request.body()
                    request._body = body_bytes  # re-attach body for FastAPI

                    if len(body_bytes) <= MAX_BODY_SIZE:
                        if "application/json" in request.headers.get(
                            "content-type", ""
                        ):
                            body_json = json.loads(body_bytes)
                            body_content = mask_sensitive_data(body_json)
                    else:
                        body_content = "Body too large to log"
            except Exception:
                body_content = "Failed to read body"
        # --------------------------------

        try:
            response = await call_next(request)
        except Exception:
            logger.exception(
                "unhandled_exception",
                method=request.method,
                path=request.url.path,
                request_body=body_content,
                service=SERVICE_NAME,
            )
            raise

        duration_ms = round((time.time() - start_time) * 1000, 2)

        logger.info(
            "http_request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
            client=request.client.host if request.client else None,
            request_body=(
                json.dumps(body_content, ensure_ascii=False) if body_content else None
            ),
            service=SERVICE_NAME,
        )

        response.headers[CORRELATION_HEADER] = correlation_id

        # Clean contextvars
        structlog.contextvars.clear_contextvars()

        return response
