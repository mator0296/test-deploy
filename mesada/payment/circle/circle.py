"""
Circle communications lay in this file.

For more information on the Circle Payments API check out:
https://developers.circle.com/docs/getting-started-with-the-circle-payments-api
"""

import requests
from django.conf import settings
from ...core.utils import generate_idempotency_key

CIRCLE_API_KEY = settings.CIRCLE_API_KEY
CIRCLE_BASE_URL = settings.CIRCLE_BASE_URL
CIRCLE_WALLET_ID = settings.CIRCLE_WALLET_ID
CIRCLE_BLOCKCHAIN_ADDRESS = settings.CIRCLE_BLOCKCHAIN_ADDRESS
HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {CIRCLE_API_KEY}",
}


def create_card(body):
    """Save a card within the Circle API.

    Args:
        body (dict): Request body.
    """
    url = f"{CIRCLE_BASE_URL}/cards"
    response = requests.request("POST", url, headers=HEADERS, json=body)
    response.raise_for_status()

    return response.json().get("data")


def request_encryption_key():
    """Request a public encryption key from the Circle API.

    The key retrieved is an RSA public key that needs to be b64 decoded
    to get the actual PGP public key.
    """
    url = f"{CIRCLE_BASE_URL}/encryption/public"
    response = requests.request("GET", url, headers=HEADERS)
    response.raise_for_status()

    data = response.json().get("data")

    return data.get("keyId"), data.get("publicKey")


def create_trasfer_by_blackchain(amount):
    """ Create a transfer by blockchain within the Circle API
    
    Args:
        amount: Amount to transfer.
    """
    payload = {
        "idempotencyKey": generate_idempotency_key(),
        "source": {
            "type": "wallet",
            "id": f"{CIRCLE_WALLET_ID}"
        },
        "amount": {
            "amount": f"{amount}",
            "currency": "USD"
        },
        "destination": {
            "type": "blockchain",
            "address": f"{CIRCLE_BLOCKCHAIN_ADDRESS}",
            "chain": "ETH"
        }
    }
    
    url = f"{CIRCLE_BASE_URL}/transfers"
    response = requests.request("POST", url, headers=HEADERS, json=payload)
    response.raise_for_status()

    return response
