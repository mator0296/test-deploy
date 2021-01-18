from ..celery import app
from .models import Payment


@app.task
def check_payment_status():
    payment = Payment.objects.first()
    print("Status Checked---- call api {}".format(payment.pk))
