from unittest.mock import patch

import pytest
from django.conf import settings

from mesada.payment.circle import HEADERS


@pytest.mark.integration
@patch("mesada.payment.circle.requests")
def test_create_public_key(mock_requests, user_api_client):
    query = """
    mutation createPublicKey{
        createPublicKey{
            keyId
            publicKey
        }
    }
    """
    variables_values = {}
    user_api_client.post_graphql(query, variables_values)

    url = f"{settings.CIRCLE_BASE_URL}/encryption/public"
    mock_requests.request.assert_called_once_with("GET", url, headers=HEADERS)


@pytest.mark.integration
@patch("mesada.payment.circle.requests")
@patch("mesada.graphql.payment.mutations.generate_idempotency_key")
@patch("mesada.graphql.payment.mutations.hash_session_id")
def test_create_card(mock_hash_session_id, mock_idempotency_key, mock_requests, user_api_client):
    mock_idempotency_key.return_value = "mocked_idempotency_key"
    mock_hash_session_id.return_value = "mocked_hashed_session_id"
    query = """
    mutation createCard($input: CardInput!) {
        createCard(input: $input) {
            paymentMethod {
                id
            }
        }
    }
    """
    variables_values = {
        "input": {
            "encryptedData": "wcBMA0XWSFlFRpVhAQf+IXmsnGTySkDGR6EdOmL+e9FDCZxmKjkDk4oW27FpQ38JgkZmV7lokS42wxotWqNGWmOGH3UPKiqtYJhtqAR7kjqLeAJHJPloqxBqJy3lotmufuX0dtznRuAdVygQ2z0Dks5OwQe86fEX28YBxf7z75+FGUhaNYNtEH0hbsQrrsAKWzEeA75nyhGMpitkO3XdgVJ4ZD/98FJuRcInjnWLggvOaEIjJrhaLGJtlTAeJNtWtrhzRgjyYFEedXdUi4AuPv9lo7qs0iIhDOp8HfqyKtGpSbhdllx0K5e8iIx0AaPZJ99At4ODjItAyE1jt8efraNKMg3Vv+agGOzNvTdvQtJYAWmgLGcxCP8JpOiqs5CjJHh4Brrz3w5TmK6U6RIgiGRArcDB7eUqWohdoRmG9vUgj/IzHj08zGcnAxKnTtuYtc18ZM0ScjdnCcrcc1YkAvplNLbNcZDFJQ==",  # noqa: E501
            "keyId": "key1",
            "expMonth": 4,
            "expYear": 2026,
            "billingDetails": {
                "name": "Gustavo Mejia",
                "city": "Adger",
                "country": "US",
                "line1": "Address line 1",
                "line2": "Address line 2",
                "district": "AL",
                "postalCode": "35006",
            },
        }
    }
    response = user_api_client.post_graphql(query, variables_values)
    variables_values["input"]["idempotencyKey"] = mock_idempotency_key.return_value
    variables_values["input"]["metadata"] = {
        "email": user_api_client.user.email,
        "phoneNumber": str(user_api_client.user.phone),
        "sessionId": mock_hash_session_id.return_value,
        "ipAddress": response.wsgi_request.META["REMOTE_ADDR"],
    }
    url = f"{settings.CIRCLE_BASE_URL}/cards"
    mock_requests.request.assert_called_once_with("POST", url, headers=HEADERS, json=variables_values["input"])
