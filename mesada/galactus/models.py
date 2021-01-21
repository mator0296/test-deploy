from django.db import models
from . import GalactusStatus

# Create your models here.


class GalactusTransaction(models.Model):

    status = models.CharField(
        max_length=9, choices=GalactusStatus.choices, default=GalactusStatus.PENDING
    )
    detail = models.JSONField()

    def __str__(self):
        return "%s %s" % (self.status, self.detail)
