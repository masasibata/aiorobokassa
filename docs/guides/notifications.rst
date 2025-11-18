Handling Notifications
======================

RoboKassa sends notifications to your server in two scenarios:

1. **ResultURL** - Server-to-server notification after payment
2. **SuccessURL** - User redirect after successful payment

ResultURL (Server Notification)
--------------------------------

ResultURL is called by RoboKassa server after payment processing. You must verify the signature and return ``OK{invoice_id}``.

Example with FastAPI:

.. code-block:: python

   from fastapi import FastAPI, Request
   from aiorobokassa import RoboKassaClient, SignatureError

   app = FastAPI()
   client = RoboKassaClient(
       merchant_login="your_merchant_login",
       password1="password1",
       password2="password2",
   )

   @app.post("/payment/result")
   async def handle_result_url(request: Request):
       params = dict(request.query_params)
       parsed = client.parse_result_url_params(params)
       
       try:
           client.verify_result_url(
               out_sum=parsed["out_sum"],
               inv_id=parsed["inv_id"],
               signature_value=parsed["signature_value"],
               shp_params=parsed.get("shp_params"),
           )
           
           # Payment is valid, update your database
           invoice_id = parsed["inv_id"]
           amount = parsed["out_sum"]
           # ... update order status in database
           
           return f"OK{invoice_id}"
       except SignatureError:
           return "ERROR"

Example with Django:

.. code-block:: python

   from django.http import HttpResponse
   from aiorobokassa import RoboKassaClient, SignatureError

   def handle_result_url(request):
       client = RoboKassaClient(
           merchant_login="your_merchant_login",
           password1="password1",
           password2="password2",
       )
       
       params = client.parse_result_url_params(request.GET.dict())
       
       try:
           client.verify_result_url(
               out_sum=params["out_sum"],
               inv_id=params["inv_id"],
               signature_value=params["signature_value"],
               shp_params=params.get("shp_params"),
           )
           # Update database
           return HttpResponse(f"OK{params['inv_id']}")
       except SignatureError:
           return HttpResponse("ERROR")

SuccessURL (User Redirect)
---------------------------

SuccessURL is where users are redirected after successful payment. Verify signature before showing success page:

.. code-block:: python

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
           # Show success page
           return "Payment successful!"
       except SignatureError:
           return "Payment verification failed"

Important Notes
---------------

1. **Always verify signatures** - Never trust data without signature verification
2. **Return correct response** - ResultURL must return ``OK{invoice_id}`` or ``ERROR``
3. **Handle errors gracefully** - Catch exceptions and return appropriate responses
4. **Idempotency** - ResultURL may be called multiple times, handle this in your code
5. **Use password2** - ResultURL verification uses password2
6. **Use password1** - SuccessURL verification uses password1

Parameter Parsing
-----------------

The library provides helper methods to parse notification parameters:

.. code-block:: python

   # Parse ResultURL parameters
   params = client.parse_result_url_params(request_params)
   # Returns: {
   #     "out_sum": "100.00",
   #     "inv_id": "12345",
   #     "signature_value": "ABC123...",
   #     "shp_params": {"user_id": "123", "order_id": "456"}
   # }

   # Parse SuccessURL parameters
   params = client.parse_success_url_params(request_params)
   # Same structure as above

Custom Parameters (Shp_*)
-------------------------

Custom parameters passed in payment URL are available in notifications. **Important:** These parameters are included in signature calculation, so you must pass them when verifying signatures.

When creating payment URL:

.. code-block:: python

   # When creating payment URL
   url = client.create_payment_url(
       out_sum=Decimal("100.00"),
       description="Payment",
       user_parameters={"user_id": "123", "order_id": "456"},
   )

In notification handler:

.. code-block:: python

   # In notification handler
   params = client.parse_result_url_params(request_params)
   
   # Extract shp_params
   user_id = params["shp_params"]["user_id"]  # "123"
   order_id = params["shp_params"]["order_id"]  # "456"
   
   # IMPORTANT: Pass shp_params when verifying signature
   client.verify_result_url(
       out_sum=params["out_sum"],
       inv_id=params["inv_id"],
       signature_value=params["signature_value"],
       shp_params=params.get("shp_params"),  # Required if shp_params were used
   )

**Note:** If you used ``user_parameters`` when creating the payment URL, you **must** pass ``shp_params`` to signature verification methods. Otherwise, signature verification will fail.

