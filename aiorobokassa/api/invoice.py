"""Invoice operations for RoboKassa API."""

from decimal import Decimal
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
from aiorobokassa.models.requests import InvoiceRequest


class InvoiceMixin:
    """Mixin for invoice operations."""

    async def create_invoice(
        self,
        out_sum: Decimal,
        description: str,
        inv_id: Optional[int] = None,
        email: Optional[str] = None,
        expiration_date: Optional[str] = None,
        user_parameters: Optional[Dict[str, str]] = None,
        signature_algorithm: Union[str, SignatureAlgorithm] = DEFAULT_SIGNATURE_ALGORITHM,
    ) -> Dict[str, str]:
        """Create invoice via XML API."""
        if TYPE_CHECKING:
            client = cast("ClientProtocol", self)
        else:
            client = self  # type: ignore[assignment]
        request = InvoiceRequest(
            merchant_login=client.merchant_login,
            out_sum=out_sum,
            description=description,
            inv_id=inv_id,
            email=email,
            expiration_date=expiration_date,
            user_parameters=user_parameters,
        )

        base_data = {
            "MerchantLogin": client.merchant_login,
            "Amount": str(request.out_sum),
            "Description": request.description,
        }

        optional_fields: Dict[str, Optional[str]] = {}
        if request.inv_id is not None:
            optional_fields["InvoiceID"] = str(request.inv_id)
        if request.email:
            optional_fields["Email"] = request.email
        if request.expiration_date:
            optional_fields["ExpirationDate"] = request.expiration_date

        root = client._build_xml_and_signature(
            "OperationRequest", base_data, optional_fields, signature_algorithm
        )

        if request.user_parameters:
            params_elem = ET.SubElement(root, "Params")
            for key, value in request.user_parameters.items():
                param_elem = ET.SubElement(params_elem, "Param")
                ET.SubElement(param_elem, "Name").text = f"Shp_{key}"
                ET.SubElement(param_elem, "Value").text = value

        xml_string = ET.tostring(root, encoding="utf-8", method="xml").decode("utf-8")

        response = await client._post(
            f"{client.base_url}{XML_SERVICE_ENDPOINT}/OpState",
            data=xml_string,
            headers={"Content-Type": XML_CONTENT_TYPE},
        )
        async with response:
            response_text = await response.text()
            result = client._parse_xml_response(response_text)
            return result
