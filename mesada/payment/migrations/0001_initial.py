# Generated by Django 3.1.4 on 2020-12-28 18:31

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_countries.fields
import django_enumfield.db.fields
import mesada.payment.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="paymentMethods",
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
                ("type", models.CharField(max_length=50)),
                (
                    "exp_month",
                    models.PositiveIntegerField(
                        blank=True,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(12),
                        ],
                    ),
                ),
                (
                    "exp_year",
                    models.PositiveIntegerField(
                        blank=True,
                        null=True,
                        validators=[django.core.validators.MaxValueValidator(2050)],
                    ),
                ),
                ("network", models.CharField(blank=True, max_length=50)),
                ("last_digits", models.CharField(blank=True, max_length=4)),
                ("fingerprint", models.CharField(blank=True, max_length=36)),
                (
                    "verification_cvv",
                    django_enumfield.db.fields.EnumField(
                        default=0, enum=mesada.payment.models.verificationCvv
                    ),
                ),
                (
                    "verification_avs",
                    django_enumfield.db.fields.EnumField(
                        default=0, enum=mesada.payment.models.verificationAvs
                    ),
                ),
                ("phonenumber", models.CharField(blank=True, max_length=15)),
                ("email", models.EmailField(blank=True, max_length=256)),
                ("name", models.CharField(blank=True, max_length=256)),
                ("address_line_1", models.CharField(blank=True, max_length=256)),
                ("address_line_2", models.CharField(blank=True, max_length=256)),
                ("postal_code", models.CharField(blank=True, max_length=6)),
                ("city", models.CharField(blank=True, max_length=256)),
                ("district", models.CharField(blank=True, max_length=256)),
                ("country_code", django_countries.fields.CountryField(max_length=2)),
                (
                    "created",
                    models.DateTimeField(
                        default=django.utils.timezone.now, editable=False
                    ),
                ),
                ("updated", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payment_methods",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        )
    ]
