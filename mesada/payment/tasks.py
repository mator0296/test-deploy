from ..celery import app
from . import PaymentMethodStatus, PaymentMethodTypes
from .circle import get_ach_status
from .models import PaymentMethods as PaymentMethodsModel


@app.task
def check_payment_status():
    print("Status Checked---- call api {}".format("test"))


@app.task
def check_ach_status():
    """
    Get all pending ach payments methods status, and update their state according to Circle
    """
    pending_ach = PaymentMethodsModel.objects.filter(
        status=PaymentMethodStatus.PENDING, type=PaymentMethodTypes.ACH
    )
    for payment_methods in pending_ach:
        status = get_ach_status(payment_methods.payment_method_token)
        if status != PaymentMethodStatus.PENDING:
            payment_methods.status = status
            payment_methods.save()
