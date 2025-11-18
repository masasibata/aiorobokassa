"""Pydantic models for request/response validation."""

import json
from decimal import Decimal
from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator

from aiorobokassa.enums import PaymentMethod, PaymentObject, TaxRate
from aiorobokassa.models.receipt import Receipt


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
        # Convert to Decimal
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

        # Validate amount is positive
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
            # Try to create Receipt from dict
            try:
                receipt = Receipt.from_dict(v)
                return receipt.to_json_string()
            except Exception:
                # Fallback to direct JSON dump if Receipt model fails
                return json.dumps(v, ensure_ascii=False)
        if isinstance(v, str):
            # Validate it's valid JSON
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
    """Model for refund request."""

    invoice_id: int = Field(..., description="Invoice ID to refund")
    amount: Optional[Decimal] = Field(None, description="Refund amount (full if not specified)")

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Validate refund amount is positive if specified."""
        if v is not None and v <= 0:
            raise ValueError("Refund amount must be positive")
        return v
