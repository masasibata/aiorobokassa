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
)
from aiorobokassa.enums import SignatureAlgorithm
from aiorobokassa.exceptions import SignatureError, ValidationError
from aiorobokassa.models.requests import (
    PaymentRequest,
    ResultURLNotification,
    SuccessURLNotification,
)
from aiorobokassa.utils.helpers import build_url, parse_shp_params
from aiorobokassa.utils.signature import (
    calculate_payment_signature,
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
            "Description": request.description,
        }

        # Map request fields to URL parameters
        field_mapping = {
            "inv_id": "InvId",
            "email": "Email",
            "culture": "Culture",
            "encoding": "Encoding",
            "expiration_date": "ExpirationDate",
        }

        for field, param_name in field_mapping.items():
            value = getattr(request, field, None)
            if value is not None:
                params[param_name] = str(value)

        # Test mode
        if request.is_test is not None:
            params["IsTest"] = str(request.is_test)
        elif client.test_mode:
            params["IsTest"] = "1"

        # User parameters
        if request.user_parameters:
            params.update({f"Shp_{k}": v for k, v in request.user_parameters.items()})

        # Receipt for fiscalization
        receipt_str: Optional[str] = None
        if request.receipt:
            # Receipt is already JSON string after validation (validator converts it)
            # Type ignore because validator ensures it's a string
            receipt_str = request.receipt  # type: ignore[assignment]
            # URL-encode receipt before adding to params
            if receipt_str is not None:
                params["Receipt"] = quote(receipt_str, safe="")

        # Calculate signature (receipt must be included if present)
        signature = calculate_payment_signature(
            merchant_login=client.merchant_login,
            out_sum=str(request.out_sum),
            inv_id=str(request.inv_id) if request.inv_id else None,
            password=client.password1,
            algorithm=signature_algorithm,
            receipt=receipt_str,  # Use original JSON string for signature
        )
        params["SignatureValue"] = signature

        return params

    async def create_payment_url(
        self,
        out_sum: Decimal,
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
            out_sum: Payment amount
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
