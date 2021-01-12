"""
Circle communications lay in this file.

For more information on the Circle Payments API check out:
https://developers.circle.com/docs/getting-started-with-the-circle-payments-api
"""

import requests
from django.conf import settings
from ...core.utils import generate_idempotency_key


HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {settings.CIRCLE_API_KEY}",
}


def create_card(body):
    """Save a card within the Circle API.

    Args:
        body (dict): Request body.
    """
    url = f"{settings.CIRCLE_BASE_URL}/cards"
    response = requests.request("POST", url, headers=HEADERS, json=body)
    response.raise_for_status()

    return response.json().get("data")


def request_encryption_key():
    """Request a public encryption key from the Circle API.

    The key retrieved is an RSA public key that needs to be b64 decoded
    to get the actual PGP public key.
    """
    url = f"{settings.CIRCLE_BASE_URL}/encryption/public"
    response = requests.request("GET", url, headers=HEADERS)
    response.raise_for_status()

    data = response.json().get("data")

    return data.get("keyId"), data.get("publicKey")


def create_payment(body):
    """Send a POST request to create a payment using the Circle's Payments API

    Args:
        body (dict): Request body.
    """
    url = f"{settings.CIRCLE_BASE_URL}/payments"
    response = requests.request("POST", url, headers=HEADERS, json=body)
    response.raise_for_status()

    return response.json().get("data")


def register_ach(payment_method):
    """Register an ACH payment within the Circle API.

    Args:
        payment_method (PaymentMethod): ACH payment method instance.
    """
    url = f"{settings.CIRCLE_BASE_URL}/banks/ach"
    body = {
        "idempotencyKey": generate_idempotency_key(),
        "plaidProcessorToken": payment_method.processor_token,
        "billingDetails": {
            "name": payment_method.name,
            "city": payment_method.city,
            "country": payment_method.country_code.code,
            "line1": payment_method.address_line_1,
            "line2": payment_method.address_line_2,
            "district": payment_method.district,
            "postalCode": payment_method.postal_code,
        },
    }
    response = requests.request("POST", url, headers=HEADERS, json=body)
    response.raise_for_status()

    return response.json().get("data")
