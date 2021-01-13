from django.db import models
from djmoney.models.fields import MoneyField

from ..account.models import User
# Create your models here.


class BitsoWithdrawalStatus(models.TextChoices):
    "Status of the withdrawal in Bitso"

    PENDING = "pending"
    COMPLETE = "complete"


class BitsoSpeiWithdrawal(models.Model):
    wid = models.CharField(max_length=256, unique=True)
    status = models.CharField(max_length=8, choices=BitsoWithdrawalStatus.choices)
    created_at = models.DateField()
    currency = models.CharField(max_length=10)
    method = models.CharField(max_length=10)
    amount = MoneyField(max_digits=19, decimal_places=4, default_currency="BTC")
    details = models.JSONField(null=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bitso_spei_withdrawal"
    )
