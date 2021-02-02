from unittest.mock import patch

import pytest

from ..utils import get_graphql_content

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


def test_checkout_create_success(recipient, payment_method_ach, user_api_client):
    query = """
    mutation checkoutCreate($input: CheckoutInput!) {
        checkoutCreate(input: $input) {
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
    variables_values = {
        "input": {
            "amount": "200.0",
            "fees": "1.25",
            "totalAmount": "201.25",
            "recipientAmount": "55.5",
            "recipient": recipient.pk,
            "paymentMethod": payment_method_ach.pk,
        }
    }
    response = user_api_client.post_graphql(query, variables_values)
    content = get_graphql_content(response)
    data = content["data"]["checkoutCreate"]
    assert data["checkout"] is not None
    assert data["checkout"]["checkoutToken"] is not None


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
    assert data["checkout"]["recipientAmount"] == "$45.50"


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
    assert data["checkout"]["recipientAmount"] == "$99.90"


def test_query_checkout(checkout, user_api_client):
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
