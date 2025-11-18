"""Tests for custom exceptions."""

from aiorobokassa.exceptions import (
    APIError,
    ConfigurationError,
    InvalidSignatureAlgorithmError,
    RoboKassaError,
    SignatureError,
    ValidationError,
    XMLParseError,
)


class TestRoboKassaError:
    """Tests for base RoboKassaError."""

    def test_robo_kassa_error_creation(self):
        """Test creating base error."""
        error = RoboKassaError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)


class TestSignatureError:
    """Tests for SignatureError."""

    def test_signature_error_creation(self):
        """Test creating signature error."""
        error = SignatureError("Invalid signature")
        assert str(error) == "Invalid signature"
        assert isinstance(error, RoboKassaError)


class TestAPIError:
    """Tests for APIError."""

    def test_api_error_creation(self):
        """Test creating API error."""
        error = APIError("API request failed")
        assert str(error) == "API request failed"
        assert error.status_code is None
        assert error.response is None

    def test_api_error_with_status_code(self):
        """Test API error with status code."""
        error = APIError("Not found", status_code=404)
        assert error.status_code == 404

    def test_api_error_with_response(self):
        """Test API error with response."""
        error = APIError("Error", status_code=500, response="Error details")
        assert error.response == "Error details"


class TestValidationError:
    """Tests for ValidationError."""

    def test_validation_error_creation(self):
        """Test creating validation error."""
        error = ValidationError("Invalid data")
        assert str(error) == "Invalid data"
        assert isinstance(error, RoboKassaError)


class TestConfigurationError:
    """Tests for ConfigurationError."""

    def test_configuration_error_creation(self):
        """Test creating configuration error."""
        error = ConfigurationError("Invalid config")
        assert str(error) == "Invalid config"
        assert isinstance(error, RoboKassaError)


class TestInvalidSignatureAlgorithmError:
    """Tests for InvalidSignatureAlgorithmError."""

    def test_invalid_signature_algorithm_error_creation(self):
        """Test creating invalid signature algorithm error."""
        error = InvalidSignatureAlgorithmError("Unsupported algorithm")
        assert str(error) == "Unsupported algorithm"
        assert isinstance(error, ConfigurationError)


class TestXMLParseError:
    """Tests for XMLParseError."""

    def test_xml_parse_error_creation(self):
        """Test creating XML parse error."""
        error = XMLParseError("Parse failed", response="<invalid>")
        assert str(error) == "Parse failed"
        assert error.response == "<invalid>"
        assert isinstance(error, APIError)
