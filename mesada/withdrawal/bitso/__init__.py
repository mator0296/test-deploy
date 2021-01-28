import bitso

# from bitso import Withdrawal
from bitso.errors import ApiError
from django.conf import settings
from graphql import GraphQLError


def make_bitso_spei_withdrawal(clabe, first_name, last_name, amount):
    try:
        bitso_api = bitso.Api(settings.BITSO_API_KEY, settings.BITSO_SECRET)
        withdrawal = bitso_api.spei_withdrawal(
            amount=amount, first_names=first_name, last_names=last_name, clabe=clabe
        )
        return withdrawal

    except ApiError as err:
        """ return Withdrawal(
            wid="123456",
            currency="MXN",
            method="MXN",
            amount=amount,
            status="pending",
            created_at="01-28-2021 17:19:28.512376-04",
            details={"status": "PENDING", "message": "This withdrawal is pending"},
        ) """
        raise GraphQLError("Internal Server Error: %s" % err)
