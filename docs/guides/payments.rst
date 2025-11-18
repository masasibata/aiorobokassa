Payment Link Generation
=======================

This guide explains how to generate payment links for redirecting users to RoboKassa.

Basic Payment URL
------------------

The simplest way to create a payment URL:

.. code-block:: python

   from decimal import Decimal
   from aiorobokassa import RoboKassaClient

   async with RoboKassaClient(
       merchant_login="your_merchant_login",
       password1="password1",
       password2="password2",
   ) as client:
       url = client.create_payment_url(
           out_sum=Decimal("100.00"),
           description="Payment for order #123",
       )

Payment with Invoice ID
-----------------------

Include an invoice ID to track payments:

.. code-block:: python

   url = client.create_payment_url(
       out_sum=Decimal("100.00"),
       description="Payment for order #123",
       inv_id=12345,
   )

Payment with Customer Email
---------------------------

Send payment receipt to customer email:

.. code-block:: python

   url = client.create_payment_url(
       out_sum=Decimal("100.00"),
       description="Payment for order #123",
       inv_id=12345,
       email="customer@example.com",
   )

Custom Parameters
-----------------

Add custom user parameters (Shp_*):

.. code-block:: python

   url = client.create_payment_url(
       out_sum=Decimal("100.00"),
       description="Payment for order #123",
       inv_id=12345,
       user_parameters={
           "user_id": "123",
           "order_id": "456",
       },
   )

These parameters will be available in notifications as ``Shp_user_id`` and ``Shp_order_id``.

Language and Encoding
---------------------

Specify language and encoding:

.. code-block:: python

   url = client.create_payment_url(
       out_sum=Decimal("100.00"),
       description="Payment for order #123",
       culture="en",  # or "ru"
       encoding="utf-8",
   )

Signature Algorithms
--------------------

Choose signature algorithm (MD5, SHA256, or SHA512):

.. code-block:: python

   from aiorobokassa import RoboKassaClient, SignatureAlgorithm

   url = client.create_payment_url(
       out_sum=Decimal("100.00"),
       description="Payment for order #123",
       signature_algorithm=SignatureAlgorithm.SHA256,
   )

Payment Expiration
------------------

Set payment expiration date:

.. code-block:: python

   from datetime import datetime, timedelta

   expiration = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
   
   url = client.create_payment_url(
       out_sum=Decimal("100.00"),
       description="Payment for order #123",
       expiration_date=expiration,
   )

Test Mode
---------

Enable test mode for development:

.. code-block:: python

   client = RoboKassaClient(
       merchant_login="your_merchant_login",
       password1="password1",
       password2="password2",
       test_mode=True,  # Enable test mode
   )

In test mode, payments won't be processed but you can test the integration.

Fiscalization (Receipt)
------------------------

For fiscalization support, see :doc:`fiscalization` guide.

Basic example with receipt:

.. code-block:: python

   receipt_data = {
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
   
   url = client.create_payment_url(
       out_sum=Decimal("100.00"),
       description="Payment",
       receipt=receipt_data,
   )

Split Payment
------------

Split payment allows distributing a payment between multiple merchants. This is useful for marketplace scenarios where payment needs to be split between the platform and sellers.

Basic Split Payment
~~~~~~~~~~~~~~~~~~~

Create a split payment URL:

.. code-block:: python

   split_merchants = [
       {
           "id": "merchant1",
           "amount": 50.00,
       },
       {
           "id": "merchant2",
           "amount": 50.50,
       },
   ]

   url = client.create_split_payment_url(
       out_amount=Decimal("100.50"),
       merchant_id="master_merchant",
       split_merchants=split_merchants,
   )

Split Payment with Receipt
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add fiscalization receipts for each merchant:

.. code-block:: python

   from aiorobokassa.models.receipt import Receipt, ReceiptItem
   from aiorobokassa.enums import TaxRate, TaxSystem, PaymentMethod, PaymentObject

   receipt = Receipt(
       items=[
           ReceiptItem(
               name="Item 1",
               quantity=1,
               cost=50.0,
               tax=TaxRate.VAT20,
               payment_method=PaymentMethod.FULL_PAYMENT,
               payment_object=PaymentObject.COMMODITY,
           )
       ],
       sno=TaxSystem.OSN,
   )

   split_merchants = [
       {
           "id": "merchant1",
           "amount": 50.00,
           "invoice_id": 100,
           "receipt": receipt,
       },
       {
           "id": "merchant2",
           "amount": 50.50,
       },
   ]

   url = client.create_split_payment_url(
       out_amount=Decimal("100.50"),
       merchant_id="master_merchant",
       split_merchants=split_merchants,
   )

Split Payment with All Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use all available parameters:

.. code-block:: python

   shop_params = [
       {"name": "param1", "value": "value1"},
       {"name": "param2", "value": "value2"},
   ]

   url = client.create_split_payment_url(
       out_amount=Decimal("100.50"),
       merchant_id="master_merchant",
       split_merchants=split_merchants,
       merchant_comment="Split payment for order #123",
       shop_params=shop_params,
       email="customer@example.com",
       inc_curr="BankCard",
       language="ru",
       is_test=True,
       expiration_date="2024-12-31T23:59:59",
       signature_algorithm=SignatureAlgorithm.SHA256,
   )

Split Payment Notes
~~~~~~~~~~~~~~~~~~~

- **Master merchant** initiates the split operation and receives the payment
- **Split merchants** receive their portion of the payment
- **Amounts can be zero** for merchants that don't need payment
- **Receipts are optional** but recommended for fiscalization compliance
- **Signature algorithm** defaults to MD5 but SHA256/SHA512 are recommended for production

