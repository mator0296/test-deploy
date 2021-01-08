import graphene
from graphene_django.types import DjangoObjectType
from ...payment.models import PaymentMethods


class PaymentMethod(DjangoObjectType):
    class Meta:
        description = "Represents a Payment Method"
        model = PaymentMethods
        fields = "__all__"


class BillingDetailsInput(graphene.InputObjectType):
    name = graphene.String(description="Full name of the card holder", required=True)
    city = graphene.String(required=True)
    country = graphene.String(
        description="Country portion of the address. Formatted as a two-letter country code", required=True
    )
    line1 = graphene.String(description="Line one of the street address", required=True)
    line2 = graphene.String(description="Line two of the street address")
    district = graphene.String(
        description=(
            "Region portion of the address. If the country is US or Canada district is required and should use"
            " the two-letter code for the subdivision."
        )
    )
    postalCode = graphene.String(description="ZIP code of the address", required=True)
