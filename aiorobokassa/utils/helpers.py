"""Utility functions for aiorobokassa."""

from typing import Dict, Optional
from urllib.parse import urlencode


def build_url(base_url: str, params: Dict[str, Optional[str]]) -> str:
    """
    Build URL with query parameters.

    Parameters are properly URL-encoded. SignatureValue should be last.

    Args:
        base_url: Base URL
        params: Dictionary of query parameters (None values are skipped)

    Returns:
        URL with query string
    """
    filtered_params = {k: str(v) for k, v in params.items() if v is not None}

    if not filtered_params:
        return base_url

    query_string = urlencode(filtered_params, doseq=False)

    return f"{base_url}?{query_string}"


def parse_shp_params(params: Dict[str, str]) -> Dict[str, str]:
    """
    Parse Shp_* parameters from request.

    Args:
        params: Dictionary of all parameters

    Returns:
        Dictionary with only Shp_* parameters (with Shp_ prefix removed)
    """
    shp_params = {}
    for key, value in params.items():
        if key.startswith("Shp_"):
            shp_key = key[4:]
            shp_params[shp_key] = value
    return shp_params
