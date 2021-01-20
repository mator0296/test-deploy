from django.db import models


class TransferStatus(models.TextChoices):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"