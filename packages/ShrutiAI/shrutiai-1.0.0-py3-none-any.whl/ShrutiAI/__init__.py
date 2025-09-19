"""
ShrutiAI SDK - Python client for ShrutiAI API
"""

from .client import ShrutiAIClient
from .exceptions import ShrutiAIError, AuthenticationError, RateLimitError, NotFoundError, ValidationError, ServerError, NetworkError

__version__ = "1.0.0"
__all__ = [
    "ShrutiAIClient",
    "ShrutiAIError",
    "AuthenticationError",
    "RateLimitError",
    "NotFoundError",
    "ValidationError",
    "ServerError",
    "NetworkError"
]
