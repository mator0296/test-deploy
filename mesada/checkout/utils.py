import requests
from django.conf import settings
from graphql import GraphQLError

from .payment import PaymentMethodTypes

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {123456789}",
}


def calculate_fees(initial_amount, payment_type):
    if payment_type == PaymentMethodTypes.CARD:
        circle_fee = initial_amount * (settings.COMMISSION_FEE_DEBIT_CARD / 100)
    elif payment_type == PaymentMethodTypes.ACH:
        circle_fee = initial_amount * (settings.COMMISSION_FEE_ACH / 100)

    mesada_fee = initial_amount * (settings.COMMISSION_FEE_MESADA / 100)

    return initial_amount - (mesada_fee + circle_fee)

  
def get_amount(body: dict) -> dict:
    """
    Function to get the amount from galactus
    """
    url = f"{settings.GALACTUS_URL}/get_amount"
    try:
        response = requests.request("GET", url, headers=HEADERS, json=body)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise GraphQLError("Internal Server Error: %s" % err.response.json()["message"])

    return response.json()
  