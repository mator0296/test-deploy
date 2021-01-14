from bitso import Api as BitsoAPI
from django.conf import settings


def make_bitso_sei_withdrawal(clabe, first_name, last_name, amount):
    bitso_api = BitsoAPI(settings.BITSO_API_KEY, settings.BITSO_SECRET)
    withdrawal = bitso_api.spei_withdrawal(
        amount=amount, first_names=first_name, last_names=last_name, clabe=clabe
    )
    return withdrawal
