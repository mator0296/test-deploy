from unittest.mock import patch

import pytest
from bitso import Withdrawal

from ..conftest import random_numbers

from mesada.order import OrderStatus
from mesada.order.tasks import update_pending_order_status
from mesada.transfer.models import CircleTransfer, CircleTransferStatus


@pytest.mark.integration
@patch("mesada.order.tasks.create_transfer_by_blockchain")
@patch("mesada.order.tasks.make_bitso_spei_withdrawal")
@patch("mesada.order.tasks.confirm_order")
def test_update_pending_order_status(
    mock_confirm_order, mock_withdrawal, mock_transfer, order
):
    mock_transfer.return_value = CircleTransfer.objects.create(
        transfer_id=random_numbers(8),
        source_type="wallet",
        source_id=random_numbers(5),
        destination_type="blockchain",
        destination_address="0x8381470ED67C3802402dbbFa0058E8871F017A6F",
        destination_chain="ETH",
        amount=order.total_amount,
        status=CircleTransferStatus.PENDING,
        create_date="2020-04-10",
        user_id=order.user,
    )
    mock_withdrawal.return_value = Withdrawal(
        wid=random_numbers(8),
        currency="MXN",
        method="MXN",
        amount=order.recipient_amount.amount,
        status="pending",
        created_at="01-28-2021 17:19:28.512376-04",
        details={"status": "PENDING", "message": "This withdrawal is pending"},
    )
    mock_confirm_order.return_value = {
        "status": "success",
        "response_data": {"message": "The order was confirmed successfully"},
    }
    update_pending_order_status()
    mock_transfer.assert_called_once_with(order.total_amount.amount, order.user)
    mock_withdrawal.assert_called_once_with(
        order.recipient.clabe,
        order.recipient.first_name,
        order.recipient.last_name,
        order.recipient_amount.amount,
    )
    mock_confirm_order.assert_called_once_with(order.checkout.checkout_token)
    order.refresh_from_db()
    assert order.status == OrderStatus.PROCESSING


@pytest.mark.integration
@patch("mesada.graphql.order.mutations.CreateOrder.create_order_payment")
@patch("mesada.graphql.order.mutations.hash_session_id")
@patch("mesada.graphql.order.mutations.Payment.objects.create")
@patch("mesada.graphql.order.mutations.Order.objects.create")
def test_create_order(
    mock_order,
    mock_payment,
    mock_hash_session_id,
    mock_create_payment,
    user_api_client,
    checkout,
    payment,
):
    mock_hash_session_id.return_value = "return_value"
    mock_payment.return_value = payment
    mock_create_payment.return_value = {
        "id": "0620c4dd-eb27-44e9-bb92-35c7ce9deacd",
        "type": "payment",
        "merchantId": "8f1a836b-cc7b-4e62-ac76-e89a15e59d76",
        "merchantWalletId": "1000059237",
        "source": {"id": "851aab36-006c-4eef-83f1-bb2bd486efaa", "type": "card"},
        "description": "Description for new payment.",
        "amount": {"amount": "100.00", "currency": "USD"},
        "status": "pending",
        "refunds": [],
        "createDate": "2021-02-01T18:36:04.504Z",
        "updateDate": "2021-02-01T18:36:04.504Z",
        "metadata": {"phoneNumber": "+16167144457", "email": "test@mail.com"},
    }
    query = """
    mutation createOrder {
        createOrder {
            order {
            id
            }
            errors{
            field
            message
            }
        }
        }
    """
    variables_values = {}
    response = user_api_client.post_graphql(query, variables_values)
    mock_create_payment.assert_called_once_with(
        checkout,
        mock_hash_session_id.return_value,
        response.wsgi_request.META["REMOTE_ADDR"],
    )
    mock_order.assert_called_once_with(
        checkout_id=checkout.id,
        status=OrderStatus.PENDING,
        amount=checkout.amount,
        fees=checkout.fees,
        total_amount=checkout.total_amount,
        recipient_amount=checkout.recipient_amount,
        user_id=checkout.user_id,
        recipient_id=checkout.recipient_id,
        payment_method_id=checkout.payment_method_id,
        payment_id=payment.id,
    )
    checkout.refresh_from_db()
    assert checkout.active is False
