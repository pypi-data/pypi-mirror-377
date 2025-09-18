from typing import Optional


class HoodPayError(Exception):
    """Base exception for HoodPay API errors."""

    pass


class HoodPayAuthError(HoodPayError):
    """Exception raised for authentication errors."""

    pass


class HoodPayAPIError(HoodPayError):
    """Exception raised for API errors."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class HoodPayValidationError(HoodPayError):
    """Exception raised for validation errors."""

    pass
