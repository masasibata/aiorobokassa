"""JWT token creation for RoboKassa Invoice API."""

import base64
import hmac
import json
from typing import Any, Dict, Union

from aiorobokassa.enums import SignatureAlgorithm
from aiorobokassa.exceptions import InvalidSignatureAlgorithmError

# Algorithm mapping for HMAC
HMAC_ALGORITHMS = {
    SignatureAlgorithm.MD5: "md5",
    "RIPEMD160": "ripemd160",
    "SHA1": "sha1",
    "HS1": "sha1",
    "SHA256": "sha256",
    "HS256": "sha256",
    "SHA384": "sha384",
    "HS384": "sha384",
    "SHA512": "sha512",
    "HS512": "sha512",
}


def base64url_encode(data: bytes) -> str:
    """
    Encode bytes to Base64URL (URL-safe base64 without padding).

    Args:
        data: Bytes to encode

    Returns:
        Base64URL encoded string
    """
    encoded = base64.urlsafe_b64encode(data).decode("utf-8")
    return encoded.rstrip("=")


def base64url_decode(data: str) -> bytes:
    """
    Decode Base64URL string to bytes.

    Args:
        data: Base64URL encoded string

    Returns:
        Decoded bytes
    """
    padding = 4 - len(data) % 4
    if padding != 4:
        data += "=" * padding
    return base64.urlsafe_b64decode(data)


def create_jwt_token(
    payload: Dict[str, Any],
    secret_key: str,
    algorithm: Union[str, SignatureAlgorithm] = SignatureAlgorithm.MD5,
) -> str:
    """
    Create JWT token for RoboKassa Invoice API.

    Args:
        payload: Payload dictionary (will be converted to JSON)
        secret_key: Secret key for HMAC signature (merchant_login:password1)
        algorithm: Hash algorithm for HMAC

    Returns:
        JWT token string (header.payload.signature)

    Raises:
        InvalidSignatureAlgorithmError: If algorithm is not supported
    """
    if isinstance(algorithm, str):
        alg_str = algorithm.upper()
        if alg_str in ["SHA1", "HS1"]:
            alg_str = "SHA1"
        elif alg_str in ["SHA256", "HS256"]:
            alg_str = "SHA256"
        elif alg_str in ["SHA384", "HS384"]:
            alg_str = "SHA384"
        elif alg_str in ["SHA512", "HS512"]:
            alg_str = "SHA512"
        elif alg_str == "MD5":
            alg_str = "MD5"
        elif alg_str == "RIPEMD160":
            alg_str = "RIPEMD160"
        else:
            raise InvalidSignatureAlgorithmError(f"Unsupported algorithm: {algorithm}")
    else:
        alg_str = algorithm.value.upper()

    header = {"typ": "JWT", "alg": alg_str}
    header_json = json.dumps(header, separators=(",", ":"))
    header_encoded = base64url_encode(header_json.encode("utf-8"))

    payload_json = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    payload_encoded = base64url_encode(payload_json.encode("utf-8"))

    message = f"{header_encoded}.{payload_encoded}".encode("utf-8")
    secret_bytes = secret_key.encode("utf-8")

    hash_name = HMAC_ALGORITHMS.get(alg_str)
    if hash_name is None:
        raise InvalidSignatureAlgorithmError(f"Unsupported algorithm: {alg_str}")

    import hashlib

    if hash_name == "ripemd160":
        try:
            hashlib.new("ripemd160")
            digestmod: Union[str, Any] = "ripemd160"
        except ValueError:
            raise InvalidSignatureAlgorithmError(
                "RIPEMD160 is not available in this Python installation. "
                "Install pycryptodome or use another algorithm."
            )
    else:
        digestmod = hash_name

    signature_bytes = hmac.new(secret_bytes, message, digestmod=digestmod).digest()
    signature_encoded = base64url_encode(signature_bytes)

    return f"{header_encoded}.{payload_encoded}.{signature_encoded}"
