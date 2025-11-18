FastAPI Integration
====================

Complete example of integrating aiorobokassa with FastAPI.

Basic Setup
-----------

.. code-block:: python

   from fastapi import FastAPI, Request
   from fastapi.responses import RedirectResponse
   from decimal import Decimal
   from aiorobokassa import RoboKassaClient, SignatureError

   app = FastAPI()

   # Initialize client (you might want to use dependency injection)
   client = RoboKassaClient(
       merchant_login="your_merchant_login",
       password1="password1",
       password2="password2",
   )

   @app.post("/payment/create")
   async def create_payment(order_id: int, amount: Decimal):
       """Create payment URL for order."""
       payment_url = client.create_payment_url(
           out_sum=amount,
           description=f"Payment for order #{order_id}",
           inv_id=order_id,
           user_parameters={"order_id": str(order_id)},
       )
       return {"payment_url": payment_url}

   @app.post("/payment/result")
   async def handle_result_url(request: Request):
       """Handle ResultURL notification from RoboKassa."""
       params = dict(request.query_params)
       parsed = client.parse_result_url_params(params)
       
       try:
           client.verify_result_url(
               out_sum=parsed["out_sum"],
               inv_id=parsed["inv_id"],
               signature_value=parsed["signature_value"],
               shp_params=parsed.get("shp_params"),
           )
           
           # Update order status in database
           order_id = parsed["inv_id"]
           # ... update database
           
           return f"OK{order_id}"
       except SignatureError:
           return "ERROR"

   @app.get("/payment/success")
   async def handle_success_url(request: Request):
       """Handle SuccessURL redirect."""
       params = dict(request.query_params)
       parsed = client.parse_success_url_params(params)
       
       try:
           client.verify_success_url(
               out_sum=parsed["out_sum"],
               inv_id=parsed["inv_id"],
               signature_value=parsed["signature_value"],
               shp_params=parsed.get("shp_params"),
           )
           return {"status": "success", "invoice_id": parsed["inv_id"]}
       except SignatureError:
           return {"status": "error", "message": "Invalid signature"}

Using Dependency Injection
---------------------------

.. code-block:: python

   from fastapi import Depends
   from aiorobokassa import RoboKassaClient

   def get_client() -> RoboKassaClient:
       return RoboKassaClient(
           merchant_login="your_merchant_login",
           password1="password1",
           password2="password2",
       )

   @app.post("/payment/create")
   async def create_payment(
       order_id: int,
       amount: Decimal,
       client: RoboKassaClient = Depends(get_client),
   ):
       payment_url = client.create_payment_url(
           out_sum=amount,
           description=f"Payment for order #{order_id}",
           inv_id=order_id,
       )
       return {"payment_url": payment_url}

