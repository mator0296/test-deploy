from django.conf import settings
from twilio.rest import Client as ClientTwilio

client = ClientTwilio(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)


def send_code(phone):
    return client.verify.services(
        settings.TWILIO_VERIFICATION_SID
    ).verifications.create(to=phone, channel="sms")


def check_code(phone, code):
    return client.verify.services(
        settings.TWILIO_VERIFICATION_SID
    ).verification_checks.create(to=phone, code=code)
