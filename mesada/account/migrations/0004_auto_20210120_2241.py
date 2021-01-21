# Generated by Django 3.1.4 on 2021-01-20 22:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("account", "0003_remove_user_postal_code")]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="default_address",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="user",
                to="account.address",
            ),
        )
    ]
