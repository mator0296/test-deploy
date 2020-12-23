from django.db import models
from djmoney.models.fields import MoneyField


class Payment(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending"
        CONFIRMED = "confirmed"
        PAID = "paid"
        FAILED = "failed"

    type = models.CharField(max_length=256)
    merchant_id = models.CharField(max_length=256, unique=True)
    merchant_wallet_id = models.CharField(max_length=256, unique=True)
    amount = MoneyField(
        max_digits=19, decimal_places=4, default_currency='USD'
    )
    source = models.JSONField()
    description = models.TextField(blank=True, default="")
    status = models.CharField()
    verification = models.JSONField()
    cancel = models.JSONField()
    refunds = models.JSONField()
    fees = models.JSONField()
    tracking_ref = models.CharField()
    error_code = models.CharField()
    metadata = models.JSONField()
    risk_evaluation = models.JSONField()
    create_date = models.DateTimeField()
    update_date = models.DateTimeField()
