from django.db import models
from djmoney.models.fields import MoneyField

from ..account.models import User


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending"
        CONFIRMED = "confirmed"
        PAID = "paid"
        FAILED = "failed"

    class ErrorCode(models.TextChoices):
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

    type = models.CharField(max_length=256)
    merchant_id = models.CharField(max_length=256, unique=True)
    merchant_wallet_id = models.CharField(max_length=256, unique=True)
    amount = MoneyField(max_digits=19, decimal_places=4, default_currency="USD")
    source = models.JSONField()
    description = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=9, choices=Status.choices, default=Status.PENDING
    )
    verification = models.JSONField()
    cancel = models.JSONField()
    refunds = models.JSONField()
    fees = models.JSONField()
    tracking_ref = models.CharField(max_length=256, null=True)
    error_code = models.CharField(max_length=256, null=True, choices=ErrorCode.choices)
    metadata = models.JSONField()
    risk_evaluation = models.JSONField()
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payment")
