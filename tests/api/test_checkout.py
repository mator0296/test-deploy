import json
from unittest.mock import patch

import pytest

from mesada.checkout.utils import calculate_fees
from mesada.payment import PaymentMethodTypes


@pytest.mark.integration
@patch("mesada.graphql.checkout.mutations.generate_idempotency_key")
@patch("mesada.checkout.utils.get_amount")
def test_calculate_order_amount_no_previous_checkout(
    mock_get_amount, mock_idempotency_key, payment_method_ach, user_api_client
):
    mock_get_amount.return_value = {"amount": "123123.0", "blockAmount": True}
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
    content = json.loads(response.content)
    assert "errors" not in content
    mock_get_amount.assert_called_once_with(galactus_body)


@pytest.mark.integration
@patch("mesada.graphql.checkout.mutations.generate_idempotency_key")
@patch("mesada.checkout.utils.get_amount")
def test_calculate_order_amount_with_previous_checkout(
    mock_get_amount, mock_idempotency_key, payment_method_ach, checkout, user_api_client
):
    mock_get_amount.return_value = {"amount": "123123.0", "blockAmount": True}
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
    content = json.loads(response.content)
    assert "errors" not in content
    mock_get_amount.assert_called_once_with(galactus_body)


def test_checkout_create_success(recipient, payment_method_ach, user_api_client):
    query = """
        mutation checkoutCreate($input: CheckoutCreateInput!) {
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
            "amount": "1000.0",
            "fees": "1.50",
            "totalAmount": "1001.5",
            "recipientAmount": "50.25",
            "recipient": recipient.pk,
            "paymentMethod": payment_method_ach.pk,
        }
    }
    response = user_api_client.post_graphql(query, variables_values)
    content = json.loads(response.content)
    assert "errors" not in content


def test_checkout_update_success(
    recipient, payment_method_ach, checkout, user_api_client
):
    query = """
        mutation checkoutUpdate($input: CheckoutUpdateInput!) {
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
            "recipientAmount": "255.75",
            "recipient": recipient.pk,
        }
    }
    response = user_api_client.post_graphql(query, variables_values)
    content = json.loads(response.content)
    assert "errors" not in content
