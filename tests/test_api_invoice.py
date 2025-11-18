"""Tests for InvoiceMixin."""

import pytest
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

from aiorobokassa.enums import InvoiceType, SignatureAlgorithm, TaxRate, PaymentMethod, PaymentObject
from aiorobokassa.models.requests import InvoiceItem


class TestInvoiceMixin:
    """Tests for InvoiceMixin."""

    @pytest.mark.asyncio
    async def test_create_invoice_basic(self, client):
        """Test creating basic invoice."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={
                "isSuccess": True,
                "id": "test-id-123",
                "url": "https://auth.robokassa.ru/merchant/Invoice/test-id-123",
                "invId": 12345,
                "encodedId": "test-id-123",
            }
        )
        mock_response.close = MagicMock()

        with patch.object(client, "_post", return_value=mock_response):
            result = await client.create_invoice(
                out_sum=Decimal("100.50"),
                description="Test invoice",
            )

            assert result["id"] == "test-id-123"
            assert result["url"] == "https://auth.robokassa.ru/merchant/Invoice/test-id-123"
            assert result["inv_id"] == 12345

    @pytest.mark.asyncio
    async def test_create_invoice_with_all_params(self, client):
        """Test creating invoice with all parameters."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={
                "isSuccess": True,
                "id": "test-id-456",
                "url": "https://auth.robokassa.ru/merchant/Invoice/test-id-456",
                "invId": 67890,
            }
        )
        mock_response.close = MagicMock()

        invoice_items = [
            InvoiceItem(
                name="Test Item",
                quantity=1,
                cost=100.50,
                tax=TaxRate.VAT20,
                payment_method=PaymentMethod.FULL_PAYMENT,
                payment_object=PaymentObject.COMMODITY,
            )
        ]

        with patch.object(client, "_post", return_value=mock_response):
            result = await client.create_invoice(
                out_sum=Decimal("100.50"),
                description="Test invoice",
                invoice_type=InvoiceType.ONE_TIME,
                inv_id=67890,
                culture="ru",
                merchant_comments="Test comment",
                invoice_items=invoice_items,
                user_fields={"user_id": "123"},
                success_url="https://example.com/success",
                fail_url="https://example.com/fail",
            )

            assert result["id"] == "test-id-456"
            assert result["inv_id"] == 67890

    @pytest.mark.asyncio
    async def test_create_invoice_jwt_structure(self, client):
        """Test that invoice JWT has correct structure."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={"isSuccess": True, "id": "test-id", "url": "https://test.com"}
        )
        mock_response.close = MagicMock()

        with patch.object(client, "_post", return_value=mock_response) as mock_post:
            await client.create_invoice(
                out_sum=Decimal("100.50"),
                description="Test invoice",
                inv_id=12345,
            )

            # Verify POST was called
            assert mock_post.called
            call_args = mock_post.call_args

            # Verify endpoint
            assert "CreateInvoice" in call_args[0][0]

            # Verify JWT token is sent as data (string)
            jwt_token = call_args[1]["data"]
            assert isinstance(jwt_token, str)
            assert len(jwt_token.split(".")) == 3  # JWT has 3 parts

    @pytest.mark.asyncio
    async def test_create_invoice_with_invoice_items(self, client):
        """Test creating invoice with invoice items."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={"isSuccess": True, "id": "test-id", "url": "https://test.com"}
        )
        mock_response.close = MagicMock()

        invoice_items = [
            InvoiceItem(
                name="Item 1",
                quantity=2,
                cost=50.0,
                tax=TaxRate.VAT20,
            ),
            InvoiceItem(
                name="Item 2",
                quantity=1,
                cost=100.0,
                tax=TaxRate.VAT10,
                payment_method=PaymentMethod.FULL_PAYMENT,
                payment_object=PaymentObject.SERVICE,
            ),
        ]

        with patch.object(client, "_post", return_value=mock_response) as mock_post:
            await client.create_invoice(
                out_sum=Decimal("200.00"),
                description="Test invoice",
                invoice_items=invoice_items,
            )

            # Verify request was made
            assert mock_post.called

    @pytest.mark.asyncio
    async def test_create_invoice_different_algorithms(self, client):
        """Test creating invoice with different signature algorithms."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={"isSuccess": True, "id": "test-id", "url": "https://test.com"}
        )
        mock_response.close = MagicMock()

        with patch.object(client, "_post", return_value=mock_response):
            result = await client.create_invoice(
                out_sum=Decimal("100.50"),
                description="Test",
                signature_algorithm=SignatureAlgorithm.SHA256,
            )

            assert result["id"] == "test-id"

    @pytest.mark.asyncio
    async def test_create_invoice_error(self, client):
        """Test invoice creation error handling."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={
                "isSuccess": False,
                "errorMessage": "Invalid merchant login",
            }
        )
        mock_response.close = MagicMock()

        with patch.object(client, "_post", return_value=mock_response):
            from aiorobokassa.exceptions import APIError

            with pytest.raises(APIError, match="Invoice creation failed"):
                await client.create_invoice(
                    out_sum=Decimal("100.50"),
                    description="Test invoice",
                )

    @pytest.mark.asyncio
    async def test_deactivate_invoice(self, client):
        """Test deactivating invoice."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"isSuccess": True})
        mock_response.close = MagicMock()

        with patch.object(client, "_post", return_value=mock_response):
            await client.deactivate_invoice(inv_id=12345)

            # Should not raise any exception

    @pytest.mark.asyncio
    async def test_deactivate_invoice_no_identifier(self, client):
        """Test deactivating invoice without identifier raises error."""
        with pytest.raises(ValueError, match="At least one identifier"):
            await client.deactivate_invoice()

    @pytest.mark.asyncio
    async def test_get_invoice_information_list(self, client):
        """Test getting invoice information list."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={
                "isSuccess": True,
                "invoices": [],
                "totalCount": 0,
                "currentPage": 1,
                "pageSize": 10,
            }
        )
        mock_response.close = MagicMock()

        with patch.object(client, "_post", return_value=mock_response):
            result = await client.get_invoice_information_list(
                current_page=1,
                page_size=10,
                invoice_statuses=["paid", "notpaid"],
            )

            assert result["isSuccess"] is True
            assert result["currentPage"] == 1
