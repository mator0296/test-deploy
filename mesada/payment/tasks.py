from ..celery import app
from . import PaymentMethodStatus, PaymentMethodTypes, PaymentStatus
from .circle import get_ach_status, get_payment_status
from .models import Payment as PaymentModel
from .models import PaymentMethods as PaymentMethodsModel

from mesada.payment.circle import get_payment_status


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
def check_ach_status():
    """
    Get all pending ach payments methods status,
    and update their state according to Circle
    """
    pending_ach = PaymentMethodsModel.objects.filter(
        status=PaymentMethodStatus.PENDING, type=PaymentMethodTypes.ACH
    )
    for payment_methods in pending_ach:
        status = get_ach_status(payment_methods.payment_method_token)
        if status != PaymentMethodStatus.PENDING:
            payment_methods.status = status
            payment_methods.save(update_fields=["status"])


@app.task
def check_payment_paid_status():
    payments = PaymentModel.objects.filter(status=PaymentStatus.CONFIRMED)
    for payment in payments:
        status = get_payment_status(payment.payment_token)
        if status == PaymentStatus.PAID:
            payment.save(update_fields=["status"])
