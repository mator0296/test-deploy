from celery import shared_task
from .models import Payment as PaymentModel
from .circle import get_payment_status


@shared_task
def check_payment_status():
    """
    Get all pending payments, and update their state according to Circle
    """
    pending_payments = PaymentModel.objects.filter(status="pending")
    for payment in pending_payments:
        status = get_payment_status(payment.payment_token)
        if status != "pending":
            payment.status = status
            payment.save()
