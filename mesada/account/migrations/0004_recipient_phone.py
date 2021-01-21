# Generated by Django 3.1.4 on 2021-01-21 22:10

from django.db import migrations
import mesada.account.models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_auto_20210121_0109'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipient',
            name='phone',
            field=mesada.account.models.PossiblePhoneNumberField(blank=True, default='', max_length=128, region=None),
        ),
    ]
