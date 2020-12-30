import graphene

from ...payment.models import paymentMethods
from ..core.connection import CountableDjangoObjectType


class BillingDetailsInput(graphene.InputObjectType):
    name = graphene.String(
        description="Full name of the card holder",
        required=True
    )
    city = graphene.String(required=True)
    country = graphene.String(
        description="Country portion of the address. Formatted as a two-letter country code",
        required=True,
    )
    line1 = graphene.String(
        description="Line one of the street address",
        required=True
    )
    line2 = graphene.String(description="Line two of the street address")
    district = graphene.String(
        description="Region portion of the address. If the country is US or Canada district is required and should use the two-letter code for the subdivision."
    )
    postal_code = graphene.String(
        description="ZIP code of the address",
        required=True
    )


class Card(graphene.ObjectType):
    encrypted_data = graphene.String(
        description="Card encrypted data",
        required=True
    )
    key_id = graphene.String(description="Encryption key", required=True)
    exp_month = graphene.Int(
        description="Card expiration month",
        required=True
    )
    exp_year = graphene.Int(description="Card expiration year", required=True)


class PaymentMethod(CountableDjangoObjectType):
    type = graphene.String()

    class Meta:
        description = "Represents a Payment Method"
        model = paymentMethods
