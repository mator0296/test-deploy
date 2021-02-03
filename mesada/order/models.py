from django.db import models
from djmoney.models.fields import MoneyField

from ..account.models import Recipient, User
from ..checkout.models import Checkout
from ..galactus.models import GalactusTransaction
from ..payment import PaymentStatus
from ..payment.models import Payment, PaymentMethods
from ..transfer.models import CircleTransfer
from ..withdrawal.models import BitsoSpeiWithdrawal, BitsoWithdrawalStatus
from . import EventType, OrderStage, OrderStatus


class Order(models.Model):
    checkout = models.ForeignKey(Checkout, on_delete=models.SET_NULL, null=True)
    status = models.CharField(
        max_length=10, choices=OrderStatus.choices, default=OrderStatus.PENDING
    )
    amount = MoneyField(max_digits=19, decimal_places=4, default_currency="USD")
    fees = MoneyField(max_digits=19, decimal_places=4, default_currency="USD")
    total_amount = MoneyField(max_digits=19, decimal_places=4, default_currency="USD")
    recipient_amount = MoneyField(
        max_digits=19, decimal_places=4, default_currency="USD"
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    recipient = models.ForeignKey(Recipient, on_delete=models.SET_NULL, null=True)
    payment_method = models.ForeignKey(
        PaymentMethods, on_delete=models.SET_NULL, null=True
    )
    galactus_transaction = models.ForeignKey(
        GalactusTransaction, on_delete=models.SET_NULL, null=True
    )
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True)
    circle_transfer = models.ForeignKey(
        CircleTransfer, on_delete=models.SET_NULL, null=True
    )
    withdrawal = models.ForeignKey(
        BitsoSpeiWithdrawal, on_delete=models.SET_NULL, null=True
    )

    @property
    def operational_status(self):
        if self.payment.status == PaymentStatus.FAILED:
            return OrderStatus.ERROR
        elif (
            self.payment.status == PaymentStatus.PENDING
            or self.withdrawal.status == BitsoWithdrawalStatus.PENDING
        ):
            return OrderStatus.PENDING
        elif (
            self.payment.status == PaymentStatus.CONFIRMED
            or self.payment.status == PaymentStatus.PAID
            and self.withdrawal.status == BitsoWithdrawalStatus.COMPLETE
        ):
            return OrderStatus.SUCCESS


class OrderEvent(models.Model):
    order_stage = models.CharField(max_length=20, choices=OrderStage.choices)
    event_type = models.CharField(max_length=10, choices=EventType.choices)
    details = models.JSONField(null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
