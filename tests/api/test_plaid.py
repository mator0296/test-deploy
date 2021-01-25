from unittest.mock import patch

import pytest
from django.conf import settings


@pytest.mark.integration
@patch("mesada.payment.plaid.client")
def test_create_link_token(mock_client, user_api_client):
    query = """
    mutation createLinkToken {
        createLinkToken {
            linkToken
            expiration
            requestId
        }
    }
    """
    variables_values = {}
    user_api_client.post_graphql(query, variables_values)

    body = {
        "client_name": "Mesada",
        "country_codes": settings.PLAID_COUNTRIES,
        "language": "en",
        "user": {
            "client_user_id": str(user_api_client.user.id),
            "legal_name": (
                f"{user_api_client.user.first_name} {user_api_client.user.last_name}"
            ),
            "phone_number": str(user_api_client.user.phone),
            "email_address": user_api_client.user.email,
        },
        "products": settings.PLAID_PRODUCTS,
    }

    mock_client.LinkToken.create.assert_called_once_with(body)


@pytest.mark.integration
@patch("mesada.payment.plaid.client")
def test_register_ach_payment(mock_client, user_api_client):

    query = """
        mutation registerAchPayment($input: RegisterAchPaymentInput!) {
            registerAchPayment(input: $input) {
                paymentMethod {
                    type
                    processorToken
                    name
                    addressLine1
                    addressLine2
                    city
                    district
                    countryCode
                    postalCode
                }
                errors {
                    field
                    message
                }
            }
        }
        """
    variables_values = {
        "input": {
            "publicToken": "public-sandbox-03a4917e-d4f3-4e83-9597-0bcf6bdefe02",
            "accounts": ['{ "account_id": "mp1Nxn6JXncaQ8KnD1M3sG3Q6WDogWULXdN6K"}'],
            "billingDetails": {
                "name": "Satoshi Nakamoto",
                "line1": "100 Money Street",
                "line2": "Suite 1",
                "city": "Boston",
                "district": "MA",
                "country": "US",
                "postalCode": "01234",
            },
        }
    }

    user_api_client.post_graphql(query, variables_values)
    mock_client.Item.public_token.exchange.assert_called_once_with(
        variables_values["input"].get("publicToken")
    )
    mock_client.Accounts.get.assert_called_once_with(
        mock_client.Item.public_token.exchange.return_value["access_token"]
    )
    account_id = mock_client.Accounts.get.return_value["accounts"][0]["account_id"]
    access_token = mock_client.Item.public_token.exchange.return_value["access_token"]
    mock_client.Processor.tokenCreate.assert_called_once_with(
        access_token, account_id, settings.PLAID_PROCESSOR
    )
