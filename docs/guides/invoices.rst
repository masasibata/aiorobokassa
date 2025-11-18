Invoice Management
==================

This guide explains how to create and manage invoices using the XML API.

Creating Invoices
------------------

Create an invoice via XML API:

.. code-block:: python

   from decimal import Decimal
   from aiorobokassa import RoboKassaClient

   async with RoboKassaClient(
       merchant_login="your_merchant_login",
       password1="password1",
       password2="password2",
   ) as client:
       result = await client.create_invoice(
           out_sum=Decimal("100.00"),
           description="Invoice for services",
           inv_id=12345,
           email="customer@example.com",
       )
       
       print(f"Invoice created: {result}")

Invoice with Expiration Date
-----------------------------

Set expiration date for invoice:

.. code-block:: python

   from datetime import datetime, timedelta

   expiration = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
   
   result = await client.create_invoice(
       out_sum=Decimal("100.00"),
       description="Invoice for services",
       expiration_date=expiration,
   )

Invoice with Custom Parameters
------------------------------

Add custom parameters to invoice:

.. code-block:: python

   result = await client.create_invoice(
       out_sum=Decimal("100.00"),
       description="Invoice for services",
       user_parameters={
           "contract_id": "123",
           "project_id": "456",
       },
   )

Response Format
---------------

The ``create_invoice`` method returns a dictionary with response data:

.. code-block:: python

   {
       "Code": "0",  # 0 = success
       "Description": "Invoice created successfully",
       "InvoiceID": "12345",
       # ... other fields
   }

Error Handling
--------------

Handle errors when creating invoices:

.. code-block:: python

   from aiorobokassa import APIError, XMLParseError

   try:
       result = await client.create_invoice(
           out_sum=Decimal("100.00"),
           description="Invoice",
       )
   except APIError as e:
       print(f"API error: {e.status_code} - {e.response}")
   except XMLParseError as e:
       print(f"XML parse error: {e.response}")

