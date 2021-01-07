"""
Plaid communications lay in this file.

For more information on the Plaid Payments API check out:
https://plaid.com/docs/api/
"""

import requests
from django.conf import settings
from plaid import Client as ClientPlaid
from plaid.errors import PlaidError

client = ClientPlaid(
    client_id=settings.PLAID_CLIENT_ID,
    secret=settings.PLAID_SECRET_KEY,
    environment=settings.PLAID_ENVIRONMENT,
)


def processor_token_create(public_token, account_id):
    try:
        # Exchange the public token for a Plaid access token.
        exchange_token_response = client.Item.public_token.exchange(
            public_token
        )
        access_token = exchange_token_response["access_token"]

        # Fetch the client's accounts list, should only have 1.
        accounts_response = client.Accounts.get(access_token)
        accounts = accounts_response["accounts"]
        account_id = accounts[0]["account_id"]

        # Create a processor token for the account found using the access token
        create_response = client.Processor.tokenCreate(
            access_token, account_id, settings.PLAID_PROCESSOR
        )
        return create_response["processor_token"], None, None
    except PlaidError as e:
        return None, e.code, e.message


def create_link_token(body):
    """Create a Plaid link token.

    Args:
        body (dict): Request body.
    """
    try:
        response = client.LinkToken.create(body)

        return response
    except PlaidError as e:
        return None, e.code, e.message
