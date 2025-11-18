"""Tests for XML utilities."""

import pytest

from aiorobokassa.client import RoboKassaClient
from aiorobokassa.exceptions import XMLParseError


class TestXMLMixin:
    """Tests for XMLMixin methods."""

    @pytest.fixture
    def xml_client(self, merchant_login, password1, password2):
        """Create client for XML testing."""
        return RoboKassaClient(
            merchant_login=merchant_login,
            password1=password1,
            password2=password2,
            test_mode=True,
        )

    def test_parse_xml_response_valid(self, xml_client):
        """Test parsing valid XML response."""
        xml_text = """<?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Code>0</Code>
            <Description>Success</Description>
            <InvoiceID>12345</InvoiceID>
        </Response>"""
        result = xml_client._parse_xml_response(xml_text)
        assert result["Code"] == "0"
        assert result["Description"] == "Success"
        assert result["InvoiceID"] == "12345"

    def test_parse_xml_response_empty_text(self, xml_client):
        """Test parsing XML with empty text nodes."""
        xml_text = """<?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Code></Code>
            <Description>Success</Description>
        </Response>"""
        result = xml_client._parse_xml_response(xml_text)
        assert result["Code"] == ""
        assert result["Description"] == "Success"

    def test_parse_xml_response_invalid(self, xml_client):
        """Test parsing invalid XML raises error."""
        invalid_xml = "<Invalid><Unclosed>"
        with pytest.raises(XMLParseError):
            xml_client._parse_xml_response(invalid_xml)

    def test_build_xml_and_signature(self, xml_client):
        """Test building XML with signature."""
        base_data = {"MerchantLogin": "test", "Amount": "100.50"}
        optional_fields = {"InvoiceID": "12345", "Email": "test@example.com"}
        root = xml_client._build_xml_and_signature(
            "OperationRequest", base_data, optional_fields, "MD5"
        )
        assert root.tag == "OperationRequest"
        assert root.find("MerchantLogin").text == "test"
        assert root.find("Amount").text == "100.50"
        assert root.find("InvoiceID").text == "12345"
        assert root.find("Email").text == "test@example.com"
        assert root.find("SignatureValue") is not None
        assert root.find("SignatureValue").text

    def test_build_xml_and_signature_with_none_fields(self, xml_client):
        """Test building XML with None optional fields."""
        base_data = {"MerchantLogin": "test", "Amount": "100.50"}
        optional_fields = {"InvoiceID": "12345", "Email": None}
        root = xml_client._build_xml_and_signature(
            "OperationRequest", base_data, optional_fields, "MD5"
        )
        assert root.find("InvoiceID") is not None
        assert root.find("Email") is None  # None fields should not be added

    def test_build_xml_and_signature_different_algorithms(self, xml_client):
        """Test building XML with different signature algorithms."""
        base_data = {"MerchantLogin": "test", "Amount": "100.50"}
        optional_fields = {}
        root_md5 = xml_client._build_xml_and_signature(
            "OperationRequest", base_data, optional_fields, "MD5"
        )
        root_sha256 = xml_client._build_xml_and_signature(
            "OperationRequest", base_data, optional_fields, "SHA256"
        )
        sig_md5 = root_md5.find("SignatureValue").text
        sig_sha256 = root_sha256.find("SignatureValue").text
        assert sig_md5 != sig_sha256
        assert len(sig_md5) == 32  # MD5
        assert len(sig_sha256) == 64  # SHA256
