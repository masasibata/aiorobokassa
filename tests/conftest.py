"""Pytest configuration and fixtures."""

import pytest
from decimal import Decimal

from aiorobokassa.client import RoboKassaClient


@pytest.fixture
def merchant_login():
    """Fixture for merchant login."""
    return "test_merchant"


@pytest.fixture
def password1():
    """Fixture for password1."""
    return "password12345678"


@pytest.fixture
def password2():
    """Fixture for password2."""
    return "password87654321"


@pytest.fixture
def client(merchant_login, password1, password2):
    """Fixture for RoboKassaClient in test mode."""
    return RoboKassaClient(
        merchant_login=merchant_login,
        password1=password1,
        password2=password2,
        test_mode=True,
    )


@pytest.fixture
def production_client(merchant_login, password1, password2):
    """Fixture for RoboKassaClient in production mode."""
    return RoboKassaClient(
        merchant_login=merchant_login,
        password1=password1,
        password2=password2,
        test_mode=False,
    )


@pytest.fixture
def sample_amount():
    """Fixture for sample payment amount."""
    return Decimal("100.50")


@pytest.fixture
def sample_description():
    """Fixture for sample payment description."""
    return "Test payment"


@pytest.fixture
def sample_inv_id():
    """Fixture for sample invoice ID."""
    return 12345


@pytest.fixture
def sample_email():
    """Fixture for sample email."""
    return "test@example.com"
