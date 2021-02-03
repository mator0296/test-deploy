from django.conf import settings
from django.contrib.auth import get_user_model

from ..celery import app
from ..sendgrid import SendgridTemplatesIDs
from ..sendgrid.send_email import send_sendgrid_email


def collect_data_for_email(recipient, user_id):
    name = "Cliente"
    User = get_user_model()
    customer_query = User.objects.filter(pk=user_id)
    if customer_query:
        new_customer = customer_query.first()
        name = new_customer.first_name

    return {"recipient_list": recipient, "first_name": name}


@app.task
def send_new_customer_email(recipient, user_id):
    if settings.EMAIL_ENGINE_ON:
        ctx = collect_data_for_email(recipient, user_id)
        send_sendgrid_email(SendgridTemplatesIDs.NEW_CUSTOMER_TEMPLATE, ctx)
