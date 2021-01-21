from django.db import models


class TransferStatus(models.TextChoices):
    PENDING = "pending"
    COMPLETE = "complete"
    FAILED = "failed"