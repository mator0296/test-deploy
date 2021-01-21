from mesada.payment.circle import get_payment_status

from ..celery import app
from .models import Payment as PaymentModel
from .enums import PaymentStatus


@app.task
def check_payment_status():
    print("Status Checked---- call api {}".format("test"))


@app.task
def check_payment_paid_status():
    payments = PaymentModel.objects.filter(status="confirmed")
    for payment in payments:
        status = get_payment_status(payment.payment_token)
        if status == PaymentStatus.PAID:
            payment.status = status
            payment.save()
            