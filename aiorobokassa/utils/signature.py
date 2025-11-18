"""Signature calculation and verification for RoboKassa."""

import hashlib
from typing import Dict, Optional, Union

from aiorobokassa.enums import SignatureAlgorithm
from aiorobokassa.exceptions import InvalidSignatureAlgorithmError

# Algorithm mapping
ALGORITHMS = {
    SignatureAlgorithm.MD5: hashlib.md5,
    SignatureAlgorithm.SHA256: hashlib.sha256,
    SignatureAlgorithm.SHA512: hashlib.sha512,
}


def calculate_signature(
    values: Dict[str, str],
    password: str,
    algorithm: Union[str, SignatureAlgorithm] = SignatureAlgorithm.MD5,
) -> str:
    """
    Calculate signature for RoboKassa.

    Args:
        values: Dictionary of values to include in signature (sorted by key)
        password: Password for signature calculation
        algorithm: Hash algorithm (MD5, SHA256, SHA512) or SignatureAlgorithm enum

    Returns:
        Hexadecimal signature string

    Raises:
        InvalidSignatureAlgorithmError: If algorithm is not supported
    """
    # Convert string to enum if needed
    if isinstance(algorithm, str):
        try:
            algorithm = SignatureAlgorithm.from_string(algorithm)
        except ValueError as e:
            raise InvalidSignatureAlgorithmError(str(e)) from e

    # Sort values by key and create signature string
    sorted_items = sorted(values.items())
    signature_string = ":".join(str(value) for _, value in sorted_items)
    signature_string += f":{password}"

    # Calculate hash based on algorithm
    hash_func = ALGORITHMS.get(algorithm)
    if hash_func is None:
        raise InvalidSignatureAlgorithmError(f"Unsupported algorithm: {algorithm}")

    hash_obj = hash_func(signature_string.encode("utf-8"))
    return hash_obj.hexdigest().upper()


def verify_signature(
    values: Dict[str, str],
    password: str,
    received_signature: str,
    algorithm: Union[str, SignatureAlgorithm] = SignatureAlgorithm.MD5,
) -> bool:
    """
    Verify signature from RoboKassa.

    Args:
        values: Dictionary of values used in signature
        password: Password for signature verification
        received_signature: Signature received from RoboKassa
        algorithm: Hash algorithm (MD5, SHA256, SHA512)

    Returns:
        True if signature is valid, False otherwise
    """
    calculated_signature = calculate_signature(values, password, algorithm)
    return calculated_signature.upper() == received_signature.upper()


def calculate_payment_signature(
    merchant_login: str,
    out_sum: str,
    inv_id: Optional[str],
    password: str,
    algorithm: Union[str, SignatureAlgorithm] = SignatureAlgorithm.MD5,
    receipt: Optional[str] = None,
) -> str:
    """
    Calculate signature for payment URL.

    Signature format: MD5(merchant_login:out_sum:inv_id:receipt:password1)
    If receipt is provided, it must be included in signature calculation.

    Args:
        merchant_login: Merchant login
        out_sum: Payment amount
        inv_id: Invoice ID (optional)
        password: Password (password1)
        algorithm: Hash algorithm
        receipt: Receipt JSON string for fiscalization (optional)

    Returns:
        Signature string
    """
    values = {
        "MerchantLogin": merchant_login,
        "OutSum": out_sum,
    }
    if inv_id:
        values["InvId"] = inv_id
    if receipt:
        values["Receipt"] = receipt

    return calculate_signature(values, password, algorithm)


def verify_result_url_signature(
    out_sum: str,
    inv_id: str,
    password: str,
    received_signature: str,
    algorithm: Union[str, SignatureAlgorithm] = SignatureAlgorithm.MD5,
) -> bool:
    """
    Verify signature from ResultURL notification.

    Signature format: MD5(out_sum:inv_id:password2)

    Args:
        out_sum: Payment amount
        inv_id: Invoice ID
        password: Password (password2)
        received_signature: Signature from notification
        algorithm: Hash algorithm

    Returns:
        True if signature is valid
    """
    values = {
        "OutSum": out_sum,
        "InvId": inv_id,
    }
    return verify_signature(values, password, received_signature, algorithm)


def verify_success_url_signature(
    out_sum: str,
    inv_id: str,
    password: str,
    received_signature: str,
    algorithm: Union[str, SignatureAlgorithm] = SignatureAlgorithm.MD5,
) -> bool:
    """
    Verify signature from SuccessURL redirect.

    Signature format: MD5(out_sum:inv_id:password1)

    Args:
        out_sum: Payment amount
        inv_id: Invoice ID
        password: Password (password1)
        received_signature: Signature from redirect
        algorithm: Hash algorithm

    Returns:
        True if signature is valid
    """
    values = {
        "OutSum": out_sum,
        "InvId": inv_id,
    }
    return verify_signature(values, password, received_signature, algorithm)
