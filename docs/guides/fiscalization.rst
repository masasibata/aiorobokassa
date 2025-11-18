Фискализация (Receipt)
======================

Для клиентов Robokassa, использующих Облачное решение, Кассовое решение или решение Робочеки, необходимо передавать параметр ``Receipt`` для фискализации платежей в соответствии с требованиями ФЗ-54.

Важно
-----

- Отсутствие номенклатуры в чеке является нарушением ФЗ-54
- Параметр ``Receipt`` должен быть включен в расчет контрольной подписи
- Рекомендуется использовать метод POST для передачи запросов с Receipt
- Для решений Робочеки и Облачное в чеке не может быть более ста товарных позиций

Базовый пример с Pydantic моделями
-----------------------------------

Рекомендуемый способ - использование Pydantic моделей с enums:

.. code-block:: python

   from decimal import Decimal
   from aiorobokassa import (
       RoboKassaClient,
       Receipt,
       ReceiptItem,
       TaxRate,
       TaxSystem,
       PaymentMethod,
       PaymentObject,
   )

   async with RoboKassaClient(
       merchant_login="your_merchant_login",
       password1="password1",
       password2="password2",
   ) as client:
       # Создаем позицию чека
       item = ReceiptItem(
           name="Название товара 1",
           quantity=1,
           sum=Decimal("100.00"),
           tax=TaxRate.VAT10,
           payment_method=PaymentMethod.FULL_PAYMENT,
           payment_object=PaymentObject.COMMODITY,
       )
       
       # Создаем чек
       receipt = Receipt(
           items=[item],
           sno=TaxSystem.OSN,
       )
       
       url = await client.create_payment_url(
           out_sum=Decimal("100.00"),
           description="Payment for goods",
           receipt=receipt,  # Передаем Receipt модель
       )

Базовый пример с dict
---------------------

Также можно передать receipt как словарь:

.. code-block:: python

   from decimal import Decimal
   from aiorobokassa import RoboKassaClient

   async with RoboKassaClient(
       merchant_login="your_merchant_login",
       password1="password1",
       password2="password2",
   ) as client:
       receipt_data = {
           "sno": "osn",
           "items": [
               {
                   "name": "Название товара 1",
                   "quantity": 1,
                   "sum": 100,
                   "payment_method": "full_payment",
                   "payment_object": "commodity",
                   "tax": "vat10",
               }
           ],
       }
       
       url = await client.create_payment_url(
           out_sum=Decimal("100.00"),
           description="Payment for goods",
           receipt=receipt_data,  # Передаем как dict
       )

Передача как JSON строка
------------------------

Также можно передать receipt как JSON строку:

.. code-block:: python

   receipt_json = '{"sno":"osn","items":[{"name":"Товар","quantity":1,"sum":100,"tax":"vat10"}]}'
   
   url = await client.create_payment_url(
       out_sum=Decimal("100.00"),
       description="Payment",
       receipt=receipt_json,  # Передаем как JSON строку
   )

Параметры Receipt
-----------------

sno (Система налогообложения)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Необязательное поле, если у организации имеется только один тип налогообложения.

Возможные значения:

- ``osn`` - Общая СН
- ``usn_income`` - Упрощенная СН (доходы)
- ``usn_income_outcome`` - Упрощенная СН (доходы минус расходы)
- ``esn`` - Единый сельскохозяйственный налог
- ``patent`` - Патентная СН

items (Массив товаров)
~~~~~~~~~~~~~~~~~~~~~~~

Обязательный массив данных о позициях чека.

Обязательные поля для каждого товара:

- ``name`` - Наименование товара (максимум 128 символов)
- ``quantity`` - Количество товаров
- ``sum`` - Полная сумма в рублях за все количество товара
- ``tax`` - Налоговая ставка (см. ниже)

Опциональные поля:

- ``cost`` - Цена за единицу товара (можно передать вместо sum)
- ``payment_method`` - Признак способа расчёта
- ``payment_object`` - Признак предмета расчёта
- ``nomenclature_code`` - Код маркировки товара

Налоговые ставки (tax)
~~~~~~~~~~~~~~~~~~~~~~

Обязательное поле для каждого товара:

- ``none`` - Без НДС
- ``vat0`` - НДС по ставке 0%
- ``vat10`` - НДС по ставке 10%
- ``vat110`` - НДС по расчетной ставке 10/110
- ``vat20`` - НДС по ставке 20%
- ``vat120`` - НДС по расчетной ставке 20/120
- ``vat5`` - НДС по ставке 5%
- ``vat7`` - НДС по ставке 7%
- ``vat105`` - НДС по расчетной ставке 5/105
- ``vat107`` - НДС по расчетной ставке 7/107

Признаки способа расчёта (payment_method)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``full_prepayment`` - Предоплата 100%
- ``prepayment`` - Предоплата
- ``advance`` - Аванс
- ``full_payment`` - Полный расчёт
- ``partial_payment`` - Частичный расчёт и кредит
- ``credit`` - Передача в кредит
- ``credit_payment`` - Оплата кредита

Признаки предмета расчёта (payment_object)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``commodity`` - Товар
- ``excise`` - Подакцизный товар
- ``job`` - Работа
- ``service`` - Услуга
- ``gambling_bet`` - Ставка азартной игры
- ``gambling_prize`` - Выигрыш азартной игры
- ``lottery`` - Лотерейный билет
- ``lottery_prize`` - Выигрыш лотереи
- ``intellectual_activity`` - Предоставление результатов интеллектуальной деятельности
- ``payment`` - Платеж
- ``agent_commission`` - Агентское вознаграждение
- ``composite`` - Составной предмет расчета
- ``resort_fee`` - Курортный сбор
- ``another`` - Иной предмет расчета
- ``property_right`` - Имущественное право
- ``non-operating_gain`` - Внереализационный доход
- ``insurance_premium`` - Страховые взносы
- ``sales_tax`` - Торговый сбор
- ``tovar_mark`` - Товар, подлежащий маркировке

Примеры
-------

Чек с несколькими товарами (с Pydantic моделями)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from aiorobokassa import Receipt, ReceiptItem, TaxRate, TaxSystem, PaymentMethod, PaymentObject
   from decimal import Decimal

   items = [
       ReceiptItem(
           name="Товар 1",
           quantity=1,
           sum=Decimal("100.00"),
           tax=TaxRate.VAT10,
           payment_method=PaymentMethod.FULL_PAYMENT,
           payment_object=PaymentObject.COMMODITY,
       ),
       ReceiptItem(
           name="Товар 2",
           quantity=2,
           cost=Decimal("100.00"),  # Цена за единицу (sum будет вычислена автоматически)
           tax=TaxRate.VAT20,
           payment_method=PaymentMethod.FULL_PAYMENT,
           payment_object=PaymentObject.COMMODITY,
       ),
   ]
   
   receipt = Receipt(items=items, sno=TaxSystem.OSN)

Чек с маркированным товаром
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from aiorobokassa import Receipt, ReceiptItem, TaxRate, TaxSystem

   item = ReceiptItem(
       name="Маркированный товар",
       quantity=1,
       sum=Decimal("100.00"),
       tax=TaxRate.VAT10,
       nomenclature_code="04620034587217",  # Код маркировки
   )
   
   receipt = Receipt(items=[item], sno=TaxSystem.OSN)

Чек с услугами
~~~~~~~~~~~~~~

.. code-block:: python

   from aiorobokassa import Receipt, ReceiptItem, TaxRate, TaxSystem, PaymentMethod, PaymentObject

   item = ReceiptItem(
       name="Консультация",
       quantity=1,
       sum=Decimal("500.00"),
       tax=TaxRate.VAT20,
       payment_method=PaymentMethod.FULL_PAYMENT,
       payment_object=PaymentObject.SERVICE,
   )
   
   receipt = Receipt(items=[item], sno=TaxSystem.USN_INCOME)

Правила формирования чека
--------------------------

1. В чеке должна быть хотя бы одна позиция
2. Во всех позициях должно быть указано наименование
3. Наименование не должно содержать спецсимволов (кроме русского и английского)
4. Наименование не должно превышать 128 символов
5. Цена и сумма позиции не должны быть отрицательными
6. Общая сумма всех позиций должна быть больше нуля
7. Сумма всех позиций в чеке должна быть равна сумме операции (out_sum)
8. Все телефоны должны быть в формате "+Ц" (максимум 18 цифр)

Важные замечания
----------------

1. **Подпись**: Receipt автоматически включается в расчет подписи
2. **URL-кодирование**: Receipt автоматически URL-кодируется перед отправкой
3. **Валидация**: Библиотека проверяет, что receipt является валидным JSON
4. **POST метод**: Рекомендуется использовать POST для запросов с Receipt из-за возможной большой длины

Пример полного использования
-----------------------------

.. code-block:: python

   import asyncio
   from decimal import Decimal
   from aiorobokassa import RoboKassaClient

   async def main():
       async with RoboKassaClient(
           merchant_login="your_merchant_login",
           password1="password1",
           password2="password2",
       ) as client:
           receipt_data = {
               "sno": "osn",
               "items": [
                   {
                       "name": "Товар 1",
                       "quantity": 2,
                       "sum": 200,
                       "cost": 100,
                       "payment_method": "full_payment",
                       "payment_object": "commodity",
                       "tax": "vat10",
                   },
                   {
                       "name": "Услуга",
                       "quantity": 1,
                       "sum": 300,
                       "payment_method": "full_payment",
                       "payment_object": "service",
                       "tax": "vat20",
                   },
               ],
           }
           
           url = await client.create_payment_url(
               out_sum=Decimal("500.00"),  # Сумма должна совпадать с суммой позиций
               description="Payment for order #123",
               inv_id=123,
               email="customer@example.com",
               receipt=receipt_data,
           )
           
           print(f"Payment URL: {url}")

   asyncio.run(main())

