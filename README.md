[![Downloads](https://pepy.tech/badge/aiorobokassa)](https://pepy.tech/project/aiorobokassa)
[![Downloads](https://pepy.tech/badge/aiorobokassa/month)](https://pepy.tech/project/aiorobokassa)
[![Downloads](https://pepy.tech/badge/aiorobokassa/week)](https://pepy.tech/project/aiorobokassa)

<div align="center">

![aiorobokassa banner](docs/_static/banner.png)

# aiorobokassa

**Async Python library for RoboKassa payment gateway integration**

`aiorobokassa` is a modern async Python library for integrating with RoboKassa payment gateway. The library provides full support for RoboKassa API, including payment link generation, notification handling, invoice creation, refunds, fiscalization, and more.

</div>

## ✨ Features

- 🚀 **Full async/await support** with `aiohttp` for high performance
- 💳 **Payment link generation** with customizable parameters
- 🔔 **Notification handling** (ResultURL, SuccessURL) with signature verification
- 📄 **Invoice creation** via Invoice API (JWT-based)
- 💰 **Refund operations** (full and partial) via legacy XML API and modern JWT API
- 🧾 **Fiscalization support** (Receipt) with Pydantic models and enums for ФЗ-54 compliance
- 🔐 **Signature verification** (MD5, SHA256, SHA512)
- 🛡️ **Type hints** throughout the codebase
- ✅ **Pydantic validation** for all requests and responses
- 🧪 **Test mode support** for development
- 🏗️ **Clean architecture** (SOLID, DRY, KISS principles)

## 🔗 Links

- 📚 **Documentation:** [aiorobokassa.readthedocs.io](https://aiorobokassa.readthedocs.io)
- 🐛 **Issue Tracker:** [GitHub Issues](https://github.com/masasibata/aiorobokassa/issues)
- 📦 **PyPI:** [pypi.org/project/aiorobokassa](https://pypi.org/project/aiorobokassa/)
- 🖱️ **Developer contacts:** [![Dev-Telegram](https://img.shields.io/badge/Telegram-blue.svg?style=flat-square&logo=telegram)](https://t.me/masaasibaata)
- 💝 **Support project:** [![Tribute](https://img.shields.io/badge/Support%20Project-Tribute-green.svg?style=flat-square&logo=telegram)](https://t.me/tribute/app?startapp=dzqR)

## 🐦 Dependencies

| Library  |                       Description                       |
| :------: | :-----------------------------------------------------: |
| aiohttp  | Asynchronous HTTP Client/Server for asyncio and Python. |
| pydantic |                   JSON Data Validator                   |

## 📁 Project Structure

```
aiorobokassa/
├── api/                    # API mixins
│   ├── base.py            # Base API client
│   ├── invoice.py        # Invoice operations
│   ├── payment.py        # Payment operations
│   └── refund.py         # Refund operations
├── models/                # Pydantic models
│   ├── receipt.py        # Receipt models for fiscalization
│   └── requests.py       # Request/response models
├── utils/                 # Utility functions
│   ├── helpers.py        # Helper functions
│   ├── jwt.py            # JWT token creation
│   ├── signature.py      # Signature calculation
│   └── xml.py            # XML parsing
├── client.py             # Main RoboKassa client
├── constants.py          # Constants
├── enums.py              # Enums
└── exceptions.py         # Custom exceptions
```

## 🚀 Quick Start

### Installation

```bash
pip install aiorobokassa
```

### Basic Usage

```python
import asyncio
from decimal import Decimal
from aiorobokassa import RoboKassaClient

async def main():
    # Initialize client
    client = RoboKassaClient(
        merchant_login="your_merchant_login",
        password1="password1",
        password2="password2",
        test_mode=True,  # Use test mode for development
    )

    # Create payment URL
    payment_url = client.create_payment_url(
        out_sum=Decimal("100.00"),
        description="Test payment",
        inv_id=123,
        email="customer@example.com",
    )

    print(f"Payment URL: {payment_url}")

    # Close client session
    await client.close()

asyncio.run(main())
```

## 🎯 Supported Features

The library supports **all RoboKassa API features**:

- 💳 **Payments** — payment link generation with customizable parameters
- 🔔 **Notifications** — ResultURL and SuccessURL signature verification
- 📄 **Invoices** — create and manage invoices via Invoice API (JWT-based)
- 💰 **Refunds** — full and partial refunds via legacy XML API and modern JWT API
- 🧾 **Fiscalization** — receipt generation for ФЗ-54 compliance
- 🔐 **Signatures** — MD5, SHA256, SHA512 signature algorithms
- 🧪 **Test Mode** — development and testing support

## 📋 Main Methods

### 💳 Payments

```python
from decimal import Decimal
from aiorobokassa import RoboKassaClient

# Create payment URL
payment_url = client.create_payment_url(
    out_sum=Decimal("100.00"),
    description="Payment for order #12345",
    inv_id=12345,
    email="customer@example.com",
    culture="ru",
    user_parameters={"user_id": "123", "order_id": "456"},
)

# Verify ResultURL notification
params = client.parse_result_url_params(request_params)
client.verify_result_url(
    out_sum=params["out_sum"],
    inv_id=params["inv_id"],
    signature_value=params["signature_value"],
    shp_params=params.get("shp_params"),
)

# Verify SuccessURL redirect
params = client.parse_success_url_params(request_params)
client.verify_success_url(
    out_sum=params["out_sum"],
    inv_id=params["inv_id"],
    signature_value=params["signature_value"],
    shp_params=params.get("shp_params"),
)
```

### 📄 Invoices

```python
from aiorobokassa import RoboKassaClient, InvoiceType
from aiorobokassa.models.requests import InvoiceItem
from aiorobokassa.enums import TaxRate, PaymentMethod, PaymentObject

# Create simple invoice
result = await client.create_invoice(
    out_sum=Decimal("100.00"),
    description="Invoice payment",
    invoice_type=InvoiceType.ONE_TIME,
    inv_id=123,
    culture="ru",
)

# Create invoice with fiscalization
invoice_items = [
    InvoiceItem(
        name="Service 1",
        quantity=1,
        cost=100.0,
        tax=TaxRate.VAT20,
        payment_method=PaymentMethod.FULL_PAYMENT,
        payment_object=PaymentObject.SERVICE,
    )
]

result = await client.create_invoice(
    out_sum=Decimal("100.00"),
    description="Invoice with items",
    invoice_items=invoice_items,
)

# Deactivate invoice
await client.deactivate_invoice(inv_id=123)

# Get invoice information list
invoices = await client.get_invoice_information_list(
    current_page=1,
    page_size=10,
    invoice_statuses=["paid", "notpaid"],
)
```

### 💰 Refunds

```python
from decimal import Decimal

# Legacy XML API - Full refund
refund_result = await client.create_refund(invoice_id=123)

# Legacy XML API - Partial refund
partial_refund = await client.create_refund(
    invoice_id=123,
    amount=Decimal("50.00"),
)

# Legacy XML API - Check refund status
status = await client.get_refund_status(invoice_id=123)

# Modern JWT API - Create refund (requires password3)
refund = await client.create_refund_v2(
    op_key="operation_key_from_payment",
    refund_sum=Decimal("50.00"),
)

# Modern JWT API - Get refund status
refund_status = await client.get_refund_status_v2(
    request_id=refund.request_id
)
```

### 🧾 Fiscalization (Receipt) - ФЗ-54

For clients using RoboKassa's cloud or cash solutions, fiscalization is required:

```python
from aiorobokassa import (
    RoboKassaClient,
    Receipt,
    ReceiptItem,
    TaxRate,
    TaxSystem,
    PaymentMethod,
    PaymentObject,
)

# Create receipt item
item = ReceiptItem(
    name="Товар 1",
    quantity=1,
    sum=Decimal("100.00"),
    tax=TaxRate.VAT10,
    payment_method=PaymentMethod.FULL_PAYMENT,
    payment_object=PaymentObject.COMMODITY,
)

# Create receipt
receipt = Receipt(
    items=[item],
    sno=TaxSystem.OSN,
)

# Create payment URL with receipt
url = client.create_payment_url(
    out_sum=Decimal("100.00"),
    description="Payment with receipt",
    receipt=receipt,
)
```

### 🔔 Handling Notifications

#### ResultURL (Server-to-Server Notification)

```python
from aiorobokassa import RoboKassaClient, SignatureError

# In your web framework (FastAPI, Django, etc.)
async def handle_result_url(request_params: dict):
    client = RoboKassaClient(
        merchant_login="your_merchant_login",
        password1="password1",
        password2="password2",
    )

    # Parse parameters
    params = client.parse_result_url_params(request_params)

    try:
        # Verify signature
        client.verify_result_url(
            out_sum=params["out_sum"],
            inv_id=params["inv_id"],
            signature_value=params["signature_value"],
            shp_params=params.get("shp_params"),
        )

        # Payment is valid, update order status
        invoice_id = params["inv_id"]
        amount = params["out_sum"]
        # ... update your database

        return "OK" + invoice_id  # RoboKassa expects this response
    except SignatureError:
        # Invalid signature, reject payment
        return "ERROR"
```

#### SuccessURL (User Redirect)

```python
from aiorobokassa import RoboKassaClient, SignatureError

async def handle_success_url(request_params: dict):
    client = RoboKassaClient(
        merchant_login="your_merchant_login",
        password1="password1",
        password2="password2",
    )

    params = client.parse_success_url_params(request_params)

    try:
        client.verify_success_url(
            out_sum=params["out_sum"],
            inv_id=params["inv_id"],
            signature_value=params["signature_value"],
            shp_params=params.get("shp_params"),
        )

        # Show success page to user
        return "Payment successful!"
    except SignatureError:
        return "Payment verification failed"
```

## 🔧 Context Manager

```python
import asyncio
from decimal import Decimal
from aiorobokassa import RoboKassaClient

async with RoboKassaClient(
    merchant_login="your_merchant_login",
    password1="password1",
    password2="password2",
    test_mode=True,
) as client:
    payment_url = client.create_payment_url(
        out_sum=Decimal("100.00"),
        description="Test payment",
    )
    print(f"Payment URL: {payment_url}")
    # Client automatically closes
```

## 🛠️ Installation and Setup

### Requirements

- Python 3.8+
- aiohttp >= 3.8.0
- pydantic >= 2.0.0

### Installation via pip

```bash
pip install aiorobokassa
```

### Installation via Poetry

```bash
poetry add aiorobokassa
```

## 📖 Documentation

📚 **Full documentation is available at [aiorobokassa.readthedocs.io](https://aiorobokassa.readthedocs.io)**

The documentation includes:

- 📖 Installation guide
- 🚀 Quick start tutorial
- 📝 Detailed guides (payments, notifications, invoices, refunds, fiscalization)
- 🔧 API reference
- 💡 Code examples (FastAPI, Django, Flask)
- ❌ Error handling guide

For more information about RoboKassa API, visit [official RoboKassa documentation](https://docs.robokassa.ru/).

## 🤝 Supporting the Project

If the library was helpful, you can support the project:

- 💝 **[Tribute](https://t.me/tribute/app?startapp=dzqR)** — support through Telegram
- 🐛 **Report a bug** — [GitHub Issues](https://github.com/masasibata/aiorobokassa/issues)
- 💬 **Contact developer** — [![Dev-Telegram](https://img.shields.io/badge/Telegram-blue.svg?style=flat-square&logo=telegram)](https://t.me/masaasibaata)

## 🚀 Contributing

We welcome contributions to the library! Here's how you can help:

### Quick Start for Developers

```bash
# Clone the repository
git clone https://github.com/masasibata/aiorobokassa.git
cd aiorobokassa

# Install dependencies for development
poetry install --extras dev

# Or with pip
pip install -e ".[dev]"
```

### Available Commands

```bash
# Testing
make test                 # Run tests
make test-cov            # Tests with code coverage
make test-fast           # Fast tests without coverage

# Code Quality
make lint                # Linting (Black)
make format              # Format code
make type-check          # Type checking (MyPy)
make all-checks          # All quality checks

# Build and Publish
make build               # Build package
make clean               # Clean artifacts

# Documentation
make docs                # Build documentation
make docs-serve          # Local documentation server
```

### Contribution Process

1. **Fork the repository** on GitHub
2. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make changes** and ensure all checks pass:
   ```bash
   make all-checks
   ```
4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```
5. **Push your changes**:
   ```bash
   git push origin feature/your-feature-name
   ```
6. **Create a Pull Request** on GitHub

### Pull Request Requirements

- ✅ **All tests pass** (`make test`)
- ✅ **Code is formatted** (`make format`)
- ✅ **Linting passes** (`make lint`)
- ✅ **Type checking passes** (`make type-check`)
- ✅ **Documentation updated** (if necessary)
- ✅ **Descriptive commit message**

### Contribution Types

- 🐛 **Bug fixes** — fixing errors in code
- ✨ **New features** — adding new functionality
- 📚 **Documentation** — improving documentation and examples
- ⚡ **Optimization** — improving performance
- 🧪 **Tests** — adding or improving tests
- 🔧 **Infrastructure** — improving development tools

### Commit Conventions

Use [Conventional Commits](https://www.conventionalcommits.org/):

```bash
feat: add new payment method support
fix: resolve timeout issue in payment creation
docs: update API documentation
test: add tests for refund functionality
refactor: improve error handling
```

### Getting Help

- 💬 **Questions** — [GitHub Issues](https://github.com/masasibata/aiorobokassa/issues)
- 🐛 **Problems** — [GitHub Issues](https://github.com/masasibata/aiorobokassa/issues)

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---
