from django.db import models


class PaymentStatus(models.TextChoices):
    PENDING = "pending"
    CONFIRMED  = "confirmed"
    PAID = "paid"
    FAILED = "failed" 