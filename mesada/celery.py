from __future__ import absolute_import

import os

from celery import Celery
from django.conf import settings

from mesada.payment.tasks import check_payment_status

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mesada.settings")
app = Celery("mesada")

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object("django.conf:settings")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # calls check_payment_status every minute.
    sender.add_periodic_task(settings.CELERY_CHECK_PAYMENT_STATUS, check_payment_status.s(), name="check status every minute")
