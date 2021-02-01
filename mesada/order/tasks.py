from djmoney.money import Money

from ..celery import app
from ..galactus import GalactusStatus
from ..galactus.models import GalactusTransaction
from ..payment import PaymentStatus
from ..payment.circle import create_transfer_by_blockchain
from ..withdrawal.bitso import make_bitso_spei_withdrawal
from ..withdrawal.models import BitsoSpeiWithdrawal
from . import OrderStatus
from .models import Order


def confirm_order(checkout_token):
    return {
        "status": "success",
        "response_data": {"message": "The order was confirmed successfully"},
    }


def check_transaction_status(checkout_token):
    return {
        "status": "success",
        "response_data": {"message": "The order was confirmed successfully"},
    }


@app.task
def update_pending_order_status():
    """Update the order status of a pending order and trigger the following tasks
    depending on the current order status.
    """

    orders = Order.objects.select_related(
        "recipient", "payment", "user", "checkout"
    ).filter(status=OrderStatus.PENDING)

    for order in orders:
        if order.payment.status == PaymentStatus.CONFIRMED:
            order_confirmation = confirm_order(
                order.checkout.checkout_token
            )  # TODO: Connect to the real Galactus service
            circle_transfer = create_transfer_by_blockchain(
                order.total_amount.amount, order.user
            )
            withdrawal = make_bitso_spei_withdrawal(
                order.recipient.clabe,
                order.recipient.first_name,
                order.recipient.last_name,
                order.recipient_amount.amount,
            )

            bitso_spei_withdrawal = BitsoSpeiWithdrawal.objects.create(
                amount=Money(
                    withdrawal._default_params.pop("amount"), withdrawal.currency
                ),
                user=order.user,
                **withdrawal._default_params
            )
            galactus_transactions = GalactusTransaction.objects.create(
                **order_confirmation
            )

            order.status = OrderStatus.PROCESSING
            order.circle_transfer = circle_transfer
            order.withdrawal = bitso_spei_withdrawal
            order.galactus_transaction = galactus_transactions
            order.save(
                update_fields=[
                    "status",
                    "circle_transfer",
                    "withdrawal",
                    "galactus_transaction",
                ]
            )


@app.task
def update_processing_order_status():
    """Update the order status of a processing order."""

    orders = Order.objects.filter(status=OrderStatus.PROCESSING)

    for order in orders:
        if order.operational_status != OrderStatus.PENDING:
            order.status = order.operational_status
            order.transfer
            order.save(update_fields=["status"])


def update_galactus_transaction_status():
    """Update all pending galactus_transaction status."""
    # TODO: Connect to the real Galactus service

    transactions = GalactusTransaction.objects.filter(status=GalactusStatus.PENDING)
    for transaction in transactions:
        response = check_transaction_status(transaction.id)
        transaction.status = response.get("status")
        transaction.response_data = response.get("response_data")
        transaction.save()
