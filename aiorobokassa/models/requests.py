"""Pydantic models for request/response validation."""

import json
from decimal import Decimal
from typing import Any, Dict, Optional, Union, cast

from pydantic import BaseModel, ConfigDict, Field, field_validator

from aiorobokassa.enums import PaymentMethod, PaymentObject, TaxRate, TaxSystem
from aiorobokassa.models.receipt import Receipt, ReceiptItem


class PaymentRequest(BaseModel):
    """Model for payment link generation."""

    out_sum: Union[Decimal, float, int, str] = Field(
        ..., description="Payment amount (Decimal, float, int, or string)"
    )
    description: str = Field(..., description="Payment description")
    inv_id: Optional[int] = Field(None, description="Invoice ID (optional)")
    email: Optional[str] = Field(None, description="Customer email")
    culture: Optional[str] = Field("ru", description="Language (ru, en)")
    encoding: Optional[str] = Field("utf-8", description="Encoding")
    is_test: Optional[int] = Field(None, description="Test mode flag (1 for test)")
    expiration_date: Optional[str] = Field(None, description="Payment expiration date")
    user_parameters: Optional[Dict[str, str]] = Field(
        None, description="Additional user parameters"
    )
    receipt: Optional[Union[Receipt, str, Dict[str, Any]]] = Field(
        None, description="Receipt data for fiscalization (Receipt model, JSON string or dict)"
    )

    @field_validator("out_sum", mode="before")
    @classmethod
    def validate_amount(cls, v: Union[Decimal, float, int, str]) -> Decimal:
        """Validate and convert payment amount to Decimal."""
        if isinstance(v, Decimal):
            amount = v
        elif isinstance(v, (int, float)):
            amount = Decimal(str(v))
        elif isinstance(v, str):
            try:
                amount = Decimal(v)
            except (ValueError, TypeError) as e:
                raise ValueError(f"Invalid amount format: {v}") from e
        else:
            raise ValueError(f"Amount must be Decimal, float, int, or string, got {type(v)}")

        if amount <= 0:
            raise ValueError("Payment amount must be positive")
        return amount

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate description is not empty."""
        if not v.strip():
            raise ValueError("Description cannot be empty")
        return v

    @field_validator("receipt", mode="before")
    @classmethod
    def validate_receipt(cls, v: Union[Receipt, str, Dict[str, Any], None]) -> Optional[str]:
        """Convert receipt to JSON string."""
        if v is None:
            return None
        if isinstance(v, Receipt):
            return v.to_json_string()
        if isinstance(v, dict):
            try:
                receipt = Receipt.from_dict(v)
                return receipt.to_json_string()
            except Exception:
                return json.dumps(v, ensure_ascii=False)
        if isinstance(v, str):
            try:
                json.loads(v)
            except json.JSONDecodeError:
                raise ValueError("receipt must be valid JSON string, dict or Receipt model")
            return v
        raise ValueError("receipt must be Receipt model, JSON string or dict")


class ResultURLNotification(BaseModel):
    """Model for ResultURL notification from RoboKassa."""

    model_config = ConfigDict(populate_by_name=True)

    out_sum: str = Field(..., description="Payment amount")
    inv_id: str = Field(..., description="Invoice ID")
    signature_value: str = Field(..., alias="SignatureValue", description="Signature")
    shp_params: Optional[Dict[str, str]] = Field(None, description="Additional parameters")


class SuccessURLNotification(BaseModel):
    """Model for SuccessURL redirect from RoboKassa."""

    model_config = ConfigDict(populate_by_name=True)

    out_sum: str = Field(..., description="Payment amount")
    inv_id: str = Field(..., description="Invoice ID")
    signature_value: str = Field(..., alias="SignatureValue", description="Signature")
    shp_params: Optional[Dict[str, str]] = Field(None, description="Additional parameters")


class InvoiceItem(BaseModel):
    """Model for invoice item."""

    name: str = Field(..., description="Item name (max 128 characters)", max_length=128)
    quantity: Union[int, float, Decimal] = Field(..., description="Item quantity", gt=0)
    cost: Union[float, Decimal] = Field(..., description="Price per unit", ge=0)
    tax: TaxRate = Field(..., description="Tax rate")
    payment_method: Optional[PaymentMethod] = Field(None, description="Payment method")
    payment_object: Optional[PaymentObject] = Field(None, description="Payment object")
    nomenclature_code: Optional[str] = Field(
        None, description="Product marking code (required for marked products)"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate item name."""
        if not v.strip():
            raise ValueError("Item name cannot be empty")
        if len(v) > 128:
            raise ValueError("Item name cannot exceed 128 characters")
        return v.strip()

    def to_api_dict(self) -> Dict[str, Any]:
        """Convert to dict for API (camelCase keys)."""
        data: Dict[str, Any] = {
            "Name": self.name,
            "Quantity": float(self.quantity),
            "Cost": float(self.cost),
            "Tax": self.tax.value,
        }
        if self.payment_method:
            data["PaymentMethod"] = self.payment_method.value
        if self.payment_object:
            data["PaymentObject"] = self.payment_object.value
        if self.nomenclature_code:
            data["NomenclatureCode"] = self.nomenclature_code
        return data


class RefundRequest(BaseModel):
    """Model for refund request (legacy XML API)."""

    invoice_id: int = Field(..., description="Invoice ID to refund")
    amount: Optional[Decimal] = Field(None, description="Refund amount (full if not specified)")

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Validate refund amount is positive if specified."""
        if v is not None and v <= 0:
            raise ValueError("Refund amount must be positive")
        return v


class RefundItem(BaseModel):
    """Model for refund item (InvoiceItems in refund request)."""

    name: str = Field(..., description="Item name (max 128 characters)", max_length=128)
    quantity: Union[int, float, Decimal] = Field(..., description="Item quantity", gt=0)
    cost: Union[float, Decimal] = Field(..., description="Price per unit", ge=0)
    tax: TaxRate = Field(..., description="Tax rate")
    payment_method: Optional[PaymentMethod] = Field(None, description="Payment method")
    payment_object: Optional[PaymentObject] = Field(None, description="Payment object")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate item name."""
        if not v.strip():
            raise ValueError("Item name cannot be empty")
        if len(v) > 128:
            raise ValueError("Item name cannot exceed 128 characters")
        return v.strip()

    def to_api_dict(self) -> Dict[str, Any]:
        """Convert to dict for API (camelCase keys)."""
        data: Dict[str, Any] = {
            "Name": self.name,
            "Quantity": float(self.quantity),
            "Cost": float(self.cost),
            "Tax": self.tax.value,
        }
        if self.payment_method:
            data["PaymentMethod"] = self.payment_method.value
        if self.payment_object:
            data["PaymentObject"] = self.payment_object.value
        return data


class RefundCreateRequest(BaseModel):
    """Model for refund creation request (JWT-based API)."""

    op_key: str = Field(
        ..., description="Operation key (unique identifier from OpStateExt or Result2)"
    )
    refund_sum: Optional[Union[Decimal, float, int, str]] = Field(
        None, description="Partial refund amount (omit for full refund)"
    )
    invoice_items: Optional[list[RefundItem]] = Field(
        None, description="Invoice items to refund (optional)"
    )

    @field_validator("refund_sum", mode="before")
    @classmethod
    def validate_refund_sum(cls, v: Union[Decimal, float, int, str, None]) -> Optional[Decimal]:
        """Validate and convert refund_sum to Decimal."""
        if v is None:
            return None
        if isinstance(v, Decimal):
            amount = v
        elif isinstance(v, (int, float)):
            amount = Decimal(str(v))
        elif isinstance(v, str):
            try:
                amount = Decimal(v)
            except (ValueError, TypeError) as e:
                raise ValueError(f"Invalid amount format: {v}") from e
        else:
            raise ValueError(f"Amount must be Decimal, float, int, or string, got {type(v)}")

        if amount <= 0:
            raise ValueError("Refund amount must be positive")
        return amount

    def to_api_dict(self) -> Dict[str, Any]:
        """Convert to dict for API (camelCase keys)."""
        data: Dict[str, Any] = {
            "OpKey": self.op_key,
        }
        if self.refund_sum is not None:
            data["RefundSum"] = float(self.refund_sum)
        if self.invoice_items:
            data["InvoiceItems"] = [item.to_api_dict() for item in self.invoice_items]
        return data


class RefundCreateResponse(BaseModel):
    """Model for refund creation response."""

    success: bool = Field(..., description="Whether refund request was created successfully")
    message: Optional[str] = Field(None, description="Error message (if success is False)")
    request_id: Optional[str] = Field(None, description="Request ID (GUID, if success is True)")

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "RefundCreateResponse":
        """Create RefundCreateResponse from API response."""
        return cls(
            success=data.get("success", False),
            message=data.get("message"),
            request_id=data.get("requestId"),
        )


class RefundStatusResponse(BaseModel):
    """Model for refund status response."""

    request_id: Optional[str] = Field(None, description="Request ID (GUID)")
    amount: Optional[Decimal] = Field(None, description="Refund amount")
    label: Optional[str] = Field(None, description="Refund status (finished, processing, canceled)")
    message: Optional[str] = Field(None, description="Error message (if request failed)")

    @field_validator("amount", mode="before")
    @classmethod
    def validate_amount(cls, v: Union[Decimal, float, int, str, None]) -> Optional[Decimal]:
        """Validate and convert amount to Decimal."""
        if v is None:
            return None
        if isinstance(v, Decimal):
            return v
        if isinstance(v, (int, float)):
            return Decimal(str(v))
        if isinstance(v, str):
            try:
                return Decimal(v)
            except (ValueError, TypeError):
                return None
        return None

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "RefundStatusResponse":
        """Create RefundStatusResponse from API response."""
        amount = data.get("amount")
        if amount is not None:
            try:
                amount = Decimal(str(amount))
            except (ValueError, TypeError):
                amount = None

        return cls(
            request_id=data.get("requestId"),
            amount=amount,
            label=data.get("label"),
            message=data.get("message"),
        )


class InvoiceResponse(BaseModel):
    """Model for invoice creation response."""

    id: Optional[str] = Field(None, description="Invoice ID (UUID)")
    url: Optional[str] = Field(None, description="Payment URL")
    inv_id: Optional[int] = Field(None, description="Invoice number")
    encoded_id: Optional[str] = Field(None, description="Encoded invoice ID (last part of URL)")

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "InvoiceResponse":
        """Create InvoiceResponse from API response."""
        return cls(
            id=data.get("id"),
            url=data.get("url"),
            inv_id=data.get("invId"),
            encoded_id=data.get("encodedId"),
        )


class ShopParam(BaseModel):
    """Model for shop parameter in split payment."""

    name: str = Field(..., description="Parameter name")
    value: str = Field(..., description="Parameter value")


class SplitMerchantReceipt(BaseModel):
    """Model for receipt in split merchant."""

    sno: Optional[TaxSystem] = Field(None, description="Tax system")
    items: list[ReceiptItem] = Field(..., description="List of receipt items", min_length=1)

    def to_api_dict(self) -> Dict[str, Any]:
        """Convert to dict for API (camelCase keys)."""
        data: Dict[str, Any] = {}
        if self.sno:
            data["sno"] = self.sno.value
        data["items"] = [item.model_dump_for_json() for item in self.items]
        return data


class SplitMerchant(BaseModel):
    """Model for split merchant in split payment."""

    id: str = Field(..., description="Merchant ID")
    invoice_id: Optional[int] = Field(
        None, description="Invoice ID (optional, auto-generated if not provided or 0)"
    )
    amount: Union[Decimal, float, int, str] = Field(..., description="Amount for this merchant")
    receipt: Optional[Union[SplitMerchantReceipt, Receipt, str, Dict[str, Any]]] = Field(
        None, description="Receipt data for fiscalization"
    )

    @field_validator("amount", mode="before")
    @classmethod
    def validate_amount(cls, v: Union[Decimal, float, int, str]) -> Decimal:
        """Validate and convert amount to Decimal."""
        if isinstance(v, Decimal):
            amount = v
        elif isinstance(v, (int, float)):
            amount = Decimal(str(v))
        elif isinstance(v, str):
            try:
                amount = Decimal(v)
            except (ValueError, TypeError) as e:
                raise ValueError(f"Invalid amount format: {v}") from e
        else:
            raise ValueError(f"Amount must be Decimal, float, int, or string, got {type(v)}")

        if amount < 0:
            raise ValueError("Amount must be non-negative")
        return amount

    @field_validator("receipt", mode="before")
    @classmethod
    def validate_receipt(
        cls, v: Union[SplitMerchantReceipt, Receipt, str, Dict[str, Any], None]
    ) -> Optional[SplitMerchantReceipt]:
        """Convert receipt to SplitMerchantReceipt."""
        if v is None:
            return None
        if isinstance(v, SplitMerchantReceipt):
            return v
        if isinstance(v, Receipt):
            return SplitMerchantReceipt(sno=v.sno, items=v.items)
        if isinstance(v, dict):
            try:
                receipt = Receipt.from_dict(v)
                return SplitMerchantReceipt(sno=receipt.sno, items=receipt.items)
            except Exception:
                sno_value = v.get("sno")
                sno = TaxSystem(sno_value) if sno_value else None
                items_data = v.get("items", [])
                items = [ReceiptItem(**item) for item in items_data]
                return SplitMerchantReceipt(sno=sno, items=items)
        if isinstance(v, str):
            try:
                receipt_dict = json.loads(v)
                receipt = Receipt.from_dict(receipt_dict)
                return SplitMerchantReceipt(sno=receipt.sno, items=receipt.items)
            except json.JSONDecodeError:
                raise ValueError(
                    "receipt must be valid JSON string, dict, Receipt or SplitMerchantReceipt model"
                )
        raise ValueError("receipt must be SplitMerchantReceipt, Receipt model, JSON string or dict")

    def to_api_dict(self) -> Dict[str, Any]:
        """Convert to dict for API (camelCase keys)."""
        data: Dict[str, Any] = {
            "id": self.id,
            "amount": float(self.amount),
        }
        if self.invoice_id is not None:
            data["InvoiceId"] = self.invoice_id
        if self.receipt:
            receipt = cast(SplitMerchantReceipt, self.receipt)
            receipt_dict = receipt.to_api_dict()
            data["receipt"] = receipt_dict
        return data


class SplitPaymentRequest(BaseModel):
    """Model for split payment request."""

    out_amount: Union[Decimal, float, int, str] = Field(..., description="Total payment amount")
    merchant_id: str = Field(..., description="Master merchant ID")
    merchant_comment: Optional[str] = Field(
        None, description="Order description (max 100 characters)", max_length=100
    )
    split_merchants: list[SplitMerchant] = Field(
        ..., description="List of split merchants", min_length=1
    )
    shop_params: Optional[list[ShopParam]] = Field(None, description="Additional shop parameters")
    email: Optional[str] = Field(None, description="Customer email")
    inc_curr: Optional[str] = Field(None, description="Payment method (e.g., BankCard)")
    language: Optional[str] = Field(None, description="Language (ru, en)")
    is_test: Optional[bool] = Field(None, description="Test mode flag")
    expiration_date: Optional[str] = Field(None, description="Payment expiration date (ISO 8601)")

    @field_validator("out_amount", mode="before")
    @classmethod
    def validate_out_amount(cls, v: Union[Decimal, float, int, str]) -> Decimal:
        """Validate and convert out_amount to Decimal."""
        if isinstance(v, Decimal):
            amount = v
        elif isinstance(v, (int, float)):
            amount = Decimal(str(v))
        elif isinstance(v, str):
            try:
                amount = Decimal(v)
            except (ValueError, TypeError) as e:
                raise ValueError(f"Invalid amount format: {v}") from e
        else:
            raise ValueError(f"Amount must be Decimal, float, int, or string, got {type(v)}")

        if amount <= 0:
            raise ValueError("Payment amount must be positive")
        return amount

    @field_validator("merchant_comment")
    @classmethod
    def validate_merchant_comment(cls, v: Optional[str]) -> Optional[str]:
        """Validate merchant comment length."""
        if v is not None and len(v) > 100:
            raise ValueError("Merchant comment cannot exceed 100 characters")
        return v

    @field_validator("split_merchants")
    @classmethod
    def validate_split_merchants(cls, v: list[SplitMerchant]) -> list[SplitMerchant]:
        """Validate split merchants list."""
        if not v:
            raise ValueError("At least one split merchant is required")
        return v

    def to_api_dict(self) -> Dict[str, Any]:
        """Convert to dict for API (camelCase keys)."""
        data: Dict[str, Any] = {
            "outAmount": float(self.out_amount),
            "merchant": {
                "id": self.merchant_id,
            },
            "splitMerchants": [merchant.to_api_dict() for merchant in self.split_merchants],
        }

        if self.merchant_comment:
            data["merchant"]["comment"] = self.merchant_comment

        if self.shop_params:
            data["shop_params"] = [{"name": p.name, "value": p.value} for p in self.shop_params]

        if self.email:
            data["email"] = self.email

        if self.inc_curr:
            data["incCurr"] = self.inc_curr

        if self.language:
            data["language"] = self.language

        if self.is_test is not None:
            data["isTest"] = self.is_test

        if self.expiration_date:
            data["expirationDate"] = self.expiration_date

        return data

    def to_json_string(self) -> str:
        """Convert request to JSON string (for signature calculation)."""
        return json.dumps(self.to_api_dict(), ensure_ascii=False, separators=(",", ":"))
