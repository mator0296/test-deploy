import base64

from django.conf import settings
from django.db import models
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Attachment,
    Content,
    Disposition,
    DynamicTemplateData,
    FileContent,
    FileName,
    FileType,
    From,
    Mail,
    TemplateId,
    To,
)

from . import SendgridTemplatesIDs

ATTACHMENT_FILE_TYPES = ("text/csv", "text/plain")

ATTACHMENT_DISPOSITIONS = ("attachment",)


class SendGrid:
    @classmethod
    def _get_client(cls):
        return SendGridAPIClient(settings.SENDGRID_API_KEY)

    @classmethod
    def prepare_attachment(
        cls,
        binary_content,
        file_type,
        file_name="filename",
        *,
        disposition="attachment",
    ):
        encoded = base64.b64encode(binary_content).decode()

        if file_type not in ATTACHMENT_FILE_TYPES:
            raise NotImplementedError(f"Unknown file_type: {file_type}")

        if not file_name or file_name == "":
            raise ValueError(f"Unsupported file_name value: {file_name}")

        if disposition not in ATTACHMENT_DISPOSITIONS:
            raise NotImplementedError(f"Unknown disposition: {disposition}")

        attachment = Attachment()
        attachment.file_content = FileContent(encoded)

        attachment.file_type = FileType(file_type)
        attachment.file_name = FileName(file_name)
        attachment.disposition = Disposition(disposition)

        return attachment

    @classmethod
    def send_mail(cls, *, to, subject, text, from_email=None, attachment=None):
        message = Mail()
        message.to = To(to)
        message.subject = subject

        if from_email:
            message.from_email = from_email
        else:
            message.from_email = From(
                email=settings.DEFAULT_FROM_EMAIL, name=settings.DEFAULT_NAME_EMAIL
            )

        if text:
            message.content = Content("text/plain", text)

        if attachment:
            message.attachment = attachment

        return cls._get_client().send(message)


class SendgridTemplatesManager(models.Manager):
    def get_template_id(self, TEMPLATE):
        query_set = self.get_queryset().filter(name=TEMPLATE)
        if query_set.count() > 0:
            obj = query_set.first()
            return True, obj
        else:
            return False, None  # Exist, obj


class SendgridTemplates(models.Model):
    name = models.CharField(max_length=150, choices=SendgridTemplatesIDs.TEMPLATES)
    template_id = models.CharField(max_length=100, null=False, blank=False)

    objects = SendgridTemplatesManager()

    class Meta:
        unique_together = (("name",),)

    def __str__(self):
        return self.name

    def _client(self):
        return SendGridAPIClient(settings.SENDGRID_API_KEY)

    def send_templated_mail(self, **kwargs):
        recipient_list = kwargs.get("recipient_list")
        sg = self._client()
        message = Mail()
        message.from_email = From(
            email=settings.DEFAULT_FROM_EMAIL, name=settings.DEFAULT_NAME_EMAIL
        )
        message.to = To(recipient_list)
        message.template_id = TemplateId(self.template_id)
        message.dynamic_template_data = DynamicTemplateData(kwargs)
        try:
            response = sg.send(message)
            return True, response.status_code
        except Exception as e:
            return False, e


class SendEmailSendgridEvent(models.Model):
    """
    This class registrer a send events with sendgrid
    Args:
        success: Boolean
        causes: Short string max 150
    """

    success = models.BooleanField(default=False)
    causes = models.CharField(max_length=150)
    created = models.DateField(auto_now_add=True)
    template_id = models.CharField(max_length=100, null=False, blank=False)

    def __str__(self):
        return f"{self.success} - {self.template_id}"
