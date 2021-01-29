from unittest.mock import patch

import pytest
from bitso import Withdrawal

from ..utils import random_numbers

from mesada.order.tasks import update_pending_order_status
from mesada.transfer.models import CircleTransfer

@pytest.mark.integration
@patch("mesada.order.tasks.create_transfer_by_blockchain")
@patch("mesada.order.tasks.make_bitso_spei_withdrawal")
def test_update_pending_order_status(mock_withdrawal, mock_transfer, order):
    mock_transfer.return_value = CircleTransfer()
    mock_withdrawal.return_value = Withdrawal(
        wid=random_numbers(8),
        currency="MXN",
        method="MXN",
        amount=order.recipient_amount.amount,
        status="pending",
        created_at="01-28-2021 17:19:28.512376-04",
        details={"status": "PENDING", "message": "This withdrawal is pending"},
    )
    update_pending_order_status()
    mock_transfer.assert_called_once_with(order.total_amount.amount, order.user)
