from ..celery import app
from . import PaymentStatus
from .circle import get_payment_status
from .models import Payment as PaymentModel


@app.task
def check_payment_status():
    """
    Get all pending payments, and update their state according to Circle
    """
    pending_payments = PaymentModel.objects.filter(status=PaymentStatus.PENDING)
    for payment in pending_payments:
        status = get_payment_status(payment.payment_token)
        if status != PaymentStatus.PENDING:
            payment.status = status
            payment.save(update_fields=["status"])


@app.task
def check_payment_paid_status():
    payments = PaymentModel.objects.filter(status=PaymentStatus.CONFIRMED)
    for payment in payments:
        status = get_payment_status(payment.payment_token)
        if status == PaymentStatus.PAID:
            payment.save(update_fields=["status"])
