"""Tests for RefundMixin."""

import pytest
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from xml.etree import ElementTree as ET

from aiorobokassa.enums import SignatureAlgorithm


class TestRefundMixin:
    """Tests for RefundMixin."""

    @pytest.mark.asyncio
    async def test_create_refund_full(self, client):
        """Test creating full refund."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(
            return_value='<?xml version="1.0"?><Response><Code>0</Code><Description>Success</Description></Response>'
        )
        mock_response.close = MagicMock()

        with patch.object(client, "_post", return_value=mock_response):
            result = await client.create_refund(invoice_id=12345)

            assert result["Code"] == "0"
            assert result["Description"] == "Success"

    @pytest.mark.asyncio
    async def test_create_refund_partial(self, client):
        """Test creating partial refund."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(
            return_value='<?xml version="1.0"?><Response><Code>0</Code></Response>'
        )
        mock_response.close = MagicMock()

        with patch.object(client, "_post", return_value=mock_response):
            result = await client.create_refund(invoice_id=12345, amount=Decimal("50.25"))

            assert result["Code"] == "0"

    @pytest.mark.asyncio
    async def test_create_refund_xml_structure(self, client):
        """Test that refund XML has correct structure."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(
            return_value='<?xml version="1.0"?><Response><Code>0</Code></Response>'
        )
        mock_response.close = MagicMock()

        with patch.object(client, "_post", return_value=mock_response) as mock_post:
            await client.create_refund(invoice_id=12345, amount=Decimal("50.25"))

            assert mock_post.called
            call_args = mock_post.call_args
            xml_data = call_args[1]["data"]

            root = ET.fromstring(xml_data)
            assert root.tag == "RefundRequest"
            assert root.find("MerchantLogin").text == client.merchant_login
            assert root.find("InvoiceID").text == "12345"
            assert root.find("Amount").text == "50.25"
            assert root.find("SignatureValue") is not None

    @pytest.mark.asyncio
    async def test_create_refund_without_amount(self, client):
        """Test creating refund without amount (full refund)."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(
            return_value='<?xml version="1.0"?><Response><Code>0</Code></Response>'
        )
        mock_response.close = MagicMock()

        with patch.object(client, "_post", return_value=mock_response) as mock_post:
            await client.create_refund(invoice_id=12345)

            call_args = mock_post.call_args
            xml_data = call_args[1]["data"]
            root = ET.fromstring(xml_data)

            # Amount should not be present for full refund
            assert root.find("Amount") is None

    @pytest.mark.asyncio
    async def test_get_refund_status(self, client):
        """Test getting refund status."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(
            return_value='<?xml version="1.0"?><Response><Code>0</Code><State>5</State></Response>'
        )
        mock_response.close = MagicMock()

        with patch.object(client, "_post", return_value=mock_response):
            result = await client.get_refund_status(invoice_id=12345)

            assert result["Code"] == "0"
            assert result["State"] == "5"

    @pytest.mark.asyncio
    async def test_get_refund_status_xml_structure(self, client):
        """Test that refund status XML has correct structure."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(
            return_value='<?xml version="1.0"?><Response><Code>0</Code></Response>'
        )
        mock_response.close = MagicMock()

        with patch.object(client, "_post", return_value=mock_response) as mock_post:
            await client.get_refund_status(invoice_id=12345)

            assert mock_post.called
            call_args = mock_post.call_args
            xml_data = call_args[1]["data"]

            root = ET.fromstring(xml_data)
            assert root.tag == "RefundStatusRequest"
            assert root.find("MerchantLogin").text == client.merchant_login
            assert root.find("InvoiceID").text == "12345"
            assert root.find("SignatureValue") is not None

    @pytest.mark.asyncio
    async def test_refund_different_algorithms(self, client):
        """Test refund operations with different signature algorithms."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(
            return_value='<?xml version="1.0"?><Response><Code>0</Code></Response>'
        )
        mock_response.close = MagicMock()

        with patch.object(client, "_post", return_value=mock_response) as mock_post:
            await client.create_refund(
                invoice_id=12345, signature_algorithm=SignatureAlgorithm.SHA512
            )

            call_args = mock_post.call_args
            xml_data = call_args[1]["data"]
            root = ET.fromstring(xml_data)
            signature = root.find("SignatureValue").text

            # SHA512 signature should be 128 characters
            assert len(signature) == 128
