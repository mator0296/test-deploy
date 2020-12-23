from django.db import models
from django_countries.fields import CountryField

from ..account.models import User


class paymentMethods(models.Model):

    type = models.CharField(max_length=50)
    exp_month = models.PositiveIntegerField(
        min_value=1, max_value=12, null=True, blank=True
    )
    exp_year = models.PositiveIntegerField(
        min_value=2000, max_value=2050, null=True, blank=True
    )
    network = models.CharField(max_length=50, blank=True)
    last_digits = models.CharField(max_length=4, blank=True)
    fingerprint = models.CharField(max_length=36, blank=True)
    verification_cvv = models.CharField(max_length=50, blank=True)
    verification_avs = models.CharField(max_length=50, blank=True)
    phonenumber = models.CharField(max_length=15)
    email = models.EmailField(max_length=256)
    name = models.CharField(max_length=256)
    address_line_1 = models.CharField(max_length=256, blank=True)
    address_line_2 = models.CharField(max_length=256, blank=True)
    postal_code = models.CharField(max_length=6, blank=True)
    city = models.CharField(max_length=256, blank=True)
    district = models.CharField(max_length=256, blank=True)
    country_code = CountryField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="payment_methods"
    )
