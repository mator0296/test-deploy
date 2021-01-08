from django.db import models
from djmoney.models.fields import MoneyField

# Create your models here.


class CircleTransferStatus(models.TextChoices):
    """ State of the transfer in Circle """

    PENDING = "pending"
    COMPLETE = "complete"
    FAILED = "failed"


class CircleTransferType(models.TextChoices):
    """ Circle transfer type """

    BLOCKCHAIN = "blockchain"
    WALLET = "wallet"


class CircleTransfer(models.Model):
    """ Model of a circle transfer """

    transfer_id = models.CharField(max_length=256, unique=True)
    source_type = models.CharField(max_length=10, choices=CircleTransferType.choices)
    source_id = models.CharField(max_length=10)
    destination_type = models.CharField(
        max_length=10, choices=CircleTransferType.choices
    )
    destination_address = models.CharField(max_length=256)
    destination_chain = models.CharField(max_length=4)
    amount = MoneyField(max_digits=19, decimal_places=4, default_currency="USD")
    status = models.CharField(
        max_length=8, choices=CircleTransferStatus.choices, blank=False, null=False
    )
    create_date = models.DateField()

    class Meta:
        ordering = ("pk",)

    @property
    def full_transfer(self):
        return "%s %s %s %s %s %s %s %s %s" % (
            self.source_type,
            self.destination_type,
            self.destination_address,
            self.destination_chain,
            self.amount,
            self.currency,
            self.status,
            self.createDate,
        )
