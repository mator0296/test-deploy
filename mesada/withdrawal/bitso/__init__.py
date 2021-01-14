import json

from bitso import Api as BitsoAPI
from bitso.errors import ApiError
from django.conf import settings


def make_bitso_spei_withdrawal(clabe, first_name, last_name, amount):
    try:
        bitso_api = BitsoAPI(settings.BITSO_API_KEY, settings.BITSO_SECRET)
        withdrawal = bitso_api.spei_withdrawal(
            amount=amount, first_names=first_name, last_names=last_name, clabe=clabe
        )
        return withdrawal

    except ApiError as e:
        #error_code = json.loads(str(e).replace("'", "\""))["code"]
        return None
