from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django_countries.fields import CountryField
from django_enumfield import enum
from djmoney.models.fields import MoneyField

from ..account.models import User
from . import (
    PaymentErrorCode,
    PaymentMethodStatus,
    PaymentMethodTypes,
    PaymentStatus
)


class VerificationAvsEnum(enum.Enum):
    NOT_REQUESTED = 0
    PENDING = 1
    A = 2
    B = 3
    C = 4
    D = 5
    E = 6
    F = 7
    G = 8
    I = 9  # noqa: E741
    K = 10
    L = 11
    M = 12
    N = 13
    O = 14  # noqa: E741
    P = 15
    R = 16
    S = 17
    U = 18
    W = 19
    X = 20
    Y = 21
    Z = 22


class VerificationCvvEnum(enum.Enum):
    NOT_REQUESTED = 0
    PASS = 1
    FAIL = 2
    UNAVAILABLE = 3
    PENDING = 4


class PaymentMethods(models.Model):

    type = models.CharField(
        max_length=50,
        choices=PaymentMethodTypes.choices,
        default=PaymentMethodTypes.CARD,
    )
    exp_month = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)], null=True, blank=True
    )
    exp_year = models.PositiveIntegerField(
        validators=[MaxValueValidator(2050)], null=True, blank=True
    )
    network = models.CharField(max_length=50, blank=True)
    last_digits = models.CharField(max_length=4, blank=True)
    fingerprint = models.CharField(max_length=36, blank=True)
    verification_cvv = enum.EnumField(
        VerificationCvvEnum, default=VerificationCvvEnum.NOT_REQUESTED
    )
    verification_avs = enum.EnumField(
        VerificationAvsEnum, default=VerificationAvsEnum.NOT_REQUESTED
    )
    phonenumber = models.CharField(max_length=15, blank=True)
    email = models.EmailField(max_length=256, blank=True)
    name = models.CharField(max_length=256, blank=True)
    address_line_1 = models.CharField(max_length=256, blank=True)
    address_line_2 = models.CharField(max_length=256, blank=True)
    postal_code = models.CharField(max_length=6, blank=True)
    city = models.CharField(max_length=256, blank=True)
    district = models.CharField(max_length=256, blank=True)
    country_code = CountryField()
    created = models.DateTimeField(default=timezone.now, editable=False)
    updated = models.DateTimeField(auto_now=True)
    payment_method_token = models.CharField(max_length=256, blank=True)
    processor_token = models.CharField(max_length=256, blank=True)
    status = models.CharField(
        max_length=50,
        choices=PaymentMethodStatus.choices,
        default=PaymentMethodStatus.PENDING,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="payment_methods",
        null=True,
        blank=True,
    )

    @property
    def __str__(self):
        if self.last_digits:
            return f"{self.type} {self.user} {self.last_digits}"
        return f"{self.type} {self.user}"

    __hash__ = models.Model.__hash__


class Payment(models.Model):

    type = models.CharField(max_length=256)
    merchant_id = models.CharField(max_length=256)
    merchant_wallet_id = models.CharField(max_length=256)
    amount = MoneyField(max_digits=19, decimal_places=4, default_currency="USD")
    source = models.JSONField()
    description = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=9, choices=PaymentStatus.choices, default=PaymentStatus.PENDING
    )
    verification = models.JSONField(null=True)
    cancel = models.JSONField(null=True)
    refunds = models.JSONField(null=True)
    fees = models.JSONField(null=True)
    tracking_ref = models.CharField(max_length=256, null=True)
    error_code = models.CharField(
        max_length=256, null=True, choices=PaymentErrorCode.choices
    )
    metadata = models.JSONField()
    risk_evaluation = models.JSONField(null=True)
    payment_token = models.CharField(
        max_length=256, blank=True
    )  # Unique circle system generated identifier for the payment item.
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payment")
