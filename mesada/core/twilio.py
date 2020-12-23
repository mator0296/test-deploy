import environ

from twilio.rest import Client as ClientTwilio


env = environ.Env()


def send_token(phone):
    account_sid = env("TWILIO_ACCOUNT_SID")
    auth_token = env("TWILIO_AUTH_TOKEN")
    service = env("TWILIO_SERVICE")
    client = ClientTwilio(account_sid, auth_token)
    verify = client.verify.services(service).verifications.create(
        to=phone, channel="sms"
    )
    return verify
