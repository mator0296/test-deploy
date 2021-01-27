import os

from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mesada.settings")
app = Celery("mesada")

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object("django.conf:settings")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    from mesada.payment.tasks import check_payment_paid_status, check_payment_status
    from mesada.transfer.tasks import check_transfer_status
    from mesada.order.tasks import update_pending_order_status, update_processing_order_status

    sender.add_periodic_task(
        settings.CELERY_CHECK_PAYMENT_STATUS,
        check_payment_status.s(),
        name="check payment status every minute",
    )
    sender.add_periodic_task(
        settings.CELERY_CHECK_TRANSFER_STATUS,
        check_transfer_status.s(),
        name="check transfer status every minute",
    )
    sender.add_periodic_task(
        crontab(hour=7, minute=0),
        check_payment_paid_status.s(),
        name="check the status every day",
    )
    sender.add_periodic_task(
        settings.CELERY_UPDATE_PENDING_ORDER_STATUS,
        update_pending_order_status.s(),
        name="Update the status of a PENDING order every minute",
    )
