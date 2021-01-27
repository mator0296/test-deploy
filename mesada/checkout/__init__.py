from django.db import models
from .utils import get_amount, HEADERS


class CheckoutStatus(models.TextChoices):
    PENDING = "pending"
    COMPLETE = "complete"
