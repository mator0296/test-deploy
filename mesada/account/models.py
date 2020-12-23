from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q
from django.forms.models import model_to_dict
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import pgettext_lazy
from django_countries.fields import Country, CountryField
from phonenumber_field.modelfields import PhoneNumber, PhoneNumberField

from .validators import validate_possible_number


class PossiblePhoneNumberField(PhoneNumberField):
    """Less strict field for phone numbers written to database."""

    default_validators = [validate_possible_number]


class Address(models.Model):
    address_name = models.CharField(max_length=256, blank=True, null=True)
    first_name = models.CharField(max_length=256, blank=True)
    last_name = models.CharField(max_length=256, blank=True)
    company_name = models.CharField(max_length=256, blank=True)
    street_address_1 = models.CharField(max_length=256, blank=True)
    street_address_2 = models.CharField(max_length=256, blank=True)
    city = models.CharField(max_length=256, blank=True)
    city_area = models.CharField(max_length=128, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = CountryField()
    country_area = models.CharField(max_length=128, blank=True)
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ("pk",)

    @property
    def full_name(self):
        return "%s %s" % (self.first_name, self.last_name)

    def __str__(self):
        if self.address_name:
            return "%s" % (self.address_name)
        if self.company_name:
            return "%s - %s" % (self.company_name, self.full_name)
        return self.full_name

    def __eq__(self, other):
        try:
            return self.as_data() == other.as_data()
        except Exception:
            return False

    __hash__ = models.Model.__hash__

    def as_data(self):
        """Return the address as a dict suitable for passing as kwargs.

        Result does not contain the primary key or an associated user.
        """
        data = model_to_dict(self, exclude=["id", "user", "address_name", "is_visible"])
        if isinstance(data["country"], Country):
            data["country"] = data["country"].code
        if isinstance(data["phone"], PhoneNumber):
            data["phone"] = data["phone"].as_e164
        return data

    def as_data_with_name(self):
        """Return the address with Address Name as a dict suitable
        for passing as kwargs.

        Result does not contain the primary key or an associated user.
        """
        data = model_to_dict(self, exclude=["id", "user"])
        if isinstance(data["country"], Country):
            data["country"] = data["country"].code
        if isinstance(data["phone"], PhoneNumber):
            data["phone"] = data["phone"].as_e164
        return data

    def get_copy(self):
        """Return a new instance of the same address."""
        return Address.objects.create(**self.as_data())

    def delete(self, user=None):
        self.is_visible = False
        self.save(update_fields=["is_visible"])
        if user:
            update_fields = []
            if user.default_shipping_address == self:
                user.default_shipping_address = None
                update_fields.append("default_shipping_address")
            if user.default_billing_address == self:
                user.default_billing_address = None
                update_fields.append("default_billing_address")
            user.save(update_fields=update_fields)

    def clean(self):
        """
        Raise exception if one of the
        two values (lat and long) are
        None individually, i.e, both have
        to be None or both are not None.
        """
        if (self.latitude is None) != (self.longitude is None):
            raise ValidationError(
                pgettext_lazy(
                    "Validation Error",
                    "Los valores de Latitud y Longitud no"
                    "pueden ser NULL individualmente.",
                )
            )


class UserManager(BaseUserManager):
    def create_user(
        self, email, password=None, is_staff=False, is_active=True, **extra_fields
    ):
        """Create a user instance with the given email and password."""
        email = UserManager.normalize_email(email)
        # Google OAuth2 backend send unnecessary username field
        extra_fields.pop("username", None)

        user = self.model(
            email=email, is_active=is_active, is_staff=is_staff, **extra_fields
        )
        if password:
            user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        return self.create_user(
            email, password, is_staff=True, is_superuser=True, **extra_fields
        )

    def customers(self):
        return self.get_queryset().filter(Q(is_staff=False) | (Q(is_staff=True)))

    def staff(self):
        return self.get_queryset().filter(is_staff=True)


class Recipient(models.Model):

    first_name = models.CharField(max_length=256, blank=False)
    last_name = models.CharField(max_length=256, blank=False)
    alias = models.CharField(max_length=256, blank=True)
    email = models.EmailField(unique=True)
    clabe = models.CharField(
        max_length=18,
        validators=[
            RegexValidator(
                regex="\d{18}",
                message="Clabe must have 18 digits",
                code="invalid_clabe",
            )
        ],
    )
    bank_name = models.CharField(max_length=256, blank=False)

    class Meta:
        ordering = ("first_name", "last_name", "alias")

    def __str__(self):
        return "%s %s" % (self.first_name, self.last_name)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    phone = PossiblePhoneNumberField(blank=True, default="")
    first_name = models.CharField(max_length=256, blank=True)
    last_name = models.CharField(max_length=256, blank=True)
    addresses = models.ManyToManyField(
        Address, blank=True, related_name="user_addresses"
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    note = models.TextField(null=True, blank=True)
    postal_code = models.CharField(max_length=6, null=True)
    date_joined = models.DateTimeField(default=timezone.now, editable=False)
    default_address = models.ForeignKey(
        Address, related_name="+", null=True, blank=True, on_delete=models.SET_NULL
    )
    utm_tracking = models.CharField(max_length=300, blank=True, null=True)
    recipients = models.ForeignKey(
        Recipient, null=True, blank=True, on_delete=models.SET_NULL
    )
    USERNAME_FIELD = "email"

    objects = UserManager()

    class Meta:
        permissions = (
            (
                "manage_users",
                pgettext_lazy("Permission description", "Manage customers."),
            ),
            ("manage_staff", pgettext_lazy("Permission description", "Manage staff.")),
            (
                "impersonate_users",
                pgettext_lazy("Permission description", "Impersonate customers."),
            ),
        )

    def get_full_name(self):
        if self.first_name or self.last_name:
            return ("%s %s" % (self.first_name, self.last_name)).strip()
        if self.default_billing_address:
            first_name = self.default_billing_address.first_name
            last_name = self.default_billing_address.last_name
            if first_name or last_name:
                return ("%s %s" % (first_name, last_name)).strip()
        return self.email
