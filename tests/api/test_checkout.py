from unittest.mock import patch

import pytest

from ..utils import _get_graphql_content_from_response, get_graphql_content

from mesada.checkout.utils import calculate_fees
from mesada.payment import PaymentMethodTypes


@pytest.mark.integration
@patch("mesada.graphql.checkout.mutations.generate_idempotency_key")
@patch("mesada.checkout.utils.get_amount")
def test_calculate_order_amount_no_previous_checkout(
    mock_get_amount, mock_idempotency_key, payment_method_ach, user_api_client
):
    mock_get_amount.return_value = {"amount": "123.0", "blockAmount": True}
    mock_idempotency_key.return_value = "mocked_idempotency_key"
    query = """
    mutation calculateOrderAmount($input: CalculateOrderAmountInput!) {
        calculateOrderAmount(input: $input) {
            amountToConvert
            feesAmount
            mesadaFeeAmount
            totalAmount
            blockAmount
            checkout {
                id
                checkoutToken
            }
        }
    }
    """
    variables_values = {
        "input": {"initialAmount": "100.0", "paymentMethod": payment_method_ach.pk}
    }
    response = user_api_client.post_graphql(query, variables_values)
    galactus_amount_to_convert = str(calculate_fees("100.0", PaymentMethodTypes.ACH)[0])
    galactus_body = {
        "amountToConvert": galactus_amount_to_convert,
        "blockAmount": True,
        "checkoutToken": "mocked_idempotency_key",
    }
    mock_get_amount.assert_called_once_with(galactus_body)
    content = get_graphql_content(response)
    data = content["data"]["calculateOrderAmount"]
    assert data["amountToConvert"] is not None
    assert data["checkout"] is not None


@pytest.mark.integration
@patch("mesada.graphql.checkout.mutations.generate_idempotency_key")
@patch("mesada.checkout.utils.get_amount")
def test_calculate_order_amount_with_previous_checkout(
    mock_get_amount, mock_idempotency_key, payment_method_ach, checkout, user_api_client
):
    mock_get_amount.return_value = {"amount": "123.0", "blockAmount": True}
    mock_idempotency_key.return_value = "mocked_idempotency_key"
    query = """
    mutation calculateOrderAmount($input: CalculateOrderAmountInput!) {
        calculateOrderAmount(input: $input) {
            amountToConvert
            feesAmount
            mesadaFeeAmount
            totalAmount
            blockAmount
            checkout {
                id
                checkoutToken
                totalAmount
            }
        }
    }
    """
    variables_values = {
        "input": {"initialAmount": "100.0", "paymentMethod": payment_method_ach.pk}
    }
    response = user_api_client.post_graphql(query, variables_values)
    galactus_amount_to_convert = str(calculate_fees("100.0", PaymentMethodTypes.ACH)[0])
    galactus_body = {
        "amountToConvert": galactus_amount_to_convert,
        "blockAmount": True,
        "checkoutToken": checkout.checkout_token,
    }
    mock_get_amount.assert_called_once_with(galactus_body)
    content = get_graphql_content(response)
    data = content["data"]["calculateOrderAmount"]
    assert data["amountToConvert"] is not None
    assert data["checkout"] is not None
    assert data["checkout"]["checkoutToken"] == checkout.checkout_token


def test_checkout_create_success(user_api_client):
    query = """
    mutation checkoutCreate {
        checkoutCreate {
            checkout {
                id
                checkoutToken
                amount
                fees
                totalAmount
                recipientAmount
                user {
                    id
                }
                recipient {
                    id
                }
                paymentMethod {
                    id
                }
                status
                active
            }
        }
    }
    """
    variables_values = {}
    response = user_api_client.post_graphql(query, variables_values)
    content = get_graphql_content(response)
    data = content["data"]["checkoutCreate"]
    assert data["checkout"] is not None
    assert data["checkout"]["checkoutToken"] is not None
    assert data["checkout"]["user"] is not None
    assert data["checkout"]["amount"] is None


def test_checkout_update_success1(
    recipient, payment_method_ach, checkout, user_api_client
):
    query = """
    mutation checkoutUpdate($input: CheckoutInput!) {
        checkoutUpdate(input: $input) {
            checkout {
                id
                checkoutToken
                amount
                fees
                totalAmount
                recipientAmount
                user {
                    id
                }
                recipient {
                    id
                    firstName
                }
            }
        }
    }
    """
    variables_values = {
        "input": {
            "amount": "999.9",
            "fees": "5.25",
            "totalAmount": "1005.25",
            "recipient": recipient.pk,
        }
    }
    response = user_api_client.post_graphql(query, variables_values)
    content = get_graphql_content(response)
    data = content["data"]["checkoutUpdate"]
    assert data["checkout"] is not None
    assert data["checkout"]["checkoutToken"] == checkout.checkout_token
    assert data["checkout"]["recipient"]["firstName"] == "Alexander"
    assert data["checkout"]["recipientAmount"] == "45.5000"


def test_checkout_update_success2(
    recipient, payment_method_ach, checkout, user_api_client
):
    query = """
    mutation checkoutUpdate($input: CheckoutInput!) {
        checkoutUpdate(input: $input) {
            checkout {
                id
                checkoutToken
                amount
                fees
                totalAmount
                recipientAmount
                user {
                    id
                }
                recipient {
                    id
                    firstName
                }
            }
        }
    }
    """
    variables_values = {"input": {"recipientAmount": "99.90"}}
    response = user_api_client.post_graphql(query, variables_values)
    content = get_graphql_content(response)
    data = content["data"]["checkoutUpdate"]
    assert data["checkout"] is not None
    assert data["checkout"]["checkoutToken"] == checkout.checkout_token
    assert data["checkout"]["recipient"]["firstName"] == "Daniel"
    assert data["checkout"]["recipientAmount"] == "99.9000"


def test_query_checkout_success(checkout, user_api_client):
    query = """
    query checkoutQuery {
        checkout {
            id
            amount
            fees
            totalAmount
            user {
                id
            }
            recipient {
                id
            }
        }
    }
    """
    variables_values = {}
    response = user_api_client.post_graphql(query, variables_values)
    content = get_graphql_content(response)
    data = content["data"]["checkout"]
    assert data["id"]


def test_query_checkout_failure(user_api_client):
    query = """
    query checkoutQuery {
        checkout {
            id
            amount
            fees
            totalAmount
            user {
                id
            }
            recipient {
                id
            }
        }
    }
    """
    variables_values = {}
    response = user_api_client.post_graphql(query, variables_values)
    content = _get_graphql_content_from_response(response)
    expected_message = "Internal Server Error: Checkout matching query does not exist."
    assert "errors" in content
    assert content["errors"][0]["message"] == expected_message
