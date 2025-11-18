"""Invoice operations for RoboKassa API."""

from decimal import Decimal
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union, cast

if TYPE_CHECKING:
    from aiorobokassa.api._protocols import ClientProtocol

from aiorobokassa.constants import DEFAULT_SIGNATURE_ALGORITHM, INVOICE_API_BASE_URL
from aiorobokassa.enums import InvoiceType, SignatureAlgorithm
from aiorobokassa.exceptions import APIError
from aiorobokassa.models.receipt import Receipt
from aiorobokassa.models.requests import InvoiceItem
from aiorobokassa.utils.jwt import create_jwt_token


class InvoiceMixin:
    """Mixin for invoice operations."""

    async def create_invoice(
        self,
        out_sum: Union[Decimal, float, int, str],
        description: str,
        invoice_type: Union[InvoiceType, str] = InvoiceType.ONE_TIME,
        inv_id: Optional[int] = None,
        culture: Optional[str] = None,
        merchant_comments: Optional[str] = None,
        invoice_items: Optional[List[InvoiceItem]] = None,
        receipt: Optional[Union[Receipt, str, Dict[str, Any]]] = None,
        user_fields: Optional[Dict[str, str]] = None,
        success_url: Optional[str] = None,
        success_url_method: str = "GET",
        fail_url: Optional[str] = None,
        fail_url_method: str = "GET",
        signature_algorithm: Union[str, SignatureAlgorithm] = DEFAULT_SIGNATURE_ALGORITHM,
    ) -> Dict[str, Any]:
        """
        Create invoice via Invoice API (JWT-based).

        Args:
            out_sum: Payment amount
            description: Payment description
            invoice_type: Invoice type (OneTime or Reusable)
            inv_id: Invoice ID (optional)
            culture: Language code (ru, en) (optional)
            merchant_comments: Internal comment for staff (optional)
            invoice_items: List of invoice items for fiscalization (optional)
            receipt: Receipt data for fiscalization - Receipt model, JSON string or dict (optional).
                     If provided and invoice_items is not, receipt items will be converted to invoice_items.
            user_fields: Additional user parameters (optional)
            success_url: Success redirect URL (optional)
            success_url_method: HTTP method for success URL (GET or POST)
            fail_url: Fail redirect URL (optional)
            fail_url_method: HTTP method for fail URL (GET or POST)
            signature_algorithm: Signature algorithm (optional, default: MD5)

        Returns:
            Dictionary with invoice information (id, url, etc.)

        Raises:
            APIError: If invoice creation fails
            ValueError: If both invoice_items and receipt are provided
        """
        if TYPE_CHECKING:
            client = cast("ClientProtocol", self)
        else:
            client = self  # type: ignore[assignment]

        # Convert invoice_type to string if enum
        if isinstance(invoice_type, InvoiceType):
            invoice_type_str = invoice_type.value
        else:
            invoice_type_str = str(invoice_type)

        # Build payload
        payload: Dict[str, Any] = {
            "MerchantLogin": client.merchant_login,
            "InvoiceType": invoice_type_str,
            "OutSum": float(Decimal(str(out_sum))),
            "Description": description,
        }

        if inv_id is not None:
            payload["InvId"] = inv_id
        if culture:
            payload["Culture"] = culture
        if merchant_comments:
            payload["MerchantComments"] = merchant_comments
        if user_fields:
            payload["UserFields"] = user_fields

        # Handle receipt and invoice_items
        if invoice_items and receipt:
            raise ValueError("Cannot provide both invoice_items and receipt. Use only one.")

        # Convert receipt to invoice_items if receipt is provided and invoice_items is not
        if receipt and not invoice_items:
            # Parse receipt
            if isinstance(receipt, Receipt):
                receipt_model = receipt
            elif isinstance(receipt, dict):
                receipt_model = Receipt.from_dict(receipt)
            elif isinstance(receipt, str):
                import json

                receipt_dict = json.loads(receipt)
                receipt_model = Receipt.from_dict(receipt_dict)
            else:
                raise ValueError("receipt must be Receipt model, JSON string or dict")

            # Convert ReceiptItem to InvoiceItem
            invoice_items = []
            for receipt_item in receipt_model.items:
                # Calculate cost from sum/quantity if needed
                cost_value: Union[float, Decimal] = 0.0
                if receipt_item.cost is not None:
                    cost_value = float(receipt_item.cost)
                elif receipt_item.sum is not None:
                    cost_value = float(receipt_item.sum / Decimal(str(receipt_item.quantity)))

                invoice_item = InvoiceItem(
                    name=receipt_item.name,
                    quantity=receipt_item.quantity,
                    cost=cost_value,
                    tax=receipt_item.tax,
                    payment_method=receipt_item.payment_method,
                    payment_object=receipt_item.payment_object,
                    nomenclature_code=receipt_item.nomenclature_code,
                )
                invoice_items.append(invoice_item)

            # Add Sno from receipt if present
            if receipt_model.sno:
                payload["Sno"] = receipt_model.sno.value

        # Add invoice items if provided
        if invoice_items:
            payload["InvoiceItems"] = [item.to_api_dict() for item in invoice_items]

        # Add URL redirects if provided
        if success_url:
            payload["SuccessUrl2Data"] = {"Url": success_url, "Method": success_url_method}
        if fail_url:
            payload["FailUrl2Data"] = {"Url": fail_url, "Method": fail_url_method}

        # Create JWT token
        secret_key = f"{client.merchant_login}:{client.password1}"
        jwt_token = create_jwt_token(payload, secret_key, signature_algorithm)

        # Send request (JWT token as string in request body, not JSON)
        response = await client._post(
            f"{INVOICE_API_BASE_URL}/CreateInvoice",
            data=jwt_token,
            headers={"Content-Type": "application/json"},
        )
        async with response:
            result = await response.json()

            if not result.get("isSuccess", False):
                error_message = result.get("errorMessage", "Failed to create invoice")
                raise APIError(f"Invoice creation failed: {error_message}")

            return {
                "id": result.get("id"),
                "url": result.get("url"),
                "inv_id": result.get("invId"),
                "encoded_id": result.get("encodedId"),
            }

    async def deactivate_invoice(
        self,
        inv_id: Optional[int] = None,
        invoice_id: Optional[str] = None,
        encoded_id: Optional[str] = None,
        signature_algorithm: Union[str, SignatureAlgorithm] = DEFAULT_SIGNATURE_ALGORITHM,
    ) -> None:
        """
        Deactivate invoice.

        Args:
            inv_id: Invoice ID (number specified by merchant)
            invoice_id: Invoice identifier (returned from create_invoice)
            encoded_id: Encoded invoice ID (last part of invoice URL)
            signature_algorithm: Signature algorithm (optional, default: MD5)

        Raises:
            APIError: If deactivation fails
            ValueError: If no identifier is provided
        """
        if TYPE_CHECKING:
            client = cast("ClientProtocol", self)
        else:
            client = self  # type: ignore[assignment]

        if not any([inv_id, invoice_id, encoded_id]):
            raise ValueError(
                "At least one identifier (inv_id, invoice_id, or encoded_id) must be provided"
            )

        # Build payload
        payload: Dict[str, Any] = {"MerchantLogin": client.merchant_login}
        if inv_id is not None:
            payload["InvId"] = inv_id
        if invoice_id:
            payload["Id"] = invoice_id
        if encoded_id:
            payload["EncodedId"] = encoded_id

        # Create JWT token
        secret_key = f"{client.merchant_login}:{client.password1}"
        jwt_token = create_jwt_token(payload, secret_key, signature_algorithm)

        # Send request (JWT token as string in request body, not JSON)
        response = await client._post(
            f"{INVOICE_API_BASE_URL}/DeactivateInvoice",
            data=jwt_token,
            headers={"Content-Type": "application/json"},
        )
        async with response:
            result = await response.json()

            if not result.get("isSuccess", False):
                error_message = result.get("errorMessage", "Failed to deactivate invoice")
                raise APIError(f"Invoice deactivation failed: {error_message}")

    async def get_invoice_information_list(
        self,
        current_page: int = 1,
        page_size: int = 10,
        invoice_statuses: Optional[List[str]] = None,
        keywords: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        is_ascending: bool = True,
        invoice_types: Optional[List[str]] = None,
        payment_aliases: Optional[List[str]] = None,
        sum_from: Optional[float] = None,
        sum_to: Optional[float] = None,
        signature_algorithm: Union[str, SignatureAlgorithm] = DEFAULT_SIGNATURE_ALGORITHM,
    ) -> Dict[str, Any]:
        """
        Get invoice information list.

        Args:
            current_page: Current page number (from 1)
            page_size: Page size (number of invoices per page)
            invoice_statuses: List of invoice statuses (paid, expired, notpaid)
            keywords: Search keywords
            date_from: Start date (ISO 8601 format)
            date_to: End date (ISO 8601 format)
            is_ascending: Sort ascending
            invoice_types: List of invoice types (onetime, reusable)
            payment_aliases: List of payment method aliases
            sum_from: Minimum invoice amount
            sum_to: Maximum invoice amount
            signature_algorithm: Signature algorithm (optional, default: MD5)

        Returns:
            Dictionary with invoice list and pagination info

        Raises:
            APIError: If request fails
        """
        if TYPE_CHECKING:
            client = cast("ClientProtocol", self)
        else:
            client = self  # type: ignore[assignment]

        # Build payload
        payload: Dict[str, Any] = {
            "MerchantLogin": client.merchant_login,
            "CurrentPage": current_page,
            "PageSize": page_size,
        }

        if invoice_statuses:
            payload["InvoiceStatuses"] = invoice_statuses
        if keywords:
            payload["Keywords"] = keywords
        if date_from:
            payload["DateFrom"] = date_from
        if date_to:
            payload["DateTo"] = date_to
        if is_ascending is not None:
            payload["IsAscending"] = is_ascending
        if invoice_types:
            payload["InvoiceTypes"] = invoice_types
        if payment_aliases:
            payload["PaymentAliases"] = payment_aliases
        if sum_from is not None:
            payload["SumFrom"] = sum_from
        if sum_to is not None:
            payload["SumTo"] = sum_to

        # Create JWT token
        secret_key = f"{client.merchant_login}:{client.password1}"
        jwt_token = create_jwt_token(payload, secret_key, signature_algorithm)

        # Send request (JWT token as string in request body, not JSON)
        response = await client._post(
            f"{INVOICE_API_BASE_URL}/GetInvoiceInformationList",
            data=jwt_token,
            headers={"Content-Type": "application/json"},
        )
        async with response:
            result = await response.json()

            if not result.get("isSuccess", False):
                error_message = result.get("errorMessage", "Failed to get invoice information")
                raise APIError(f"Get invoice information failed: {error_message}")

            return cast(Dict[str, Any], result)
