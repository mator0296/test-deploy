from ..celery import app
from .models import Order
from . import OrderStatus
from ..payment import PaymentStatus
from ..payment.circle import create_transfer_by_blockchain
from ..withdrawal.bitso import make_bitso_spei_withdrawal


@app.task
def update_pending_order_status():
    """Update the order status and trigger the following tasks depending on the current
    order status.
    """

    orders = Order.objects.filter(status=OrderStatus.PENDING)
    for order in orders:
        if order.payment.status == PaymentStatus.CONFIRMED:
            pass
