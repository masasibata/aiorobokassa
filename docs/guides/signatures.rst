Signature Algorithms
====================

aiorobokassa supports multiple signature algorithms for secure payment processing.

Supported Algorithms
--------------------

- **MD5** (default) - Fast, widely supported
- **SHA256** - More secure, recommended for new integrations
- **SHA512** - Most secure, best for high-value transactions

Using Different Algorithms
---------------------------

Specify algorithm when creating payment URL:

.. code-block:: python

   from aiorobokassa import RoboKassaClient, SignatureAlgorithm

   async with RoboKassaClient(
       merchant_login="your_merchant_login",
       password1="password1",
       password2="password2",
   ) as client:
       # Use SHA256
       url = await client.create_payment_url(
           out_sum=Decimal("100.00"),
           description="Payment",
           signature_algorithm=SignatureAlgorithm.SHA256,
       )
       
       # Use SHA512
       url = await client.create_payment_url(
           out_sum=Decimal("100.00"),
           description="Payment",
           signature_algorithm=SignatureAlgorithm.SHA512,
       )

Verifying Signatures
--------------------

When verifying notifications, use the same algorithm:

.. code-block:: python

   # Verify ResultURL with SHA256
   client.verify_result_url(
       out_sum="100.00",
       inv_id="12345",
       signature_value="ABC123...",
       signature_algorithm=SignatureAlgorithm.SHA256,
   )

Algorithm Selection
-------------------

Choose algorithm based on your needs:

- **MD5**: Fast, compatible with older systems
- **SHA256**: Good balance of security and performance (recommended)
- **SHA512**: Maximum security for sensitive transactions

Important Notes
---------------

1. **Consistency** - Use the same algorithm for payment URL and verification
2. **Configuration** - Algorithm must be configured in RoboKassa merchant panel
3. **Default** - If not specified, MD5 is used
4. **Case-insensitive** - Algorithm names are case-insensitive

