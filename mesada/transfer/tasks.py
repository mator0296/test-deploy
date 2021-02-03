from django.db import transaction

from ..celery import app
from .enums import TransferStatus
from .models import CircleTransfer

from mesada.payment.circle import get_circle_transfer_status


@app.task
def check_transfer_status():
    transfers = CircleTransfer.objects.select_for_update().filter(
        status=TransferStatus.PENDING
    )

    with transaction.atomic():
        for transfer in transfers:
            status = get_circle_transfer_status(transfer.transfer_id)
            if status != TransferStatus.PENDING:
                transfer.status = status
                transfer.save()
