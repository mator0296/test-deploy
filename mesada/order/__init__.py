from django.db import models


class OrderStatus(models.TextChoices):
    PENDING = "pending"
    SUCCESS = "success"
    ERROR = "error"


class OrderStage(models.TextChoices):
    PAYMENT = "payment"
    TRANSFER = "transfer"
    WITHDRAWAL = "withdrawal"
    GALACTUS_TRANSACTION = "galactus_transaction"


class EventType(models.TextChoices):
    ERROR = "error"
    SUCCESS = "success"
