"""Custom exceptions for aiorobokassa library."""

from typing import Optional


class RoboKassaError(Exception):
    """Base exception for all RoboKassa errors."""

    pass


class SignatureError(RoboKassaError):
    """Raised when signature verification fails."""

    pass


class APIError(RoboKassaError):
    """Raised when API request fails."""

    def __init__(
        self, message: str, status_code: Optional[int] = None, response: Optional[str] = None
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class ValidationError(RoboKassaError):
    """Raised when data validation fails."""

    pass


class ConfigurationError(RoboKassaError):
    """Raised when client configuration is invalid."""

    pass


class InvalidSignatureAlgorithmError(ConfigurationError):
    """Raised when unsupported signature algorithm is used."""

    pass


class XMLParseError(APIError):
    """Raised when XML response cannot be parsed."""

    pass
