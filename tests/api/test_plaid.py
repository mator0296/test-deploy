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
            errors {
            field
            message
            }
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
            "legal_name": f"{user_api_client.user.first_name} {user_api_client.user.last_name}",
            "phone_number": str(user_api_client.user.phone),
            "email_address": user_api_client.user.email,
        },
        "products": settings.PLAID_PRODUCTS,
    }

    mock_client.LinkToken.create.assert_called_once_with(body)
