import json
from unittest.mock import patch

import pytest

from mesada.checkout.utils import calculate_fees
from mesada.payment import PaymentMethodTypes


@pytest.mark.integration
@patch("mesada.graphql.checkout.mutations.generate_idempotency_key")
@patch("mesada.checkout.utils.get_amount")
def test_calculate_order_amount_no_previous_checkout(
    mock_get_amount, mock_idempotency_key, user_api_client, payment_method_ach
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
