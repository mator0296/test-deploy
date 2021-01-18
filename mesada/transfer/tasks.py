from celery import shared_task

from mesada.payment.circle import get_circle_transfer_status
from .models import CircleTransfer


@shared_task
def check_transfer_status():
    transfers = CircleTransfer.objects.filter(status="pending")
    for transfer in transfers:
        status = get_circle_transfer_status(transfer.transfer_id)
        if status is not "pending":
            transfer.status = status
            transfer.save()
