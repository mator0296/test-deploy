from django.db import models

from . import GalactusStatus


class GalactusTransaction(models.Model):

    status = models.CharField(
        max_length=9, choices=GalactusStatus.choices, default=GalactusStatus.PENDING
    )
    response_data = models.JSONField()

    def __str__(self):
        return "%s %s" % (self.status, self.response_data)
