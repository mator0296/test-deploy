# Generated by Django 3.1.4 on 2021-01-21 22:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("account", "0006_user_birth_date")]

    operations = [migrations.RemoveField(model_name="user", name="is_phone_verified")]
