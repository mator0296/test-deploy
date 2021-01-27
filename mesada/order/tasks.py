from ..celery import app
from ..galactus.models import GalactusTransaction
from ..payment import PaymentStatus
from ..payment.circle import create_transfer_by_blockchain
from ..withdrawal.bitso import make_bitso_spei_withdrawal
from . import OrderStatus
from .models import Order


def confirm_order(checkout_token):
    return {
        "status": "success",
        "response_data": {"message": "The order was confirmed successfully"},
    }


@app.task
def update_pending_order_status():
    """Update the order status and trigger the following tasks depending on the current
    order status.
    """

    orders = Order.objects.select_related(
        "recipient", "payment", "user", "checkout"
    ).filter(status=OrderStatus.PENDING)
    for order in orders:
        if order.payment.status == PaymentStatus.CONFIRMED:
            create_transfer_by_blockchain(order.total_amount.amount, order.user)
            make_bitso_spei_withdrawal(
                order.recipient.clabe,
                order.recipient.first_name,
                order.recipient.last_name,
                order.recipient_amount.amount,
            )
            order_confirmation = confirm_order(order.checkout.checkout_token)
            GalactusTransaction.objects.create(**order_confirmation)
            order.status = OrderStatus.PROCESSING
            order.save(update_fields=["status"])
