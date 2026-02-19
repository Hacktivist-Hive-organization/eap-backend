# app/common/exceptions.py

from fastapi import status


class BusinessException(Exception):
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ConfigurationException(Exception):
    """
    Raised when backend configuration is invalid.
    Represents server-side configuration errors.
    """

    def __init__(
        self,
        message: str = "Invalid server configuration",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ExternalServiceException(Exception):
    """
    Raised when an external service (e.g., email provider) fails.
    """

    def __init__(
        self,
        message: str = "External service error",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ):
        self.message = message
        self.status_code = status_code
        super().__init__(message)
