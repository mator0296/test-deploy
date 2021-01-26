from django.db import models


class CheckoutStatus(models.TextChoices):
    PENDING = "pending"
    COMPLETE = "complete"
