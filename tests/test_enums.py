"""Tests for enums."""

import pytest
from aiorobokassa.enums import Culture, SignatureAlgorithm


class TestSignatureAlgorithm:
    """Tests for SignatureAlgorithm enum."""

    def test_signature_algorithm_values(self):
        """Test enum values."""
        assert SignatureAlgorithm.MD5.value == "MD5"
        assert SignatureAlgorithm.SHA256.value == "SHA256"
        assert SignatureAlgorithm.SHA512.value == "SHA512"

    def test_from_string_md5(self):
        """Test from_string with MD5."""
        assert SignatureAlgorithm.from_string("MD5") == SignatureAlgorithm.MD5
        assert SignatureAlgorithm.from_string("md5") == SignatureAlgorithm.MD5
        assert SignatureAlgorithm.from_string("Md5") == SignatureAlgorithm.MD5

    def test_from_string_sha256(self):
        """Test from_string with SHA256."""
        assert SignatureAlgorithm.from_string("SHA256") == SignatureAlgorithm.SHA256
        assert SignatureAlgorithm.from_string("sha256") == SignatureAlgorithm.SHA256

    def test_from_string_sha512(self):
        """Test from_string with SHA512."""
        assert SignatureAlgorithm.from_string("SHA512") == SignatureAlgorithm.SHA512
        assert SignatureAlgorithm.from_string("sha512") == SignatureAlgorithm.SHA512

    def test_from_string_invalid(self):
        """Test from_string with invalid value."""
        with pytest.raises(ValueError, match="Unsupported algorithm"):
            SignatureAlgorithm.from_string("INVALID")


class TestCulture:
    """Tests for Culture enum."""

    def test_culture_values(self):
        """Test enum values."""
        assert Culture.RU.value == "ru"
        assert Culture.EN.value == "en"
