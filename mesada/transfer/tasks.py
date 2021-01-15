from celery import shared_task

from .models import CircleTransfer

from mesada.payment.circle import get_circle_transfer_status


@shared_task
def check_transfer_status():
    transfers = CircleTransfer.objects.filter(status="pending")
    for transfer in transfers:
        status = get_circle_transfer_status(transfer.transfer_id)
        if status is not "pending":  # noqa: F632
            transfer.status = status
            transfer.save()
