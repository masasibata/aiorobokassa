"""Tests for signature utilities."""

import pytest
from aiorobokassa.enums import SignatureAlgorithm
from aiorobokassa.exceptions import InvalidSignatureAlgorithmError
from aiorobokassa.utils.signature import (
    calculate_payment_signature,
    calculate_signature,
    verify_result_url_signature,
    verify_signature,
    verify_success_url_signature,
)


class TestCalculateSignature:
    """Tests for calculate_signature function."""

    def test_calculate_md5_signature(self):
        """Test MD5 signature calculation."""
        values = {"MerchantLogin": "test", "OutSum": "100.50"}
        password = "password123"
        signature = calculate_signature(values, password, SignatureAlgorithm.MD5)
        assert signature
        assert len(signature) == 32  # MD5 produces 32 hex characters
        assert signature.isupper()

    def test_calculate_sha256_signature(self):
        """Test SHA256 signature calculation."""
        values = {"MerchantLogin": "test", "OutSum": "100.50"}
        password = "password123"
        signature = calculate_signature(values, password, SignatureAlgorithm.SHA256)
        assert signature
        assert len(signature) == 64  # SHA256 produces 64 hex characters
        assert signature.isupper()

    def test_calculate_sha512_signature(self):
        """Test SHA512 signature calculation."""
        values = {"MerchantLogin": "test", "OutSum": "100.50"}
        password = "password123"
        signature = calculate_signature(values, password, SignatureAlgorithm.SHA512)
        assert signature
        assert len(signature) == 128  # SHA512 produces 128 hex characters
        assert signature.isupper()

    def test_calculate_signature_with_string_algorithm(self):
        """Test signature calculation with string algorithm."""
        values = {"MerchantLogin": "test", "OutSum": "100.50"}
        password = "password123"
        signature = calculate_signature(values, password, "MD5")
        assert signature
        assert len(signature) == 32

    def test_calculate_signature_sorts_keys(self):
        """Test that signature calculation sorts keys."""
        values1 = {"MerchantLogin": "test", "OutSum": "100.50"}
        values2 = {"OutSum": "100.50", "MerchantLogin": "test"}
        password = "password123"
        sig1 = calculate_signature(values1, password, SignatureAlgorithm.MD5)
        sig2 = calculate_signature(values2, password, SignatureAlgorithm.MD5)
        assert sig1 == sig2

    def test_calculate_signature_invalid_algorithm(self):
        """Test signature calculation with invalid algorithm."""
        values = {"MerchantLogin": "test", "OutSum": "100.50"}
        password = "password123"
        with pytest.raises(InvalidSignatureAlgorithmError):
            calculate_signature(values, password, "INVALID")


class TestVerifySignature:
    """Tests for verify_signature function."""

    def test_verify_valid_signature(self):
        """Test verification of valid signature."""
        values = {"MerchantLogin": "test", "OutSum": "100.50"}
        password = "password123"
        calculated = calculate_signature(values, password, SignatureAlgorithm.MD5)
        assert verify_signature(values, password, calculated, SignatureAlgorithm.MD5)

    def test_verify_invalid_signature(self):
        """Test verification of invalid signature."""
        values = {"MerchantLogin": "test", "OutSum": "100.50"}
        password = "password123"
        invalid_signature = "INVALID_SIGNATURE"
        assert not verify_signature(values, password, invalid_signature, SignatureAlgorithm.MD5)

    def test_verify_signature_case_insensitive(self):
        """Test that signature verification is case-insensitive."""
        values = {"MerchantLogin": "test", "OutSum": "100.50"}
        password = "password123"
        calculated = calculate_signature(values, password, SignatureAlgorithm.MD5)
        # Should work with lowercase signature
        assert verify_signature(values, password, calculated.lower(), SignatureAlgorithm.MD5)


class TestCalculatePaymentSignature:
    """Tests for calculate_payment_signature function."""

    def test_calculate_payment_signature_without_inv_id(self):
        """Test payment signature calculation without invoice ID."""
        signature = calculate_payment_signature(
            merchant_login="test_merchant",
            out_sum="100.50",
            inv_id=None,
            password="password123",
            algorithm=SignatureAlgorithm.MD5,
        )
        assert signature
        assert len(signature) == 32

    def test_calculate_payment_signature_with_inv_id(self):
        """Test payment signature calculation with invoice ID."""
        signature = calculate_payment_signature(
            merchant_login="test_merchant",
            out_sum="100.50",
            inv_id="12345",
            password="password123",
            algorithm=SignatureAlgorithm.MD5,
        )
        assert signature
        assert len(signature) == 32

    def test_calculate_payment_signature_different_algorithms(self):
        """Test payment signature with different algorithms."""
        base_params = {
            "merchant_login": "test_merchant",
            "out_sum": "100.50",
            "inv_id": "12345",
            "password": "password123",
        }
        md5_sig = calculate_payment_signature(**base_params, algorithm=SignatureAlgorithm.MD5)
        sha256_sig = calculate_payment_signature(**base_params, algorithm=SignatureAlgorithm.SHA256)
        sha512_sig = calculate_payment_signature(**base_params, algorithm=SignatureAlgorithm.SHA512)

        assert md5_sig != sha256_sig
        assert sha256_sig != sha512_sig
        assert md5_sig != sha512_sig

    def test_calculate_payment_signature_with_shp_params(self):
        """Test payment signature calculation with shp_params."""
        signature_with_shp = calculate_payment_signature(
            merchant_login="test_merchant",
            out_sum="100.50",
            inv_id="12345",
            password="password123",
            algorithm=SignatureAlgorithm.MD5,
            shp_params={"user_id": "123", "order_id": "456"},
        )
        signature_without_shp = calculate_payment_signature(
            merchant_login="test_merchant",
            out_sum="100.50",
            inv_id="12345",
            password="password123",
            algorithm=SignatureAlgorithm.MD5,
        )

        # Signatures should be different when shp_params are included
        assert signature_with_shp != signature_without_shp
        assert len(signature_with_shp) == 32

    def test_calculate_payment_signature_shp_params_sorted(self):
        """Test that shp_params are sorted alphabetically in signature."""
        # Same params in different order should produce same signature
        signature1 = calculate_payment_signature(
            merchant_login="test_merchant",
            out_sum="100.50",
            inv_id="12345",
            password="password123",
            algorithm=SignatureAlgorithm.MD5,
            shp_params={"user_id": "123", "order_id": "456"},
        )
        signature2 = calculate_payment_signature(
            merchant_login="test_merchant",
            out_sum="100.50",
            inv_id="12345",
            password="password123",
            algorithm=SignatureAlgorithm.MD5,
            shp_params={"order_id": "456", "user_id": "123"},  # Different order
        )

        # Signatures should be the same (sorted alphabetically)
        assert signature1 == signature2


class TestVerifyResultURLSignature:
    """Tests for verify_result_url_signature function."""

    def test_verify_result_url_signature_valid(self):
        """Test valid ResultURL signature verification."""
        out_sum = "100.50"
        inv_id = "12345"
        password = "password123"
        # Calculate signature manually with correct order: OutSum:InvId:password2
        import hashlib

        signature_string = f"{out_sum}:{inv_id}:{password}"
        calculated = hashlib.md5(signature_string.encode("utf-8")).hexdigest().upper()
        assert verify_result_url_signature(
            out_sum, inv_id, password, calculated, SignatureAlgorithm.MD5
        )

    def test_verify_result_url_signature_invalid(self):
        """Test invalid ResultURL signature verification."""
        out_sum = "100.50"
        inv_id = "12345"
        password = "password123"
        invalid_signature = "INVALID"
        assert not verify_result_url_signature(
            out_sum, inv_id, password, invalid_signature, SignatureAlgorithm.MD5
        )

    def test_verify_result_url_signature_with_shp_params(self):
        """Test ResultURL signature verification with Shp parameters."""
        out_sum = "100.50"
        inv_id = "12345"
        password = "password123"
        shp_params = {"user_id": "123", "order_id": "456"}
        # Calculate signature with shp_params in correct order: OutSum:InvId:password2:Shp_order_id=456:Shp_user_id=123
        # Shp_ parameters must be sorted alphabetically by key and in format "Shp_key=value"
        import hashlib

        sorted_shp = sorted(shp_params.items())  # [('order_id', '456'), ('user_id', '123')]
        signature_parts = [out_sum, inv_id, password]
        for key, value in sorted_shp:
            signature_parts.append(f"Shp_{key}={value}")
        signature_string = ":".join(signature_parts)
        calculated = hashlib.md5(signature_string.encode("utf-8")).hexdigest().upper()
        assert verify_result_url_signature(
            out_sum, inv_id, password, calculated, SignatureAlgorithm.MD5, shp_params=shp_params
        )


class TestVerifySuccessURLSignature:
    """Tests for verify_success_url_signature function."""

    def test_verify_success_url_signature_valid(self):
        """Test valid SuccessURL signature verification."""
        out_sum = "100.50"
        inv_id = "12345"
        password = "password123"
        # Calculate signature manually with correct order: OutSum:InvId:password1
        import hashlib

        signature_string = f"{out_sum}:{inv_id}:{password}"
        calculated = hashlib.md5(signature_string.encode("utf-8")).hexdigest().upper()
        assert verify_success_url_signature(
            out_sum, inv_id, password, calculated, SignatureAlgorithm.MD5
        )

    def test_verify_success_url_signature_invalid(self):
        """Test invalid SuccessURL signature verification."""
        out_sum = "100.50"
        inv_id = "12345"
        password = "password123"
        invalid_signature = "INVALID"
        assert not verify_success_url_signature(
            out_sum, inv_id, password, invalid_signature, SignatureAlgorithm.MD5
        )

    def test_verify_success_url_signature_with_shp_params(self):
        """Test SuccessURL signature verification with Shp parameters."""
        out_sum = "100.50"
        inv_id = "12345"
        password = "password123"
        shp_params = {"user_id": "123"}
        # Calculate signature with shp_params in correct order: OutSum:InvId:password1:Shp_user_id=123
        # Shp_ parameters must be in format "Shp_key=value"
        import hashlib

        sorted_shp = sorted(shp_params.items())  # [('user_id', '123')]
        signature_parts = [out_sum, inv_id, password]
        for key, value in sorted_shp:
            signature_parts.append(f"Shp_{key}={value}")
        signature_string = ":".join(signature_parts)
        calculated = hashlib.md5(signature_string.encode("utf-8")).hexdigest().upper()
        assert verify_success_url_signature(
            out_sum, inv_id, password, calculated, SignatureAlgorithm.MD5, shp_params=shp_params
        )
