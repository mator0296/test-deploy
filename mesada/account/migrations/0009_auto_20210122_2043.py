# Generated by Django 3.1.4 on 2021-01-22 20:43

import django.db.models.deletion
from django.db import migrations, models

import mesada.account.models


class Migration(migrations.Migration):

    dependencies = [("account", "0008_recipient_phone")]

    operations = [
        migrations.RemoveField(model_name="recipient", name="bank_name"),
        migrations.AddField(
            model_name="recipient",
            name="bank",
            field=models.CharField(
                choices=[
                    ("bbva", "Bbva"),
                    ("banamex", "Banamex"),
                    ("banorte", "Banorte"),
                    ("santander", "Santander"),
                ],
                default="bbva",
                max_length=10,
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="recipient",
            name="phone",
            field=mesada.account.models.PossiblePhoneNumberField(
                blank=True, max_length=128, null=True, region=None
            ),
        ),
        migrations.AlterField(
            model_name="recipient",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="account.user"
            ),
        ),
    ]