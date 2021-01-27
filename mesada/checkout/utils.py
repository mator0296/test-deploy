from django.conf import settings

from .payment import PaymentMethodTypes


def calculate_fees(initial_amount, payment_type):
    if payment_type == PaymentMethodTypes.CARD:
        circle_fee = initial_amount * (settings.COMMISSION_FEE_DEBIT_CARD / 100)
    elif payment_type == PaymentMethodTypes.ACH:
        circle_fee = initial_amount * (settings.COMMISSION_FEE_ACH / 100)

    mesada_fee = initial_amount * (settings.COMMISSION_FEE_MESADA / 100)

    return initial_amount - (mesada_fee + circle_fee)
