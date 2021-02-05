from unittest.mock import patch

import pytest

from mesada.payment import PaymentMethodStatus, PaymentStatus
from mesada.payment.tasks import (
    _transition_to_status,
    check_ach_status,
    check_payment_paid_status,
    check_payment_status,
)


@patch("mesada.payment.tasks.get_payment_status")
def test_check_payment_status_confirmed(mock_get_payment_status, pending_payment):
    mock_get_payment_status.return_value = "confirmed"
    check_payment_status()
    pending_payment.refresh_from_db()

    mock_get_payment_status.assert_called_once_with(pending_payment.payment_token)
    assert pending_payment.status == PaymentStatus.CONFIRMED


@patch("mesada.payment.tasks.get_payment_status")
def test_check_payment_status_circle_error(mock_get_payment_status, pending_payment):
    mock_get_payment_status.side_effect = Exception("Circle Error")
    try:
        check_payment_status()
    except Exception:
        pending_payment.refresh_from_db()

        mock_get_payment_status.assert_called_once_with(pending_payment.payment_token)
        # Should stay pending
        assert pending_payment.status == PaymentStatus.PENDING


@patch("mesada.payment.tasks.get_ach_status")
def test_check_ach_status_complete(mock_get_ach_status, pending_ach_payment_method):
    mock_get_ach_status.return_value = "complete"
    check_ach_status()
    pending_ach_payment_method.refresh_from_db()

    mock_get_ach_status.assert_called_once_with(
        pending_ach_payment_method.payment_method_token
    )
    assert pending_ach_payment_method.status == PaymentMethodStatus.COMPLETE


@patch("mesada.payment.tasks.get_ach_status")
def test_check_ach_status_complete_circle_error(
    mock_get_ach_status, pending_ach_payment_method
):
    mock_get_ach_status.side_effect = Exception("Circle Error")
    try:
        check_ach_status()

    except Exception:
        pending_ach_payment_method.refresh_from_db()
        mock_get_ach_status.assert_called_once_with(
            pending_ach_payment_method.payment_method_token
        )
        assert pending_ach_payment_method.status == PaymentMethodStatus.PENDING


@patch("mesada.payment.tasks.get_payment_status")
def test_check_payment_status_paid(mock_get_payment_status, confirmed_payment):
    mock_get_payment_status.return_value = "paid"
    check_payment_paid_status()
    confirmed_payment.refresh_from_db()

    mock_get_payment_status.assert_called_once_with(confirmed_payment.payment_token)
    assert confirmed_payment.status == PaymentStatus.PAID


@patch("mesada.payment.tasks.get_payment_status")
def test_check_payment_status_paid_circle_error(
    mock_get_payment_status, confirmed_payment
):
    mock_get_payment_status.side_effect = Exception("Circle Error")

    try:
        check_payment_paid_status()

    except Exception:
        confirmed_payment.refresh_from_db()
        mock_get_payment_status.assert_called_once_with(confirmed_payment.payment_token)
        assert confirmed_payment.status == PaymentStatus.CONFIRMED


def test_transition_to_status(pending_payment):
    _transition_to_status(pending_payment, PaymentStatus.PAID, PaymentStatus)
    pending_payment.refresh_from_db()

    assert pending_payment.status == PaymentStatus.PAID


def test_transition_to_status_unknown_status(pending_payment):
    with pytest.raises(ValueError):
        _transition_to_status(pending_payment, "notastatus", PaymentStatus)

    pending_payment.refresh_from_db()
    assert pending_payment.status == PaymentStatus.PENDING
