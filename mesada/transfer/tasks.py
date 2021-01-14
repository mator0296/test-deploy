from celery import shared_task

from mesada.payment.circle import get_circle_transfer_status


@shared_task
def check_transfer_status():
    from .models import CircleTransfer
    
    transfers = CircleTransfer.objects.filter(status="pending")
    for transfer in transfers:
        status = get_circle_transfer_status(transfer.transfer_id)
        if status is not "pending":
            print("Transfer " + transfer.transfer_id + ": " + status)
            transfer.status = status
            transfer.save()
