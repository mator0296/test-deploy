from celery import shared_task


@shared_task
def check_payment_status():
    print("Status Checked---- call api")
