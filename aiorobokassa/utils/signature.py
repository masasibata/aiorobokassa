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
    if isinstance(algorithm, str):
        try:
            algorithm = SignatureAlgorithm.from_string(algorithm)
        except ValueError as e:
            raise InvalidSignatureAlgorithmError(str(e)) from e

    sorted_items = sorted(values.items())
    signature_string = ":".join(str(value) for _, value in sorted_items)
    signature_string += f":{password}"

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
    shp_params: Optional[Dict[str, str]] = None,
) -> str:
    """
    Calculate signature for payment URL.

    Signature format: MD5(merchant_login:out_sum:inv_id:receipt:Shp_param1:Shp_param2:...:password1)
    Order is FIXED: MerchantLogin:OutSum:InvId:Receipt:Shp_param1:Shp_param2:...:password1
    If InvId is not provided, it must be empty but present (two colons: ::)
    If receipt is provided, it must be included in signature calculation.
    Shp_ parameters must be sorted alphabetically by key (without Shp_ prefix).

    Args:
        merchant_login: Merchant login
        out_sum: Payment amount
        inv_id: Invoice ID (optional)
        password: Password (password1)
        algorithm: Hash algorithm
        receipt: Receipt JSON string for fiscalization (optional)
        shp_params: Additional Shp_ parameters (without Shp_ prefix) (optional)

    Returns:
        Signature string
    """
    if isinstance(algorithm, str):
        try:
            algorithm = SignatureAlgorithm.from_string(algorithm)
        except ValueError as e:
            raise InvalidSignatureAlgorithmError(str(e)) from e

    signature_parts = [merchant_login, out_sum]
    signature_parts.append(inv_id if inv_id else "")

    if receipt:
        signature_parts.append(receipt)

    signature_parts.append(password)

    if shp_params:
        sorted_shp = sorted(shp_params.items())
        for key, value in sorted_shp:
            signature_parts.append(f"Shp_{key}={value}")

    signature_string = ":".join(signature_parts)

    hash_func = ALGORITHMS.get(algorithm)
    if hash_func is None:
        raise InvalidSignatureAlgorithmError(f"Unsupported algorithm: {algorithm}")

    hash_obj = hash_func(signature_string.encode("utf-8"))
    return hash_obj.hexdigest().upper()


def verify_result_url_signature(
    out_sum: str,
    inv_id: str,
    password: str,
    received_signature: str,
    algorithm: Union[str, SignatureAlgorithm] = SignatureAlgorithm.MD5,
    shp_params: Optional[Dict[str, str]] = None,
) -> bool:
    """
    Verify signature from ResultURL notification.

    Signature format: MD5(OutSum:InvId:Shp_param1:Shp_param2:...:password2)
    Where Shp_ parameters are sorted alphabetically.
    Order is FIXED: OutSum:InvId (not sorted alphabetically)

    Args:
        out_sum: Payment amount
        inv_id: Invoice ID
        password: Password (password2)
        received_signature: Signature from notification
        algorithm: Hash algorithm
        shp_params: Additional Shp_ parameters (without Shp_ prefix)

    Returns:
        True if signature is valid
    """
    if isinstance(algorithm, str):
        try:
            algorithm = SignatureAlgorithm.from_string(algorithm)
        except ValueError as e:
            raise InvalidSignatureAlgorithmError(str(e)) from e

    signature_parts = [out_sum, inv_id, password]

    if shp_params:
        sorted_shp = sorted(shp_params.items())
        for key, value in sorted_shp:
            signature_parts.append(f"Shp_{key}={value}")

    signature_string = ":".join(signature_parts)

    hash_func = ALGORITHMS.get(algorithm)
    if hash_func is None:
        raise InvalidSignatureAlgorithmError(f"Unsupported algorithm: {algorithm}")

    hash_obj = hash_func(signature_string.encode("utf-8"))
    calculated_signature = hash_obj.hexdigest().upper()

    return calculated_signature == received_signature.upper()


def verify_success_url_signature(
    out_sum: str,
    inv_id: str,
    password: str,
    received_signature: str,
    algorithm: Union[str, SignatureAlgorithm] = SignatureAlgorithm.MD5,
    shp_params: Optional[Dict[str, str]] = None,
) -> bool:
    """
    Verify signature from SuccessURL redirect.

    Signature format: MD5(OutSum:InvId:Shp_param1:Shp_param2:...:password1)
    Where Shp_ parameters are sorted alphabetically.
    Order is FIXED: OutSum:InvId (not sorted alphabetically)

    Args:
        out_sum: Payment amount
        inv_id: Invoice ID
        password: Password (password1)
        received_signature: Signature from redirect
        algorithm: Hash algorithm
        shp_params: Additional Shp_ parameters (without Shp_ prefix)

    Returns:
        True if signature is valid
    """
    if isinstance(algorithm, str):
        try:
            algorithm = SignatureAlgorithm.from_string(algorithm)
        except ValueError as e:
            raise InvalidSignatureAlgorithmError(str(e)) from e

    signature_parts = [out_sum, inv_id, password]

    if shp_params:
        sorted_shp = sorted(shp_params.items())
        for key, value in sorted_shp:
            signature_parts.append(f"Shp_{key}={value}")

    signature_string = ":".join(signature_parts)

    hash_func = ALGORITHMS.get(algorithm)
    if hash_func is None:
        raise InvalidSignatureAlgorithmError(f"Unsupported algorithm: {algorithm}")

    hash_obj = hash_func(signature_string.encode("utf-8"))
    calculated_signature = hash_obj.hexdigest().upper()

    return calculated_signature == received_signature.upper()


def calculate_split_signature(
    invoice_json: str,
    password: str,
    algorithm: Union[str, SignatureAlgorithm] = SignatureAlgorithm.MD5,
) -> str:
    """
    Calculate signature for split payment.

    Signature format: MD5(invoice_json + password1)
    Where invoice_json is the JSON string in "pure" form (not URL-encoded).

    Args:
        invoice_json: Invoice JSON string (not URL-encoded)
        password: Password (password1 of master merchant)
        algorithm: Hash algorithm

    Returns:
        Hexadecimal signature string

    Raises:
        InvalidSignatureAlgorithmError: If algorithm is not supported
    """
    if isinstance(algorithm, str):
        try:
            algorithm = SignatureAlgorithm.from_string(algorithm)
        except ValueError as e:
            raise InvalidSignatureAlgorithmError(str(e)) from e

    signature_string = invoice_json + password

    hash_func = ALGORITHMS.get(algorithm)
    if hash_func is None:
        raise InvalidSignatureAlgorithmError(f"Unsupported algorithm: {algorithm}")

    hash_obj = hash_func(signature_string.encode("utf-8"))
    return hash_obj.hexdigest().lower()
