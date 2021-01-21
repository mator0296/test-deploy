from django.db import models

# Create your models here.
class GalactusTransaction(models.Model):

    status = models.CharField(max_length=256, blank=False, null=True)
    detail = models.CharField(max_length=256, blank=False, null=True)

    def __str__(self):
        return "%s %s" % (self.status, self.detail)
