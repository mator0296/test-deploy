from unittest.mock import patch

import pytest
from django.conf import settings

from mesada.payment.circle import HEADERS
from mesada.payment.models import PaymentMethods


@pytest.mark.integration
@patch("mesada.payment.circle.requests")
def test_create_public_key(mock_requests, user_api_client):
    query = """
    mutation createPublicKey{
        createPublicKey{
            keyId
            publicKey
            errors{
            field
            message
            }
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
