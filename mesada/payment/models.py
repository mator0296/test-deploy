from django.db import models
from django_countries.fields import CountryField
from django.core.validators import MinValueValidator, MaxValueValidator
from ..account.models import User
from django.utils import timezone
from django_enumfield import enum
from djmoney.models.fields import MoneyField

from . import PaymentErrorCode, PaymentStatus


class verificationAvs(enum.Enum):
    NOT_REQUESTED = 0
    PENDING = 1


class verificationCvv(enum.Enum):
    NOT_REQUESTED = 0
    PASS = 1
    FAIL = 2
    UNAVAILABLE = 3
    PENDING = 4


class paymentMethods(models.Model):

    type = models.CharField(max_length=50, blank=False)
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
        verificationCvv, default=verificationCvv.NOT_REQUESTED
    )
    verification_avs = enum.EnumField(
        verificationAvs, default=verificationAvs.NOT_REQUESTED
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