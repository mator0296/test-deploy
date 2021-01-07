from django.conf import settings
from plaid import Client as ClientPlaid
from plaid.errors import PlaidError


def processor_token_create(public_token, account_id):
    client = ClientPlaid(
        client_id=settings.PLAID_CLIENT_ID,
        secret=settings.PLAID_SECRET,
        environment=settings.PLAID_ENVIRONMENT
    )
    try:
        # Exchange the public token for a Plaid access token.
        exchange_token_response = client.Item.public_token.exchange(public_token)
        access_token = exchange_token_response["access_token"]

        # Fetch the client's accounts list, should only have 1.
        accounts_response = client.Accounts.get(access_token)
        accounts = accounts_response['accounts']
        account_id = accounts[0]["account_id"]

        # Create a processor token for the account found using the access token
        create_response = client.Processor.tokenCreate(
            access_token, account_id, settings.PLAID_PROCESSOR
        )
        return create_response["processor_token"], None, None
    except PlaidError as e:
        return None, e.code, e.message
