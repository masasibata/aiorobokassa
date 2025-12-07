"""Pydantic models for Receipt (fiscalization)."""

import json
from decimal import Decimal
from typing import Any, List, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator

from aiorobokassa.enums import PaymentMethod, PaymentObject, TaxRate, TaxSystem


class ReceiptItem(BaseModel):
    """Model for receipt item."""

    name: str = Field(..., description="Item name (max 128 characters)", max_length=128)
    quantity: Union[int, float, Decimal] = Field(..., description="Item quantity", gt=0)
    sum: Optional[Decimal] = Field(
        None,
        description="Total sum for all quantity of this item (required if cost is not provided)",
        ge=0,
    )
    cost: Optional[Decimal] = Field(
        None,
        description="Price per unit (optional, can be used instead of sum)",
        ge=0,
    )
    tax: TaxRate = Field(..., description="Tax rate")
    payment_method: Optional[PaymentMethod] = Field(
        None,
        description="Payment method (optional, uses default from merchant panel if not provided)",
    )
    payment_object: Optional[PaymentObject] = Field(
        None,
        description="Payment object (optional, uses default from merchant panel if not provided)",
    )
    nomenclature_code: Optional[str] = Field(
        None, description="Product marking code (required for marked products)"
    )

    @model_validator(mode="after")
    def validate_sum_or_cost(self) -> "ReceiptItem":
        """Validate that either sum or cost is provided."""
        if self.sum is None and self.cost is None:
            raise ValueError("Either 'sum' or 'cost' must be provided")
        if self.sum is not None and self.cost is not None:
            calculated_sum = Decimal(str(self.cost)) * Decimal(str(self.quantity))
            if abs(self.sum - calculated_sum) > Decimal("0.01"):
                raise ValueError(f"sum ({self.sum}) must equal cost * quantity ({calculated_sum})")
        if self.sum is None and self.cost is not None:
            self.sum = Decimal(str(self.cost)) * Decimal(str(self.quantity))
        return self

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate item name."""
        if not v.strip():
            raise ValueError("Item name cannot be empty")
        if len(v) > 128:
            raise ValueError("Item name cannot exceed 128 characters")
        return v.strip()

    def model_dump_for_json(self) -> dict:
        """Convert to dict for JSON serialization."""
        data = {
            "name": self.name,
            "quantity": float(self.quantity),
            "tax": self.tax.value,
        }

        if self.cost is not None:
            calculated_sum = Decimal(str(self.cost)) * Decimal(str(self.quantity))
            if self.sum is None or abs(self.sum - calculated_sum) < Decimal("0.01"):
                data["cost"] = float(self.cost)
            else:
                data["sum"] = float(self.sum)
        elif self.sum is not None:
            data["sum"] = float(self.sum)

        if self.payment_method:
            data["payment_method"] = self.payment_method.value
        if self.payment_object:
            data["payment_object"] = self.payment_object.value
        if self.nomenclature_code:
            data["nomenclature_code"] = self.nomenclature_code

        return data


class Receipt(BaseModel):
    """Model for Receipt (fiscalization data)."""

    items: List[ReceiptItem] = Field(..., description="List of receipt items", min_length=1)
    sno: Optional[TaxSystem] = Field(
        None,
        description="Tax system (optional if organization has only one tax system type)",
    )

    @field_validator("items")
    @classmethod
    def validate_items(cls, v: List[ReceiptItem]) -> List[ReceiptItem]:
        """Validate items list."""
        if not v:
            raise ValueError("Receipt must contain at least one item")
        if len(v) > 100:
            raise ValueError("Receipt cannot contain more than 100 items")
        return v

    @model_validator(mode="after")
    def validate_total_sum(self) -> "Receipt":
        """Validate that total sum of items is positive."""
        total = sum(
            (
                item.sum
                if item.sum is not None
                else (
                    (item.cost * Decimal(str(item.quantity)))
                    if item.cost is not None
                    else Decimal("0")
                )
            )
            for item in self.items
        )
        if total <= 0:
            raise ValueError("Total sum of receipt items must be greater than zero")
        return self

    def to_json_string(self) -> str:
        """Convert receipt to JSON string."""
        data: dict[str, Any] = {}
        if self.sno:
            data["sno"] = self.sno.value
        data["items"] = [item.model_dump_for_json() for item in self.items]
        return json.dumps(data, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict) -> "Receipt":
        """Create Receipt from dictionary."""
        items_data = data.get("items", [])
        items = [ReceiptItem(**item) for item in items_data]

        sno_value = data.get("sno")
        sno = TaxSystem(sno_value) if sno_value else None

        return cls(items=items, sno=sno)
