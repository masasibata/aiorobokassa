Invoice Management
==================

This guide explains how to create and manage invoices using the Invoice API.

Creating Invoices
------------------

Create an invoice via Invoice API (JWT-based):

.. code-block:: python

   from decimal import Decimal
   from aiorobokassa import RoboKassaClient, InvoiceType
   from aiorobokassa.models.requests import InvoiceItem
   from aiorobokassa.enums import TaxRate, PaymentMethod, PaymentObject

   async with RoboKassaClient(
       merchant_login="your_merchant_login",
       password1="password1",
       password2="password2",
   ) as client:
       result = await client.create_invoice(
           out_sum=Decimal("100.00"),
           description="Invoice for services",
           invoice_type=InvoiceType.ONE_TIME,
           inv_id=12345,
           culture="ru",
       )
       
       print(f"Invoice created: {result}")
       print(f"Invoice URL: {result['url']}")

Invoice with Fiscalization
---------------------------

Create invoice with fiscalization items:

.. code-block:: python

   invoice_items = [
       InvoiceItem(
           name="Service 1",
           quantity=1,
           cost=50.0,
           tax=TaxRate.VAT20,
           payment_method=PaymentMethod.FULL_PAYMENT,
           payment_object=PaymentObject.SERVICE,
       ),
       InvoiceItem(
           name="Service 2",
           quantity=2,
           cost=25.0,
           tax=TaxRate.VAT20,
           payment_method=PaymentMethod.FULL_PAYMENT,
           payment_object=PaymentObject.SERVICE,
       ),
   ]
   
   result = await client.create_invoice(
       out_sum=Decimal("100.00"),
       description="Invoice for services",
       invoice_items=invoice_items,
   )

Invoice with Custom Parameters
------------------------------

Add custom parameters to invoice:

.. code-block:: python

   result = await client.create_invoice(
       out_sum=Decimal("100.00"),
       description="Invoice for services",
       user_fields={
           "contract_id": "123",
           "project_id": "456",
       },
   )

Invoice with Redirect URLs
---------------------------

Set success and fail redirect URLs:

.. code-block:: python

   result = await client.create_invoice(
       out_sum=Decimal("100.00"),
       description="Invoice for services",
       success_url="https://example.com/success",
       success_url_method="GET",
       fail_url="https://example.com/fail",
       fail_url_method="POST",
   )

Response Format
---------------

The ``create_invoice`` method returns a dictionary with invoice information:

.. code-block:: python

   {
       "id": "invoice-id-123",  # Invoice identifier
       "url": "https://auth.robokassa.ru/merchant/Invoice/...",  # Payment URL
       "inv_id": 12345,  # Invoice ID (if specified)
       "encoded_id": "invoice-id-123",  # Encoded invoice ID
   }

Deactivating Invoices
---------------------

Deactivate an invoice:

.. code-block:: python

   # By invoice ID
   await client.deactivate_invoice(inv_id=12345)
   
   # By invoice identifier
   await client.deactivate_invoice(invoice_id="invoice-id-123")
   
   # By encoded ID (from URL)
   await client.deactivate_invoice(encoded_id="invoice-id-123")

Getting Invoice List
---------------------

Get list of invoices with filtering:

.. code-block:: python

   from datetime import datetime

   result = await client.get_invoice_information_list(
       current_page=1,
       page_size=10,
       invoice_statuses=["paid", "notpaid"],
       invoice_types=["onetime"],
       keywords="services",
       date_from="2025-01-01T00:00:00+00:00",
       date_to="2025-12-31T23:59:59+00:00",
       is_ascending=True,
       sum_from=10.0,
       sum_to=1000.0,
   )

Error Handling
--------------

Handle errors when creating invoices:

.. code-block:: python

   from aiorobokassa import APIError

   try:
       result = await client.create_invoice(
           out_sum=Decimal("100.00"),
           description="Invoice",
       )
   except APIError as e:
       print(f"API error: {e.status_code} - {e.response}")
