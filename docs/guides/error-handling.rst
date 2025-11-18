Error Handling
==============

This guide explains how to handle errors and exceptions in aiorobokassa.

Exception Hierarchy
--------------------

All exceptions inherit from :class:`RoboKassaError`:

.. code-block:: text

   RoboKassaError (base exception)
   ├── SignatureError
   ├── APIError
   ├── ValidationError
   ├── ConfigurationError
   │   └── InvalidSignatureAlgorithmError
   └── XMLParseError

Common Exceptions
-----------------

SignatureError
~~~~~~~~~~~~~~

Raised when signature verification fails:

.. code-block:: python

   from aiorobokassa import SignatureError

   try:
       client.verify_result_url(
           out_sum="100.00",
           inv_id="12345",
           signature_value="invalid_signature",
       )
   except SignatureError as e:
       print(f"Signature verification failed: {e}")

APIError
~~~~~~~~

Raised when API request fails:

.. code-block:: python

   from aiorobokassa import APIError

   try:
       result = await client.create_invoice(
           out_sum=Decimal("100.00"),
           description="Invoice",
       )
   except APIError as e:
       print(f"API error: {e.status_code}")
       print(f"Response: {e.response}")

ValidationError
~~~~~~~~~~~~~~~

Raised when data validation fails:

.. code-block:: python

   from aiorobokassa import ValidationError
   from decimal import Decimal

   try:
       url = client.create_payment_url(
           out_sum=Decimal("-100.00"),  # Invalid: negative amount
           description="",  # Invalid: empty description
       )
   except ValidationError as e:
       print(f"Validation error: {e}")

ConfigurationError
~~~~~~~~~~~~~~~~~~

Raised when client configuration is invalid:

.. code-block:: python

   from aiorobokassa import ConfigurationError

   try:
       client = RoboKassaClient(
           merchant_login="",  # Invalid: empty login
           password1="short",  # Invalid: too short
           password2="password2",
       )
   except ConfigurationError as e:
       print(f"Configuration error: {e}")

XMLParseError
~~~~~~~~~~~~~

Raised when XML response cannot be parsed:

.. code-block:: python

   from aiorobokassa import XMLParseError

   try:
       result = await client.create_invoice(
           out_sum=Decimal("100.00"),
           description="Invoice",
       )
   except XMLParseError as e:
       print(f"XML parse error: {e.response}")

Best Practices
--------------

1. **Always catch specific exceptions** - Don't catch generic Exception
2. **Log errors** - Record errors for debugging
3. **Handle gracefully** - Provide user-friendly error messages
4. **Retry logic** - For transient errors, implement retry logic
5. **Validate input** - Validate data before making API calls

Example: Complete Error Handling
---------------------------------

.. code-block:: python

   from aiorobokassa import (
       RoboKassaClient,
       SignatureError,
       APIError,
       ValidationError,
       ConfigurationError,
   )
   from decimal import Decimal
   import logging

   logger = logging.getLogger(__name__)

   async def process_payment(amount: Decimal, description: str):
       try:
           client = RoboKassaClient(
               merchant_login="your_merchant_login",
               password1="password1",
               password2="password2",
           )
       except ConfigurationError as e:
           logger.error(f"Invalid configuration: {e}")
           return None
       
       try:
           url = client.create_payment_url(
               out_sum=amount,
               description=description,
           )
           return url
       except ValidationError as e:
           logger.error(f"Invalid payment data: {e}")
           return None
       except APIError as e:
           logger.error(f"API error: {e.status_code} - {e.response}")
           return None
       finally:
           await client.close()

