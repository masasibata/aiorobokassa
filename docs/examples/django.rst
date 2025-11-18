Django Integration
==================

Complete example of integrating aiorobokassa with Django.

Views
-----

.. code-block:: python

   from django.http import HttpResponse, JsonResponse
   from django.views.decorators.csrf import csrf_exempt
   from django.views.decorators.http import require_http_methods
   from decimal import Decimal
   from aiorobokassa import RoboKassaClient, SignatureError
   import asyncio

   @csrf_exempt
   @require_http_methods(["POST"])
   async def create_payment(request):
       """Create payment URL."""
       order_id = request.POST.get("order_id")
       amount = Decimal(request.POST.get("amount"))
       
       client = RoboKassaClient(
           merchant_login="your_merchant_login",
           password1="password1",
           password2="password2",
       )
       
       try:
           payment_url = client.create_payment_url(
               out_sum=amount,
               description=f"Payment for order #{order_id}",
               inv_id=int(order_id),
           )
           return JsonResponse({"payment_url": payment_url})
       finally:
           await client.close()

   @csrf_exempt
   @require_http_methods(["POST", "GET"])
   async def handle_result_url(request):
       """Handle ResultURL notification."""
       params = request.GET.dict() if request.method == "GET" else request.POST.dict()
       
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
           order_id = parsed["inv_id"]
           # ... update database
           
           return HttpResponse(f"OK{order_id}")
       except SignatureError:
           return HttpResponse("ERROR")
       finally:
           await client.close()

URL Configuration
-----------------

.. code-block:: python

   # urls.py
   from django.urls import path
   from . import views

   urlpatterns = [
       path("payment/create/", views.create_payment, name="create_payment"),
       path("payment/result/", views.handle_result_url, name="result_url"),
   ]

