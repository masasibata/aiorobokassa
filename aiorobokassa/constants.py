"""Constants for RoboKassa API."""

from typing import Final

# Base URLs
PRODUCTION_BASE_URL: Final[str] = "https://auth.robokassa.ru"
TEST_BASE_URL: Final[str] = "https://auth.robokassa.ru"

# API Endpoints
PAYMENT_ENDPOINT: Final[str] = "/Merchant/Index.aspx"
XML_SERVICE_ENDPOINT: Final[str] = "/Merchant/WebService/Service.asmx"
INVOICE_API_BASE_URL: Final[str] = "https://services.robokassa.ru/InvoiceServiceWebApi/api"

# Default values
DEFAULT_CULTURE: Final[str] = "ru"
DEFAULT_ENCODING: Final[str] = "utf-8"
DEFAULT_SIGNATURE_ALGORITHM: Final[str] = "MD5"

# HTTP
XML_CONTENT_TYPE: Final[str] = "application/x-www-form-urlencoded"
DEFAULT_TIMEOUT: Final[int] = 30

# Validation
MIN_PASSWORD_LENGTH: Final[int] = 8
