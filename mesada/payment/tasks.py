from django.db import transaction

from ..celery import app
from . import PaymentMethodStatus, PaymentMethodTypes, PaymentStatus
from .circle import get_ach_status, get_payment_status
from .models import Payment as PaymentModel
from .models import PaymentMethods as PaymentMethodsModel


def _transition_to_status(model_obj, status, status_enum):
    if status not in status_enum:
        raise ValueError("Circle returned unknown status")

    model_obj.status = status_enum(status)
    model_obj.save(update_fields=["status"])


@app.task
def check_payment_status():
    """
    Get all pending payments, and update their state according to Circle
    """
    pending_payments = PaymentModel.objects.select_for_update().filter(
        status=PaymentStatus.PENDING
    )

    with transaction.atomic():
        for payment in pending_payments:
            status = get_payment_status(payment.payment_token)
            if status != PaymentStatus.PENDING:
                _transition_to_status(payment, status, PaymentStatus)


@app.task
def check_ach_status():
    """
    Get all pending ach payments methods status,
    and update their state according to Circle
    """
    pending_ach = PaymentMethodsModel.objects.select_for_update().filter(
        status=PaymentMethodStatus.PENDING, type=PaymentMethodTypes.ACH
    )

    with transaction.atomic():
        for payment_method in pending_ach:
            status = get_ach_status(payment_method.payment_method_token)
            if status != PaymentMethodStatus.PENDING:
                _transition_to_status(payment_method, status, PaymentMethodStatus)


@app.task
def check_payment_paid_status():
    payments = PaymentModel.objects.select_for_update().filter(
        status=PaymentStatus.CONFIRMED
    )

    with transaction.atomic():
        for payment in payments:
            status = get_payment_status(payment.payment_token)
            if status == PaymentStatus.PAID:
                _transition_to_status(payment, PaymentStatus.PAID, PaymentStatus)
