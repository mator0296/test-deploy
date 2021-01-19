"""
Circle communications lay in this file.

For more information on the Circle Payments API check out:
https://developers.circle.com/docs/getting-started-with-the-circle-payments-api
"""

from typing import Tuple

import requests
from django.conf import settings
from django.utils import dateparse

from ...core.utils import generate_idempotency_key

from mesada.transfer.models import CircleTransfer

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


def create_transfer_by_blockchain(amount, user):
    """ Create a transfer by blockchain within the Circle API
    Args:
        amount: Amount to transfer.
        user: User to which the foreign key will be associated in the CreateTransfer model.
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
    data = response.json()["data"]

    CircleTransfer.objects.create(
        transfer_id=data["id"],
        source_type=data["source"]["type"],
        source_id=data["source"]["id"],
        destination_type=data["destination"]["type"],
        destination_address=data["destination"]["address"],
        destination_chain=data["destination"]["chain"],
        amount=(data["amount"]["amount"], data["amount"]["currency"]),
        status=data["status"],
        create_date=dateparse.parse_datetime(data["createDate"]),
        user_id=user,
    )

    return data["id"]


def register_ach(processor_token, billing_details):
    """Register an ACH payment within the Circle API.

    Args:
        processor_token: A Circle processor token generated via Plaid's API.
        billing_details: Client's billind details.
    """
    url = f"{settings.CIRCLE_BASE_URL}/banks/ach"
    body = {
        "idempotencyKey": generate_idempotency_key(),
        "plaidProcessorToken": processor_token,
        "billingDetails": {
            "name": billing_details.get("name"),
            "city": billing_details.get("city"),
            "country": billing_details.get("country"),
            "line1": billing_details.get("line1"),
            "line2": billing_details.get("line2", ""),
            "district": billing_details.get("district"),
            "postalCode": billing_details.get("postalCode"),
        },
    }
    response = requests.request("POST", url, headers=HEADERS, json=body)
    response.raise_for_status()

    return response.json().get("data")


def get_circle_transfer_status(transfer_id):
    """
    Get the status of a transfer using a get request to the circle api

    Args:
        transfer_id: Id of the transfer in circle
    """
    url = f"{settings.CIRCLE_BASE_URL}/transfers/{transfer_id}"
    response = requests.request("GET", url, headers=HEADERS)
    response.raise_for_status()

    return response.json()["data"]["status"]
