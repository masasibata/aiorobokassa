"""Tests for Receipt usage with Pydantic models."""

import pytest
from decimal import Decimal
from urllib.parse import unquote

from aiorobokassa.enums import PaymentMethod, PaymentObject, SignatureAlgorithm, TaxRate, TaxSystem
from aiorobokassa.models.receipt import Receipt, ReceiptItem
from aiorobokassa.models.requests import PaymentRequest


class TestReceiptWithPaymentRequest:
    """Tests for using Receipt model with PaymentRequest."""

    def test_payment_request_with_receipt_model(self):
        """Test PaymentRequest with Receipt model."""
        item = ReceiptItem(
            name="Товар 1",
            quantity=1,
            sum=Decimal("100.00"),
            tax=TaxRate.VAT10,
        )
        receipt = Receipt(items=[item], sno=TaxSystem.OSN)

        request = PaymentRequest(
            out_sum=Decimal("100.00"),
            description="Test payment",
            receipt=receipt,
        )
        assert request.receipt is not None
        assert isinstance(request.receipt, str)
        assert "osn" in request.receipt
        assert "Товар 1" in request.receipt

    def test_payment_request_with_receipt_item_direct(self):
        """Test PaymentRequest with ReceiptItem directly (should work via dict)."""
        item = ReceiptItem(
            name="Товар",
            quantity=1,
            sum=Decimal("100.00"),
            tax=TaxRate.VAT10,
        )
        receipt = Receipt(items=[item])

        request = PaymentRequest(
            out_sum=Decimal("100.00"),
            description="Test",
            receipt=receipt,
        )
        assert request.receipt is not None

    def test_build_payment_params_with_receipt_model(self, client):
        """Test building payment parameters with Receipt model."""
        item = ReceiptItem(
            name="Товар",
            quantity=1,
            sum=Decimal("100.00"),
            tax=TaxRate.VAT10,
        )
        receipt = Receipt(items=[item], sno=TaxSystem.OSN)

        request = PaymentRequest(
            out_sum=Decimal("100.00"),
            description="Test payment",
            receipt=receipt,
        )
        params = client._build_payment_params(request, SignatureAlgorithm.MD5)

        assert "Receipt" in params
        receipt_param = params["Receipt"]
        assert receipt_param is not None
        decoded = unquote(receipt_param)
        assert "osn" in decoded
        assert "Товар" in decoded

    @pytest.mark.asyncio
    async def test_create_payment_url_with_receipt_model(self, client):
        """Test creating payment URL with Receipt model."""
        item = ReceiptItem(
            name="Товар",
            quantity=1,
            sum=Decimal("100.00"),
            tax=TaxRate.VAT10,
            payment_method=PaymentMethod.FULL_PAYMENT,
            payment_object=PaymentObject.COMMODITY,
        )
        receipt = Receipt(items=[item], sno=TaxSystem.OSN)

        url = await client.create_payment_url(
            out_sum=Decimal("100.00"),
            description="Test payment",
            receipt=receipt,
        )
        assert "Receipt=" in url

    def test_receipt_with_all_enums(self, client):
        """Test receipt with all enum types."""
        item = ReceiptItem(
            name="Услуга",
            quantity=1,
            sum=Decimal("500.00"),
            tax=TaxRate.VAT20,
            payment_method=PaymentMethod.FULL_PAYMENT,
            payment_object=PaymentObject.SERVICE,
        )
        receipt = Receipt(items=[item], sno=TaxSystem.USN_INCOME)

        request = PaymentRequest(
            out_sum=Decimal("500.00"),
            description="Service payment",
            receipt=receipt,
        )
        params = client._build_payment_params(request, SignatureAlgorithm.MD5)
        assert "Receipt" in params

    def test_receipt_with_nomenclature_code(self, client):
        """Test receipt with nomenclature code."""
        item = ReceiptItem(
            name="Маркированный товар",
            quantity=1,
            sum=Decimal("100.00"),
            tax=TaxRate.VAT10,
            nomenclature_code="04620034587217",
        )
        receipt = Receipt(items=[item])

        request = PaymentRequest(
            out_sum=Decimal("100.00"),
            description="Test",
            receipt=receipt,
        )
        params = client._build_payment_params(request, SignatureAlgorithm.MD5)
        decoded = unquote(params["Receipt"])
        assert "04620034587217" in decoded

    def test_receipt_multiple_items(self, client):
        """Test receipt with multiple items."""
        items = [
            ReceiptItem(
                name="Товар 1",
                quantity=1,
                sum=Decimal("100.00"),
                tax=TaxRate.VAT10,
            ),
            ReceiptItem(
                name="Товар 2",
                quantity=2,
                cost=Decimal("50.00"),
                tax=TaxRate.VAT20,
            ),
        ]
        receipt = Receipt(items=items, sno=TaxSystem.OSN)

        request = PaymentRequest(
            out_sum=Decimal("200.00"),
            description="Test",
            receipt=receipt,
        )
        params = client._build_payment_params(request, SignatureAlgorithm.MD5)
        assert "Receipt" in params
