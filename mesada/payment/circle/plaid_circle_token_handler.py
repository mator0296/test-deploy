import os
import environ

from django.conf import settings
from plaid import Client as ClientPlaid

# Plaid credentials
client = ClientPlaid(
    client_id=settings.PLAID_CLIENT_ID,
    secret=settings.PLAID_SECRET,
    environment="sandbox"
)

# Sandbox shenanigans
public_token_response = client.Sandbox.public_token.create(
    "ins_1", ["assets"]
)
public_token = public_token_response["public_token"]
exchange_token_response = client.Item.public_token.exchange(public_token)
access_token = exchange_token_response["access_token"]
item_id = exchange_token_response["item_id"]

# Obtain client's accounts list
accounts_response = client.Accounts.get(access_token)
accounts = accounts_response["accounts"]
account_id = accounts[0]["account_id"]

create_response = client.Processor.tokenCreate(
    access_token, account_id, "circle"
)
processor_token = create_response["processor_token"]
print(processor_token)
