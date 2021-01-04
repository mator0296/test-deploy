import graphene

from ..account.types import User
from ...payment.models import paymentMethods
from ..core.connection import CountableDjangoObjectType


class BillingDetailsInput(graphene.InputObjectType):
    name = graphene.String(description="Full name of the card holder", required=True)
    city = graphene.String(required=True)
    country = graphene.String(
        description="Country portion of the address. Formatted as a two-letter country code",
        required=True,
    )
    line1 = graphene.String(description="Line one of the street address", required=True)
    line2 = graphene.String(description="Line two of the street address")
    district = graphene.String(
        description="Region portion of the address. If the country is US or Canada district is required and should use the two-letter code for the subdivision."
    )
    postal_code = graphene.String(description="ZIP code of the address", required=True)


class PaymentMethod(CountableDjangoObjectType):
    type = graphene.String()
    exp_month = graphene.Int()
    exp_year = graphene.Int()
    network = graphene.String()
    last_digits = graphene.String()
    fingerprint = graphene.String()
    verification_cvv = graphene.Int()
    verification_avs = graphene.Int()
    phonenumber = graphene.String()
    email = graphene.String()
    name = graphene.String()
    address_line_1 = graphene.String()
    address_line_2 = graphene.String()
    postal_code = graphene.String()
    city = graphene.String()
    district = graphene.String()
    country_code = graphene.String()
    created = graphene.DateTime()
    updated = graphene.DateTime()
    user = graphene.Field(User)

    class Meta:
        description = "Represents a Payment Method"
        model = paymentMethods
