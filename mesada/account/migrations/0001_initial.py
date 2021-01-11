# Generated by Django 3.1.4 on 2021-01-08 18:26

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
import django_countries.fields
from django.db import migrations, models

import mesada.account.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [("auth", "0012_alter_user_first_name_max_length")]

    operations = [
        migrations.CreateModel(
            name="Address",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "address_name",
                    models.CharField(blank=True, max_length=256, null=True),
                ),
                ("first_name", models.CharField(blank=True, max_length=256)),
                ("last_name", models.CharField(blank=True, max_length=256)),
                ("company_name", models.CharField(blank=True, max_length=256)),
                ("street_address_1", models.CharField(blank=True, max_length=256)),
                ("street_address_2", models.CharField(blank=True, max_length=256)),
                ("city", models.CharField(blank=True, max_length=256)),
                ("city_area", models.CharField(blank=True, max_length=128)),
                ("postal_code", models.CharField(blank=True, max_length=20)),
                ("country", django_countries.fields.CountryField(max_length=2)),
                ("country_area", models.CharField(blank=True, max_length=128)),
                ("is_visible", models.BooleanField(default=True)),
            ],
            options={"ordering": ("pk",)},
        ),
        migrations.CreateModel(
            name="Recipient",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("first_name", models.CharField(max_length=256)),
                ("last_name", models.CharField(max_length=256)),
                ("alias", models.CharField(blank=True, max_length=256)),
                ("email", models.EmailField(max_length=254, unique=True)),
                (
                    "clabe",
                    models.CharField(
                        max_length=18,
                        validators=[
                            django.core.validators.RegexValidator(
                                code="invalid_clabe",
                                message="Clabe must have 18 digits",
                                regex="\\d{18}",
                            )
                        ],
                    ),
                ),
                ("bank_name", models.CharField(max_length=256)),
            ],
            options={"ordering": ("first_name", "last_name", "alias")},
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                ("email", models.EmailField(max_length=254, unique=True)),
                (
                    "phone",
                    mesada.account.models.PossiblePhoneNumberField(
                        blank=True, default="", max_length=128, region=None
                    ),
                ),
                ("first_name", models.CharField(blank=True, max_length=256, null=True)),
                ("last_name", models.CharField(blank=True, max_length=256, null=True)),
                ("is_staff", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("is_phone_verified", models.BooleanField(default=False)),
                ("note", models.TextField(blank=True, null=True)),
                ("postal_code", models.CharField(max_length=6, null=True)),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, editable=False
                    ),
                ),
                (
                    "utm_tracking",
                    models.CharField(blank=True, max_length=300, null=True),
                ),
                (
                    "addresses",
                    models.ManyToManyField(
                        blank=True, related_name="user_addresses", to="account.Address"
                    ),
                ),
                (
                    "default_address",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="account.address",
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.Group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "recipients",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="account.recipient",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.Permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "permissions": (
                    ("manage_users", "Manage customers."),
                    ("manage_staff", "Manage staff."),
                    ("impersonate_users", "Impersonate customers."),
                )
            },
        ),
    ]
