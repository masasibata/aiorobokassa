"""Protocols for mixin type checking."""

from typing import Any, Dict, Optional, Protocol
from xml.etree.ElementTree import Element


class ClientProtocol(Protocol):
    """Protocol for client attributes used by mixins."""

    merchant_login: str
    password1: str
    password2: str
    test_mode: bool
    base_url: str

    async def _post(self, url: str, **kwargs: Any) -> Any:
        """Make POST request."""
        ...

    def _parse_xml_response(self, response_text: str) -> Dict[str, str]:
        """Parse XML response."""
        ...

    def _build_xml_and_signature(
        self,
        root_name: str,
        base_data: Dict[str, str],
        optional_fields: Dict[str, Optional[str]],
        signature_algorithm: str,
    ) -> Element:
        """Build XML and signature."""
        ...

    async def _xml_request(
        self,
        endpoint: str,
        root_name: str,
        xml_data: Dict[str, Optional[str]],
        signature_data: Dict[str, str],
        signature_algorithm: str,
    ) -> Dict[str, str]:
        """Make XML request."""
        ...
