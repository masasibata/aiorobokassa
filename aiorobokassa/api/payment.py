"""Payment operations for RoboKassa API."""

from decimal import Decimal
from typing import TYPE_CHECKING, Any, Dict, Optional, Union, cast
from urllib.parse import quote

from aiorobokassa.models.receipt import Receipt

if TYPE_CHECKING:
    from aiorobokassa.api._protocols import ClientProtocol

from aiorobokassa.constants import (
    DEFAULT_CULTURE,
    DEFAULT_ENCODING,
    DEFAULT_SIGNATURE_ALGORITHM,
    PAYMENT_ENDPOINT,
    SPLIT_PAYMENT_ENDPOINT,
)
from aiorobokassa.enums import SignatureAlgorithm
from aiorobokassa.exceptions import SignatureError, ValidationError
from aiorobokassa.models.requests import (
    PaymentRequest,
    ResultURLNotification,
    SplitPaymentRequest,
    SuccessURLNotification,
)
from aiorobokassa.utils.helpers import build_url, parse_shp_params
from aiorobokassa.utils.signature import (
    calculate_payment_signature,
    calculate_split_signature,
    verify_result_url_signature,
    verify_success_url_signature,
)


class PaymentMixin:
    """Mixin for payment operations."""

    def _build_payment_params(
        self, request: PaymentRequest, signature_algorithm: Union[str, SignatureAlgorithm]
    ) -> Dict[str, Optional[str]]:
        """Build payment URL parameters."""
        if TYPE_CHECKING:
            client = cast("ClientProtocol", self)
        else:
            client = self  # type: ignore[assignment]

        params: Dict[str, Optional[str]] = {
            "MerchantLogin": client.merchant_login,
            "OutSum": str(request.out_sum),
        }

        if request.inv_id is not None:
            params["InvId"] = str(request.inv_id)

        params["Description"] = request.description

        field_mapping = {
            "email": "Email",
            "culture": "Culture",
            "encoding": "Encoding",
            "expiration_date": "ExpirationDate",
        }

        for field, param_name in field_mapping.items():
            value = getattr(request, field, None)
            if value is not None:
                params[param_name] = str(value)

        if request.is_test is not None:
            params["IsTest"] = str(request.is_test)
        elif client.test_mode:
            params["IsTest"] = "1"

        receipt_str: Optional[str] = None
        if request.receipt:
            receipt_str = request.receipt  # type: ignore[assignment]
            if receipt_str is not None:
                params["Receipt"] = quote(receipt_str, safe="")

        signature = calculate_payment_signature(
            merchant_login=client.merchant_login,
            out_sum=str(request.out_sum),
            inv_id=str(request.inv_id) if request.inv_id is not None else None,
            password=client.password1,
            algorithm=signature_algorithm,
            receipt=receipt_str,
            shp_params=request.user_parameters,
        )

        # Shp_ parameters must be sorted alphabetically by full name to match signature order
        if request.user_parameters:
            sorted_shp_items = sorted(
                ((f"Shp_{k}", v) for k, v in request.user_parameters.items()), key=lambda x: x[0]
            )
            for param_name, param_value in sorted_shp_items:
                params[param_name] = param_value

        params["SignatureValue"] = signature

        return params

    def create_payment_url(
        self,
        out_sum: Union[Decimal, float, int, str],
        description: str,
        inv_id: Optional[int] = None,
        email: Optional[str] = None,
        culture: Optional[str] = None,
        encoding: Optional[str] = None,
        is_test: Optional[int] = None,
        expiration_date: Optional[str] = None,
        user_parameters: Optional[Dict[str, str]] = None,
        receipt: Optional[Union[Receipt, str, Dict[str, Any]]] = None,
        signature_algorithm: Union[str, SignatureAlgorithm] = DEFAULT_SIGNATURE_ALGORITHM,
    ) -> str:
        """
        Create payment URL for RoboKassa.

        Args:
            out_sum: Payment amount (Decimal, float, int, or string)
            description: Payment description
            inv_id: Invoice ID (optional)
            email: Customer email (optional)
            culture: Language code (ru, en) (optional)
            encoding: Encoding (optional, default: utf-8)
            is_test: Test mode flag (optional)
            expiration_date: Payment expiration date (optional)
            user_parameters: Additional user parameters (Shp_*) (optional)
            receipt: Receipt data for fiscalization - Receipt model, JSON string or dict (optional)
            signature_algorithm: Signature algorithm (optional, default: MD5)

        Returns:
            Payment URL string
        """
        request = PaymentRequest(
            out_sum=out_sum,
            description=description,
            inv_id=inv_id,
            email=email,
            culture=culture or DEFAULT_CULTURE,
            encoding=encoding or DEFAULT_ENCODING,
            is_test=is_test,
            expiration_date=expiration_date,
            user_parameters=user_parameters,
            receipt=receipt,
        )

        if TYPE_CHECKING:
            client = cast("ClientProtocol", self)
        else:
            client = self  # type: ignore[assignment]
        params = self._build_payment_params(request, signature_algorithm)
        return build_url(f"{client.base_url}{PAYMENT_ENDPOINT}", params)

    def _verify_notification(
        self,
        out_sum: str,
        inv_id: str,
        signature_value: str,
        password: str,
        notification_class: type,
        verify_func,
        error_message: str,
        shp_params: Optional[Dict[str, str]] = None,
        signature_algorithm: Union[str, SignatureAlgorithm] = DEFAULT_SIGNATURE_ALGORITHM,
    ) -> bool:
        """Generic notification verification."""
        try:
            notification = notification_class(
                out_sum=out_sum,
                inv_id=inv_id,
                SignatureValue=signature_value,
                shp_params=shp_params or {},
            )
        except Exception as e:
            raise ValidationError(f"Invalid notification data: {e}") from e

        is_valid = verify_func(
            out_sum=notification.out_sum,
            inv_id=notification.inv_id,
            password=password,
            received_signature=notification.signature_value,
            algorithm=signature_algorithm,
            shp_params=notification.shp_params,
        )

        if not is_valid:
            raise SignatureError(error_message)
        return True

    def verify_result_url(
        self,
        out_sum: str,
        inv_id: str,
        signature_value: str,
        shp_params: Optional[Dict[str, str]] = None,
        signature_algorithm: Union[str, SignatureAlgorithm] = DEFAULT_SIGNATURE_ALGORITHM,
    ) -> bool:
        """Verify ResultURL notification signature."""
        if TYPE_CHECKING:
            client = cast("ClientProtocol", self)
        else:
            client = self  # type: ignore[assignment]
        return self._verify_notification(
            out_sum=out_sum,
            inv_id=inv_id,
            signature_value=signature_value,
            password=client.password2,
            notification_class=ResultURLNotification,
            verify_func=verify_result_url_signature,
            error_message="ResultURL signature verification failed",
            shp_params=shp_params,
            signature_algorithm=signature_algorithm,
        )

    def verify_success_url(
        self,
        out_sum: str,
        inv_id: str,
        signature_value: str,
        shp_params: Optional[Dict[str, str]] = None,
        signature_algorithm: Union[str, SignatureAlgorithm] = DEFAULT_SIGNATURE_ALGORITHM,
    ) -> bool:
        """Verify SuccessURL redirect signature."""
        if TYPE_CHECKING:
            client = cast("ClientProtocol", self)
        else:
            client = self  # type: ignore[assignment]
        return self._verify_notification(
            out_sum=out_sum,
            inv_id=inv_id,
            signature_value=signature_value,
            password=client.password1,
            notification_class=SuccessURLNotification,
            verify_func=verify_success_url_signature,
            error_message="SuccessURL signature verification failed",
            shp_params=shp_params,
            signature_algorithm=signature_algorithm,
        )

    @staticmethod
    def parse_result_url_params(params: Dict[str, str]) -> Dict[str, Union[str, Dict[str, str]]]:
        """Parse ResultURL parameters from request."""
        return {
            "out_sum": params.get("OutSum", ""),
            "inv_id": params.get("InvId", ""),
            "signature_value": params.get("SignatureValue", ""),
            "shp_params": parse_shp_params(params),
        }

    @staticmethod
    def parse_success_url_params(params: Dict[str, str]) -> Dict[str, Union[str, Dict[str, str]]]:
        """Parse SuccessURL parameters from request."""
        return {
            "out_sum": params.get("OutSum", ""),
            "inv_id": params.get("InvId", ""),
            "signature_value": params.get("SignatureValue", ""),
            "shp_params": parse_shp_params(params),
        }

    def create_split_payment_url(
        self,
        out_amount: Union[Decimal, float, int, str],
        merchant_id: str,
        split_merchants: list[Dict[str, Any]],
        merchant_comment: Optional[str] = None,
        shop_params: Optional[list[Dict[str, str]]] = None,
        email: Optional[str] = None,
        inc_curr: Optional[str] = None,
        language: Optional[str] = None,
        is_test: Optional[bool] = None,
        expiration_date: Optional[str] = None,
        signature_algorithm: Union[str, SignatureAlgorithm] = DEFAULT_SIGNATURE_ALGORITHM,
    ) -> str:
        """
        Create split payment URL for RoboKassa.

        Split payment allows distributing a payment between multiple merchants.

        Args:
            out_amount: Total payment amount (Decimal, float, int, or string)
            merchant_id: Master merchant ID (initiates the split operation)
            split_merchants: List of split merchant dictionaries, each containing:
                - id: Merchant ID (required)
                - invoice_id: Invoice ID (optional, auto-generated if not provided or 0)
                - amount: Amount for this merchant (required, can be 0.00)
                - receipt: Receipt data (optional) - Receipt model, JSON string or dict
            merchant_comment: Order description (max 100 characters, optional)
            shop_params: List of shop parameter dictionaries with 'name' and 'value' (optional)
            email: Customer email (optional)
            inc_curr: Payment method (e.g., "BankCard") (optional)
            language: Language code (ru, en) (optional)
            is_test: Test mode flag (optional)
            expiration_date: Payment expiration date in ISO 8601 format (optional)
            signature_algorithm: Signature algorithm (optional, default: MD5)

        Returns:
            Split payment URL string

        Raises:
            ValidationError: If request data is invalid
        """
        if TYPE_CHECKING:
            client = cast("ClientProtocol", self)
        else:
            client = self  # type: ignore[assignment]

        shop_params_list = None
        if shop_params:
            from aiorobokassa.models.requests import ShopParam

            shop_params_list = [ShopParam(name=p["name"], value=p["value"]) for p in shop_params]

        from aiorobokassa.models.requests import SplitMerchant

        split_merchants_list = []
        for merchant_data in split_merchants:
            split_merchant = SplitMerchant(
                id=merchant_data["id"],
                invoice_id=merchant_data.get("invoice_id"),
                amount=merchant_data["amount"],
                receipt=merchant_data.get("receipt"),
            )
            split_merchants_list.append(split_merchant)

        request = SplitPaymentRequest(
            out_amount=out_amount,
            merchant_id=merchant_id,
            merchant_comment=merchant_comment,
            split_merchants=split_merchants_list,
            shop_params=shop_params_list,
            email=email,
            inc_curr=inc_curr,
            language=language,
            is_test=is_test,
            expiration_date=expiration_date,
        )

        invoice_json = request.to_json_string()

        signature = calculate_split_signature(
            invoice_json=invoice_json,
            password=client.password1,
            algorithm=signature_algorithm,
        )

        from urllib.parse import quote

        invoice_encoded = quote(invoice_json, safe="")

        params: Dict[str, Optional[str]] = {
            "invoice": invoice_encoded,
            "signature": signature,
        }

        return build_url(f"{client.base_url}{SPLIT_PAYMENT_ENDPOINT}", params)
