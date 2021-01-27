from django.db import models

from .utils import HEADERS, get_amount


class CheckoutStatus(models.TextChoices):
    PENDING = "pending"
    COMPLETE = "complete"
