Quick Start
===========

This guide will help you get started with aiorobokassa in just a few minutes.

Basic Setup
-----------

First, import the necessary modules and create a client:

.. code-block:: python

   import asyncio
   from decimal import Decimal
   from aiorobokassa import RoboKassaClient

   async def main():
       client = RoboKassaClient(
           merchant_login="your_merchant_login",
           password1="password1",
           password2="password2",
           test_mode=True,  # Use test mode for development
       )
       
       # Your code here
       
       await client.close()

   asyncio.run(main())

Using Context Manager
---------------------

The recommended way to use the client is with an async context manager:

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
           # Your code here
           pass

   asyncio.run(main())

Create Payment URL
------------------

Generate a payment URL to redirect users to RoboKassa:

.. code-block:: python

   async with RoboKassaClient(
       merchant_login="your_merchant_login",
       password1="password1",
       password2="password2",
       test_mode=True,
   ) as client:
       payment_url = client.create_payment_url(
           out_sum=Decimal("100.00"),
           description="Test payment",
           inv_id=123,
           email="customer@example.com",
       )
       print(f"Payment URL: {payment_url}")

Handle Notifications
---------------------

Verify incoming notifications from RoboKassa:

.. code-block:: python

   from aiorobokassa import RoboKassaClient, SignatureError

   async def handle_result_url(request_params: dict):
       client = RoboKassaClient(
           merchant_login="your_merchant_login",
           password1="password1",
           password2="password2",
       )
       
       params = client.parse_result_url_params(request_params)
       
       try:
           client.verify_result_url(
               out_sum=params["out_sum"],
               inv_id=params["inv_id"],
               signature_value=params["signature_value"],
               shp_params=params.get("shp_params"),
           )
           # Payment is valid, update your database
           return f"OK{params['inv_id']}"
       except SignatureError:
           return "ERROR"

Next Steps
----------

- Read the :doc:`guides/index` for detailed guides
- Check out :doc:`examples/index` for more examples
- Browse the :doc:`api/index` for complete API reference

