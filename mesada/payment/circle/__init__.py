"""
Circle communications lay in this file.

For more information on the Circle Payments API check out:
https://developers.circle.com/docs/getting-started-with-the-circle-payments-api
"""

from typing import Tuple

import requests
from django.conf import settings
from django.utils import dateparse
from django.core.exceptions import ValidationError
from ...core.utils import generate_idempotency_key

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {settings.CIRCLE_API_KEY}",
}


def create_card(body: dict) -> dict:
    """
    Save a card within the Circle API.
    """
    url = f"{settings.CIRCLE_BASE_URL}/cards"
    response = requests.request("POST", url, headers=HEADERS, json=body)
    response.raise_for_status()

    return response.json().get("data")


def request_encryption_key() -> Tuple[str, str]:
    """
    Request a public encryption key from the Circle API.
    The key retrieved is an RSA public key that needs to be b64 decoded
    to get the actual PGP public key.
    """
    url = f"{settings.CIRCLE_BASE_URL}/encryption/public"
    response = requests.request("GET", url, headers=HEADERS)
    response.raise_for_status()

    data = response.json().get("data")

    return data.get("keyId"), data.get("publicKey")


def create_payment(body: dict):
    """
    Send a POST request to create a payment using the Circle's Payments API
    """
    url = f"{settings.CIRCLE_BASE_URL}/payments"
    response = requests.request("POST", url, headers=HEADERS, json=body)
    response.raise_for_status()

    return response.json().get("data")
