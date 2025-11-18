"""Tests for PaymentMixin."""

import pytest
from decimal import Decimal

from aiorobokassa.enums import SignatureAlgorithm
from aiorobokassa.exceptions import SignatureError
from aiorobokassa.utils.signature import (
    calculate_payment_signature,
)


class TestPaymentMixin:
    """Tests for PaymentMixin."""

    def test_build_payment_params_basic(self, client):
        """Test building basic payment parameters."""
        from aiorobokassa.models.requests import PaymentRequest

        request = PaymentRequest(
            out_sum=Decimal("100.50"),
            description="Test payment",
        )
        params = client._build_payment_params(request, SignatureAlgorithm.MD5)

        assert params["MerchantLogin"] == client.merchant_login
        assert params["OutSum"] == "100.50"
        assert params["Description"] == "Test payment"
        assert "SignatureValue" in params

    def test_build_payment_params_with_inv_id(self, client):
        """Test building payment parameters with invoice ID."""
        from aiorobokassa.models.requests import PaymentRequest

        request = PaymentRequest(
            out_sum=Decimal("100.50"),
            description="Test payment",
            inv_id=12345,
        )
        params = client._build_payment_params(request, SignatureAlgorithm.MD5)

        assert params["InvId"] == "12345"
        assert "SignatureValue" in params

    def test_build_payment_params_with_email(self, client):
        """Test building payment parameters with email."""
        from aiorobokassa.models.requests import PaymentRequest

        request = PaymentRequest(
            out_sum=Decimal("100.50"),
            description="Test payment",
            email="test@example.com",
        )
        params = client._build_payment_params(request, SignatureAlgorithm.MD5)

        assert params["Email"] == "test@example.com"

    def test_build_payment_params_with_culture(self, client):
        """Test building payment parameters with culture."""
        from aiorobokassa.models.requests import PaymentRequest

        request = PaymentRequest(
            out_sum=Decimal("100.50"),
            description="Test payment",
            culture="en",
        )
        params = client._build_payment_params(request, SignatureAlgorithm.MD5)

        assert params["Culture"] == "en"

    def test_build_payment_params_with_user_parameters(self, client):
        """Test building payment parameters with user parameters."""
        from aiorobokassa.models.requests import PaymentRequest

        request = PaymentRequest(
            out_sum=Decimal("100.50"),
            description="Test payment",
            user_parameters={"user_id": "123", "order_id": "456"},
        )
        params = client._build_payment_params(request, SignatureAlgorithm.MD5)

        assert params["Shp_user_id"] == "123"
        assert params["Shp_order_id"] == "456"

    def test_build_payment_params_test_mode(self, client):
        """Test building payment parameters in test mode."""
        from aiorobokassa.models.requests import PaymentRequest

        request = PaymentRequest(
            out_sum=Decimal("100.50"),
            description="Test payment",
        )
        params = client._build_payment_params(request, SignatureAlgorithm.MD5)

        assert params["IsTest"] == "1"

    def test_build_payment_params_production_mode(self, production_client):
        """Test building payment parameters in production mode."""
        from aiorobokassa.models.requests import PaymentRequest

        request = PaymentRequest(
            out_sum=Decimal("100.50"),
            description="Test payment",
        )
        params = production_client._build_payment_params(request, SignatureAlgorithm.MD5)

        # IsTest should not be set if not explicitly provided in production
        assert "IsTest" not in params or params["IsTest"] is None

    def test_build_payment_params_explicit_test(self, production_client):
        """Test building payment parameters with explicit test flag."""
        from aiorobokassa.models.requests import PaymentRequest

        request = PaymentRequest(
            out_sum=Decimal("100.50"),
            description="Test payment",
            is_test=1,
        )
        params = production_client._build_payment_params(request, SignatureAlgorithm.MD5)

        assert params["IsTest"] == "1"

    def test_build_payment_params_signature_verification(self, client):
        """Test that payment signature is correctly calculated."""
        from aiorobokassa.models.requests import PaymentRequest

        request = PaymentRequest(
            out_sum=Decimal("100.50"),
            description="Test payment",
            inv_id=12345,
        )
        params = client._build_payment_params(request, SignatureAlgorithm.MD5)

        expected_signature = calculate_payment_signature(
            merchant_login=client.merchant_login,
            out_sum="100.50",
            inv_id="12345",
            password=client.password1,
            algorithm=SignatureAlgorithm.MD5,
        )
        assert params["SignatureValue"] == expected_signature

    @pytest.mark.asyncio
    async def test_create_payment_url_basic(self, client):
        """Test creating basic payment URL."""
        url = await client.create_payment_url(
            out_sum=Decimal("100.50"),
            description="Test payment",
        )
        assert url.startswith(client.base_url)
        assert "MerchantLogin" in url
        assert "OutSum=100.50" in url
        assert "Description" in url
        assert "SignatureValue" in url

    @pytest.mark.asyncio
    async def test_create_payment_url_with_all_params(self, client):
        """Test creating payment URL with all parameters."""
        url = await client.create_payment_url(
            out_sum=Decimal("100.50"),
            description="Test payment",
            inv_id=12345,
            email="test@example.com",
            culture="en",
            encoding="utf-8",
            user_parameters={"user_id": "123"},
        )
        assert "InvId=12345" in url
        assert "Email=test%40example.com" in url or "Email=test@example.com" in url
        assert "Culture=en" in url
        assert "Shp_user_id=123" in url

    @pytest.mark.asyncio
    async def test_create_payment_url_different_algorithms(self, client):
        """Test creating payment URL with different algorithms."""
        url_md5 = await client.create_payment_url(
            out_sum=Decimal("100.50"),
            description="Test",
            signature_algorithm=SignatureAlgorithm.MD5,
        )
        url_sha256 = await client.create_payment_url(
            out_sum=Decimal("100.50"),
            description="Test",
            signature_algorithm=SignatureAlgorithm.SHA256,
        )

        # URLs should be different due to different signatures
        assert url_md5 != url_sha256

    def test_verify_result_url_valid(self, client):
        """Test verifying valid ResultURL signature."""
        out_sum = "100.50"
        inv_id = "12345"
        # Calculate correct signature for ResultURL (uses password2)
        from aiorobokassa.utils.signature import calculate_signature

        values = {"OutSum": out_sum, "InvId": inv_id}
        signature = calculate_signature(values, client.password2, SignatureAlgorithm.MD5)

        # Verify using client method
        result = client.verify_result_url(
            out_sum=out_sum,
            inv_id=inv_id,
            signature_value=signature,
        )
        assert result is True

    def test_verify_result_url_invalid(self, client):
        """Test verifying invalid ResultURL signature."""
        with pytest.raises(SignatureError, match="ResultURL signature verification failed"):
            client.verify_result_url(
                out_sum="100.50",
                inv_id="12345",
                signature_value="INVALID_SIGNATURE",
            )

    def test_verify_result_url_with_shp_params(self, client):
        """Test verifying ResultURL with Shp parameters."""
        out_sum = "100.50"
        inv_id = "12345"
        # Calculate correct signature
        from aiorobokassa.utils.signature import calculate_signature

        values = {"OutSum": out_sum, "InvId": inv_id}
        signature = calculate_signature(values, client.password2, SignatureAlgorithm.MD5)

        # Should not raise
        result = client.verify_result_url(
            out_sum=out_sum,
            inv_id=inv_id,
            signature_value=signature,
            shp_params={"user_id": "123"},
        )
        assert result is True

    def test_verify_success_url_valid(self, client):
        """Test verifying valid SuccessURL signature."""
        out_sum = "100.50"
        inv_id = "12345"
        # Calculate correct signature using password1
        from aiorobokassa.utils.signature import calculate_signature

        values = {"OutSum": out_sum, "InvId": inv_id}
        signature = calculate_signature(values, client.password1, SignatureAlgorithm.MD5)

        result = client.verify_success_url(
            out_sum=out_sum,
            inv_id=inv_id,
            signature_value=signature,
        )
        assert result is True

    def test_verify_success_url_invalid(self, client):
        """Test verifying invalid SuccessURL signature."""
        with pytest.raises(SignatureError, match="SuccessURL signature verification failed"):
            client.verify_success_url(
                out_sum="100.50",
                inv_id="12345",
                signature_value="INVALID_SIGNATURE",
            )

    def test_parse_result_url_params(self, client):
        """Test parsing ResultURL parameters."""
        params = {
            "OutSum": "100.50",
            "InvId": "12345",
            "SignatureValue": "ABC123",
            "Shp_user_id": "123",
            "Shp_order_id": "456",
        }
        result = client.parse_result_url_params(params)
        assert result["out_sum"] == "100.50"
        assert result["inv_id"] == "12345"
        assert result["signature_value"] == "ABC123"
        assert result["shp_params"]["user_id"] == "123"
        assert result["shp_params"]["order_id"] == "456"

    def test_parse_success_url_params(self, client):
        """Test parsing SuccessURL parameters."""
        params = {
            "OutSum": "100.50",
            "InvId": "12345",
            "SignatureValue": "ABC123",
            "Shp_user_id": "123",
        }
        result = client.parse_success_url_params(params)
        assert result["out_sum"] == "100.50"
        assert result["inv_id"] == "12345"
        assert result["signature_value"] == "ABC123"
        assert result["shp_params"]["user_id"] == "123"
