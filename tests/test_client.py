"""Tests for RoboKassaClient."""

import pytest
from aiorobokassa.client import RoboKassaClient
from aiorobokassa.constants import MIN_PASSWORD_LENGTH
from aiorobokassa.exceptions import ConfigurationError


class TestRoboKassaClient:
    """Tests for RoboKassaClient."""

    def test_init_valid(self, merchant_login, password1, password2):
        """Test valid initialization."""
        client = RoboKassaClient(
            merchant_login=merchant_login,
            password1=password1,
            password2=password2,
            test_mode=True,
        )
        assert client.merchant_login == merchant_login
        assert client.password1 == password1
        assert client.password2 == password2
        assert client.test_mode is True

    def test_init_test_mode(self, merchant_login, password1, password2):
        """Test initialization in test mode."""
        client = RoboKassaClient(
            merchant_login=merchant_login,
            password1=password1,
            password2=password2,
            test_mode=True,
        )
        assert client.test_mode is True
        assert client.base_url == RoboKassaClient.TEST_BASE_URL

    def test_init_production_mode(self, merchant_login, password1, password2):
        """Test initialization in production mode."""
        client = RoboKassaClient(
            merchant_login=merchant_login,
            password1=password1,
            password2=password2,
            test_mode=False,
        )
        assert client.test_mode is False
        assert client.base_url == RoboKassaClient.PRODUCTION_BASE_URL

    def test_init_with_base_url_override(self, merchant_login, password1, password2):
        """Test initialization with base URL override."""
        custom_url = "https://custom.example.com"
        client = RoboKassaClient(
            merchant_login=merchant_login,
            password1=password1,
            password2=password2,
            base_url_override=custom_url,
        )
        assert client.base_url == custom_url

    def test_init_empty_merchant_login(self, password1, password2):
        """Test initialization with empty merchant login."""
        with pytest.raises(ConfigurationError, match="merchant_login cannot be empty"):
            RoboKassaClient(
                merchant_login="",
                password1=password1,
                password2=password2,
            )

    def test_init_whitespace_merchant_login(self, password1, password2):
        """Test initialization with whitespace-only merchant login."""
        with pytest.raises(ConfigurationError, match="merchant_login cannot be empty"):
            RoboKassaClient(
                merchant_login="   ",
                password1=password1,
                password2=password2,
            )

    def test_init_missing_password1(self, merchant_login, password2):
        """Test initialization without password1."""
        with pytest.raises(ConfigurationError, match="password1 is required"):
            RoboKassaClient(
                merchant_login=merchant_login,
                password1="",
                password2=password2,
            )

    def test_init_short_password1(self, merchant_login, password2):
        """Test initialization with short password1."""
        short_password = "a" * (MIN_PASSWORD_LENGTH - 1)
        with pytest.raises(ConfigurationError, match="password1 is too short"):
            RoboKassaClient(
                merchant_login=merchant_login,
                password1=short_password,
                password2=password2,
            )

    def test_init_missing_password2(self, merchant_login, password1):
        """Test initialization without password2."""
        with pytest.raises(ConfigurationError, match="password2 is required"):
            RoboKassaClient(
                merchant_login=merchant_login,
                password1=password1,
                password2="",
            )

    def test_init_short_password2(self, merchant_login, password1):
        """Test initialization with short password2."""
        short_password = "a" * (MIN_PASSWORD_LENGTH - 1)
        with pytest.raises(ConfigurationError, match="password2 is too short"):
            RoboKassaClient(
                merchant_login=merchant_login,
                password1=password1,
                password2=short_password,
            )

    def test_init_minimum_password_length(self, merchant_login):
        """Test initialization with minimum password length."""
        min_password = "a" * MIN_PASSWORD_LENGTH
        client = RoboKassaClient(
            merchant_login=merchant_login,
            password1=min_password,
            password2=min_password,
        )
        assert client.password1 == min_password
        assert client.password2 == min_password

    def test_clear_sensitive_data(self, client):
        """Test clearing sensitive data."""
        original_password1 = client.password1
        original_password2 = client.password2
        client.clear_sensitive_data()
        assert client.password1 == ""
        assert client.password2 == ""
        assert client.password1 != original_password1
        assert client.password2 != original_password2
