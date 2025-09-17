"""Custom exceptions for the RxNorm API client."""

from typing import Any, Dict, Optional


class RxNormError(Exception):
    """Base exception for all RxNorm API related errors."""
    
    def __init__(self, message: str, response_data: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.response_data = response_data


class RxNormConnectionError(RxNormError):
    """Raised when there are network connectivity issues with the RxNorm API."""
    pass


class RxNormTimeoutError(RxNormConnectionError):
    """Raised when requests to the RxNorm API time out."""
    pass


class RxNormHTTPError(RxNormError):
    """Raised for HTTP-related errors (4xx, 5xx status codes)."""
    
    def __init__(self, message: str, status_code: int, response_data: Optional[Dict[str, Any]] = None):
        super().__init__(message, response_data)
        self.status_code = status_code


class RxNormNotFoundError(RxNormHTTPError):
    """Raised when a requested resource is not found (404)."""
    
    def __init__(self, message: str, response_data: Optional[Dict[str, Any]] = None):
        super().__init__(message, 404, response_data)


class RxNormServerError(RxNormHTTPError):
    """Raised when the RxNorm API returns a server error (5xx)."""
    pass


class RxNormValidationError(RxNormError):
    """Raised when client-side parameter validation fails."""
    pass


class RxNormParsingError(RxNormError):
    """Raised when API response cannot be parsed or validated."""
    
    def __init__(self, message: str, raw_response: Optional[str] = None):
        super().__init__(message)
        self.raw_response = raw_response


class RxNormSessionError(RxNormError):
    """Raised when there are issues with the HTTP session."""
    pass