from celery import shared_task


@shared_task
def check_payment_status():
    print("Status Checked---- call api")


@shared_task
def check_payment_paid_status():
    from .models import Payment as PaymentModel
    payments = PaymentModel.objects.filter(status="confirmed")
    for payment in payments:
        status = get_payment_status(payment.payment_token)
        if status == "paid":
            payment.status = status
            payment.save()
