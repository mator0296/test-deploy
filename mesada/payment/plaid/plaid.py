"""
Plaid communications lay in this file.

For more information on the Plaid Payments API check out:
https://plaid.com/docs/api/
"""

import requests
from django.conf import settings

PLAID_BASE_URL = settings.PLAID_BASE_URL
PLAID_CLIENT_ID = settings.PLAID_CLIENT_ID
PLAID_SECRET_KEY = settings.PLAID_SECRET_KEY
HEADERS = {"Content-Type": "application/json"}


def create_link_token(body):
    """Create a Plaid link token.

    Args:
        body (dict): Request body.
    """
    body["client_id"] = PLAID_CLIENT_ID
    body["secret"] = PLAID_SECRET_KEY

    url = f"{PLAID_BASE_URL}/link/token/create"
    response = requests.request("POST", url, headers=HEADERS, json=body)
    response.raise_for_status()

    return response.json()
