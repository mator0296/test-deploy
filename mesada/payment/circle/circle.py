"""
Circle communications lay in this file.

For more information on the Circle Payments API check out:
https://developers.circle.com/docs/getting-started-with-the-circle-payments-api
"""

import requests
from django.conf import settings
from django.utils import dateparse
from django.core.exceptions import ValidationError
from ...transfer.models import CircleTransfer
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


def create_trasfer_by_blackchain(amount, user):
    """ Create a transfer by blockchain within the Circle API
    Args:
        amount: Amount to transfer.
    """
    payload = {
        "source": {"type": "wallet", "id": f"{settings.CIRCLE_WALLET_ID}"},
        "destination": {
            "type": "blockchain",
            "address": f"{settings.BITSO_BLOCKCHAIN_ADDRESS}",
            "chain": f"{settings.CIRCLE_BLOCKCHAIN_CHAIN}",
        },
        "amount": {"amount": "{:.2f}".format(amount), "currency": "USD"},
        "idempotencyKey": generate_idempotency_key(),
    }

    url = f"{settings.CIRCLE_BASE_URL}/transfers"
    response = requests.request("POST", url, headers=HEADERS, json=payload)
    response.raise_for_status()

    try:
        transfer = CircleTransfer(
            transfer_id = response.json()["data"]["id"],
            source_type = response.json()["data"]["source"]["type"],
            source_id = response.json()["data"]["source"]["id"],
            destination_type = response.json()["data"]["destination"]["type"],
            destination_address = response.json()["data"]["destination"]["address"],
            destination_chain = response.json()["data"]["destination"]["chain"],
            amount = (response.json()["data"]["amount"]["amount"],response.json()["data"]["amount"]["currency"]),
            status = response.json()["data"]["status"],
            create_date = dateparse.parse_datetime(response.json()["data"]["createDate"]),
            user_id = user
        )
        transfer.save()
    except:
        raise ValidationError({"CircleTransfer": "Error in Circle response from transfer"})

    return response.json()["data"]["id"]
