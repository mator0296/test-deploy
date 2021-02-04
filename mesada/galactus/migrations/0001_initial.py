# Generated by Django 3.1.4 on 2021-01-21 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="GalactusTransaction",
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
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("success", "Success"),
                            ("error", "Error"),
                        ],
                        default="pending",
                        max_length=9,
                    ),
                ),
                ("response_data", models.JSONField()),
            ],
        )
    ]