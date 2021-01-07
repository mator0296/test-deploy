from django.db import models

# Create your models here.

from django.db import models
from djmoney.models.fields import MoneyField
# Create your models here.


class CircleTransfer(models.Model):

    transfer_id = models.CharField(max_length=256,
                                   blank=False, null=False)
    source_type = models.CharField(max_length=256, blank=False, null=False)
    source_id = models.CharField(max_length=256, blank=False, null=False)
    destination_type = models.CharField(
        max_length=256, blank=False, null=False)
    destination_address = models.CharField(
        max_length=256, blank=False, null=False)
    destination_chain = models.CharField(
        max_length=256, blank=False, null=False)
    amount = MoneyField(max_digits=19, decimal_places=4,
                        default_currency="USD")
    currency = models.CharField(max_length=256, blank=False, null=False)
    status = models.CharField(max_length=256, blank=False, null=False)
    create_date = models.DateTimeField(null=False, blank=False)

    class Meta:
        ordering = ("pk",)

    @property
    def full_transfer(self):
        return "%s %s %s %s %s %s %s %s %s" % (self.source_type, self.destination_type, self.destination_address, self.destination_chain, self.amount, self.currency, self.status, self.createDate)
