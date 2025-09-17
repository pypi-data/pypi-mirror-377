"""
Sharokey exceptions module.

Defines custom exceptions for the Sharokey Python SDK.
"""


class SharokeyError(Exception):
    """Base exception class for all Sharokey errors."""
    pass


class AuthenticationError(SharokeyError):
    """Raised when authentication fails (invalid token, etc.)."""
    pass


class ValidationError(SharokeyError):
    """Raised when input validation fails."""
    pass


class NotFoundError(SharokeyError):
    """Raised when a secret is not found."""
    pass


class NetworkError(SharokeyError):
    """Raised when network/API communication fails."""
    pass


class EncryptionError(SharokeyError):
    """Raised when encryption/decryption fails."""
    pass


class AttachmentError(SharokeyError):
    """Raised when attachment processing fails."""
    pass