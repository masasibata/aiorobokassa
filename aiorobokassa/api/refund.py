"""Refund operations for RoboKassa API."""

from decimal import Decimal
from typing import TYPE_CHECKING, Dict, List, Optional, Union, cast

if TYPE_CHECKING:
    from aiorobokassa.api._protocols import ClientProtocol

from aiorobokassa.constants import DEFAULT_SIGNATURE_ALGORITHM, REFUND_API_BASE_URL
from aiorobokassa.enums import SignatureAlgorithm
from aiorobokassa.exceptions import APIError, ConfigurationError
from aiorobokassa.models.requests import (
    RefundCreateRequest,
    RefundCreateResponse,
    RefundItem,
    RefundRequest,
    RefundStatusResponse,
)
from aiorobokassa.utils.jwt import create_jwt_token


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

    async def create_refund_v2(
        self,
        op_key: str,
        refund_sum: Optional[Union[Decimal, float, int, str]] = None,
        invoice_items: Optional[List[RefundItem]] = None,
        signature_algorithm: Union[str, SignatureAlgorithm] = SignatureAlgorithm.SHA256,
    ) -> RefundCreateResponse:
        """
        Create refund via Refund API (JWT-based).

        Args:
            op_key: Operation key (unique identifier from OpStateExt or Result2)
            refund_sum: Partial refund amount (omit for full refund)
            invoice_items: Invoice items to refund (optional)
            signature_algorithm: Signature algorithm (HS256, HS384, or HS512, default: HS256)

        Returns:
            RefundCreateResponse with refund request information

        Raises:
            ConfigurationError: If password3 is not configured
            APIError: If refund creation fails
        """
        if TYPE_CHECKING:
            client = cast("ClientProtocol", self)
        else:
            client = self  # type: ignore[assignment]

        if not client.password3:
            raise ConfigurationError(
                "password3 is required for refund operations. "
                "Please provide password3 when initializing the client."
            )

        request = RefundCreateRequest(
            op_key=op_key,
            refund_sum=refund_sum,
            invoice_items=invoice_items,
        )

        payload = request.to_api_dict()

        jwt_token = create_jwt_token(
            payload=payload,
            secret_key=client.password3,
            algorithm=signature_algorithm,
        )

        response = await client._post(
            f"{REFUND_API_BASE_URL}/Create",
            json=jwt_token,
        )

        async with response:
            result = await response.json()

            if not result.get("success", False):
                error_message = result.get("message", "Failed to create refund")
                raise APIError(f"Refund creation failed: {error_message}")

            return RefundCreateResponse.from_api_response(result)

    async def get_refund_status_v2(
        self,
        request_id: str,
    ) -> RefundStatusResponse:
        """
        Get refund status via Refund API.

        Args:
            request_id: Request ID (GUID) from RefundCreateResponse

        Returns:
            RefundStatusResponse with refund status information

        Raises:
            APIError: If request fails
        """
        if TYPE_CHECKING:
            client = cast("ClientProtocol", self)
        else:
            client = self  # type: ignore[assignment]

        response = await client._get(
            f"{REFUND_API_BASE_URL}/GetState",
            params={"id": request_id},
        )

        async with response:
            result = await response.json()

            if "message" in result and "requestId" not in result:
                raise APIError(f"Failed to get refund status: {result.get('message')}")

            return RefundStatusResponse.from_api_response(result)
