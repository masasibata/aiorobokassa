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
       url = await client.create_payment_url(
           out_sum=Decimal("100.00"),
           description="Payment for order #123",
       )

Payment with Invoice ID
-----------------------

Include an invoice ID to track payments:

.. code-block:: python

   url = await client.create_payment_url(
       out_sum=Decimal("100.00"),
       description="Payment for order #123",
       inv_id=12345,
   )

Payment with Customer Email
---------------------------

Send payment receipt to customer email:

.. code-block:: python

   url = await client.create_payment_url(
       out_sum=Decimal("100.00"),
       description="Payment for order #123",
       inv_id=12345,
       email="customer@example.com",
   )

Custom Parameters
-----------------

Add custom user parameters (Shp_*):

.. code-block:: python

   url = await client.create_payment_url(
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

   url = await client.create_payment_url(
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

   url = await client.create_payment_url(
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
   
   url = await client.create_payment_url(
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
   
   url = await client.create_payment_url(
       out_sum=Decimal("100.00"),
       description="Payment",
       receipt=receipt_data,
   )

