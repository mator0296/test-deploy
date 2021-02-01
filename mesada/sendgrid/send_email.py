from . import SendgridTemplatesIDs, events
from .models import SendgridTemplates


def send_sendgrid_email(template_id: SendgridTemplatesIDs.TEMPLATES, ctx: dict):
    """
    Send email to sendgrid
    Arg:
        template_id: A SendgridTemplatesIDs subtipes
        ctx: Dict
    """
    recipient_list = ctx.get("recipient_list")
    if not recipient_list:
        events.send_sendgrid_email_event(False, template_id, "No recipient list")
        return

    exist, client = SendgridTemplates.objects.get_template_id(template_id)
    if not exist:
        events.send_sendgrid_email_event(False, template_id)
    else:
        succes, status = client.send_templated_mail(**ctx)
        events.send_sendgrid_email_event(succes, template_id, status)
