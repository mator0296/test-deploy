from django.db import models


class GalactusStatus(models.TextChoices):
    PENDING = "pending"
    SUCCESS = "success"
    ERROR = "error"
