"""Tests for InvoiceMixin."""

import pytest
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from xml.etree import ElementTree as ET

from aiorobokassa.enums import SignatureAlgorithm


class TestInvoiceMixin:
    """Tests for InvoiceMixin."""

    @pytest.mark.asyncio
    async def test_create_invoice_basic(self, client):
        """Test creating basic invoice."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(
            return_value='<?xml version="1.0"?><Response><Code>0</Code><Description>Success</Description></Response>'
        )
        mock_response.close = MagicMock()

        with patch.object(client, "_post", return_value=mock_response):
            result = await client.create_invoice(
                out_sum=Decimal("100.50"),
                description="Test invoice",
            )

            assert result["Code"] == "0"
            assert result["Description"] == "Success"

    @pytest.mark.asyncio
    async def test_create_invoice_with_all_params(self, client):
        """Test creating invoice with all parameters."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(
            return_value='<?xml version="1.0"?><Response><Code>0</Code><InvoiceID>12345</InvoiceID></Response>'
        )
        mock_response.close = MagicMock()

        with patch.object(client, "_post", return_value=mock_response):
            result = await client.create_invoice(
                out_sum=Decimal("100.50"),
                description="Test invoice",
                inv_id=12345,
                email="test@example.com",
                expiration_date="2024-12-31",
                user_parameters={"user_id": "123"},
            )

            assert result["Code"] == "0"
            assert result["InvoiceID"] == "12345"

    @pytest.mark.asyncio
    async def test_create_invoice_xml_structure(self, client):
        """Test that invoice XML has correct structure."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(
            return_value='<?xml version="1.0"?><Response><Code>0</Code></Response>'
        )
        mock_response.close = MagicMock()

        with patch.object(client, "_post", return_value=mock_response) as mock_post:
            await client.create_invoice(
                out_sum=Decimal("100.50"),
                description="Test invoice",
                inv_id=12345,
                email="test@example.com",
            )

            # Verify POST was called
            assert mock_post.called
            call_args = mock_post.call_args
            xml_data = call_args[1]["data"]

            # Parse XML and verify structure
            root = ET.fromstring(xml_data)
            assert root.tag == "OperationRequest"
            assert root.find("MerchantLogin").text == client.merchant_login
            assert root.find("Amount").text == "100.50"
            assert root.find("Description").text == "Test invoice"
            assert root.find("InvoiceID").text == "12345"
            assert root.find("Email").text == "test@example.com"
            assert root.find("SignatureValue") is not None

    @pytest.mark.asyncio
    async def test_create_invoice_with_user_parameters(self, client):
        """Test creating invoice with user parameters."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(
            return_value='<?xml version="1.0"?><Response><Code>0</Code></Response>'
        )
        mock_response.close = MagicMock()

        with patch.object(client, "_post", return_value=mock_response) as mock_post:
            await client.create_invoice(
                out_sum=Decimal("100.50"),
                description="Test invoice",
                user_parameters={"user_id": "123", "order_id": "456"},
            )

            call_args = mock_post.call_args
            xml_data = call_args[1]["data"]
            root = ET.fromstring(xml_data)

            # Check for Params element
            params_elem = root.find("Params")
            assert params_elem is not None

            # Check for Param elements
            param_elements = params_elem.findall("Param")
            assert len(param_elements) == 2

            # Verify param structure
            param_names = [p.find("Name").text for p in param_elements]
            param_values = [p.find("Value").text for p in param_elements]

            assert "Shp_user_id" in param_names
            assert "Shp_order_id" in param_names
            assert "123" in param_values
            assert "456" in param_values

    @pytest.mark.asyncio
    async def test_create_invoice_different_algorithms(self, client):
        """Test creating invoice with different signature algorithms."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(
            return_value='<?xml version="1.0"?><Response><Code>0</Code></Response>'
        )
        mock_response.close = MagicMock()

        with patch.object(client, "_post", return_value=mock_response) as mock_post:
            await client.create_invoice(
                out_sum=Decimal("100.50"),
                description="Test",
                signature_algorithm=SignatureAlgorithm.SHA256,
            )

            call_args = mock_post.call_args
            xml_data = call_args[1]["data"]
            root = ET.fromstring(xml_data)
            signature = root.find("SignatureValue").text

            # SHA256 signature should be 64 characters
            assert len(signature) == 64
