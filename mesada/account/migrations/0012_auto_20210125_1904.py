# Generated by Django 3.1.4 on 2021-01-25 19:04

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("account", "0011_auto_20210125_1839")]

    operations = [
        migrations.AlterField(
            model_name="recipient",
            name="user",
            field=models.ForeignKey(
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="recipients",
                to=settings.AUTH_USER_MODEL,
            ),
        )
    ]
