from django.db import models


class OrderStatus(models.TextChoices):
    PENDING = "pending"
    SUCCESS = "success"
    ERROR = "error"
