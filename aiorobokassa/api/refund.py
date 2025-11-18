"""Refund operations for RoboKassa API."""

from decimal import Decimal
from typing import TYPE_CHECKING, Dict, Optional, Union, cast

if TYPE_CHECKING:
    from aiorobokassa.api._protocols import ClientProtocol

from aiorobokassa.constants import DEFAULT_SIGNATURE_ALGORITHM
from aiorobokassa.enums import SignatureAlgorithm
from aiorobokassa.models.requests import RefundRequest


class RefundMixin:
    """Mixin for refund operations."""

    async def create_refund(
        self,
        invoice_id: int,
        amount: Optional[Decimal] = None,
        signature_algorithm: Union[str, SignatureAlgorithm] = DEFAULT_SIGNATURE_ALGORITHM,
    ) -> Dict[str, str]:
        """Create refund for invoice."""
        if TYPE_CHECKING:
            client = cast("ClientProtocol", self)
        else:
            client = self  # type: ignore[assignment]
        request = RefundRequest(invoice_id=invoice_id, amount=amount)

        xml_data: Dict[str, Optional[str]] = {
            "MerchantLogin": client.merchant_login,
            "InvoiceID": str(request.invoice_id),
        }
        if request.amount is not None:
            xml_data["Amount"] = str(request.amount)

        signature_values = {
            "MerchantLogin": client.merchant_login,
            "InvoiceID": str(request.invoice_id),
        }
        if request.amount is not None:
            signature_values["Amount"] = str(request.amount)

        result = await client._xml_request(
            "OpRefund", "RefundRequest", xml_data, signature_values, signature_algorithm
        )
        return result

    async def get_refund_status(
        self,
        invoice_id: int,
        signature_algorithm: Union[str, SignatureAlgorithm] = DEFAULT_SIGNATURE_ALGORITHM,
    ) -> Dict[str, str]:
        """Get refund status for invoice."""
        if TYPE_CHECKING:
            client = cast("ClientProtocol", self)
        else:
            client = self  # type: ignore[assignment]
        xml_data: Dict[str, Optional[str]] = {
            "MerchantLogin": client.merchant_login,
            "InvoiceID": str(invoice_id),
        }

        signature_values = {
            "MerchantLogin": client.merchant_login,
            "InvoiceID": str(invoice_id),
        }

        result = await client._xml_request(
            "OpRefundStatus",
            "RefundStatusRequest",
            xml_data,
            signature_values,
            signature_algorithm,
        )
        return result
