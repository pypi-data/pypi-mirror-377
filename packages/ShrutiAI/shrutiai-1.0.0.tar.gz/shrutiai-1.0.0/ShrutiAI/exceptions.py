"""
Custom exceptions for ShrutiAI SDK
"""

from typing import Optional


class ShrutiAIError(Exception):
    """Base exception for ShrutiAI SDK"""

    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[object] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response = response

    def __str__(self):
        if self.status_code:
            return f"{self.message} (Status: {self.status_code})"
        return self.message


class AuthenticationError(ShrutiAIError):
    """Raised when authentication fails"""
    pass


class RateLimitError(ShrutiAIError):
    """Raised when rate limit is exceeded"""
    pass


class NotFoundError(ShrutiAIError):
    """Raised when resource is not found"""
    pass


class ValidationError(ShrutiAIError):
    """Raised when request validation fails"""
    pass


class ServerError(ShrutiAIError):
    """Raised when server returns 5xx error"""
    pass


class NetworkError(ShrutiAIError):
    """Raised when network request fails"""
    pass
