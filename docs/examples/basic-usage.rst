Basic Usage Examples
====================

Simple examples for common operations.

Create Payment URL
------------------

.. code-block:: python

   import asyncio
   from decimal import Decimal
   from aiorobokassa import RoboKassaClient

   async def main():
       async with RoboKassaClient(
           merchant_login="your_merchant_login",
           password1="password1",
           password2="password2",
           test_mode=True,
       ) as client:
           url = client.create_payment_url(
               out_sum=Decimal("100.00"),
               description="Test payment",
               inv_id=123,
           )
           print(f"Payment URL: {url}")

   asyncio.run(main())

Verify Notification
-------------------

.. code-block:: python

   from aiorobokassa import RoboKassaClient, SignatureError

   def verify_payment(params: dict):
       client = RoboKassaClient(
           merchant_login="your_merchant_login",
           password1="password1",
           password2="password2",
       )
       
       parsed = client.parse_result_url_params(params)
       
       try:
           client.verify_result_url(
               out_sum=parsed["out_sum"],
               inv_id=parsed["inv_id"],
               signature_value=parsed["signature_value"],
               shp_params=parsed.get("shp_params"),
           )
           return True
       except SignatureError:
           return False

Create Invoice
--------------

.. code-block:: python

   import asyncio
   from decimal import Decimal
   from aiorobokassa import RoboKassaClient

   async def main():
       async with RoboKassaClient(
           merchant_login="your_merchant_login",
           password1="password1",
           password2="password2",
       ) as client:
           result = await client.create_invoice(
               out_sum=Decimal("100.00"),
               description="Invoice payment",
               inv_id=123,
           )
           print(f"Invoice created: {result}")

   asyncio.run(main())

Process Refund
--------------

.. code-block:: python

   import asyncio
   from decimal import Decimal
   from aiorobokassa import RoboKassaClient

   async def main():
       async with RoboKassaClient(
           merchant_login="your_merchant_login",
           password1="password1",
           password2="password2",
       ) as client:
           # Full refund
           result = await client.create_refund(invoice_id=123)
           print(f"Refund: {result}")
           
           # Partial refund
           result = await client.create_refund(
               invoice_id=123,
               amount=Decimal("50.00"),
           )
           print(f"Partial refund: {result}")

   asyncio.run(main())

