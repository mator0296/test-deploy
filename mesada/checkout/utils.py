from decimal import Decimal

import requests
from django.conf import settings
from graphql import GraphQLError

from ..payment import PaymentMethodTypes

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {123456789}",
}


def calculate_fees(
    initial_amount: str, payment_type: PaymentMethodTypes
) -> (float, float, float):
    initial_amount = Decimal(initial_amount)
    fee_debit_card = Decimal(settings.COMMISSION_FEE_DEBIT_CARD)
    fee_ach = Decimal(settings.COMMISSION_FEE_ACH)
    fee_mesada = Decimal(settings.COMMISSION_FEE_MESADA)

    if payment_type == PaymentMethodTypes.CARD:
        circle_fee = initial_amount * (fee_debit_card / 100)
    elif payment_type == PaymentMethodTypes.ACH:
        circle_fee = initial_amount * (fee_ach / 100)

    mesada_fee = initial_amount * (fee_mesada / 100)
    amount_minus_fees = str(initial_amount - (mesada_fee + circle_fee))

    return amount_minus_fees, str(circle_fee), str(mesada_fee)


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


def galactus_call(amount_to_convert, block_amount, checkout_token=None):
    if checkout_token is None:
        body = {"amountToConvert": amount_to_convert, "blockAmount": block_amount}
    else:
        body = {
            "amountToConvert": amount_to_convert,
            "blockAmount": block_amount,
            "checkoutToken": checkout_token,
        }

    galactus_response = get_amount(body)
    return galactus_response["amount"]
