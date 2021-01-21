from unittest.mock import Mock, patch

import pytest
from django.conf import settings

from mesada.account.models import User
from mesada.payment.circle import (
    HEADERS,
    create_transfer_by_blockchain,
    register_ach,
    get_circle_transfer_status,
)
from mesada.payment.models import PaymentMethods
from mesada.transfer.models import CircleTransfer


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


@pytest.mark.integration
@patch("mesada.payment.circle.requests")
@patch("mesada.graphql.payment.mutations.generate_idempotency_key")
@patch("mesada.graphql.payment.mutations.hash_session_id")
@patch("mesada.graphql.payment.mutations.PaymentMethods")
def test_create_payment(
    mock_payment_methods, mock_hash_session_id, mock_idempotency_key, mock_requests, user_api_client
):
    mock_idempotency_key.return_value = "mocked_idempotency_key"
    mock_hash_session_id.return_value = "mocked_hashed_session_id"
    mock_payment_methods.objects.get.return_value = PaymentMethods(
        payment_method_token="bbbeefe7-6349-4834-a386-6f49c76f1712", phonenumber="+15417543010", email="test@mail.com"
    )
    query = """
    mutation createPayment($type: String!, $paymentMethod: Int!, $amount: Float!, $currency: String, $description: String){  # noqa: E501
        createPayment(type: $type, paymentMethod: $paymentMethod, amount: $amount, currency: $currency, description: $description) {  # noqa: E501
            payment{
                id
            }
        }
    }
    """
    variables_values = {
        "type": "CARD",
        "paymentMethod": 1,
        "amount": 100,
        "currency": "USD",
        "description": "Description for new payment.",
    }

    response = user_api_client.post_graphql(query, variables_values)
    body = {
        "idempotencyKey": mock_idempotency_key.return_value,
        "amount": {"amount": str(float(variables_values["amount"])), "currency": variables_values["currency"]},
        "source": {
            "id": mock_payment_methods.objects.get.return_value.payment_method_token,
            "type": variables_values["type"].lower(),
        },
        "description": variables_values["description"],
        "metadata": {
            "email": mock_payment_methods.objects.get.return_value.email,
            "phoneNumber": mock_payment_methods.objects.get.return_value.phonenumber,
            "sessionId": mock_hash_session_id.return_value,
            "ipAddress": response.wsgi_request.META["REMOTE_ADDR"],
        },
        "verification": "none",
    }
    url = f"{settings.CIRCLE_BASE_URL}/payments"
    mock_requests.request.assert_called_once_with("POST", url, headers=HEADERS, json=body)


@pytest.mark.integration
@patch("mesada.payment.circle.requests")
@patch("mesada.payment.circle.generate_idempotency_key")
def test_register_ach(mock_idempotency_key, mock_requests):
    payment_method = Mock()
    url = f"{settings.CIRCLE_BASE_URL}/banks/ach"
    body = {
        "idempotencyKey": mock_idempotency_key.return_value,
        "plaidProcessorToken": payment_method.processor_token,
        "billingDetails": {
            "name": payment_method.name,
            "city": payment_method.city,
            "country": payment_method.country_code.code,
            "line1": payment_method.address_line_1,
            "line2": payment_method.address_line_2,
            "district": payment_method.district,
            "postalCode": payment_method.postal_code,
        },
    }

    register_ach(payment_method)
    mock_requests.request.assert_called_once_with("POST", url, headers=HEADERS, json=body)


def mocked_create(**kwargs):
    """Created to mock the create method of CircleTransfer.objects."""
    pass


@pytest.mark.integration
@patch("mesada.payment.circle.requests")
@patch("mesada.payment.circle.generate_idempotency_key")
@patch("mesada.payment.circle.dateparse")
@patch.object(CircleTransfer.objects, "create", side_effect=mocked_create)
def test_create_transfer_by_blockchain(mock_CircleTransfer, mock_dateparse, mock_idempotency_key, mock_requests):
    user = User()
    amount = 100

    payload = {
        "source": {"type": "wallet", "id": f"{settings.CIRCLE_WALLET_ID}"},
        "destination": {
            "type": "blockchain",
            "address": f"{settings.BITSO_BLOCKCHAIN_ADDRESS}",
            "chain": f"{settings.CIRCLE_BLOCKCHAIN_CHAIN}",
        },
        "amount": {"amount": "{:.2f}".format(amount), "currency": "USD"},
        "idempotencyKey": mock_idempotency_key.return_value,
    }
    url = f"{settings.CIRCLE_BASE_URL}/transfers"

    create_transfer_by_blockchain(amount=amount, user=user)
    mock_dateparse.parse_datetime.return_value = "2020-01-15"
    mock_requests.request("POST", url, headers=HEADERS, json=payload)


@pytest.mark.integration
@patch("mesada.payment.circle.requests")
def test_get_transfer_status(mock_requests, user_api_client):
    transfer_id = "11652dfa-8511-40fd-99bb-a76d6869d71c"
    get_circle_transfer_status(transfer_id)
    url = f"{settings.CIRCLE_BASE_URL}/transfers/{transfer_id}"
    mock_requests.request.assert_called_once_with("GET", url, headers=HEADERS)
