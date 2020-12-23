from django.db import models
from djmoney.models.fields import MoneyField

from ..account.models import User
from . import PaymentErrorCode, PaymentStatus


class Payment(models.Model):

    type = models.CharField(max_length=256)
    merchant_id = models.CharField(max_length=256, unique=True)
    merchant_wallet_id = models.CharField(max_length=256, unique=True)
    amount = MoneyField(max_digits=19, decimal_places=4, default_currency="USD")
    source = models.JSONField()
    description = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=9, choices=PaymentStatus.choices, default=PaymentStatus.PENDING
    )
    verification = models.JSONField()
    cancel = models.JSONField()
    refunds = models.JSONField()
    fees = models.JSONField()
    tracking_ref = models.CharField(max_length=256, null=True)
    error_code = models.CharField(
        max_length=256, null=True, choices=PaymentErrorCode.choices
    )
    metadata = models.JSONField()
    risk_evaluation = models.JSONField()
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payment")
