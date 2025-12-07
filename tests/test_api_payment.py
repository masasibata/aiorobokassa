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

        # Verify that signature includes shp_params
        expected_signature = calculate_payment_signature(
            merchant_login=client.merchant_login,
            out_sum="100.50",
            inv_id=None,
            password=client.password1,
            algorithm=SignatureAlgorithm.MD5,
            shp_params={"user_id": "123", "order_id": "456"},
        )
        assert params["SignatureValue"] == expected_signature

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

    def test_build_payment_params_signature_with_shp_params(self, client):
        """Test that payment signature correctly includes shp_params."""
        from aiorobokassa.models.requests import PaymentRequest

        request = PaymentRequest(
            out_sum=Decimal("100.50"),
            description="Test payment",
            inv_id=12345,
            user_parameters={"user_id": "123", "order_id": "456"},
        )
        params = client._build_payment_params(request, SignatureAlgorithm.MD5)

        # Verify signature includes shp_params (sorted alphabetically: order_id, then user_id)
        expected_signature = calculate_payment_signature(
            merchant_login=client.merchant_login,
            out_sum="100.50",
            inv_id="12345",
            password=client.password1,
            algorithm=SignatureAlgorithm.MD5,
            shp_params={"user_id": "123", "order_id": "456"},
        )
        assert params["SignatureValue"] == expected_signature

    @pytest.mark.asyncio
    async def test_create_payment_url_basic(self, client):
        """Test creating basic payment URL."""
        url = client.create_payment_url(
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
        url = client.create_payment_url(
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
        url_md5 = client.create_payment_url(
            out_sum=Decimal("100.50"),
            description="Test",
            signature_algorithm=SignatureAlgorithm.MD5,
        )
        url_sha256 = client.create_payment_url(
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
        # Calculate correct signature for ResultURL (uses password2) with correct order: OutSum:InvId:password2
        import hashlib
        signature_string = f"{out_sum}:{inv_id}:{client.password2}"
        signature = hashlib.md5(signature_string.encode("utf-8")).hexdigest().upper()

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
        shp_params = {"user_id": "123"}
        # Calculate correct signature WITH shp_params in correct order: OutSum:InvId:Shp_user_id=123:password2
        # Shp_ parameters must be in format "Shp_key=value"
        import hashlib
        sorted_shp = sorted(shp_params.items())
        signature_parts = [out_sum, inv_id]
        for key, value in sorted_shp:
            signature_parts.append(f"Shp_{key}={value}")
        signature_parts.append(client.password2)
        signature_string = ":".join(signature_parts)
        signature = hashlib.md5(signature_string.encode("utf-8")).hexdigest().upper()

        # Should not raise
        result = client.verify_result_url(
            out_sum=out_sum,
            inv_id=inv_id,
            signature_value=signature,
            shp_params=shp_params,
        )
        assert result is True

    def test_verify_success_url_valid(self, client):
        """Test verifying valid SuccessURL signature."""
        out_sum = "100.50"
        inv_id = "12345"
        # Calculate correct signature using password1 with correct order: OutSum:InvId:password1
        import hashlib
        signature_string = f"{out_sum}:{inv_id}:{client.password1}"
        signature = hashlib.md5(signature_string.encode("utf-8")).hexdigest().upper()

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

    def test_verify_success_url_with_shp_params(self, client):
        """Test verifying SuccessURL with Shp parameters."""
        out_sum = "100.50"
        inv_id = "12345"
        shp_params = {"user_id": "123", "order_id": "456"}
        # Calculate correct signature WITH shp_params in correct order: OutSum:InvId:Shp_order_id=456:Shp_user_id=123:password1
        # Shp_ parameters must be in format "Shp_key=value"
        import hashlib
        sorted_shp = sorted(shp_params.items())  # [('order_id', '456'), ('user_id', '123')]
        signature_parts = [out_sum, inv_id]
        for key, value in sorted_shp:
            signature_parts.append(f"Shp_{key}={value}")
        signature_parts.append(client.password1)
        signature_string = ":".join(signature_parts)
        signature = hashlib.md5(signature_string.encode("utf-8")).hexdigest().upper()

        # Should not raise
        result = client.verify_success_url(
            out_sum=out_sum,
            inv_id=inv_id,
            signature_value=signature,
            shp_params=shp_params,
        )
        assert result is True

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

    def test_create_split_payment_url_basic(self, client):
        """Test creating basic split payment URL."""
        split_merchants = [
            {
                "id": "merchant1",
                "amount": 50.00,
            },
            {
                "id": "merchant2",
                "amount": 50.50,
            },
        ]

        url = client.create_split_payment_url(
            out_amount=Decimal("100.50"),
            merchant_id="master_merchant",
            split_merchants=split_merchants,
        )

        assert url.startswith(client.base_url)
        assert "invoice=" in url
        assert "signature=" in url

    def test_create_split_payment_url_with_all_params(self, client):
        """Test creating split payment URL with all parameters."""
        from aiorobokassa.models.receipt import Receipt, ReceiptItem
        from aiorobokassa.enums import TaxRate, TaxSystem, PaymentMethod, PaymentObject

        receipt = Receipt(
            items=[
                ReceiptItem(
                    name="Item 1",
                    quantity=1,
                    cost=50.0,
                    tax=TaxRate.VAT20,
                    payment_method=PaymentMethod.FULL_PAYMENT,
                    payment_object=PaymentObject.COMMODITY,
                )
            ],
            sno=TaxSystem.OSN,
        )

        split_merchants = [
            {
                "id": "merchant1",
                "amount": 50.00,
                "invoice_id": 100,
                "receipt": receipt,
            },
            {
                "id": "merchant2",
                "amount": 50.50,
            },
        ]

        shop_params = [
            {"name": "param1", "value": "value1"},
            {"name": "param2", "value": "value2"},
        ]

        url = client.create_split_payment_url(
            out_amount=Decimal("100.50"),
            merchant_id="master_merchant",
            split_merchants=split_merchants,
            merchant_comment="Test split payment",
            shop_params=shop_params,
            email="test@example.com",
            inc_curr="BankCard",
            language="ru",
            is_test=True,
            expiration_date="2024-12-31T23:59:59",
        )

        assert url.startswith(client.base_url)
        assert "invoice=" in url
        assert "signature=" in url

    def test_create_split_payment_url_with_receipt_dict(self, client):
        """Test creating split payment URL with receipt as dict."""
        receipt_dict = {
            "items": [
                {
                    "name": "Item 1",
                    "quantity": 1,
                    "cost": 50.0,
                    "tax": "vat20",
                }
            ],
            "sno": "osn",
        }

        split_merchants = [
            {
                "id": "merchant1",
                "amount": 50.00,
                "receipt": receipt_dict,
            },
        ]

        url = client.create_split_payment_url(
            out_amount=Decimal("50.00"),
            merchant_id="master_merchant",
            split_merchants=split_merchants,
        )

        assert url.startswith(client.base_url)
        assert "invoice=" in url
        assert "signature=" in url

    def test_create_split_payment_url_with_receipt_json_string(self, client):
        """Test creating split payment URL with receipt as JSON string."""
        import json

        receipt_json = json.dumps(
            {
                "items": [
                    {
                        "name": "Item 1",
                        "quantity": 1,
                        "cost": 50.0,
                        "tax": "vat20",
                    }
                ],
                "sno": "osn",
            }
        )

        split_merchants = [
            {
                "id": "merchant1",
                "amount": 50.00,
                "receipt": receipt_json,
            },
        ]

        url = client.create_split_payment_url(
            out_amount=Decimal("50.00"),
            merchant_id="master_merchant",
            split_merchants=split_merchants,
        )

        assert url.startswith(client.base_url)
        assert "invoice=" in url
        assert "signature=" in url

    def test_create_split_payment_url_different_algorithms(self, client):
        """Test creating split payment URL with different signature algorithms."""
        split_merchants = [
            {
                "id": "merchant1",
                "amount": 50.00,
            },
        ]

        url_md5 = client.create_split_payment_url(
            out_amount=Decimal("50.00"),
            merchant_id="master_merchant",
            split_merchants=split_merchants,
            signature_algorithm=SignatureAlgorithm.MD5,
        )

        url_sha256 = client.create_split_payment_url(
            out_amount=Decimal("50.00"),
            merchant_id="master_merchant",
            split_merchants=split_merchants,
            signature_algorithm=SignatureAlgorithm.SHA256,
        )

        # URLs should be different due to different signatures
        assert url_md5 != url_sha256

    def test_create_split_payment_url_with_zero_amount_merchant(self, client):
        """Test creating split payment URL with merchant having zero amount."""
        split_merchants = [
            {
                "id": "merchant1",
                "amount": 100.00,
            },
            {
                "id": "merchant2",
                "amount": 0.00,  # Zero amount is allowed
            },
        ]

        url = client.create_split_payment_url(
            out_amount=Decimal("100.00"),
            merchant_id="master_merchant",
            split_merchants=split_merchants,
        )

        assert url.startswith(client.base_url)
        assert "invoice=" in url
        assert "signature=" in url

    def test_create_split_payment_url_signature_verification(self, client):
        """Test that split payment signature is correctly calculated."""
        from aiorobokassa.utils.signature import calculate_split_signature
        from urllib.parse import unquote, parse_qs

        split_merchants = [
            {
                "id": "merchant1",
                "amount": 50.00,
            },
        ]

        url = client.create_split_payment_url(
            out_amount=Decimal("50.00"),
            merchant_id="master_merchant",
            split_merchants=split_merchants,
        )

        # Parse URL to get invoice and signature
        query_string = url.split("?")[1]
        params = parse_qs(query_string)
        invoice_json = unquote(params["invoice"][0])
        received_signature = params["signature"][0]

        # Calculate expected signature
        expected_signature = calculate_split_signature(
            invoice_json=invoice_json,
            password=client.password1,
            algorithm=SignatureAlgorithm.MD5,
        )

        # Signature should match (case-insensitive comparison)
        assert received_signature.lower() == expected_signature.lower()
