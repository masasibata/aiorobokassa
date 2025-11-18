"""Tests for Receipt Pydantic models."""

import pytest
from decimal import Decimal

from aiorobokassa.enums import PaymentMethod, PaymentObject, TaxRate, TaxSystem
from aiorobokassa.models.receipt import Receipt, ReceiptItem


class TestReceiptItem:
    """Tests for ReceiptItem model."""

    def test_receipt_item_basic(self):
        """Test creating basic receipt item."""
        item = ReceiptItem(
            name="Товар 1",
            quantity=1,
            sum=Decimal("100.00"),
            tax=TaxRate.VAT10,
        )
        assert item.name == "Товар 1"
        assert item.quantity == 1
        assert item.sum == Decimal("100.00")
        assert item.tax == TaxRate.VAT10

    def test_receipt_item_with_cost(self):
        """Test receipt item with cost instead of sum."""
        item = ReceiptItem(
            name="Товар 1",
            quantity=2,
            cost=Decimal("50.00"),
            tax=TaxRate.VAT10,
        )
        # Sum should be calculated automatically
        assert item.sum == Decimal("100.00")

    def test_receipt_item_with_all_fields(self):
        """Test receipt item with all optional fields."""
        item = ReceiptItem(
            name="Товар 1",
            quantity=1,
            sum=Decimal("100.00"),
            tax=TaxRate.VAT20,
            payment_method=PaymentMethod.FULL_PAYMENT,
            payment_object=PaymentObject.COMMODITY,
            nomenclature_code="04620034587217",
        )
        assert item.payment_method == PaymentMethod.FULL_PAYMENT
        assert item.payment_object == PaymentObject.COMMODITY
        assert item.nomenclature_code == "04620034587217"

    def test_receipt_item_empty_name(self):
        """Test that empty name raises error."""
        with pytest.raises(ValueError, match="Item name cannot be empty"):
            ReceiptItem(
                name="",
                quantity=1,
                sum=Decimal("100.00"),
                tax=TaxRate.VAT10,
            )

    def test_receipt_item_name_too_long(self):
        """Test that name longer than 128 chars raises error."""
        long_name = "A" * 129
        with pytest.raises(Exception):  # Pydantic validation error
            ReceiptItem(
                name=long_name,
                quantity=1,
                sum=Decimal("100.00"),
                tax=TaxRate.VAT10,
            )

    def test_receipt_item_no_sum_or_cost(self):
        """Test that missing both sum and cost raises error."""
        with pytest.raises(ValueError, match="Either 'sum' or 'cost' must be provided"):
            ReceiptItem(
                name="Товар",
                quantity=1,
                tax=TaxRate.VAT10,
            )

    def test_receipt_item_negative_quantity(self):
        """Test that negative quantity raises error."""
        with pytest.raises(ValueError):
            ReceiptItem(
                name="Товар",
                quantity=-1,
                sum=Decimal("100.00"),
                tax=TaxRate.VAT10,
            )

    def test_receipt_item_model_dump_for_json(self):
        """Test model_dump_for_json method."""
        item = ReceiptItem(
            name="Товар",
            quantity=2,
            cost=Decimal("50.00"),
            tax=TaxRate.VAT10,
            payment_method=PaymentMethod.FULL_PAYMENT,
        )
        data = item.model_dump_for_json()
        assert data["name"] == "Товар"
        assert data["quantity"] == 2.0
        assert data["tax"] == "vat10"
        # When cost is provided, it should be in output
        assert "cost" in data or "sum" in data
        assert data["payment_method"] == "full_payment"


class TestReceipt:
    """Tests for Receipt model."""

    def test_receipt_basic(self):
        """Test creating basic receipt."""
        item = ReceiptItem(
            name="Товар 1",
            quantity=1,
            sum=Decimal("100.00"),
            tax=TaxRate.VAT10,
        )
        receipt = Receipt(items=[item], sno=TaxSystem.OSN)
        assert len(receipt.items) == 1
        assert receipt.sno == TaxSystem.OSN

    def test_receipt_without_sno(self):
        """Test receipt without sno (optional)."""
        item = ReceiptItem(
            name="Товар 1",
            quantity=1,
            sum=Decimal("100.00"),
            tax=TaxRate.VAT10,
        )
        receipt = Receipt(items=[item])
        assert receipt.sno is None

    def test_receipt_multiple_items(self):
        """Test receipt with multiple items."""
        items = [
            ReceiptItem(name="Товар 1", quantity=1, sum=Decimal("100.00"), tax=TaxRate.VAT10),
            ReceiptItem(name="Товар 2", quantity=2, sum=Decimal("200.00"), tax=TaxRate.VAT20),
        ]
        receipt = Receipt(items=items, sno=TaxSystem.OSN)
        assert len(receipt.items) == 2

    def test_receipt_empty_items(self):
        """Test that empty items list raises error."""
        with pytest.raises(Exception):  # Pydantic validation error
            Receipt(items=[])

    def test_receipt_too_many_items(self):
        """Test that more than 100 items raises error."""
        items = [
            ReceiptItem(name=f"Товар {i}", quantity=1, sum=Decimal("10.00"), tax=TaxRate.VAT10)
            for i in range(101)
        ]
        with pytest.raises(ValueError, match="Receipt cannot contain more than 100 items"):
            Receipt(items=items)

    def test_receipt_to_json_string(self):
        """Test to_json_string method."""
        item = ReceiptItem(
            name="Товар",
            quantity=1,
            sum=Decimal("100.00"),
            tax=TaxRate.VAT10,
        )
        receipt = Receipt(items=[item], sno=TaxSystem.OSN)
        json_str = receipt.to_json_string()
        assert "sno" in json_str
        assert "osn" in json_str
        assert "items" in json_str
        assert "Товар" in json_str

    def test_receipt_from_dict(self):
        """Test from_dict class method."""
        data = {
            "sno": "osn",
            "items": [
                {
                    "name": "Товар",
                    "quantity": 1,
                    "sum": 100,
                    "tax": "vat10",
                }
            ],
        }
        receipt = Receipt.from_dict(data)
        assert receipt.sno == TaxSystem.OSN
        assert len(receipt.items) == 1
        assert receipt.items[0].name == "Товар"

    def test_receipt_from_dict_without_sno(self):
        """Test from_dict without sno."""
        data = {
            "items": [
                {
                    "name": "Товар",
                    "quantity": 1,
                    "sum": 100,
                    "tax": "vat10",
                }
            ],
        }
        receipt = Receipt.from_dict(data)
        assert receipt.sno is None

    def test_receipt_with_enums(self):
        """Test receipt with enum values."""
        item = ReceiptItem(
            name="Услуга",
            quantity=1,
            sum=Decimal("500.00"),
            tax=TaxRate.VAT20,
            payment_method=PaymentMethod.FULL_PAYMENT,
            payment_object=PaymentObject.SERVICE,
        )
        receipt = Receipt(items=[item], sno=TaxSystem.USN_INCOME)
        json_str = receipt.to_json_string()
        assert "usn_income" in json_str
        assert "service" in json_str
        assert "full_payment" in json_str
