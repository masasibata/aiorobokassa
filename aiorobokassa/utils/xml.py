"""XML helpers for RoboKassa API."""

from typing import TYPE_CHECKING, Dict, Optional, Union, cast
from xml.etree import ElementTree as ET

if TYPE_CHECKING:
    from aiorobokassa.api._protocols import ClientProtocol

from aiorobokassa.constants import (
    DEFAULT_SIGNATURE_ALGORITHM,
    XML_CONTENT_TYPE,
    XML_SERVICE_ENDPOINT,
)
from aiorobokassa.enums import SignatureAlgorithm
from aiorobokassa.exceptions import XMLParseError
from aiorobokassa.utils.signature import calculate_signature


class XMLMixin:
    """Mixin for XML operations."""

    def _parse_xml_response(self, response_text: str) -> Dict[str, str]:
        """Parse XML response to dictionary."""
        try:
            response_xml = ET.fromstring(response_text)
            return {child.tag: child.text or "" for child in response_xml}
        except ET.ParseError as e:
            raise XMLParseError(f"Failed to parse XML response: {e}", response=response_text) from e

    def _build_xml_and_signature(
        self,
        root_name: str,
        base_data: Dict[str, str],
        optional_fields: Dict[str, Optional[str]],
        signature_algorithm: Union[str, SignatureAlgorithm] = DEFAULT_SIGNATURE_ALGORITHM,
    ) -> ET.Element:
        """Build XML element and calculate signature."""
        xml_data = {**base_data}
        signature_data = {**base_data}

        for key, value in optional_fields.items():
            if value is not None:
                xml_data[key] = str(value)
                signature_data[key] = str(value)

        root = ET.Element(root_name)
        for key, value in xml_data.items():
            ET.SubElement(root, key).text = str(value)

        if TYPE_CHECKING:
            client = cast("ClientProtocol", self)
        else:
            client = self  # type: ignore[assignment]
        signature = calculate_signature(signature_data, client.password1, signature_algorithm)
        ET.SubElement(root, "SignatureValue").text = signature

        return root

    async def _xml_request(
        self,
        endpoint: str,
        root_name: str,
        xml_data: Dict[str, Optional[str]],
        signature_data: Dict[str, str],
        signature_algorithm: Union[str, SignatureAlgorithm] = DEFAULT_SIGNATURE_ALGORITHM,
    ) -> Dict[str, str]:
        """Make XML API request."""
        root = ET.Element(root_name)
        for key, value in xml_data.items():
            if value is not None:
                ET.SubElement(root, key).text = str(value)

        if TYPE_CHECKING:
            client = cast("ClientProtocol", self)
        else:
            client = self  # type: ignore[assignment]
        signature = calculate_signature(signature_data, client.password1, signature_algorithm)
        ET.SubElement(root, "SignatureValue").text = signature

        xml_string = ET.tostring(root, encoding="utf-8", method="xml").decode("utf-8")

        if TYPE_CHECKING:
            client = cast("ClientProtocol", self)
        else:
            client = self  # type: ignore[assignment]
        response = await client._post(
            f"{client.base_url}{XML_SERVICE_ENDPOINT}/{endpoint}",
            data=xml_string,
            headers={"Content-Type": XML_CONTENT_TYPE},
        )
        async with response:
            response_text = await response.text()
            return self._parse_xml_response(response_text)
