"""Tests for Receipt (fiscalization) support."""

import json
import pytest
from decimal import Decimal
from urllib.parse import unquote

from aiorobokassa.enums import SignatureAlgorithm
from aiorobokassa.models.requests import PaymentRequest


class TestReceiptSupport:
    """Tests for Receipt parameter support."""

    def test_payment_request_with_receipt_dict(self):
        """Test PaymentRequest with receipt as dict."""
        receipt_data = {
            "sno": "osn",
            "items": [
                {
                    "name": "Товар 1",
                    "quantity": 1,
                    "sum": 100,
                    "payment_method": "full_payment",
                    "payment_object": "commodity",
                    "tax": "vat10",
                }
            ],
        }
        request = PaymentRequest(
            out_sum=Decimal("100.00"),
            description="Test payment",
            receipt=receipt_data,
        )
        assert request.receipt is not None
        assert isinstance(request.receipt, str)
        # Should be valid JSON
        parsed = json.loads(request.receipt)
        assert parsed["sno"] == "osn"
        assert len(parsed["items"]) == 1

    def test_payment_request_with_receipt_string(self):
        """Test PaymentRequest with receipt as JSON string."""
        receipt_json = (
            '{"sno":"osn","items":[{"name":"Товар 1","quantity":1,"sum":100,"tax":"vat10"}]}'
        )
        request = PaymentRequest(
            out_sum=Decimal("100.00"),
            description="Test payment",
            receipt=receipt_json,
        )
        assert request.receipt == receipt_json

    def test_payment_request_with_invalid_receipt(self):
        """Test PaymentRequest with invalid receipt raises error."""
        with pytest.raises(ValueError, match="receipt must be valid JSON"):
            PaymentRequest(
                out_sum=Decimal("100.00"),
                description="Test payment",
                receipt="invalid json",
            )

    def test_build_payment_params_with_receipt(self, client):
        """Test building payment parameters with receipt."""
        receipt_data = {
            "sno": "osn",
            "items": [
                {
                    "name": "Товар 1",
                    "quantity": 1,
                    "sum": 100,
                    "tax": "vat10",
                }
            ],
        }
        request = PaymentRequest(
            out_sum=Decimal("100.00"),
            description="Test payment",
            receipt=receipt_data,
        )
        params = client._build_payment_params(request, SignatureAlgorithm.MD5)

        assert "Receipt" in params
        # Receipt should be URL-encoded
        receipt_param = params["Receipt"]
        assert receipt_param is not None
        # Decode and verify it's valid JSON
        decoded = unquote(receipt_param)
        parsed = json.loads(decoded)
        assert parsed["sno"] == "osn"

    def test_receipt_in_signature_calculation(self, client):
        """Test that receipt is included in signature calculation."""
        from aiorobokassa.utils.signature import calculate_payment_signature

        receipt_data = {
            "sno": "osn",
            "items": [{"name": "Товар", "quantity": 1, "sum": 100, "tax": "vat10"}],
        }
        receipt_json = json.dumps(receipt_data, ensure_ascii=False)

        # Calculate signature with receipt
        sig_with_receipt = calculate_payment_signature(
            merchant_login=client.merchant_login,
            out_sum="100.00",
            inv_id="123",
            password=client.password1,
            algorithm=SignatureAlgorithm.MD5,
            receipt=receipt_json,
        )

        # Calculate signature without receipt
        sig_without_receipt = calculate_payment_signature(
            merchant_login=client.merchant_login,
            out_sum="100.00",
            inv_id="123",
            password=client.password1,
            algorithm=SignatureAlgorithm.MD5,
        )

        # Signatures should be different
        assert sig_with_receipt != sig_without_receipt

    @pytest.mark.asyncio
    async def test_create_payment_url_with_receipt_dict(self, client):
        """Test creating payment URL with receipt as dict."""
        receipt_data = {
            "sno": "osn",
            "items": [
                {
                    "name": "Товар 1",
                    "quantity": 1,
                    "sum": 100,
                    "tax": "vat10",
                }
            ],
        }
        url = await client.create_payment_url(
            out_sum=Decimal("100.00"),
            description="Test payment",
            receipt=receipt_data,
        )
        assert "Receipt=" in url

    @pytest.mark.asyncio
    async def test_create_payment_url_with_receipt_string(self, client):
        """Test creating payment URL with receipt as JSON string."""
        receipt_json = (
            '{"sno":"osn","items":[{"name":"Товар","quantity":1,"sum":100,"tax":"vat10"}]}'
        )
        url = await client.create_payment_url(
            out_sum=Decimal("100.00"),
            description="Test payment",
            receipt=receipt_json,
        )
        assert "Receipt=" in url

    def test_receipt_with_multiple_items(self, client):
        """Test receipt with multiple items."""
        receipt_data = {
            "sno": "osn",
            "items": [
                {
                    "name": "Товар 1",
                    "quantity": 1,
                    "sum": 100,
                    "tax": "vat10",
                },
                {
                    "name": "Товар 2",
                    "quantity": 2,
                    "sum": 200,
                    "tax": "vat20",
                },
            ],
        }
        request = PaymentRequest(
            out_sum=Decimal("300.00"),
            description="Test payment",
            receipt=receipt_data,
        )
        params = client._build_payment_params(request, SignatureAlgorithm.MD5)
        assert "Receipt" in params

    def test_receipt_with_nomenclature_code(self, client):
        """Test receipt with nomenclature code (marking)."""
        receipt_data = {
            "sno": "osn",
            "items": [
                {
                    "name": "Маркированный товар",
                    "quantity": 1,
                    "sum": 100,
                    "tax": "vat10",
                    "nomenclature_code": "04620034587217",
                }
            ],
        }
        request = PaymentRequest(
            out_sum=Decimal("100.00"),
            description="Test payment",
            receipt=receipt_data,
        )
        params = client._build_payment_params(request, SignatureAlgorithm.MD5)
        assert "Receipt" in params
        # Verify nomenclature_code is in receipt
        decoded = unquote(params["Receipt"])
        parsed = json.loads(decoded)
        assert parsed["items"][0]["nomenclature_code"] == "04620034587217"
