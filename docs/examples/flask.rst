Flask Integration
=================

Complete example of integrating aiorobokassa with Flask.

Basic Setup
-----------

.. code-block:: python

   from flask import Flask, request, jsonify, redirect
   from decimal import Decimal
   from aiorobokassa import RoboKassaClient, SignatureError

   app = Flask(__name__)

   @app.route("/payment/create", methods=["POST"])
   async def create_payment():
       """Create payment URL."""
       data = request.json
       order_id = data["order_id"]
       amount = Decimal(data["amount"])
       
       client = RoboKassaClient(
           merchant_login="your_merchant_login",
           password1="password1",
           password2="password2",
       )
       
       try:
           payment_url = client.create_payment_url(
               out_sum=amount,
               description=f"Payment for order #{order_id}",
               inv_id=order_id,
           )
           return jsonify({"payment_url": payment_url})
       finally:
           await client.close()

   @app.route("/payment/result", methods=["POST", "GET"])
   async def handle_result_url():
       """Handle ResultURL notification."""
       params = request.args.to_dict() if request.method == "GET" else request.form.to_dict()
       
       client = RoboKassaClient(
           merchant_login="your_merchant_login",
           password1="password1",
           password2="password2",
       )
       
       try:
           parsed = client.parse_result_url_params(params)
           
           client.verify_result_url(
               out_sum=parsed["out_sum"],
               inv_id=parsed["inv_id"],
               signature_value=parsed["signature_value"],
               shp_params=parsed.get("shp_params"),
           )
           
           # Update order status
           return f"OK{parsed['inv_id']}"
       except SignatureError:
           return "ERROR"
       finally:
           await client.close()

