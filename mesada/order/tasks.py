from ..celery import app
from ..galactus import GalactusStatus
from ..galactus.models import GalactusTransaction


def check_transaction_status(id):
    return {
        "status": "success",
        "response_data": {"message": "The order was confirmed successfully"},
    }


@app.task
def update_galactus_transaction_status():
    # TODO: Connect to the real Galatus service

    transactions = GalactusTransaction.objects.filter(status=GalactusStatus.PENDING)
    for transaction in transactions:
        response = check_transaction_status(transaction.id)
        transaction.status = response.get("status")
        transaction.response_data = response.get("response_data")
        transaction.save()
