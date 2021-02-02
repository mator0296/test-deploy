from .models import SendEmailSendgridEvent

EVENT_NO_RECIPIENT = "No found recipient"
EVENT_NO_TEMPLATE = "The template id no exists"
EVENT_SEND_GOOD = "Send ok"


def send_sendgrid_email_event(success, template_id, event=EVENT_NO_TEMPLATE):
    """
    Arg:
        success
        template_id
        event
    """
    if success:
        event = EVENT_SEND_GOOD

    SendEmailSendgridEvent.objects.create(
        success=success, causes=event, template_id=template_id
    )
