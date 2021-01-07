from django.db import models

from .circle.circle import create_card, request_encryption_key
from .plaid.plaid import create_link_token

class PaymentStatus(models.TextChoices):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PAID = "paid"
    FAILED = "failed"


class PaymentErrorCode(models.TextChoices):
    FAILED = "payment_failed"
    FRAUD = "payment_fraud_detected"
    DENIED = "payment_denied"
    NOT_SUPPORTED = "payment_not_supported_by_issuer"
    NOT_FUNDED = "payment_not_funded"
    UNPROCESSABLE = "payment_unprocessable"
    STOPPED = "payment_stopped_by_issuer"
    CANCELED = "payment_canceled"
    RETURNED = "payment_returned"
    CARD_FAILED = "card_failed"
    CARD_INVALID = "card_invalid"
    CARD_ADDRESS_MISMATCH = "card_address_mismatch"
    CARD_ZIP_MISMATCH = "card_zip_mismatch"
    CARD_CVV_INVALID = "card_cvv_invalid"
    CARD_EXPIRED = "card_expired"
    CARD_LIMIT_VIOLATED = "card_limit_violated"
    CARD_NOT_HONORED = "card_not_honored"
    CARD_CVV_REQUIRED = "card_cvv_required"
    CREDIT_CARD_NOT_ALLOWED = "credit_card_not_allowed"
    CARD_ACCOUNT_INELIGIBLE = "card_account_ineligible"
