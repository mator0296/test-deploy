from django.db import models
from djmoney.models.fields import MoneyField

from ..account.models import Recipient, User

from mesada.payment import PaymentMethodStatus

# Create your models here.


class Checkout(models.Model):
    checkout_token = models.CharField(max_length=256, blank=True)
    amount = MoneyField(max_digits=19, decimal_places=4, default_currency="USD")
    fees = MoneyField(max_digits=19, decimal_places=4, default_currency="USD")
    total_amount = MoneyField(max_digits=19, decimal_places=4, default_currency="USD")
    recipient_amount = MoneyField(
        max_digits=19, decimal_places=4, default_currency="USD"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="checkout", null=True, blank=True
    )
    recipient = models.ForeignKey(
        Recipient,
        on_delete=models.CASCADE,
        related_name="checkout",
        null=True,
        blank=True,
    )
    payment_method = models.CharField(
        max_length=50,
        choices=PaymentMethodStatus.choices,
        default=PaymentMethodStatus.PENDING,
    )
    status = models.CharField()
    active = models.BooleanField()
