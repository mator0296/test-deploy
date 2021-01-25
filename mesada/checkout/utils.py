from django.conf import settings
from .payment import PaymentMethodTypes


def calculate_fees(initial_amount, payment_method):
    if payment_method.type == PaymentMethodTypes.CARD:
        circle_fee = initial_amount * settings.COMMISSION_FEE_DEBIT_CARD
    elif payment_method.type == PaymentMethodTypes.ACH:
        circle_fee = initial_amount * settings.COMMISSION_FEE_ACH

    mesada_fee = initial_amount * settings.COMMISSION_FEE_MESADA

    return initial_amount - (mesada_fee + circle_fee)
