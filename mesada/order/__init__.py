from django.db import models


class OrderStatus(models.TextChoices):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    ERROR = "error"
