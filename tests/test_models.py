"""Tests for Pydantic models."""

import pytest
from decimal import Decimal
from pydantic import ValidationError

from aiorobokassa.models.requests import (
    InvoiceRequest,
    PaymentRequest,
    RefundRequest,
    ResultURLNotification,
    SuccessURLNotification,
)


class TestPaymentRequest:
    """Tests for PaymentRequest model."""

    def test_payment_request_valid(self):
        """Test creating valid payment request."""
        request = PaymentRequest(
            out_sum=Decimal("100.50"),
            description="Test payment",
            inv_id=12345,
            email="test@example.com",
        )
        assert request.out_sum == Decimal("100.50")
        assert request.description == "Test payment"
        assert request.inv_id == 12345
        assert request.email == "test@example.com"

    def test_payment_request_minimal(self):
        """Test creating minimal payment request."""
        request = PaymentRequest(out_sum=Decimal("100.50"), description="Test")
        assert request.out_sum == Decimal("100.50")
        assert request.description == "Test"
        assert request.inv_id is None

    def test_payment_request_negative_amount(self):
        """Test that negative amount raises validation error."""
        with pytest.raises(ValidationError):
            PaymentRequest(out_sum=Decimal("-100.50"), description="Test")

    def test_payment_request_zero_amount(self):
        """Test that zero amount raises validation error."""
        with pytest.raises(ValidationError):
            PaymentRequest(out_sum=Decimal("0"), description="Test")

    def test_payment_request_empty_description(self):
        """Test that empty description raises validation error."""
        with pytest.raises(ValidationError):
            PaymentRequest(out_sum=Decimal("100.50"), description="")

    def test_payment_request_whitespace_description(self):
        """Test that whitespace-only description raises validation error."""
        with pytest.raises(ValidationError):
            PaymentRequest(out_sum=Decimal("100.50"), description="   ")

    def test_payment_request_with_user_parameters(self):
        """Test payment request with user parameters."""
        request = PaymentRequest(
            out_sum=Decimal("100.50"),
            description="Test",
            user_parameters={"user_id": "123", "order_id": "456"},
        )
        assert request.user_parameters == {"user_id": "123", "order_id": "456"}


class TestResultURLNotification:
    """Tests for ResultURLNotification model."""

    def test_result_url_notification_valid(self):
        """Test creating valid ResultURL notification."""
        notification = ResultURLNotification(
            out_sum="100.50",
            inv_id="12345",
            SignatureValue="ABC123",
            shp_params={"user_id": "123"},
        )
        assert notification.out_sum == "100.50"
        assert notification.inv_id == "12345"
        assert notification.signature_value == "ABC123"
        assert notification.shp_params == {"user_id": "123"}

    def test_result_url_notification_with_alias(self):
        """Test that SignatureValue alias works."""
        notification = ResultURLNotification(
            out_sum="100.50",
            inv_id="12345",
            signature_value="ABC123",
        )
        assert notification.signature_value == "ABC123"


class TestSuccessURLNotification:
    """Tests for SuccessURLNotification model."""

    def test_success_url_notification_valid(self):
        """Test creating valid SuccessURL notification."""
        notification = SuccessURLNotification(
            out_sum="100.50",
            inv_id="12345",
            SignatureValue="ABC123",
        )
        assert notification.out_sum == "100.50"
        assert notification.inv_id == "12345"
        assert notification.signature_value == "ABC123"


class TestInvoiceRequest:
    """Tests for InvoiceRequest model."""

    def test_invoice_request_valid(self):
        """Test creating valid invoice request."""
        request = InvoiceRequest(
            merchant_login="test_merchant",
            out_sum=Decimal("100.50"),
            description="Test invoice",
            inv_id=12345,
            email="test@example.com",
        )
        assert request.merchant_login == "test_merchant"
        assert request.out_sum == Decimal("100.50")
        assert request.description == "Test invoice"
        assert request.inv_id == 12345

    def test_invoice_request_negative_amount(self):
        """Test that negative amount raises validation error."""
        with pytest.raises(ValidationError):
            InvoiceRequest(
                merchant_login="test_merchant",
                out_sum=Decimal("-100.50"),
                description="Test",
            )

    def test_invoice_request_with_user_parameters(self):
        """Test invoice request with user parameters."""
        request = InvoiceRequest(
            merchant_login="test_merchant",
            out_sum=Decimal("100.50"),
            description="Test",
            user_parameters={"param1": "value1"},
        )
        assert request.user_parameters == {"param1": "value1"}


class TestRefundRequest:
    """Tests for RefundRequest model."""

    def test_refund_request_valid(self):
        """Test creating valid refund request."""
        request = RefundRequest(invoice_id=12345, amount=Decimal("50.25"))
        assert request.invoice_id == 12345
        assert request.amount == Decimal("50.25")

    def test_refund_request_without_amount(self):
        """Test refund request without amount (full refund)."""
        request = RefundRequest(invoice_id=12345)
        assert request.invoice_id == 12345
        assert request.amount is None

    def test_refund_request_negative_amount(self):
        """Test that negative amount raises validation error."""
        with pytest.raises(ValidationError):
            RefundRequest(invoice_id=12345, amount=Decimal("-50.25"))

    def test_refund_request_zero_amount(self):
        """Test that zero amount raises validation error."""
        with pytest.raises(ValidationError):
            RefundRequest(invoice_id=12345, amount=Decimal("0"))
