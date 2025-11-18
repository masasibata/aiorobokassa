Refund Operations
==================

This guide explains how to process refunds for payments.

Full Refund
-----------

Create a full refund for an invoice:

.. code-block:: python

   from aiorobokassa import RoboKassaClient

   async with RoboKassaClient(
       merchant_login="your_merchant_login",
       password1="password1",
       password2="password2",
   ) as client:
       result = await client.create_refund(
           invoice_id=12345,
       )
       
       print(f"Refund result: {result}")

Partial Refund
--------------

Create a partial refund by specifying the amount:

.. code-block:: python

   from decimal import Decimal

   result = await client.create_refund(
       invoice_id=12345,
       amount=Decimal("50.00"),  # Refund only 50.00
   )

Check Refund Status
-------------------

Get the status of a refund:

.. code-block:: python

   status = await client.get_refund_status(
       invoice_id=12345,
   )
   
   print(f"Refund status: {status}")

Response Format
---------------

Refund operations return a dictionary with response data:

.. code-block:: python

   {
       "Code": "0",  # 0 = success
       "Description": "Refund processed",
       "State": "5",  # Refund state code
       # ... other fields
   }

Refund States
-------------

Common refund state codes:

- ``5`` - Refund processed successfully
- Other codes indicate different states (check RoboKassa documentation)

Error Handling
--------------

Handle errors when processing refunds:

.. code-block:: python

   from aiorobokassa import APIError

   try:
       result = await client.create_refund(
           invoice_id=12345,
           amount=Decimal("50.00"),
       )
   except APIError as e:
       print(f"Refund failed: {e.status_code} - {e.response}")

Best Practices
--------------

1. **Always verify invoice exists** before creating refund
2. **Check refund status** after creation to confirm processing
3. **Handle partial refunds carefully** - ensure amount doesn't exceed original payment
4. **Log all refund operations** for audit purposes
5. **Update your database** after successful refund

