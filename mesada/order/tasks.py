from ..celery import app

# from .models import Order


@app.task
def update_order_status():
    """Update the order status and trigger the following tasks depending on the current
    order status.
    """


#    orders = Order.objects.filter()
