from unittest.mock import patch

import pytest
from bitso import Withdrawal

from ..utils import random_numbers

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
