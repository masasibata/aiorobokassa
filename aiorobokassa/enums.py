"""Enums for RoboKassa API."""

from enum import Enum


class SignatureAlgorithm(str, Enum):
    """Supported signature algorithms."""

    MD5 = "MD5"
    SHA256 = "SHA256"
    SHA512 = "SHA512"

    @classmethod
    def from_string(cls, value: str) -> "SignatureAlgorithm":
        """Convert string to enum, case-insensitive."""
        value_upper = value.upper()
        for alg in cls:
            if alg.value == value_upper:
                return alg
        raise ValueError(
            f"Unsupported algorithm: {value}. Supported: {', '.join(a.value for a in cls)}"
        )


class Culture(str, Enum):
    """Supported languages."""

    RU = "ru"
    EN = "en"


class TaxSystem(str, Enum):
    """Tax system (sno) for fiscalization."""

    OSN = "osn"  # Общая СН
    USN_INCOME = "usn_income"  # Упрощенная СН (доходы)
    USN_INCOME_OUTCOME = "usn_income_outcome"  # Упрощенная СН (доходы минус расходы)
    ESN = "esn"  # Единый сельскохозяйственный налог
    PATENT = "patent"  # Патентная СН


class TaxRate(str, Enum):
    """Tax rate (tax) for receipt items."""

    NONE = "none"  # Без НДС
    VAT0 = "vat0"  # НДС по ставке 0%
    VAT10 = "vat10"  # НДС по ставке 10%
    VAT110 = "vat110"  # НДС по расчетной ставке 10/110
    VAT20 = "vat20"  # НДС по ставке 20%
    VAT120 = "vat120"  # НДС по расчетной ставке 20/120
    VAT5 = "vat5"  # НДС по ставке 5%
    VAT7 = "vat7"  # НДС по ставке 7%
    VAT105 = "vat105"  # НДС по расчетной ставке 5/105
    VAT107 = "vat107"  # НДС по расчетной ставке 7/107


class PaymentMethod(str, Enum):
    """Payment method (payment_method) for receipt items."""

    FULL_PREPAYMENT = "full_prepayment"  # Предоплата 100%
    PREPAYMENT = "prepayment"  # Предоплата
    ADVANCE = "advance"  # Аванс
    FULL_PAYMENT = "full_payment"  # Полный расчёт
    PARTIAL_PAYMENT = "partial_payment"  # Частичный расчёт и кредит
    CREDIT = "credit"  # Передача в кредит
    CREDIT_PAYMENT = "credit_payment"  # Оплата кредита


class PaymentObject(str, Enum):
    """Payment object (payment_object) for receipt items."""

    COMMODITY = "commodity"  # Товар
    EXCISE = "excise"  # Подакцизный товар
    JOB = "job"  # Работа
    SERVICE = "service"  # Услуга
    GAMBLING_BET = "gambling_bet"  # Ставка азартной игры
    GAMBLING_PRIZE = "gambling_prize"  # Выигрыш азартной игры
    LOTTERY = "lottery"  # Лотерейный билет
    LOTTERY_PRIZE = "lottery_prize"  # Выигрыш лотереи
    INTELLECTUAL_ACTIVITY = (
        "intellectual_activity"  # Предоставление результатов интеллектуальной деятельности
    )
    PAYMENT = "payment"  # Платеж
    AGENT_COMMISSION = "agent_commission"  # Агентское вознаграждение
    COMPOSITE = "composite"  # Составной предмет расчета
    RESORT_FEE = "resort_fee"  # Курортный сбор
    ANOTHER = "another"  # Иной предмет расчета
    PROPERTY_RIGHT = "property_right"  # Имущественное право
    NON_OPERATING_GAIN = "non-operating_gain"  # Внереализационный доход
    INSURANCE_PREMIUM = "insurance_premium"  # Страховые взносы
    SALES_TAX = "sales_tax"  # Торговый сбор
    TOVAR_MARK = "tovar_mark"  # Товар, подлежащий маркировке
