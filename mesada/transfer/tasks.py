from ..celery import app
from .models import CircleTransfer
from .enums import TransferStatus

from mesada.payment.circle import get_circle_transfer_status


@app.task
def check_transfer_status():
    transfers = CircleTransfer.objects.filter(status="pending")
    for transfer in transfers:
        status = get_circle_transfer_status(transfer.transfer_id)
        if status != TransferStatus.PENDING:
            transfer.status = status
            transfer.save()
