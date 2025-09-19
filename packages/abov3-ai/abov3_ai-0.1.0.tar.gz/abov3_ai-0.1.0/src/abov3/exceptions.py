"""Exception classes for ABOV3 AI SDK"""


class Abov3Error(Exception):
    """Base exception for all ABOV3 SDK errors."""
    pass


class APIError(Abov3Error):
    """Error from the ABOV3 API."""

    def __init__(self, message: str, status_code: int = None, response_body: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class AuthenticationError(APIError):
    """Authentication failed with the provided credentials."""
    pass


class RateLimitError(APIError):
    """Rate limit exceeded."""
    pass


class NetworkError(Abov3Error):
    """Network-related error occurred."""
    pass


class ValidationError(Abov3Error):
    """Request validation error."""
    pass


class TimeoutError(NetworkError):
    """Request timed out."""
    pass